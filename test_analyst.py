import json
import os
import sys
import traceback

from analyst_agent import run_analyst

BRIEF_FILE = "brief.txt"
ARTIFACTS_DIR = "artifacts"
REQUIREMENTS_FILE = os.path.join(ARTIFACTS_DIR, "requirements.json")


def read_brief(path=BRIEF_FILE):
    if not os.path.isfile(path):
        raise FileNotFoundError(f"Brief file not found: {path}")
    with open(path, "r", encoding="utf-8") as f:
        text = f.read()
    if not text.strip():
        raise ValueError(f"Brief file '{path}' is empty.")
    return text


def save_requirements(requirements, path=REQUIREMENTS_FILE):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(requirements, f, indent=2, ensure_ascii=False)
    return path


def main():
    print("=" * 60)
    print("TEST: Analyst Agent (Level 1 - Smoke Test)")
    print("=" * 60)

    brief_text = read_brief()
    print(f"[1/3] Brief loaded ({len(brief_text)} chars)")

    print("[2/3] Running run_analyst() ...")
    try:
        requirements = run_analyst(brief_text)
    except Exception as e:
        print(f"[ERROR] run_analyst() failed: {e}")
        traceback.print_exc()
        sys.exit(1)

    print("[3/3] Saving requirements ...")
    saved_path = save_requirements(requirements)
    print(f"      Saved to: {saved_path}")

    print("-" * 60)
    print("Validated Requirements:")
    print("-" * 60)
    print(json.dumps(requirements, indent=2, ensure_ascii=False))
    print("-" * 60)

    assert isinstance(requirements, dict), "Requirements must be a dict"
    assert set(requirements.keys()) == {
        "goal", "allowed_actions", "safe_stop", "avoid_obstacles"
    }, "Requirements keys mismatch"
    assert isinstance(requirements["allowed_actions"], list)
    assert all(
        a in {"FORWARD", "LEFT", "RIGHT", "STOP"}
        for a in requirements["allowed_actions"]
    ), "Invalid action in allowed_actions"
    print("\nPASS: Analyst Agent produced a valid requirements artifact.\n")


if __name__ == "__main__":
    main()