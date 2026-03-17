import os
import json
import time
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

SIMPLE_MODEL = "llama-3.1-8b-instant"
SMART_MODEL = "llama-3.3-70b-versatile"

def assess_complexity(code: str, task: str):
    lines = len(code.split('\n'))
    has_classes = 'class ' in code
    has_async = 'async ' in code or 'await ' in code
    has_decorators = '@' in code
    has_recursion = 'def ' in code and code.count('def ') > 2
    complex_keywords = ['threading', 'multiprocessing', 'subprocess', 'socket', 'async']
    has_complex = any(kw in code for kw in complex_keywords)

    score = 0
    if lines > 50: score += 2
    if lines > 100: score += 2
    if has_classes: score += 1
    if has_async: score += 2
    if has_decorators: score += 1
    if has_recursion: score += 1
    if has_complex: score += 2

    if score >= 5:
        return "complex", SMART_MODEL
    elif score >= 2:
        return "medium", SMART_MODEL
    else:
        return "simple", SIMPLE_MODEL

def chain_of_thought_analysis(code: str, language: str = "python"):
    complexity, model = assess_complexity(code, "bug analysis")
    print(f"Code complexity: {complexity} — using {model.split('-')[1].upper()} model")

    reasoning_prompt = f"""You are an expert {language} developer. Think through this code step by step.

Code:
{code}

Follow these reasoning steps:
1. UNDERSTAND: What is this code trying to do?
2. TRACE: Walk through the execution flow line by line
3. IDENTIFY: What could go wrong? Where are the weak points?
4. VERIFY: For each potential bug, confirm it is actually a bug
5. PRIORITIZE: Rank bugs by severity

Think out loud through each step before giving your final answer.

Return ONLY a JSON object:
{{
    "reasoning": {{
        "understanding": "<what this code does>",
        "execution_flow": "<how it executes step by step>",
        "weak_points": ["<weak point 1>", "<weak point 2>"],
        "verification": "<confirming which issues are real bugs>"
    }},
    "confidence": <0-100>,
    "language": "{language}",
    "total_bugs": <number>,
    "bugs": [
        {{
            "bug_id": 1,
            "line": <number>,
            "type": "<error type>",
            "description": "<precise description>",
            "severity": "<critical, high, medium, or low>",
            "confidence": <0-100>,
            "why_its_a_bug": "<reasoning why this is definitely a bug>"
        }}
    ]
}}

Return ONLY the JSON. No extra text."""

    start = time.time()
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": reasoning_prompt}]
    )
    duration = round(time.time() - start, 2)

    raw = response.choices[0].message.content.strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    raw = raw.strip()

    try:
        result = json.loads(raw)
        result["model_used"] = model
        result["analysis_time"] = duration
        result["complexity"] = complexity
        return result
    except:
        return None

def self_correcting_solution(code: str, bug: dict, language: str = "python"):
    complexity, model = assess_complexity(code, "fix")

    first_prompt = f"""You are an expert {language} developer.

Bug to fix:
- Line: {bug['line']}
- Type: {bug['type']}
- Description: {bug['description']}

Code:
{code}

Generate your best fix for this bug.

Return ONLY a JSON object:
{{
    "fixed_line": "<the corrected line>",
    "explanation": "<why this fix works>",
    "confidence": <0-100>
}}

Return ONLY the JSON. No extra text."""

    response1 = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": first_prompt}]
    )

    raw1 = response1.choices[0].message.content.strip()
    if raw1.startswith("```"):
        raw1 = raw1.split("```")[1]
        if raw1.startswith("json"):
            raw1 = raw1[4:]
    raw1 = raw1.strip()

    try:
        first_fix = json.loads(raw1)
    except:
        return None

    verify_prompt = f"""You are a senior code reviewer. Verify if this fix is correct.

Original bug:
- Line: {bug['line']}
- Type: {bug['type']}
- Description: {bug['description']}

Original code:
{code}

Proposed fix: {first_fix.get('fixed_line', '')}
Explanation: {first_fix.get('explanation', '')}

Critically evaluate this fix:
1. Does it actually fix the bug?
2. Does it introduce any new bugs?
3. Is there a better fix?

Return ONLY a JSON object:
{{
    "fix_is_correct": <true or false>,
    "introduces_new_bugs": <true or false>,
    "better_fix_exists": <true or false>,
    "verified_fix": "<the best fix — either confirm original or provide better one>",
    "verification_notes": "<your reasoning>",
    "final_confidence": <0-100>
}}

Return ONLY the JSON. No extra text."""

    response2 = client.chat.completions.create(
        model=SMART_MODEL,
        messages=[{"role": "user", "content": verify_prompt}]
    )

    raw2 = response2.choices[0].message.content.strip()
    if raw2.startswith("```"):
        raw2 = raw2.split("```")[1]
        if raw2.startswith("json"):
            raw2 = raw2[4:]
    raw2 = raw2.strip()

    try:
        verification = json.loads(raw2)
        return {
            "original_fix": first_fix.get("fixed_line"),
            "verified_fix": verification.get("verified_fix"),
            "fix_is_correct": verification.get("fix_is_correct"),
            "introduces_new_bugs": verification.get("introduces_new_bugs"),
            "verification_notes": verification.get("verification_notes"),
            "final_confidence": verification.get("final_confidence"),
            "explanation": first_fix.get("explanation")
        }
    except:
        return first_fix

def context_aware_analysis(files: dict, target_file: str, language: str = "python"):
    print(f"Running context-aware analysis on {target_file}...")
    print(f"Context files: {list(files.keys())}")

    context_summary = ""
    for filename, content in files.items():
        if filename != target_file:
            context_summary += f"\n--- {filename} ---\n{content[:500]}\n"

    prompt = f"""You are an expert {language} developer with full codebase context.

Target file to analyze: {target_file}
Target code:
{files.get(target_file, '')}

Other files in the codebase for context:
{context_summary[:2000]}

Analyze the target file WITH full context of the codebase.
Look for cross-file issues like:
- Wrong function signatures
- Missing imports from other files
- Incorrect variable names used across files
- Logic inconsistencies between files

Return ONLY a JSON object:
{{
    "target_file": "{target_file}",
    "context_files_used": {list(files.keys())},
    "total_bugs": <number>,
    "bugs": [
        {{
            "bug_id": 1,
            "line": <number>,
            "type": "<error type>",
            "description": "<precise description>",
            "severity": "<critical, high, medium, or low>",
            "cross_file_issue": <true or false>,
            "related_file": "<filename if cross-file issue>"
        }}
    ],
    "cross_file_issues": ["<issue1>", "<issue2>"],
    "overall_health": "<poor, fair, good, or excellent>"
}}

Return ONLY the JSON. No extra text."""

    response = client.chat.completions.create(
        model=SMART_MODEL,
        messages=[{"role": "user", "content": prompt}]
    )

    raw = response.choices[0].message.content.strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    raw = raw.strip()

    try:
        return json.loads(raw)
    except:
        return {}

def smart_route(task: str, code: str, language: str = "python"):
    complexity, model = assess_complexity(code, task)
    print(f"Smart routing: {complexity} task → {model}")
    return model

if __name__ == "__main__":
    print("=" * 40)
    print("  Smart AI Engine Test")
    print("=" * 40)
    print()

    test_code = """
def process_orders(orders):
    total = 0
    for order in orders:
        if order['status'] == 'completed':
            total = total + order['amount']
            discount = order['discount']
            final = total - (total * discount / 100)
    return final

def calculate_tax(amount, rate):
    tax = amount * rate
    return amount + tax

result = process_orders([])
print("Total: " + result)
"""

    print("Test 1 — Chain of thought analysis:")
    result = chain_of_thought_analysis(test_code, "python")
    if result:
        print(f"\nComplexity: {result.get('complexity', 'unknown')}")
        print(f"Model used: {result.get('model_used', 'unknown')}")
        print(f"Analysis time: {result.get('analysis_time', 0)}s")
        print(f"Overall confidence: {result.get('confidence', 0)}%")
        print(f"Bugs found: {result.get('total_bugs', 0)}")

        reasoning = result.get('reasoning', {})
        print(f"\nAI Reasoning:")
        print(f"  Understanding: {reasoning.get('understanding', 'N/A')[:100]}")
        print(f"  Weak points: {reasoning.get('weak_points', [])}")

        for bug in result.get('bugs', []):
            print(f"\n  Bug #{bug['bug_id']} — {bug['type']} (line {bug['line']})")
            print(f"  Severity: {bug['severity']} | Confidence: {bug.get('confidence', 0)}%")
            print(f"  Why: {bug.get('why_its_a_bug', 'N/A')[:80]}")

    print("\nTest 2 — Self correcting solution:")
    if result and result.get('bugs'):
        bug = result['bugs'][0]
        fix = self_correcting_solution(test_code, bug, "python")
        if fix:
            print(f"\nOriginal fix: {fix.get('original_fix', 'N/A')}")
            print(f"Verified fix: {fix.get('verified_fix', 'N/A')}")
            print(f"Fix is correct: {fix.get('fix_is_correct', False)}")
            print(f"Introduces new bugs: {fix.get('introduces_new_bugs', False)}")
            print(f"Final confidence: {fix.get('final_confidence', 0)}%")
            print(f"Notes: {fix.get('verification_notes', 'N/A')[:100]}")

    print("\nTest 3 — Smart model routing:")
    simple_code = "x = 1 + 1"
    complex_code = test_code
    print(f"Simple code → {smart_route('fix', simple_code)}")
    print(f"Complex code → {smart_route('fix', complex_code)}")
