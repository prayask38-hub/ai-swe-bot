import os
import cv2
import json
import hashlib
import sqlite3
import numpy as np
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

DB_PATH = "ai_swe_bot.db"

def init_biometric_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS biometric_auth (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT UNIQUE,
            face_hash TEXT,
            enrolled_at TEXT,
            last_auth TEXT,
            auth_count INTEGER DEFAULT 0,
            failed_attempts INTEGER DEFAULT 0
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS auth_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT,
            auth_type TEXT,
            success INTEGER,
            timestamp TEXT,
            details TEXT
        )
    """)
    conn.commit()
    conn.close()
    print("Biometric database initialized.")

def capture_face():
    print("Opening camera...")
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("No camera found.")
        return None

    face_cascade = cv2.CascadeClassifier(
        cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
    )

    print("Position your face in front of the camera.")
    print("Press SPACE to capture or Q to quit.")

    face_frame = None

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)

        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
            cv2.putText(frame, "Face detected", (x, y-10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

        cv2.putText(frame, "SPACE=capture Q=quit", (10, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        cv2.imshow("AI SWE Bot — Biometric Auth", frame)

        key = cv2.waitKey(1) & 0xFF
        if key == ord(' '):
            if len(faces) > 0:
                x, y, w, h = faces[0]
                face_frame = gray[y:y+h, x:x+w]
                face_frame = cv2.resize(face_frame, (100, 100))
                print("Face captured successfully.")
                break
            else:
                print("No face detected. Try again.")
        elif key == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    return face_frame

def compute_face_hash(face_frame) -> str:
    normalized = cv2.normalize(face_frame, None, 0, 255, cv2.NORM_MINMAX)
    face_bytes = normalized.tobytes()
    return hashlib.sha256(face_bytes).hexdigest()

def enroll_user(user_id: str = "prayas"):
    print(f"\nEnrolling user: {user_id}")
    print("We will capture 3 face samples for accuracy.")

    face_hashes = []

    for i in range(3):
        print(f"\nCapture {i+1} of 3:")
        face = capture_face()
        if face is not None:
            face_hash = compute_face_hash(face)
            face_hashes.append(face_hash)
            print(f"Sample {i+1} captured.")
        else:
            print(f"Sample {i+1} failed.")

    if len(face_hashes) == 0:
        print("Enrollment failed — no face samples captured.")
        return False

    primary_hash = face_hashes[0]

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT OR REPLACE INTO biometric_auth
        (user_id, face_hash, enrolled_at, last_auth, auth_count)
        VALUES (?, ?, ?, ?, 0)
    """, (user_id, primary_hash, datetime.now().strftime('%Y-%m-%d %H:%M'), "never"))

    conn.commit()
    conn.close()

    log_auth_attempt(user_id, "enrollment", True, "User enrolled successfully")
    print(f"\nUser {user_id} enrolled successfully.")
    return True

def authenticate_user(user_id: str = "prayas") -> bool:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT face_hash, failed_attempts FROM biometric_auth WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()
    conn.close()

    if not result:
        print(f"User {user_id} not enrolled. Please enroll first.")
        return False

    stored_hash = result[0]
    failed_attempts = result[1]

    if failed_attempts >= 5:
        print("Too many failed attempts. Account locked.")
        log_auth_attempt(user_id, "face_auth", False, "Account locked")
        return False

    print(f"\nAuthenticating user: {user_id}")
    print("Please look at the camera...")

    face = capture_face()

    if face is None:
        log_auth_attempt(user_id, "face_auth", False, "No face captured")
        return False

    current_hash = compute_face_hash(face)

    if current_hash == stored_hash:
        update_auth_success(user_id)
        log_auth_attempt(user_id, "face_auth", True, "Authentication successful")
        print("\nAuthentication SUCCESSFUL.")
        return True
    else:
        similarity = compare_hashes(stored_hash, current_hash)
        print(f"Hash similarity: {similarity}%")

        if similarity > 60:
            update_auth_success(user_id)
            log_auth_attempt(user_id, "face_auth", True, f"Auth successful with {similarity}% similarity")
            print("\nAuthentication SUCCESSFUL.")
            return True
        else:
            update_auth_failure(user_id)
            log_auth_attempt(user_id, "face_auth", False, f"Auth failed with {similarity}% similarity")
            print("\nAuthentication FAILED.")
            return False

def compare_hashes(hash1: str, hash2: str) -> int:
    matches = sum(c1 == c2 for c1, c2 in zip(hash1, hash2))
    return int((matches / len(hash1)) * 100)

def update_auth_success(user_id: str):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE biometric_auth
        SET last_auth=?, auth_count=auth_count+1, failed_attempts=0
        WHERE user_id=?
    """, (datetime.now().strftime('%Y-%m-%d %H:%M'), user_id))
    conn.commit()
    conn.close()

def update_auth_failure(user_id: str):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE biometric_auth
        SET failed_attempts=failed_attempts+1
        WHERE user_id=?
    """, (user_id,))
    conn.commit()
    conn.close()

def log_auth_attempt(user_id: str, auth_type: str, success: bool, details: str):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO auth_log (user_id, auth_type, success, timestamp, details)
        VALUES (?, ?, ?, ?, ?)
    """, (user_id, auth_type, 1 if success else 0,
          datetime.now().strftime('%Y-%m-%d %H:%M:%S'), details))
    conn.commit()
    conn.close()

def pin_auth(user_id: str = "prayas") -> bool:
    import getpass
    stored_pin = os.getenv("BOT_PIN", "1234")
    print(f"\nPIN Authentication for {user_id}")
    pin = input("Enter PIN: ")

    if pin == stored_pin:
        log_auth_attempt(user_id, "pin_auth", True, "PIN authentication successful")
        print("PIN Authentication SUCCESSFUL.")
        return True
    else:
        log_auth_attempt(user_id, "pin_auth", False, "Wrong PIN")
        print("PIN Authentication FAILED.")
        return False

def multi_factor_auth(user_id: str = "prayas") -> bool:
    print("\n" + "=" * 40)
    print("  Multi-Factor Authentication")
    print("=" * 40)

    print("\nStep 1: PIN Authentication")
    pin_result = pin_auth(user_id)

    if not pin_result:
        print("MFA Failed at PIN step.")
        return False

    print("\nStep 2: Face Authentication")
    face_result = authenticate_user(user_id)

    if not face_result:
        print("MFA Failed at face step.")
        return False

    print("\nAll authentication steps passed.")
    print("Access GRANTED.")
    log_auth_attempt(user_id, "mfa", True, "Full MFA passed")
    return True

def get_auth_stats():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM auth_log WHERE success=1")
    successful = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM auth_log WHERE success=0")
    failed = cursor.fetchone()[0]

    cursor.execute("""
        SELECT user_id, auth_count, last_auth, failed_attempts
        FROM biometric_auth
    """)
    users = cursor.fetchall()

    conn.close()

    print("\nAuthentication Stats:")
    print(f"  Successful auths: {successful}")
    print(f"  Failed auths: {failed}")
    print(f"\nEnrolled users:")
    for user in users:
        print(f"  {user[0]} — {user[1]} logins — last: {user[2]} — failed: {user[3]}")

if __name__ == "__main__":
    print("=" * 40)
    print("  Biometric Authentication")
    print("=" * 40)
    print()
    print("1. Enroll new user")
    print("2. Authenticate with face")
    print("3. PIN authentication")
    print("4. Multi-factor authentication")
    print("5. View auth stats")
    print()

    init_biometric_db()

    choice = input("Choose (1-5): ").strip()

    if choice == "1":
        user_id = input("User ID (default: prayas): ").strip() or "prayas"
        enroll_user(user_id)

    elif choice == "2":
        user_id = input("User ID (default: prayas): ").strip() or "prayas"
        authenticate_user(user_id)

    elif choice == "3":
        user_id = input("User ID (default: prayas): ").strip() or "prayas"
        pin_auth(user_id)

    elif choice == "4":
        user_id = input("User ID (default: prayas): ").strip() or "prayas"
        multi_factor_auth(user_id)

    elif choice == "5":
        get_auth_stats()
