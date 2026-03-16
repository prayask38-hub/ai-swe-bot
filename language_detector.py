from groq import Groq
from dotenv import load_dotenv
import os
import json

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

LANGUAGE_HINTS = {
    "python": "Look for indentation errors, missing colons, wrong variable types, undefined variables.",
    "javascript": "Look for missing semicolons, undefined variables, async/await issues, callback errors.",
    "java": "Look for missing semicolons, wrong data types, null pointer exceptions, missing imports.",
    "cpp": "Look for memory leaks, missing semicolons, pointer errors, wrong data types.",
    "go": "Look for unused variables, missing error handling, wrong goroutine usage.",
    "rust": "Look for ownership errors, borrow checker issues, lifetime problems."
}

def detect_language(code: str):
    prompt = f"""Look at this code and identify what programming language it is.

Code:
{code}

Return ONLY a JSON object like this:
{{
    "language": "<python, javascript, java, cpp, go, or rust>",
    "confidence": "<high, medium, or low>",
    "framework": "<React, Django, Spring, Express, or none>"
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
    return json.loads(raw)

def detect_bugs_multilang(code: str, language: str):
    hints = LANGUAGE_HINTS.get(language, "Look for common programming errors.")

    prompt = f"""You are an expert {language} developer. Analyze this code and find ALL bugs.

Important hints for {language}: {hints}

Code:
{code}

Return ONLY a JSON object like this:
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
    return json.loads(raw)

def analyze_code(code: str):
    print("Detecting language...\n")
    lang_result = detect_language(code)
    language = lang_result['language']
    framework = lang_result['framework']

    print(f"Language: {language.upper()}")
    print(f"Framework: {framework}")
    print(f"Confidence: {lang_result['confidence']}\n")

    print(f"Analyzing {language.upper()} code for bugs...\n")
    bug_result = detect_bugs_multilang(code, language)

    print(f"Total bugs found: {bug_result['total_bugs']}\n")
    for bug in bug_result['bugs']:
        print(f"Bug #{bug['bug_id']} — Line {bug['line']}")
        print(f"  Type: {bug['type']}")
        print(f"  Severity: {bug['severity']}")
        print(f"  Problem: {bug['description']}")
        print()

    return bug_result

# Test 1 — Python
python_code = """
def greet(name)
    print("Hello " + name)
    return

greet(123)
"""

# Test 2 — JavaScript
js_code = """
function calculateTotal(items) {
    let total = 0
    for (let i = 0; i <= items.length; i++) {
        total += items[i].price
    }
    return total
}

console.log(calculateTotal([{price: 10}, {price: 20}]))
"""

# Test 3 — Java
java_code = """
public class Calculator {
    public static int divide(int a, int b) {
        return a / b;
    }

    public static void main(String[] args) {
        System.out.println(divide(10, 0))
        String name = null;
        System.out.println(name.length());
    }
}
"""

print("=" * 50)
print("TEST 1 — PYTHON CODE")
print("=" * 50)
analyze_code(python_code)

print("=" * 50)
print("TEST 2 — JAVASCRIPT CODE")
print("=" * 50)
analyze_code(js_code)

print("=" * 50)
print("TEST 3 — JAVA CODE")
print("=" * 50)
analyze_code(java_code)
