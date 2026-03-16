import sqlite3
import json
import os
from datetime import datetime

DB_PATH = "ai_swe_bot.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            language TEXT,
            total_bugs INTEGER,
            bugs_fixed INTEGER,
            code_health TEXT,
            original_code TEXT,
            fixed_code TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS bugs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id INTEGER,
            bug_type TEXT,
            line_number INTEGER,
            description TEXT,
            severity TEXT,
            solution_used TEXT,
            FOREIGN KEY (session_id) REFERENCES sessions(id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS successful_fixes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            language TEXT,
            bug_type TEXT,
            original_line TEXT,
            fixed_line TEXT,
            times_used INTEGER DEFAULT 1
        )
    """)

    conn.commit()
    conn.close()
    print("Database initialized.")

def save_session(language, total_bugs, bugs_fixed, code_health, original_code, fixed_code):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO sessions (date, language, total_bugs, bugs_fixed, code_health, original_code, fixed_code)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (datetime.now().strftime('%Y-%m-%d %H:%M'), language, total_bugs, bugs_fixed, code_health, original_code, fixed_code))

    session_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return session_id

def save_bug(session_id, bug_type, line_number, description, severity, solution_used):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO bugs (session_id, bug_type, line_number, description, severity, solution_used)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (session_id, bug_type, line_number, description, severity, solution_used))

    conn.commit()
    conn.close()

def save_successful_fix(language, bug_type, original_line, fixed_line):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, times_used FROM successful_fixes
        WHERE language=? AND bug_type=? AND original_line=?
    """, (language, bug_type, original_line))

    existing = cursor.fetchone()

    if existing:
        cursor.execute("""
            UPDATE successful_fixes SET times_used=? WHERE id=?
        """, (existing[1] + 1, existing[0]))
        print(f"Updated existing fix — used {existing[1] + 1} times now.")
    else:
        cursor.execute("""
            INSERT INTO successful_fixes (language, bug_type, original_line, fixed_line)
            VALUES (?, ?, ?, ?)
        """, (language, bug_type, original_line, fixed_line))
        print("New fix saved to memory.")

    conn.commit()
    conn.close()

def get_known_fix(language, bug_type, original_line):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT fixed_line, times_used FROM successful_fixes
        WHERE language=? AND bug_type=? AND original_line=?
        ORDER BY times_used DESC LIMIT 1
    """, (language, bug_type, original_line))

    result = cursor.fetchone()
    conn.close()

    if result:
        return {"fixed_line": result[0], "times_used": result[1]}
    return None

def get_all_sessions():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, date, language, total_bugs, bugs_fixed, code_health
        FROM sessions ORDER BY id DESC
    """)

    sessions = cursor.fetchall()
    conn.close()
    return sessions

def print_stats():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM sessions")
    total_sessions = cursor.fetchone()[0]

    cursor.execute("SELECT SUM(total_bugs) FROM sessions")
    total_bugs = cursor.fetchone()[0] or 0

    cursor.execute("SELECT SUM(bugs_fixed) FROM sessions")
    total_fixed = cursor.fetchone()[0] or 0

    cursor.execute("SELECT COUNT(*) FROM successful_fixes")
    known_fixes = cursor.fetchone()[0]

    conn.close()

    print(f"Total sessions: {total_sessions}")
    print(f"Total bugs found: {total_bugs}")
    print(f"Total bugs fixed: {total_fixed}")
    print(f"Known fixes in memory: {known_fixes}")

# Test the storage
print("Initializing local database...\n")
init_db()

print("Saving a test session...\n")
session_id = save_session(
    language="python",
    total_bugs=2,
    bugs_fixed=2,
    code_health="good",
    original_code="return averge",
    fixed_code="return average"
)
print(f"Session saved with ID: {session_id}\n")

save_bug(session_id, "NameError", 7, "averge should be average", "high", "Typo Fix")
save_bug(session_id, "TypeError", 9, "string + float concat", "medium", "str() function")
print("Bugs saved.\n")

save_successful_fix("python", "NameError", "return averge", "return average")
save_successful_fix("python", "TypeError", 'print("Average is: " + result)', 'print("Average is: " + str(result))')

print("\nChecking if we know how to fix this bug already...")
known = get_known_fix("python", "NameError", "return averge")
if known:
    print(f"Yes! Known fix: {known['fixed_line']} (used {known['times_used']} times)")
else:
    print("No known fix yet.")

print("\nAll sessions:")
for s in get_all_sessions():
    print(f"  [{s[0]}] {s[1]} — {s[2].upper()} — {s[3]} bugs — health: {s[5]}")

print("\nOverall stats:")
print_stats()
