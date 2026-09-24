import json
from ollama import chat

PLANNER_SYSTEM_PROMPT = """
You are a Planner Agent in a multi-agent software engineering system.

Your role:
- You receive validated requirements from an Analyst Agent.
- You must decide HOW the software (a robot navigation system) should behave.
- You produce a navigation plan in strict JSON format.

The robot can only perform these actions: FORWARD, LEFT, RIGHT, STOP.

You must output ONLY a valid JSON object with EXACTLY this structure:
{
    "strategy": "A short description of the navigation strategy",
    "decisions": [
        "A list of decisions the robot can take during navigation",
        "Each decision must be a string",
        "Decisions should reference only FORWARD, LEFT, RIGHT, STOP"
    ],
    "stop_condition": "The exact point/condition at which the robot must stop"
}

Rules:
- Do NOT include any explanation, markdown, or text outside the JSON.
- Do NOT add extra keys.
- "decisions" must be a non-empty list of strings.
- "strategy" and "stop_condition" must be non-empty strings.
- Only use the allowed actions: FORWARD, LEFT, RIGHT, STOP.
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

    raw = response["message"]["content"]

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