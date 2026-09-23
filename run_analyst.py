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
        raise FileNotFoundError(
            f"Brief file not found: {path}\n"
            f"Please make sure '{path}' exists in the working directory."
        )

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
    print("Analyst Agent Runner")
    print("=" * 60)

    print(f"\n[1/3] Reading brief from '{BRIEF_FILE}' ...")
    try:
        brief_text = read_brief()
    except Exception as e:
        print(f"\n[ERROR] Failed to read brief:")
        print(f"        {e}")
        sys.exit(1)

    print(f"      Brief length: {len(brief_text)} characters")

    print("\n[2/3] Calling run_analyst() ...")
    print("      (This will call Qwen via Ollama and validate the output)")
    try:
        requirements = run_analyst(brief_text)
    except Exception as e:
        print(f"\n[ERROR] run_analyst() failed:")
        print(f"        {e}")
        print("\n--- Traceback (for debugging) ---")
        traceback.print_exc()
        sys.exit(1)

    print("\n[3/3] Saving requirements ...")
    saved_path = save_requirements(requirements)
    print(f"      Saved to: {saved_path}")
    print("\n" + "-" * 60)
    print("Validated Requirements:")
    print("-" * 60)
    print(json.dumps(requirements, indent=2, ensure_ascii=False))
    print("-" * 60)
    print("\nDone.\n")

if __name__ == "__main__":
    main()