import json
from pathlib import Path

from planner_agent import run_planner

ARTIFACTS_DIR = Path(__file__).parent / "artifacts"
REQUIREMENTS_PATH = ARTIFACTS_DIR / "requirements.json"
PLAN_PATH = ARTIFACTS_DIR / "plan.json"


def main():
    print("=" * 60)
    print("TEST: Planner Agent (Level 1 - Smoke Test)")
    print("=" * 60)

    if not REQUIREMENTS_PATH.exists():
        raise FileNotFoundError(
            f"Requirements file not found: {REQUIREMENTS_PATH}\n"
            f"Please run test_analyst.py first."
        )

    with open(REQUIREMENTS_PATH, "r", encoding="utf-8") as f:
        requirements = json.load(f)
    print(f"[1/3] Requirements loaded from {REQUIREMENTS_PATH}")

    print("[2/3] Running run_planner() ...")
    plan = run_planner(requirements)

    ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
    with open(PLAN_PATH, "w", encoding="utf-8") as f:
        json.dump(plan, f, indent=2, ensure_ascii=False)
    print(f"[3/3] Plan saved to {PLAN_PATH}")

    print("-" * 60)
    print("Validated Plan:")
    print("-" * 60)
    print(json.dumps(plan, indent=2, ensure_ascii=False))
    print("-" * 60)

    assert isinstance(plan, dict)
    assert set(plan.keys()) == {"strategy", "decisions", "stop_condition"}
    assert isinstance(plan["decisions"], list) and len(plan["decisions"]) > 0
    assert all(isinstance(d, str) and d.strip() for d in plan["decisions"])
    print("\nPASS: Planner Agent produced a valid plan artifact.\n")


if __name__ == "__main__":
    main()