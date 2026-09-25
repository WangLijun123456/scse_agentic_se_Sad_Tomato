import json
from pathlib import Path

from developer_agent import run_developer

ARTIFACTS_DIR = Path(__file__).parent / "artifacts"
PLAN_PATH = ARTIFACTS_DIR / "plan.json"
OUTPUT_PATH = ARTIFACTS_DIR / "navigation_logic.py"


def main():
    print("=" * 60)
    print("TEST: Developer Agent (Level 1 - Smoke Test)")
    print("=" * 60)

    if not PLAN_PATH.exists():
        raise FileNotFoundError(
            f"Plan file not found: {PLAN_PATH}\n"
            f"Please run test_planner.py first."
        )

    with open(PLAN_PATH, "r", encoding="utf-8") as f:
        plan = json.load(f)
    print(f"[1/3] Plan loaded from {PLAN_PATH}")

    print("[2/3] Running run_developer() ...")
    code = run_developer(plan)

    ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        f.write(code)
    print(f"[3/3] Navigation logic saved to {OUTPUT_PATH}")

    print("-" * 60)
    print("Generated Code:")
    print("-" * 60)
    print(code)
    print("-" * 60)

    assert "def navigate" in code, "navigate() missing"
    assert "def decide_next_move" in code, "decide_next_move() missing"
    for act in ["FORWARD", "LEFT", "RIGHT", "STOP"]:
        assert act in code, f"Missing action {act}"

    compile(code, "<generated>", "exec")

    print("\nPASS: Developer Agent produced valid navigation logic.\n")


if __name__ == "__main__":
    main()