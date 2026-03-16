from groq import Groq
from dotenv import load_dotenv
import os
import json

load_dotenv()

groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def ask_groq(prompt: str):
    try:
        response = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"Groq 70B error: {e}")
        return None

def ask_groq_fast(prompt: str):
    try:
        response = groq_client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"Groq 8B error: {e}")
        return None

def clean_json(raw: str):
    if not raw:
        return None
    raw = raw.strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    return raw.strip()

def ask_both(prompt: str):
    print("Asking Llama 70B (deep analysis)...")
    answer1 = ask_groq(prompt)
    print("Asking Llama 8B (fast check)...")
    answer2 = ask_groq_fast(prompt)
    return answer1, answer2

def pick_best_answer(answer1: str, answer2: str, context: str):
    if not answer1 and not answer2:
        return None, "none"
    if not answer1:
        return answer2, "llama-8b"
    if not answer2:
        return answer1, "llama-70b"

    prompt = f"""You are a judge comparing two AI answers.

Context: {context}

Answer from AI 1 (Llama 70B):
{answer1}

Answer from AI 2 (Llama 8B):
{answer2}

Which answer is more complete and accurate?

Return ONLY a JSON object:
{{
    "winner": "<ai1 or ai2>",
    "reason": "<one sentence why>",
    "best_answer": "<copy the full better answer here>"
}}

Return ONLY the JSON. No extra text."""

    result = ask_groq(prompt)
    try:
        result = clean_json(result)
        data = json.loads(result)
        winner = "llama-70b" if data["winner"] == "ai1" else "llama-8b"
        return data["best_answer"], winner
    except:
        return answer1, "llama-70b"

def multi_ai_analyze(code: str, language: str):
    prompt = f"""You are an expert {language} developer. Analyze this code and find ALL bugs.

Code:
{code}

Return ONLY a JSON object:
{{
    "language": "{language}",
    "total_bugs": <number>,
    "bugs": [
        {{
            "bug_id": 1,
            "line": <number>,
            "type": "<error type>",
            "description": "<what is wrong>",
            "severity": "<high, medium, or low>"
        }}
    ]
}}

Return ONLY the JSON. No extra text."""

    answer1, answer2 = ask_both(prompt)

    if answer1 and answer2:
        best_answer, winner = pick_best_answer(
            answer1, answer2,
            f"analyzing {language} code for bugs"
        )
    else:
        best_answer = answer1 or answer2
        winner = "llama-70b"

    print(f"Winner: {winner.upper()}")

    try:
        best_answer = clean_json(best_answer)
        result = json.loads(best_answer)
        result["winner"] = winner
        return result
    except:
        try:
            answer1_clean = clean_json(answer1)
            result = json.loads(answer1_clean)
            result["winner"] = "llama-70b"
            return result
        except:
            return {
                "language": language,
                "total_bugs": 0,
                "bugs": [],
                "winner": winner
            }

def multi_ai_fix(code: str, bug: dict):
    prompt = f"""You are an expert developer. Fix this bug.

Bug:
- Line: {bug['line']}
- Type: {bug['type']}
- Problem: {bug['description']}

Code:
{code}

Return ONLY a JSON object:
{{
    "fixed_line": "<the corrected line of code>",
    "explanation": "<why this fix works>",
    "confidence": "<high, medium, or low>"
}}

Return ONLY the JSON. No extra text."""

    answer1, answer2 = ask_both(prompt)

    if answer1 and answer2:
        best_answer, winner = pick_best_answer(
            answer1, answer2,
            f"fixing a {bug['type']} bug"
        )
    else:
        best_answer = answer1 or answer2
        winner = "llama-70b"

    print(f"Winner: {winner.upper()}")

    try:
        best_answer = clean_json(best_answer)
        result = json.loads(best_answer)
        result["winner"] = winner
        return result
    except:
        try:
            answer1_clean = clean_json(answer1)
            result = json.loads(answer1_clean)
            result["winner"] = "llama-70b"
            return result
        except:
            return {
                "fixed_line": "",
                "explanation": best_answer or "",
                "confidence": "medium",
                "winner": winner
            }

if __name__ == "__main__":
    print("=" * 40)
    print("  Multi-AI Integration Test")
    print("  Llama 70B vs Llama 8B")
    print("=" * 40)
    print()

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

    print("Testing multi-AI bug analysis...\n")
    result = multi_ai_analyze(buggy_code, "python")
    print(f"\nLanguage: {result['language']}")
    print(f"Total bugs: {result['total_bugs']}")
    print(f"Decided by: {result.get('winner', 'llama-70b').upper()}")
    for bug in result['bugs']:
        print(f"\nBug #{bug['bug_id']} — Line {bug['line']}")
        print(f"  Type: {bug['type']}")
        print(f"  Severity: {bug['severity']}")
        print(f"  Problem: {bug['description']}")

    print("\n" + "=" * 40)
    print("Testing multi-AI bug fix...\n")
    if result['bugs']:
        fix = multi_ai_fix(buggy_code, result['bugs'][0])
        print(f"Fixed line: {fix['fixed_line']}")
        print(f"Explanation: {fix['explanation']}")
        print(f"Confidence: {fix['confidence']}")
        print(f"Decided by: {fix['winner'].upper()}")
