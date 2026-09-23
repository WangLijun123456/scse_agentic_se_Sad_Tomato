from ollama import chat

MODEL_NAME = "qwen3:8b"

PROMPT_TEMPLATE = """
Read the following brief and produce software requirements for a robot
navigation system.

Describe:
- The navigation goal
- The allowed actions the robot can take
- Whether the robot should stop safely when it cannot move
- Whether the robot should avoid obstacles

Brief:
{brief}
"""

def main():
    with open("brief.txt", "r", encoding="utf-8") as f:
        brief_text = f.read()

    prompt = PROMPT_TEMPLATE.format(brief=brief_text)

    print("Calling Qwen (qwen3:8b) ... this may take 30-120 seconds.")
    response = chat(
        model=MODEL_NAME,
        messages=[
            {"role": "user", "content": prompt},
        ],
        think=False,
        options={"temperature": 0.0},
    )

    output = response.message.content

    print("\n" + "=" * 60)
    print("Qwen raw output:")
    print("=" * 60)
    print(output)
    print("=" * 60)

    with open("robot_requirements.txt", "w", encoding="utf-8") as f:
        f.write(output)

    print("\nSaved to robot_requirements.txt")

if __name__ == "__main__":
    main()