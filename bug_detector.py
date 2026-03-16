from groq import Groq
from dotenv import load_dotenv
import os
import json

load_dotenv()

client = Groq(api_key=os.getenv("GROK_API_KEY"))

def detect_bugs(code: str, language: str = "python"):
    prompt = f"""You are an expert code debugger. Analyze this {language} code and find ALL bugs and errors.

Return your response as a JSON object in this exact format:
{{
    "language": "{language}",
    "total_bugs": <number>,
    "bugs": [
        {{
            "bug_id": 1,
            "line": <line number>,
            "type": <error type e.g. "SyntaxError", "LogicError", "TypeError">,
            "description": <what is wrong>,
            "severity": <"high", "medium", or "low">
        }}
    ]
}}

Code to analyze:
{code}

Return ONLY the JSON. No extra text."""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}]
    )

    raw = response.choices[0].message.content
    result = json.loads(raw)
    return result

# Test it with real buggy code
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

print("Analyzing code for bugs...\n")
bugs = detect_bugs(buggy_code)
print(f"Language: {bugs['language']}")
print(f"Total bugs found: {bugs['total_bugs']}\n")
for bug in bugs['bugs']:
    print(f"Bug #{bug['bug_id']} — Line {bug['line']}")
    print(f"  Type: {bug['type']}")
    print(f"  Severity: {bug['severity']}")
    print(f"  Problem: {bug['description']}")
    print()
