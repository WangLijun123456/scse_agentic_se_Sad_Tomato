## A typical test case: 
""" {
    "goal_ahead": True,
    "goal_on_left": False,
    "goal_on_right": False,
    "front_blocked": False,
    "left_blocked": False,
    "right_blocked": False
},
"FORWARD" """
## Use the above test case to create more test cases for all the possible states

import importlib.util
import sys
from pathlib import Path

ARTIFACTS_DIR = Path(__file__).parent / "artifacts"
NAV_LOGIC_PATH = ARTIFACTS_DIR / "navigation_logic.py"

VALID_ACTIONS = {"FORWARD", "LEFT", "RIGHT", "STOP"}


def load_decide_next_move(path=NAV_LOGIC_PATH):
    if not path.exists():
        raise FileNotFoundError(
            f"Navigation logic not found: {path}\n"
            f"Please run test_developer.py first."
        )
    spec = importlib.util.spec_from_file_location("nav_logic", path)
    module = importlib.util.module_from_spec(spec)
    sys.modules["nav_logic"] = module
    spec.loader.exec_module(module)
    if not hasattr(module, "decide_next_move"):
        raise AttributeError(
            "navigation_logic.py does not define decide_next_move(state)"
        )
    return module.decide_next_move


TEST_CASES = [
    # --- Goal ahead, all clear ---
    (
        {
            "goal_ahead": True,
            "goal_on_left": False,
            "goal_on_right": False,
            "front_blocked": False,
            "left_blocked": False,
            "right_blocked": False,
        },
        "FORWARD",
    ),
    # --- Goal on left, all clear ---
    (
        {
            "goal_ahead": False,
            "goal_on_left": True,
            "goal_on_right": False,
            "front_blocked": False,
            "left_blocked": False,
            "right_blocked": False,
        },
        "LEFT",
    ),
    # --- Goal on right, all clear ---
    (
        {
            "goal_ahead": False,
            "goal_on_left": False,
            "goal_on_right": True,
            "front_blocked": False,
            "left_blocked": False,
            "right_blocked": False,
        },
        "RIGHT",
    ),
    # --- Goal ahead, front blocked, left clear -> LEFT ---
    (
        {
            "goal_ahead": True,
            "goal_on_left": False,
            "goal_on_right": False,
            "front_blocked": True,
            "left_blocked": False,
            "right_blocked": False,
        },
        "LEFT",
    ),
    # --- Goal ahead, front blocked, left blocked, right clear -> RIGHT ---
    (
        {
            "goal_ahead": True,
            "goal_on_left": False,
            "goal_on_right": False,
            "front_blocked": True,
            "left_blocked": True,
            "right_blocked": False,
        },
        "RIGHT",
    ),
    # --- All blocked -> STOP ---
    (
        {
            "goal_ahead": True,
            "goal_on_left": False,
            "goal_on_right": False,
            "front_blocked": True,
            "left_blocked": True,
            "right_blocked": True,
        },
        "STOP",
    ),
    # --- Goal left, left blocked, front clear -> FORWARD ---
    (
        {
            "goal_ahead": False,
            "goal_on_left": True,
            "goal_on_right": False,
            "front_blocked": False,
            "left_blocked": True,
            "right_blocked": False,
        },
        "FORWARD",
    ),
    # --- Goal right, right blocked, front clear -> FORWARD ---
    (
        {
            "goal_ahead": False,
            "goal_on_left": False,
            "goal_on_right": True,
            "front_blocked": False,
            "left_blocked": False,
            "right_blocked": True,
        },
        "FORWARD",
    ),
    # --- Goal left, left blocked, front blocked, right clear -> RIGHT ---
    (
        {
            "goal_ahead": False,
            "goal_on_left": True,
            "goal_on_right": False,
            "front_blocked": True,
            "left_blocked": True,
            "right_blocked": False,
        },
        "RIGHT",
    ),
    # --- Goal right, right blocked, front blocked, left clear -> LEFT ---
    (
        {
            "goal_ahead": False,
            "goal_on_left": False,
            "goal_on_right": True,
            "front_blocked": True,
            "left_blocked": False,
            "right_blocked": True,
        },
        "LEFT",
    ),
    # --- Goal ahead + goal left, front clear -> FORWARD ---
    (
        {
            "goal_ahead": True,
            "goal_on_left": True,
            "goal_on_right": False,
            "front_blocked": False,
            "left_blocked": False,
            "right_blocked": False,
        },
        "FORWARD",
    ),
    # --- Goal ahead + goal right, front blocked, right clear -> RIGHT ---
    (
        {
            "goal_ahead": True,
            "goal_on_left": False,
            "goal_on_right": True,
            "front_blocked": True,
            "left_blocked": False,
            "right_blocked": False,
        },
        "RIGHT",
    ),
]


def run_tests():
    print("=" * 60)
    print("TEST: Generated Navigation Logic (Level 2 - Behavioral)")
    print("=" * 60)

    decide_next_move = load_decide_next_move()
    print(f"Loaded decide_next_move from {NAV_LOGIC_PATH}\n")

    passed = 0
    failed = 0
    failures = []

    for i, (state, expected) in enumerate(TEST_CASES, start=1):
        try:
            actual = decide_next_move(state)
        except Exception as e:
            print(f"[{i:02d}] EXCEPTION: {e}")
            print(f"      state = {state}")
            failed += 1
            failures.append((i, state, expected, f"EXCEPTION: {e}"))
            continue

        ok_action = actual in VALID_ACTIONS
        ok_expected = (actual == expected)

        status = "PASS" if (ok_action and ok_expected) else "FAIL"
        print(f"[{i:02d}] {status}  state={state}")
        print(f"      expected={expected!r}  actual={actual!r}")

        if ok_action and ok_expected:
            passed += 1
        else:
            failed += 1
            failures.append((i, state, expected, actual))

    print("-" * 60)
    print(f"Total: {len(TEST_CASES)}  Passed: {passed}  Failed: {failed}")
    print("-" * 60)

    if failures:
        print("\nFailures:")
        for i, state, expected, actual in failures:
            print(f"  [{i:02d}] state={state}")
            print(f"        expected={expected!r}  actual={actual!r}")
        raise AssertionError(f"{failed} test case(s) failed.")

    print("\nPASS: All behavioral test cases passed.\n")


if __name__ == "__main__":
    run_tests()