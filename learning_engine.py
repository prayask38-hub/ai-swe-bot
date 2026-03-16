import sqlite3
import json
import os
from datetime import datetime
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

DB_PATH = "ai_swe_bot.db"

def init_learning_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS learned_fixes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            language TEXT,
            bug_type TEXT,
            bug_pattern TEXT,
            successful_fix TEXT,
            times_used INTEGER DEFAULT 1,
            success_rate REAL DEFAULT 1.0,
            last_used TEXT,
            created_at TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_patterns (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pattern_type TEXT,
            pattern_value TEXT,
            frequency INTEGER DEFAULT 1,
            last_seen TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS coding_style (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            style_key TEXT UNIQUE,
            style_value TEXT,
            updated_at TEXT
        )
    """)

    conn.commit()
    conn.close()
    print("Learning database initialized.")

def learn_from_fix(language: str, bug_type: str, bug_pattern: str, successful_fix: str):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, times_used FROM learned_fixes
        WHERE language=? AND bug_type=? AND bug_pattern=?
    """, (language, bug_type, bug_pattern))

    existing = cursor.fetchone()

    if existing:
        cursor.execute("""
            UPDATE learned_fixes
            SET times_used=?, last_used=?
            WHERE id=?
        """, (existing[1] + 1, datetime.now().strftime('%Y-%m-%d %H:%M'), existing[0]))
        print(f"Updated existing fix — used {existing[1] + 1} times now.")
    else:
        cursor.execute("""
            INSERT INTO learned_fixes
            (language, bug_type, bug_pattern, successful_fix, last_used, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            language, bug_type, bug_pattern, successful_fix,
            datetime.now().strftime('%Y-%m-%d %H:%M'),
            datetime.now().strftime('%Y-%m-%d %H:%M')
        ))
        print("New fix pattern learned.")

    conn.commit()
    conn.close()

def get_learned_fix(language: str, bug_type: str, bug_pattern: str):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT successful_fix, times_used, success_rate
        FROM learned_fixes
        WHERE language=? AND bug_type=?
        AND bug_pattern LIKE ?
        ORDER BY times_used DESC, success_rate DESC
        LIMIT 1
    """, (language, bug_type, f"%{bug_pattern[:20]}%"))

    result = cursor.fetchone()
    conn.close()

    if result:
        return {
            "fix": result[0],
            "times_used": result[1],
            "success_rate": result[2],
            "from_memory": True
        }
    return None

def learn_coding_style(code: str, language: str):
    prompt = f"""Analyze this {language} code and identify the developer's coding style preferences.

Code:
{code}

Return ONLY a JSON object:
{{
    "indentation": "<spaces or tabs>",
    "quote_style": "<single or double>",
    "naming_convention": "<camelCase, snake_case, or PascalCase>",
    "comment_style": "<inline, block, or none>",
    "line_length": "<short under 80, medium 80-120, or long over 120>"
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
        style = json.loads(raw)
        save_coding_style(style)
        return style
    except:
        return None

def save_coding_style(style: dict):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    for key, value in style.items():
        cursor.execute("""
            INSERT INTO coding_style (style_key, style_value, updated_at)
            VALUES (?, ?, ?)
            ON CONFLICT(style_key) DO UPDATE SET
            style_value=excluded.style_value,
            updated_at=excluded.updated_at
        """, (key, value, datetime.now().strftime('%Y-%m-%d %H:%M')))

    conn.commit()
    conn.close()
    print("Coding style saved.")

def get_coding_style():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT style_key, style_value FROM coding_style")
    rows = cursor.fetchall()
    conn.close()

    if rows:
        return {row[0]: row[1] for row in rows}
    return None

def learn_user_pattern(pattern_type: str, pattern_value: str):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, frequency FROM user_patterns
        WHERE pattern_type=? AND pattern_value=?
    """, (pattern_type, pattern_value))

    existing = cursor.fetchone()

    if existing:
        cursor.execute("""
            UPDATE user_patterns
            SET frequency=?, last_seen=?
            WHERE id=?
        """, (existing[1] + 1, datetime.now().strftime('%Y-%m-%d %H:%M'), existing[0]))
    else:
        cursor.execute("""
            INSERT INTO user_patterns (pattern_type, pattern_value, last_seen)
            VALUES (?, ?, ?)
        """, (pattern_type, pattern_value, datetime.now().strftime('%Y-%m-%d %H:%M')))

    conn.commit()
    conn.close()

def get_smart_suggestion(language: str, bug_type: str, bug_description: str):
    known_fix = get_learned_fix(language, bug_type, bug_description)

    if known_fix and known_fix["times_used"] >= 2:
        print(f"Memory match found — used {known_fix['times_used']} times before.")
        return {
            "suggestion": known_fix["fix"],
            "confidence": "high",
            "source": "memory",
            "times_seen": known_fix["times_used"]
        }

    prompt = f"""You are an expert {language} developer with a great memory.

Bug type: {bug_type}
Bug description: {bug_description}

Based on common patterns, what is the most likely fix?

Return ONLY a JSON object:
{{
    "suggestion": "<the most likely fix>",
    "confidence": "<high, medium, or low>",
    "reasoning": "<why this is likely the fix>"
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
        result = json.loads(raw)
        result["source"] = "ai"
        result["times_seen"] = 0
        return result
    except:
        return None

def print_learning_stats():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM learned_fixes")
    total_fixes = cursor.fetchone()[0]

    cursor.execute("SELECT SUM(times_used) FROM learned_fixes")
    total_uses = cursor.fetchone()[0] or 0

    cursor.execute("SELECT language, COUNT(*) FROM learned_fixes GROUP BY language")
    by_language = cursor.fetchall()

    cursor.execute("SELECT bug_type, times_used FROM learned_fixes ORDER BY times_used DESC LIMIT 3")
    top_bugs = cursor.fetchall()

    conn.close()

    print("\nLearning Engine Stats:")
    print(f"  Total fix patterns learned: {total_fixes}")
    print(f"  Total times memory used: {total_uses}")
    print(f"  Languages learned: {[row[0] for row in by_language]}")
    if top_bugs:
        print(f"  Most common bugs:")
        for bug in top_bugs:
            print(f"    {bug[0]} — seen {bug[1]} times")

if __name__ == "__main__":
    print("=" * 40)
    print("  Learning Engine Test")
    print("=" * 40)
    print()

    init_learning_db()

    print("\nTeaching bot a fix pattern...")
    learn_from_fix(
        language="python",
        bug_type="NameError",
        bug_pattern="return averge",
        successful_fix="return average"
    )

    learn_from_fix(
        language="python",
        bug_type="NameError",
        bug_pattern="return averge",
        successful_fix="return average"
    )

    print("\nChecking if bot remembers...")
    suggestion = get_smart_suggestion("python", "NameError", "return averge")
    if suggestion:
        print(f"Suggestion: {suggestion['suggestion']}")
        print(f"Confidence: {suggestion['confidence']}")
        print(f"Source: {suggestion['source']}")
        print(f"Times seen: {suggestion['times_seen']}")

    print("\nLearning coding style...")
    sample_code = """
def calculate_average(numbers):
    total = 0
    for num in numbers:
        total += num
    average = total / len(numbers)
    return average
"""
    style = learn_coding_style(sample_code, "python")
    if style:
        print(f"Detected style: {style}")

    print("\nGetting coding style from memory...")
    saved_style = get_coding_style()
    if saved_style:
        print(f"Saved style: {saved_style}")

    print_learning_stats()
