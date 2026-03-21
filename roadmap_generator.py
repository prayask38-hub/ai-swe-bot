import os
import json
from datetime import datetime
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def generate_roadmap(original_code: str, bugs: list, fixes_applied: list):
    prompt = f"""You are a senior software engineer writing a technical report.

Based on this debugging session, generate a clear roadmap report.

Original buggy code:
{original_code[:1000]}

Bugs found:
{json.dumps(bugs[:5], indent=2)}

Fixes applied:
{json.dumps(fixes_applied[:5], indent=2)}

Return your response as a JSON object in this exact format:
{{
    "session_date": "{datetime.now().strftime('%Y-%m-%d %H:%M')}",
    "summary": "one sentence summary of what was wrong",
    "bugs_found": {len(bugs)},
    "bugs_fixed": {len(fixes_applied)},
    "steps_taken": ["step 1", "step 2", "step 3"],
    "what_changed": [
        {{"line": 7, "before": "return averge", "after": "return average"}}
    ],
    "next_steps": ["recommendation 1", "recommendation 2", "recommendation 3"],
    "code_health": "good"
}}

Return ONLY the JSON. No extra text. No markdown."""

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

    raw = raw.replace('\n', ' ').replace('\r', ' ').replace('\t', ' ')

    try:
        result = json.loads(raw)
        return result
    except:
        return {
            "session_date": datetime.now().strftime('%Y-%m-%d %H:%M'),
            "summary": "Debugging session completed successfully",
            "bugs_found": len(bugs),
            "bugs_fixed": len(fixes_applied),
            "steps_taken": ["Detected bugs", "Generated solutions", "Applied fixes"],
            "what_changed": [],
            "next_steps": ["Review code", "Add tests", "Deploy"],
            "code_health": "good"
        }

def save_roadmap(roadmap: dict, filename: str = "roadmap.md"):
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(f"# AI SWE Bot - Debug Roadmap\n\n")
        f.write(f"**Date:** {roadmap['session_date']}\n\n")
        f.write(f"**Summary:** {roadmap['summary']}\n\n")
        f.write(f"**Code Health:** {roadmap['code_health'].upper()}\n\n")
        f.write(f"---\n\n")
        f.write(f"## Bugs Found: {roadmap['bugs_found']} | Bugs Fixed: {roadmap['bugs_fixed']}\n\n")
        f.write(f"## Steps Taken\n")
        for i, step in enumerate(roadmap['steps_taken'], 1):
            f.write(f"{i}. {step}\n")
        f.write(f"\n## What Changed\n")
        for change in roadmap.get('what_changed', []):
            f.write(f"- Line {change.get('line', '?')}: `{change.get('before', '')}` -> `{change.get('after', '')}`\n")
        f.write(f"\n## Next Steps\n")
        for i, step in enumerate(roadmap['next_steps'], 1):
            f.write(f"{i}. {step}\n")
    print(f"Roadmap saved to {filename}")

if __name__ == "__main__":
    original_code = """
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

    fixes_applied = [
        {"bug_id": 1, "solution": "Typo Fix", "fixed_line": "    return average", "status": "fixed"},
        {"bug_id": 2, "solution": "str() function", "fixed_line": "print('Average is: ' + str(result))", "status": "fixed"}
    ]

    print("Generating roadmap...\n")
    roadmap = generate_roadmap(original_code, bugs, fixes_applied)

    print(f"Session: {roadmap['session_date']}")
    print(f"Summary: {roadmap['summary']}")
    print(f"Code Health: {roadmap['code_health'].upper()}")
    print(f"Bugs Found: {roadmap['bugs_found']} | Bugs Fixed: {roadmap['bugs_fixed']}\n")

    print("Steps Taken:")
    for i, step in enumerate(roadmap['steps_taken'], 1):
        print(f"  {i}. {step}")

    print("\nNext Steps:")
    for i, step in enumerate(roadmap['next_steps'], 1):
        print(f"  {i}. {step}")

    save_roadmap(roadmap)
