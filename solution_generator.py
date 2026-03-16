from groq import Groq
from dotenv import load_dotenv
import os
import json

load_dotenv()

client = Groq(api_key=os.getenv("GROK_API_KEY"))

def generate_solutions(code: str, bug: dict):
    prompt = f"""You are an expert developer. Given this bug, provide exactly 3 different solutions.

Bug details:
- Line: {bug['line']}
- Type: {bug['type']}
- Problem: {bug['description']}

Original code:
{code}

Return ONLY this JSON, no extra text, no markdown:
{{"bug_id": {bug['bug_id']}, "solutions": [{{"solution_id": 1, "approach": "Fix 1", "explanation": "explanation here", "fixed_code": "code here"}}, {{"solution_id": 2, "approach": "Fix 2", "explanation": "explanation here", "fixed_code": "code here"}}, {{"solution_id": 3, "approach": "Fix 3", "explanation": "explanation here", "fixed_code": "code here"}}]}}"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}]
    )

    raw = response.choices[0].message.content.strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    raw = raw.strip()
    result = json.loads(raw)
    return result


if __name__ == "__main__":
    buggy_code = """
def calculate_average(numbers):
    total = 0
    for num in numbers:
        total += num
    average = total / len(numbers)
    return averge

result = calculate_average([10, 20, 30])
print("Average is: " + result)
"""

    bugs = [
        {"bug_id": 1, "line": 7, "type": "NameError", "description": "averge should be average", "severity": "high"},
        {"bug_id": 2, "line": 9, "type": "TypeError", "description": "string + float concatenation", "severity": "medium"}
    ]

    for bug in bugs:
        solutions = generate_solutions(buggy_code, bug)
        print(f"Bug #{bug['bug_id']}:")
        for s in solutions['solutions']:
            print(f"  {s['solution_id']}: {s['approach']} — {s['fixed_code']}")
        print()
