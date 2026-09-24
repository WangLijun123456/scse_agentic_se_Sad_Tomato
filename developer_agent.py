## The logic is fairly similar to the Analyst and Planner agents
import json
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

Output rules:
- Output ONLY valid Python code, nothing else.
- Do NOT include markdown fences (no ```python).
- The code must define a function called `navigate(perception)` that:
    * Takes a `perception` dictionary as input.
    * Returns one of the exact uppercase strings: "FORWARD", "LEFT", "RIGHT", or "STOP".
- The code must follow the strategy, decisions, and stop_condition from the plan.
- The code must be syntactically correct Python 3.
- Include a short module‑level docstring describing the logic.
"""


def validate_code(code):
    if not isinstance(code, str) or not code.strip():
        return False

    try:
        compile(code, "<developer_output>", "exec")
    except SyntaxError:
        return False

    if "def navigate" not in code:
        return False

    required_actions = ["FORWARD", "LEFT", "RIGHT", "STOP"]
    for act in required_actions:
        if act not in code:
            return False

    return True


def run_developer(plan):
    plan_text = json.dumps(plan, indent=2) if isinstance(plan, dict) else str(plan)
    user_prompt = (
        "Here is the validated navigation plan from the Planner Agent:\n"
        f"{plan_text}\n\n"
        "Generate the Python navigation code as specified."
    )

    response = chat(
        model="qwen3:8b",
        messages=[
            {"role": "system", "content": DEVELOPER_SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
    )
    code = response["message"]["content"].strip()

    if code.startswith("```"):
        lines = [l for l in code.splitlines() if not l.strip().startswith("```")]
        code = "\n".join(lines).strip()

    if not validate_code(code):
        raise ValueError(f"Developer returned invalid Python code:\n{code}")

    return code
