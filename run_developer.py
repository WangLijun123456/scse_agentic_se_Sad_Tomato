## the logic is similar to the run_planner and run_analyst files
import json
from pathlib import Path

from developer_agent import run_developer

ARTIFACTS_DIR = Path(__file__).parent / "artifacts"
PLAN_PATH = ARTIFACTS_DIR / "plan.json"
OUTPUT_PATH = Path(__file__).parent / "navigation_logic.py"


def main():
    if not PLAN_PATH.exists():
        raise FileNotFoundError(
            f"Plan file not found: {PLAN_PATH}\n"
            f"Please run run_planner.py first."
        )

    with open(PLAN_PATH, "r", encoding="utf-8") as f:
        plan = json.load(f)

    code = run_developer(plan)

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        f.write(code)

    print(f"Navigation logic saved to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()