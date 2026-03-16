from groq import Groq
from dotenv import load_dotenv
import os
import json
from datetime import datetime

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def generate_roadmap(original_code, bugs, fixes_applied):
    prompt = f"""You are a senior software engineer writing a technical report.

Based on this debugging session, generate a clear roadmap report.

Original buggy code:
{original_code}

Bugs found:
{json.dumps(bugs, indent=2)}

Fixes applied:
{json.dumps(fixes_applied, indent=2)}

Return your response as a JSON object in this exact format:
{{
    "session_date": "{datetime.now().strftime('%Y-%m-%d %H:%M')}",
    "summary": "<one sentence summary>",
    "bugs_found": 2,
    "bugs_fixed": 2,
    "steps_taken": ["step 1", "step 2", "step 3"],
    "what_changed": [
        {{"line": 7, "before": "return averge", "after": "return average"}},
        {{"line": 9, "before": "print string + float", "after": "print with str()"}}
    ],
    "next_steps": ["recommendation 1", "recommendation 2", "recommendation 3"],
    "code_health": "good"
}}

Return ONLY the JSON. No extra text. No markdown."""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}]
    )

    raw = response.choices[0].message.content
    raw = raw.strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    raw = raw.strip()
    result = json.loads(raw)
    return result

def save_roadmap(roadmap, filename="roadmap.md"):
    with open(filename, 'w', encoding="utf-8") as f:
        f.write(f"# AI SWE Bot — Debug Roadmap\n\n")
        f.write(f"**Date:** {roadmap['session_date']}\n\n")
        f.write(f"**Summary:** {roadmap['summary']}\n\n")
        f.write(f"**Code Health:** {roadmap['code_health'].upper()}\n\n")
        f.write(f"---\n\n")
        f.write(f"## Bugs Found: {roadmap['bugs_found']} | Bugs Fixed: {roadmap['bugs_fixed']}\n\n")
        f.write(f"## Steps Taken\n")
        for i, step in enumerate(roadmap['steps_taken'], 1):
            f.write(f"{i}. {step}\n")
        f.write(f"\n## What Changed\n")
        for change in roadmap['what_changed']:
            f.write(f"- Line {change['line']}: `{change['before']}` → `{change['after']}`\n")
        f.write(f"\n## Next Steps\n")
        for i, step in enumerate(roadmap['next_steps'], 1):
            f.write(f"{i}. {step}\n")
    print(f"Roadmap saved to {filename}")

original_code = """def calculate_average(numbers):
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

print("\nWhat Changed:")
for change in roadmap['what_changed']:
    print(f"  Line {change['line']}: {change['before']} → {change['after']}")

print("\nNext Steps:")
for i, step in enumerate(roadmap['next_steps'], 1):
    print(f"  {i}. {step}")

save_roadmap(roadmap)