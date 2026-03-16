import os
import json
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def analyze_code_quality(code: str, language: str = "python"):
    prompt = f"""You are an expert code reviewer. Analyze this {language} code quality.

Code:
{code}

Return ONLY a JSON object:
{{
    "overall_score": <0-100>,
    "maintainability": <0-100>,
    "readability": <0-100>,
    "performance": <0-100>,
    "security": <0-100>,
    "technical_debt": "<low, medium, or high>",
    "issues": [
        {{
            "type": "<issue type>",
            "severity": "<high, medium, or low>",
            "description": "<what is wrong>",
            "suggestion": "<how to fix>"
        }}
    ],
    "strengths": ["<strength1>", "<strength2>"],
    "summary": "<one sentence overall assessment>"
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

def scan_security(code: str, language: str = "python"):
    prompt = f"""You are a security expert. Scan this {language} code for vulnerabilities.

Code:
{code}

Return ONLY a JSON object:
{{
    "security_score": <0-100>,
    "vulnerabilities": [
        {{
            "type": "<vulnerability type>",
            "severity": "<critical, high, medium, or low>",
            "line": <line number>,
            "description": "<what is vulnerable>",
            "fix": "<how to fix>"
        }}
    ],
    "passed_checks": ["<check1>", "<check2>"],
    "failed_checks": ["<check1>", "<check2>"]
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

def track_technical_debt(code: str, language: str = "python"):
    prompt = f"""You are a senior developer. Identify technical debt in this {language} code.

Code:
{code}

Return ONLY a JSON object:
{{
    "debt_level": "<low, medium, or high>",
    "debt_score": <0-100 where 100 is most debt>,
    "debt_items": [
        {{
            "category": "<code smell, duplication, complexity, outdated, missing tests>",
            "description": "<what needs refactoring>",
            "effort": "<hours to fix>",
            "priority": "<high, medium, or low>"
        }}
    ],
    "estimated_fix_time": "<total hours>",
    "refactoring_suggestions": ["<suggestion1>", "<suggestion2>"]
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

def full_code_review(code: str, language: str = "python"):
    print(f"Running full code review for {language} code...\n")

    print("Analyzing code quality...")
    quality = analyze_code_quality(code, language)

    print("Scanning for security issues...")
    security = scan_security(code, language)

    print("Checking technical debt...")
    debt = track_technical_debt(code, language)

    return {
        "quality": quality,
        "security": security,
        "debt": debt
    }

def print_report(report: dict):
    quality = report.get("quality")
    security = report.get("security")
    debt = report.get("debt")

    print("\n" + "=" * 40)
    print("  CODE QUALITY REPORT")
    print("=" * 40)

    if quality:
        print(f"\nOverall Score:     {quality['overall_score']}/100")
        print(f"Maintainability:   {quality['maintainability']}/100")
        print(f"Readability:       {quality['readability']}/100")
        print(f"Performance:       {quality['performance']}/100")
        print(f"Security:          {quality['security']}/100")
        print(f"Technical Debt:    {quality['technical_debt'].upper()}")
        print(f"\nSummary: {quality['summary']}")

        if quality.get("strengths"):
            print(f"\nStrengths:")
            for s in quality["strengths"]:
                print(f"  + {s}")

        if quality.get("issues"):
            print(f"\nIssues found: {len(quality['issues'])}")
            for issue in quality["issues"]:
                print(f"  [{issue['severity'].upper()}] {issue['type']}")
                print(f"  Problem: {issue['description']}")
                print(f"  Fix: {issue['suggestion']}")
                print()

    if security:
        print(f"\nSecurity Score: {security['security_score']}/100")
        if security.get("vulnerabilities"):
            print(f"Vulnerabilities: {len(security['vulnerabilities'])}")
            for vuln in security["vulnerabilities"]:
                print(f"  [{vuln['severity'].upper()}] {vuln['type']} at line {vuln['line']}")
                print(f"  {vuln['description']}")
                print(f"  Fix: {vuln['fix']}")
                print()
        if security.get("passed_checks"):
            print(f"Passed checks: {', '.join(security['passed_checks'])}")

    if debt:
        print(f"\nTechnical Debt Level: {debt['debt_level'].upper()}")
        print(f"Estimated fix time: {debt['estimated_fix_time']}")
        if debt.get("refactoring_suggestions"):
            print(f"\nRefactoring suggestions:")
            for s in debt["refactoring_suggestions"]:
                print(f"  - {s}")

if __name__ == "__main__":
    print("=" * 40)
    print("  Code Quality Scorer")
    print("=" * 40)
    print()

    sample_code = """
import os
import sqlite3

password = "admin123"
api_key = "sk-1234567890abcdef"

def get_user(user_id):
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    query = "SELECT * FROM users WHERE id = " + user_id
    cursor.execute(query)
    return cursor.fetchone()

def calculate(a, b, c, d, e, f, g):
    if a > 0:
        if b > 0:
            if c > 0:
                if d > 0:
                    if e > 0:
                        return a + b + c + d + e + f + g
    return 0

def x(y):
    z = y * 2
    w = z + 1
    q = w / z
    return q
"""

    report = full_code_review(sample_code, "python")
    print_report(report)