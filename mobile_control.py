import os
import json
import socket
import qrcode
import threading
from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

app = Flask(__name__)
CORS(app)

task_history = []
current_status = {"status": "idle", "last_task": None, "tasks_completed": 0}

def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
    except:
        ip = "127.0.0.1"
    finally:
        s.close()
    return ip

def generate_qr_code(url: str):
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    img.save("mobile_qr.png")
    print(f"QR code saved to mobile_qr.png")

@app.route("/")
def index():
    return jsonify({
        "name": "AI SWE Bot Mobile Control",
        "version": "1.0",
        "status": current_status["status"],
        "endpoints": [
            "GET /status — bot status",
            "POST /fix — fix code bugs",
            "POST /task — run any task",
            "POST /voice — voice command",
            "GET /history — task history",
            "POST /computer — computer control",
            "GET /stats — bot statistics"
        ]
    })

@app.route("/status")
def status():
    return jsonify({
        "status": current_status["status"],
        "last_task": current_status["last_task"],
        "tasks_completed": current_status["tasks_completed"],
        "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        "bot_name": "AI SWE Bot",
        "version": "V2"
    })

@app.route("/fix", methods=["POST"])
def fix_code():
    data = request.json
    code = data.get("code", "")
    language = data.get("language", "python")

    if not code:
        return jsonify({"error": "No code provided"}), 400

    current_status["status"] = "analyzing"

    prompt = f"""Analyze this {language} code and find ALL bugs.

Code:
{code}

Return ONLY a JSON object:
{{
    "total_bugs": <number>,
    "bugs": [
        {{
            "line": <number>,
            "type": "<error type>",
            "description": "<what is wrong>",
            "fix": "<how to fix>",
            "severity": "<high, medium, or low>"
        }}
    ],
    "fixed_code": "<complete fixed version of the code>"
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
        current_status["status"] = "idle"
        current_status["last_task"] = f"Fixed {result['total_bugs']} bugs in {language} code"
        current_status["tasks_completed"] += 1
        task_history.append({
            "type": "fix_code",
            "language": language,
            "bugs_found": result["total_bugs"],
            "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M')
        })
        return jsonify(result)
    except:
        current_status["status"] = "idle"
        return jsonify({"error": "Could not analyze code"}), 500

@app.route("/task", methods=["POST"])
def run_task():
    data = request.json
    task = data.get("task", "")

    if not task:
        return jsonify({"error": "No task provided"}), 400

    current_status["status"] = "working"
    current_status["last_task"] = task

    prompt = f"""You are an AI assistant. Complete this task and provide a clear response.

Task: {task}

Return ONLY a JSON object:
{{
    "task": "{task}",
    "result": "<detailed result>",
    "steps_taken": ["<step1>", "<step2>"],
    "success": true
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
        current_status["status"] = "idle"
        current_status["tasks_completed"] += 1
        task_history.append({
            "type": "task",
            "task": task,
            "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M')
        })
        return jsonify(result)
    except:
        current_status["status"] = "idle"
        return jsonify({"error": "Could not complete task"}), 500

@app.route("/voice", methods=["POST"])
def voice_command():
    data = request.json
    command = data.get("command", "")

    if not command:
        return jsonify({"error": "No command provided"}), 400

    current_status["status"] = "processing voice"

    prompt = f"""You are an AI assistant receiving a voice command.

Command: {command}

Interpret and respond to this command clearly.

Return ONLY a JSON object:
{{
    "command": "{command}",
    "interpreted_as": "<what you understood>",
    "response": "<your response>",
    "action_taken": "<what you did or will do>"
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
        current_status["status"] = "idle"
        current_status["tasks_completed"] += 1
        return jsonify(result)
    except:
        current_status["status"] = "idle"
        return jsonify({"error": "Could not process voice command"}), 500

@app.route("/computer", methods=["POST"])
def computer_control():
    data = request.json
    action = data.get("action", "")
    params = data.get("params", {})

    if not action:
        return jsonify({"error": "No action provided"}), 400

    current_status["status"] = f"executing {action}"

    try:
        import pyautogui
        import time

        result = {"action": action, "success": False, "message": ""}

        if action == "screenshot":
            screenshot = pyautogui.screenshot()
            screenshot.save("mobile_screenshot.png")
            result["success"] = True
            result["message"] = "Screenshot saved"

        elif action == "type":
            text = params.get("text", "")
            time.sleep(2)
            pyautogui.typewrite(text, interval=0.05)
            result["success"] = True
            result["message"] = f"Typed: {text}"

        elif action == "hotkey":
            keys = params.get("keys", [])
            if keys:
                pyautogui.hotkey(*keys)
                result["success"] = True
                result["message"] = f"Pressed: {'+'.join(keys)}"

        elif action == "open_app":
            app_name = params.get("app", "")
            import subprocess
            subprocess.Popen(["cmd", "/c", "start", app_name])
            result["success"] = True
            result["message"] = f"Opened: {app_name}"

        elif action == "scroll":
            direction = params.get("direction", "down")
            amount = params.get("amount", 3)
            if direction == "down":
                pyautogui.scroll(-amount)
            else:
                pyautogui.scroll(amount)
            result["success"] = True
            result["message"] = f"Scrolled {direction}"

        current_status["status"] = "idle"
        current_status["tasks_completed"] += 1
        return jsonify(result)

    except Exception as e:
        current_status["status"] = "idle"
        return jsonify({"error": str(e)}), 500

@app.route("/history")
def history():
    return jsonify({
        "total_tasks": len(task_history),
        "tasks": task_history[-20:]
    })

@app.route("/stats")
def stats():
    try:
        import sqlite3
        conn = sqlite3.connect("ai_swe_bot.db")
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM sessions")
        sessions = cursor.fetchone()[0]
        cursor.execute("SELECT SUM(total_bugs) FROM sessions")
        bugs = cursor.fetchone()[0] or 0
        cursor.execute("SELECT SUM(bugs_fixed) FROM sessions")
        fixed = cursor.fetchone()[0] or 0
        conn.close()
        return jsonify({
            "total_sessions": sessions,
            "total_bugs_found": bugs,
            "total_bugs_fixed": fixed,
            "fix_rate": round(fixed/bugs*100, 1) if bugs > 0 else 0,
            "tasks_this_session": current_status["tasks_completed"]
        })
    except:
        return jsonify({"error": "Could not get stats"}), 500

def start_mobile_server(port: int = 5001):
    ip = get_local_ip()
    url = f"http://{ip}:{port}"

    print("=" * 40)
    print("  AI SWE Bot — Mobile Control")
    print("=" * 40)
    print(f"\nServer running at: {url}")
    print(f"\nScan QR code to connect from your phone:")
    print(f"(Both devices must be on same WiFi)")
    print()

    generate_qr_code(url)

    print(f"QR code saved — open mobile_qr.png and scan it")
    print(f"\nOr manually enter in browser: {url}")
    print(f"\nAPI endpoints:")
    print(f"  GET  {url}/status")
    print(f"  POST {url}/fix")
    print(f"  POST {url}/task")
    print(f"  POST {url}/voice")
    print(f"  GET  {url}/history")
    print(f"  GET  {url}/stats")
    print(f"\nPress Ctrl+C to stop.")

    app.run(host="0.0.0.0", port=port, debug=False)

if __name__ == "__main__":
    start_mobile_server()
