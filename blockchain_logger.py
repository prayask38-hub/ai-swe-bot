import hashlib
import json
import os
import sqlite3
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

DB_PATH = "ai_swe_bot.db"

def init_blockchain_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS blockchain_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            block_number INTEGER UNIQUE,
            timestamp TEXT,
            action_type TEXT,
            action_data TEXT,
            user_consent TEXT,
            previous_hash TEXT,
            current_hash TEXT,
            verified INTEGER DEFAULT 1
        )
    """)

    conn.commit()
    conn.close()
    print("Blockchain logger initialized.")

def get_last_block():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT block_number, current_hash
        FROM blockchain_log
        ORDER BY block_number DESC
        LIMIT 1
    """)
    result = cursor.fetchone()
    conn.close()
    return result

def calculate_hash(block_number: int, timestamp: str, action_type: str,
                   action_data: str, previous_hash: str):
    content = f"{block_number}{timestamp}{action_type}{action_data}{previous_hash}"
    return hashlib.sha256(content.encode()).hexdigest()

def log_action(action_type: str, action_data: dict, user_consent: bool = True):
    last_block = get_last_block()

    if last_block:
        block_number = last_block[0] + 1
        previous_hash = last_block[1]
    else:
        block_number = 1
        previous_hash = "0" * 64

    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    action_data_str = json.dumps(action_data)
    consent_str = "granted" if user_consent else "denied"

    current_hash = calculate_hash(
        block_number, timestamp, action_type,
        action_data_str, previous_hash
    )

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO blockchain_log
        (block_number, timestamp, action_type, action_data,
         user_consent, previous_hash, current_hash)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        block_number, timestamp, action_type, action_data_str,
        consent_str, previous_hash, current_hash
    ))

    conn.commit()
    conn.close()

    print(f"Block #{block_number} logged: {action_type}")
    print(f"Hash: {current_hash[:20]}...")
    return current_hash

def verify_chain():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT block_number, timestamp, action_type, action_data,
               previous_hash, current_hash
        FROM blockchain_log
        ORDER BY block_number ASC
    """)

    blocks = cursor.fetchall()
    conn.close()

    if not blocks:
        print("No blocks to verify.")
        return True

    print(f"\nVerifying {len(blocks)} blocks...")
    previous_hash = "0" * 64
    all_valid = True

    for block in blocks:
        block_number = block[0]
        timestamp = block[1]
        action_type = block[2]
        action_data = block[3]
        stored_previous = block[4]
        stored_hash = block[5]

        if stored_previous != previous_hash:
            print(f"Block #{block_number} — CHAIN BROKEN")
            all_valid = False
            break

        calculated_hash = calculate_hash(
            block_number, timestamp, action_type,
            action_data, previous_hash
        )

        if calculated_hash != stored_hash:
            print(f"Block #{block_number} — TAMPERED")
            all_valid = False
        else:
            print(f"Block #{block_number} — VALID")

        previous_hash = stored_hash

    if all_valid:
        print("\nBlockchain integrity: VERIFIED")
    else:
        print("\nBlockchain integrity: COMPROMISED")

    return all_valid

def get_audit_trail(action_type: str = None, limit: int = 20):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    if action_type:
        cursor.execute("""
            SELECT block_number, timestamp, action_type,
                   action_data, user_consent, current_hash
            FROM blockchain_log
            WHERE action_type = ?
            ORDER BY block_number DESC
            LIMIT ?
        """, (action_type, limit))
    else:
        cursor.execute("""
            SELECT block_number, timestamp, action_type,
                   action_data, user_consent, current_hash
            FROM blockchain_log
            ORDER BY block_number DESC
            LIMIT ?
        """, (limit,))

    blocks = cursor.fetchall()
    conn.close()
    return blocks

def print_audit_trail(action_type: str = None):
    blocks = get_audit_trail(action_type)

    print("\n" + "=" * 50)
    print("  BLOCKCHAIN AUDIT TRAIL")
    print("=" * 50)

    if not blocks:
        print("No audit records found.")
        return

    for block in blocks:
        block_number = block[0]
        timestamp = block[1]
        action_type = block[2]
        action_data = block[3]
        consent = block[4]
        hash_val = block[5]

        print(f"\nBlock #{block_number}")
        print(f"  Time:    {timestamp}")
        print(f"  Action:  {action_type}")
        print(f"  Consent: {consent.upper()}")
        print(f"  Hash:    {hash_val[:30]}...")

        try:
            data = json.loads(action_data)
            for key, value in list(data.items())[:3]:
                print(f"  {key}: {str(value)[:50]}")
        except:
            pass

def get_blockchain_stats():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM blockchain_log")
    total_blocks = cursor.fetchone()[0]

    cursor.execute("""
        SELECT action_type, COUNT(*) as count
        FROM blockchain_log
        GROUP BY action_type
        ORDER BY count DESC
    """)
    action_stats = cursor.fetchall()

    cursor.execute("""
        SELECT user_consent, COUNT(*) as count
        FROM blockchain_log
        GROUP BY user_consent
    """)
    consent_stats = cursor.fetchall()

    conn.close()

    print(f"\nBlockchain Stats:")
    print(f"  Total blocks: {total_blocks}")
    print(f"\n  Actions logged:")
    for stat in action_stats:
        print(f"    {stat[0]}: {stat[1]} times")
    print(f"\n  Consent breakdown:")
    for stat in consent_stats:
        print(f"    {stat[0]}: {stat[1]} times")

if __name__ == "__main__":
    print("=" * 40)
    print("  Blockchain Audit Logger")
    print("=" * 40)
    print()

    init_blockchain_db()

    print("\nLogging test actions...")
    log_action("bug_detected", {
        "language": "python",
        "bug_type": "NameError",
        "line": 7,
        "severity": "high"
    }, user_consent=True)

    log_action("fix_applied", {
        "language": "python",
        "fix": "return average",
        "original": "return averge",
        "confidence": "high"
    }, user_consent=True)

    log_action("file_accessed", {
        "file": "main.py",
        "operation": "read",
        "reason": "bug analysis"
    }, user_consent=True)

    log_action("computer_use", {
        "action": "open_app",
        "app": "notepad",
        "authorized": True
    }, user_consent=True)

    log_action("code_executed", {
        "language": "python",
        "sandbox": True,
        "result": "passed"
    }, user_consent=True)

    print("\nVerifying blockchain integrity...")
    verify_chain()

    print_audit_trail()
    get_blockchain_stats()
