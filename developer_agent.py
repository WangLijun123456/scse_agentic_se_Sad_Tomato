import json
import re
from ollama import chat

DEVELOPER_SYSTEM_PROMPT = """
You are a Developer Agent in a multi-agent software engineering system.
Your role:
- You receive a validated navigation plan from a Planner Agent.
- You must generate Python code that implements the robot navigation logic.

The robot can only perform these actions: FORWARD, LEFT, RIGHT, STOP.

Hard requirements you MUST obey:
1. You MUST use ALL four possible actions (FORWARD, LEFT, RIGHT, STOP) inside the navigate function logic.
2. When obstacle_ahead is detected: first attempt to turn LEFT or RIGHT to avoid obstacle. Only execute STOP when turning is not possible.
3. Strictly follow strategy, decisions list, and stop_condition given in the input plan.
4. Use perception.get(key, False) to safely read values from perception dictionary to avoid KeyError.

CRITICAL OUTPUT REQUIREMENT:
- The code MUST define a main function called `decide_next_move(state)` that:
    * Takes a `state` dictionary as input.
    * Returns one of the exact uppercase strings: "FORWARD", "LEFT", "RIGHT", or "STOP".
- The original `navigate(perception)` function MUST be retained.
- `decide_next_move(state)` MUST call `navigate(state)` internally.
- No other helper functions should be called by external programs; only `decide_next_move(state)`.

The `state` dictionary contains these keys:
    - goal_ahead (bool)
    - goal_on_left (bool)
    - goal_on_right (bool)
    - front_blocked (bool)
    - left_blocked (bool)
    - right_blocked (bool)

Output rules:
- Output ONLY valid Python code, nothing else.
- Do NOT include markdown fences (no ```python).
- The code must be syntactically correct Python 3.
- Include a short module-level docstring describing the logic.
"""


def validate_code(code):
    if not isinstance(code, str) or not code.strip():
        print("Validation failed: code is empty or not a string")
        return False

    try:
        compile(code, "<developer_output>", "exec")
    except SyntaxError as e:
        print(f"Validation failed: SyntaxError - {e}")
        return False

    if "def navigate" not in code:
        print("Validation failed: 'def navigate' not found")
        return False

    if "def decide_next_move" not in code:
        print("Validation failed: 'def decide_next_move' not found")
        return False

    required_actions = ["FORWARD", "LEFT", "RIGHT", "STOP"]
    for act in required_actions:
        if act not in code:
            print(f"Validation failed: action '{act}' not found in code")
            return False

    return True


def run_developer(plan):
    plan_text = json.dumps(plan, indent=2) if isinstance(plan, dict) else str(plan)
    user_prompt = (
        "Here is the validated navigation plan from the Planner Agent:\n"
        f"{plan_text}\n\n"
        "Generate the Python navigation code as specified. "
        "Remember: the code MUST define both `navigate(perception)` and "
        "`decide_next_move(state)`, where `decide_next_move` calls `navigate`."
    )

    response = chat(
        model="qwen3:8b",
        messages=[
            {"role": "system", "content": DEVELOPER_SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
    )

    raw_content = getattr(response, "message", None)
    if raw_content is None:
        raw_content = response["message"]
    raw_content = getattr(raw_content, "content", None) or raw_content["content"]
    raw_content = raw_content.strip()

    code_match = re.search(
        r"```(?:python)?\s*(.*?)```",
        raw_content,
        re.DOTALL | re.IGNORECASE,
    )
    if code_match:
        code = code_match.group(1).strip()
    else:
        code = raw_content

    code = code.replace("```", "").strip()

    if not validate_code(code):
        print("DEBUG: Extracted code (repr):", repr(code))
        raise ValueError(f"Developer returned invalid Python code:\n{code}")

    return code