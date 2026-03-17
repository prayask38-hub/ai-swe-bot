import os
import json
from groq import Groq
from dotenv import load_dotenv
import sqlite3
from datetime import datetime

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))
DB_PATH = "ai_swe_bot.db"

def get_historical_patterns():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT bug_type, COUNT(*) as count
        FROM bugs
        GROUP BY bug_type
        ORDER BY count DESC
        LIMIT 10
    """)
    patterns = cursor.fetchall()
    conn.close()
    return [{"type": p[0], "count": p[1]} for p in patterns]

def predict_errors(code: str, language: str = "python"):
    historical = get_historical_patterns()
    history_text = ""
    if historical:
        history_text = "Historical bug patterns from past sessions:\n"
        for p in historical:
            history_text += f"  - {p['type']}: seen {p['count']} times\n"

    prompt = f"""You are an expert {language} developer with years of experience.
Analyze this code and predict potential errors BEFORE they occur.

{history_text}

Code to analyze:
{code}

Look for:
- Potential null/none reference errors
- Off by one errors
- Resource leaks
- Race conditions
- Edge cases not handled
- Performance bottlenecks
- Memory issues
- Type mismatches
- Missing error handling
- Security vulnerabilities

Return ONLY a JSON object:
{{
    "risk_level": "<low, medium, high, or critical>",
    "risk_score": <0-100>,
    "predicted_errors": [
        {{
            "error_id": 1,
            "type": "<error type>",
            "probability": "<low, medium, or high>",
            "line": <line number or 0 if general>,
            "description": "<what could go wrong>",
            "trigger": "<what would cause this error>",
            "prevention": "<how to prevent it>",
            "severity": "<low, medium, high, or critical>"
        }}
    ],
    "performance_risks": [
        {{
            "type": "<performance issue type>",
            "description": "<what could be slow>",
            "suggestion": "<how to optimize>"
        }}
    ],
    "safe_patterns": ["<good pattern1>", "<good pattern2>"],
    "summary": "<one sentence overall risk assessment>"
}}

Return ONLY the JSON. No extra text."""

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

    try:
        return json.loads(raw)
    except:
        return None

def suggest_optimizations(code: str, language: str = "python"):
    prompt = f"""You are a performance optimization expert.
Analyze this {language} code and suggest specific optimizations.

Code:
{code}

Return ONLY a JSON object:
{{
    "current_complexity": "<O(n), O(n^2), etc>",
    "optimized_complexity": "<what it could be>",
    "optimizations": [
        {{
            "type": "<optimization type>",
            "current_code": "<current inefficient code>",
            "optimized_code": "<better version>",
            "improvement": "<how much faster/better>",
            "explanation": "<why this is better>"
        }}
    ],
    "resource_usage": {{
        "memory": "<low, medium, or high>",
        "cpu": "<low, medium, or high>",
        "io": "<low, medium, or high>"
    }},
    "bottlenecks": ["<bottleneck1>", "<bottleneck2>"]
}}

Return ONLY the JSON. No extra text."""

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

    try:
        return json.loads(raw)
    except:
        return None

def detect_bottlenecks(code: str, language: str = "python"):
    prompt = f"""You are a performance engineer.
Find performance bottlenecks in this {language} code.

Code:
{code}

Return ONLY a JSON object:
{{
    "bottlenecks": [
        {{
            "location": "<where in code>",
            "type": "<loop, database, network, memory, io>",
            "impact": "<high, medium, or low>",
            "description": "<what is slow>",
            "fix": "<how to fix it>"
        }}
    ],
    "overall_performance": "<poor, fair, good, or excellent>",
    "quick_wins": ["<easy fix1>", "<easy fix2>"]
}}

Return ONLY the JSON. No extra text."""

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

    try:
        return json.loads(raw)
    except:
        return None

def full_predictive_analysis(code: str, language: str = "python"):
    print(f"Running full predictive analysis for {language} code...\n")

    print("Predicting potential errors...")
    predictions = predict_errors(code, language)

    print("Suggesting optimizations...")
    optimizations = suggest_optimizations(code, language)

    print("Detecting bottlenecks...")
    bottlenecks = detect_bottlenecks(code, language)

    return {
        "predictions": predictions,
        "optimizations": optimizations,
        "bottlenecks": bottlenecks
    }

def print_analysis(result: dict):
    predictions = result.get("predictions")
    optimizations = result.get("optimizations")
    bottlenecks = result.get("bottlenecks")

    print("\n" + "=" * 50)
    print("  PREDICTIVE ANALYSIS REPORT")
    print("=" * 50)

    if predictions:
        print(f"\nRisk Level: {predictions['risk_level'].upper()}")
        print(f"Risk Score: {predictions['risk_score']}/100")
        print(f"Summary: {predictions['summary']}")

        if predictions.get("predicted_errors"):
            print(f"\nPredicted errors: {len(predictions['predicted_errors'])}")
            for err in predictions["predicted_errors"]:
                print(f"\n  [{err['severity'].upper()}] {err['type']}")
                print(f"  Probability: {err['probability']}")
                print(f"  Line: {err['line']}")
                print(f"  Could happen when: {err['trigger']}")
                print(f"  Prevention: {err['prevention']}")

        if predictions.get("safe_patterns"):
            print(f"\nGood patterns found:")
            for p in predictions["safe_patterns"]:
                print(f"  + {p}")

    if optimizations:
        print(f"\nCurrent complexity: {optimizations.get('current_complexity', 'unknown')}")
        print(f"Optimized complexity: {optimizations.get('optimized_complexity', 'unknown')}")

        if optimizations.get("optimizations"):
            print(f"\nOptimization suggestions:")
            for opt in optimizations["optimizations"][:3]:
                print(f"\n  Type: {opt['type']}")
                print(f"  Improvement: {opt['improvement']}")
                print(f"  Why: {opt['explanation']}")

    if bottlenecks:
        print(f"\nOverall performance: {bottlenecks.get('overall_performance', 'unknown').upper()}")

        if bottlenecks.get("bottlenecks"):
            print(f"\nBottlenecks found:")
            for b in bottlenecks["bottlenecks"]:
                print(f"  [{b['impact'].upper()}] {b['type']} — {b['description']}")
                print(f"  Fix: {b['fix']}")

        if bottlenecks.get("quick_wins"):
            print(f"\nQuick wins:")
            for w in bottlenecks["quick_wins"]:
                print(f"  - {w}")

if __name__ == "__main__":
    print("=" * 40)
    print("  Predictive Error Analysis")
    print("=" * 40)
    print()

    sample_code = """
def process_users(user_ids):
    results = []
    for user_id in user_ids:
        conn = sqlite3.connect("users.db")
        cursor = conn.cursor()
        user = cursor.execute(
            "SELECT * FROM users WHERE id = " + str(user_id)
        ).fetchone()
        results.append(user)
    return results

def calculate_stats(data):
    total = 0
    for i in range(len(data)):
        for j in range(len(data)):
            total += data[i] * data[j]
    return total / len(data)

def read_config():
    file = open("config.txt")
    content = file.read()
    return content
"""

    result = full_predictive_analysis(sample_code, "python")
    print_analysis(result)
