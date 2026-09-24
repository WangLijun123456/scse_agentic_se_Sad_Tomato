import json
from pathlib import Path

from planner_agent import run_planner

ARTIFACTS_DIR = Path(__file__).parent / "artifacts"
REQUIREMENTS_PATH = ARTIFACTS_DIR / "requirements.json"
PLAN_PATH = ARTIFACTS_DIR / "plan.json"


def main():
    if not REQUIREMENTS_PATH.exists():
        raise FileNotFoundError(
            f"Requirements file not found: {REQUIREMENTS_PATH}\n"
            f"Please run run_analyst.py first."
        )

    with open(REQUIREMENTS_PATH, "r", encoding="utf-8") as f:
        requirements = json.load(f)

    plan = run_planner(requirements)

    ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
    with open(PLAN_PATH, "w", encoding="utf-8") as f:
        json.dump(plan, f, indent=2, ensure_ascii=False)

    print(f"Plan saved to {PLAN_PATH}")


if __name__ == "__main__":
    main()