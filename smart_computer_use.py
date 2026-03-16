import pyautogui
import time
import json
import os
from groq import Groq
from dotenv import load_dotenv
from knowledge_base import format_knowledge_for_prompt

load_dotenv()

client = Groq(api_key=os.getenv("GROK_API_KEY"))

pyautogui.FAILSAFE = True
pyautogui.PAUSE = 1

DELAY_AFTER_YES = 5

def ask_permission(action: str):
    print(f"\nBot wants to: {action}")
    answer = input("Allow? (yes/no): ").strip().lower()
    if answer == "yes":
        print(f"Starting in {DELAY_AFTER_YES} seconds — switch to your target window NOW...")
        for i in range(DELAY_AFTER_YES, 0, -1):
            print(f"  {i}...")
            time.sleep(1)
        print("  Executing now.")
    return answer == "yes"

def detect_app(task: str):
    task = task.lower()
    if "word" in task or "document" in task or "doc" in task:
        return "word"
    elif "excel" in task or "spreadsheet" in task or "sheet" in task:
        return "excel"
    elif "powerpoint" in task or "presentation" in task or "slides" in task:
        return "powerpoint"
    elif "outlook" in task or "email" in task or "mail" in task:
        return "outlook"
    elif "chrome" in task or "browser" in task or "website" in task or "google" in task:
        return "chrome"
    elif "vscode" in task or "vs code" in task or "code editor" in task:
        return "vscode"
    elif "spotify" in task or "music" in task or "song" in task:
        return "spotify"
    elif "file explorer" in task or "folder" in task or "files" in task:
        return "explorer"
    else:
        return "windows"


def execute_action(action: dict):
    action_type = action.get("type")

    if action_type == "search_and_open":
        app = action["app"]
        if ask_permission(f"Open application: {app}"):
            pyautogui.hotkey("win")
            time.sleep(1.5)
            pyautogui.typewrite(app, interval=0.08)
            time.sleep(1.5)
            pyautogui.press("enter")
            time.sleep(4)
            print(f"Done — opened {app}")

    elif action_type == "focus_window":
        window = action["window"]
        print(f"\nPlease click on the {window} window.")
        print("Waiting 6 seconds for you to click...")
        time.sleep(6)
        print("Done — continuing.")

    elif action_type == "focus_click":
        x, y = action["x"], action["y"]
        reason = action.get("reason", "")
        print(f"\nAuto clicking at ({x},{y}) — {reason}")
        print("Clicking in 3 seconds...")
        time.sleep(3)
        pyautogui.click(x, y)
        time.sleep(2)
        print(f"Done — clicked ({x},{y})")

    elif action_type == "click":
        x, y = action["x"], action["y"]
        if ask_permission(f"Click at ({x},{y}) — {action.get('reason', '')}"):
            pyautogui.click(x, y)
            time.sleep(1)
            print(f"Done — clicked ({x},{y})")

    elif action_type == "type":
        text = action["text"]
        if ask_permission(f"Type text: {text}"):
            pyautogui.typewrite(text, interval=0.08)
            time.sleep(1)
            print(f"Done — typed: {text}")

    elif action_type == "hotkey":
        keys = action["keys"]
        if ask_permission(f"Press hotkey: {'+'.join(keys)} — {action.get('reason', '')}"):
            pyautogui.hotkey(*keys)
            time.sleep(1)
            print(f"Done — pressed {'+'.join(keys)}")

    elif action_type == "key":
        key = action["key"]
        if ask_permission(f"Press key: {key} — {action.get('reason', '')}"):
            pyautogui.press(key)
            time.sleep(1)
            print(f"Done — pressed {key}")

    elif action_type == "wait":
        seconds = action.get("seconds", 2)
        print(f"Waiting {seconds} seconds...")
        time.sleep(seconds)
        print("Done — waited.")

    elif action_type == "done":
        print(f"\nTask complete: {action.get('message', 'All done!')}")
        return True

    time.sleep(2)
    return False

def plan_task(task: str):
    app = detect_app(task)
    knowledge = format_knowledge_for_prompt(app)
    width, height = pyautogui.size()
    cx = width // 2
    cy = height // 2

    prompt = f"""You are an AI agent controlling a Windows {width}x{height} computer.

Task: {task}

Use this knowledge to plan correctly:
{knowledge}

IMPORTANT RULES:
- Always start with search_and_open to open the app
- Always add focus_window after opening so user can click on the app
- For Microsoft Word: after opening, always use focus_click at (192,190) to click the Blank document button
- After clicking Blank document, always add wait of 3 seconds for document to load
- After wait, always add focus_click at ({cx},{cy}) to click center of document for typing focus
- Only after focus_click at center can you use type action
- Use hotkey for keyboard shortcuts
- Use type for entering text only AFTER clicking center of document
- Use key for single keys like enter, escape, tab
- End with done when task is complete

Available actions:
- search_and_open: open app via windows search
- focus_window: user manually clicks the app window
- focus_click: automatically clicks at x,y — NO permission needed — use for blank document and document center
- hotkey: keyboard shortcut
- type: type text
- key: single key press
- wait: wait seconds
- done: task complete

Example for "open word and type Hello World":
[
  {{"type": "search_and_open", "app": "microsoft word", "reason": "opening word"}},
  {{"type": "focus_window", "window": "Microsoft Word", "reason": "click word window"}},
  {{"type": "focus_click", "x": 192, "y": 190, "reason": "click blank document button"}},
  {{"type": "wait", "seconds": 3, "reason": "wait for blank document to fully load"}},
  {{"type": "focus_click", "x": {cx}, "y": {cy}, "reason": "click center of document for typing focus"}},
  {{"type": "type", "text": "Hello World", "reason": "typing text into document"}},
  {{"type": "done", "message": "typed Hello World in word document"}}
]

Now plan for: {task}

Return ONLY a JSON array. No extra text. No markdown."""

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
    start = raw.find("[")
    end = raw.rfind("]") + 1
    if start != -1 and end != 0:
        return json.loads(raw[start:end])
    return []

def run_task(task: str):
    print(f"\nTask: {task}")
    print("=" * 40)
    print("SAFETY: Move mouse to TOP-LEFT corner anytime to stop.")
    print("=" * 40)

    app = detect_app(task)
    print(f"Detected app: {app.upper()}")

    print("\nPlanning steps using knowledge base...")
    steps = plan_task(task)

    if not steps:
        print("Could not plan task. Try rephrasing.")
        return

    print(f"\nPlan ready — {len(steps)} steps:")
    for i, step in enumerate(steps):
        print(f"  {i+1}. {step.get('type')} — {step.get('reason', step.get('message', ''))}")

    confirm = input("\nExecute this plan? (yes/no): ").strip().lower()
    if confirm != "yes":
        print("Cancelled.")
        return

    print("\nStarting execution...\n")
    for i, step in enumerate(steps):
        print(f"\n--- Step {i+1} of {len(steps)} ---")
        done = execute_action(step)
        if done:
            break

    print("\nSession ended.")

if __name__ == "__main__":
    print("=" * 40)
    print("  AI SWE Bot — Smart Computer Use")
    print("  Powered by M365 Knowledge Base")
    print("=" * 40)
    print()
    print("Examples:")
    print("  open word and write Hello World")
    print("  open excel and create a spreadsheet")
    print("  open powerpoint and add a new slide")
    print("  open notepad and write hello world")
    print()
    task = input("What do you want the bot to do? ")
    run_task(task)
