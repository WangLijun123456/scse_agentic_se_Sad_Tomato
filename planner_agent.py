import json
from ollama import chat

PLANNER_SYSTEM_PROMPT = """
You are a Planner Agent. You receive validated requirements and produce a navigation plan.
The robot can only perform: FORWARD, LEFT, RIGHT, STOP.
The robot perceives these booleans:
  goal_ahead, goal_on_left, goal_on_right,
  front_blocked, left_blocked, right_blocked
Navigation rules:
1. Never move into a blocked direction.
2. Prefer moving toward the goal when safe.
3. If front is blocked, try LEFT or RIGHT toward a safe direction.
4. If all directions are blocked -> STOP.
5. If the goal is on the left but left is blocked, and front is clear, then FORWARD.
6. If the goal is on the right but right is blocked, and front is clear, then FORWARD.
Output ONLY a JSON object with EXACTLY these three keys:
{
  "strategy":   "short description of the navigation strategy",
  "decisions":  [list of conditional rules],
  "stop_condition": "when the robot must stop"
}
Rules for "decisions":
- Each entry MUST be a conditional sentence.
- Each entry MUST reference the state fields above.
- Each entry MUST end with exactly one of: FORWARD, LEFT, RIGHT, STOP.
- BAD : "FORWARD"
- GOOD: "If goal_ahead is true and front_blocked is false, then FORWARD."
Do NOT add extra keys or text outside the JSON.
"""


def validate_plan(data):
    if not isinstance(data, dict):
        return False

    required_keys = {"strategy", "decisions", "stop_condition"}
    if set(data.keys()) != required_keys:
        return False

    if not isinstance(data["strategy"], str) or not data["strategy"].strip():
        return False

    if not isinstance(data["decisions"], list) or len(data["decisions"]) == 0:
        return False
    for d in data["decisions"]:
        if not isinstance(d, str) or not d.strip():
            return False
        if not any(action in d.upper() for action in ["FORWARD", "LEFT", "RIGHT", "STOP"]):
            return False

    if not isinstance(data["stop_condition"], str) or not data["stop_condition"].strip():
        return False

    return True


def run_planner(requirement):
    requirement_text = (
        json.dumps(requirement, indent=2)
        if isinstance(requirement, dict)
        else str(requirement)
    )

    user_prompt = (
        "Here are the validated requirements from the Analyst Agent:\n"
        f"{requirement_text}\n\n"
        "Based on these requirements, produce the navigation plan as a strict JSON object."
    )

    response = chat(
        model="qwen3:8b",
        messages=[
            {"role": "system", "content": PLANNER_SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
        format="json",
    )

    raw = response.message.content

    try:
        plan = json.loads(raw)
    except json.JSONDecodeError:
        start = raw.find("{")
        end = raw.rfind("}") + 1
        if start == -1 or end == 0:
            raise ValueError(f"Planner did not return valid JSON:\n{raw}")
        plan = json.loads(raw[start:end])

    if not validate_plan(plan):
        raise ValueError(f"Planner returned an invalid plan:\n{plan}")

    return plan