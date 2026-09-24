import json
import re
from ollama import chat

SYSTEM_PROMPT = """
You are a Requirements Engineer for a robot navigation system.
Your job is to read a human-language brief and convert it into explicit,
structured software requirements.
Your responsibilities:
- Analyze the brief text carefully.
- Extract the navigation goal.
- Determine which actions the robot is allowed to take.
- Determine whether the robot must stop safely when it cannot move.
- Determine whether the robot must avoid obstacles.
Rules and constraints (STRICT):
1. Respond ONLY with a single, valid JSON object.
2. Do NOT include any conversational filler.
3. Do NOT include markdown formatting blocks (like ```json).
4. Do NOT include any extra text before or after the JSON.
5. The JSON must contain EXACTLY these four keys:
   - "goal": a string describing the navigation objective.
   - "allowed_actions": a list of allowed actions.
     Allowed values are ONLY: "FORWARD", "LEFT", "RIGHT", "STOP".
     Do NOT invent any other action.
   - "safe_stop": a boolean (true/false).
   - "avoid_obstacles": a boolean (true/false).
6. Do NOT add any extra keys.
7. Do NOT rename the keys.
8. Do NOT use any action other than "FORWARD", "LEFT", "RIGHT", "STOP".
JSON Schema:
{
  "goal": "string",
  "allowed_actions": ["FORWARD", "LEFT", "RIGHT", "STOP"],
  "safe_stop": true,
  "avoid_obstacles": true
}
""".strip()


VALID_ACTIONS = {"FORWARD", "LEFT", "RIGHT", "STOP"}
REQUIRED_KEYS = {"goal", "allowed_actions", "safe_stop", "avoid_obstacles"}
MODEL_NAME = "qwen3:8b"

def call_qwen(messages, temperature=0.0):
    """
    messages: [{"role": "system", "content": ...},
               {"role": "user", "content": ...}]
    """
    response = chat(
        model=MODEL_NAME,
        messages=messages,
        think=False,
        options={"temperature": temperature},
    )
    return response.message.content

def _clean_json_text(text):
    if text is None:
        return ""
    text = text.strip()
    fence_pattern = re.compile(
        r"```(?:json)?\s*(.*?)```",
        re.DOTALL | re.IGNORECASE,
    )
    match = fence_pattern.search(text)
    if match:
        text = match.group(1).strip()
    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end != -1 and end > start:
        text = text[start:end + 1]

    return text.strip()

def validate_requirements(result):
    if not isinstance(result, dict):
        return False
    if set(result.keys()) != REQUIRED_KEYS:
        return False
    if not isinstance(result["goal"], str):
        return False
    if not isinstance(result["allowed_actions"], list):
        return False
    if not all(
        isinstance(a, str) and a in VALID_ACTIONS
        for a in result["allowed_actions"]
    ):
        return False
    if not isinstance(result["safe_stop"], bool):
        return False
    if not isinstance(result["avoid_obstacles"], bool):
        return False
    return True

def run_analyst(brief_text):
    if not isinstance(brief_text, str) or not brief_text.strip():
        raise ValueError("brief_text must be a non-empty string.")

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": brief_text.strip()},
    ]

    raw_response = call_qwen(messages, temperature=0.0)

    json_text = _clean_json_text(raw_response)

    try:
        requirements = json.loads(json_text)
    except json.JSONDecodeError as e:
        raise ValueError(
            f"Qwen did not return valid JSON.\n"
            f"Raw response:\n{raw_response}\n"
            f"Error: {e}"
        )

    if not validate_requirements(requirements):
        raise ValueError(
            f"Qwen output failed validation.\n"
            f"Parsed data: {requirements}"
        )

    return requirements