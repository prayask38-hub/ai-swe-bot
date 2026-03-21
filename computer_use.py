import pyautogui
import time
import json
import os
import subprocess
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.5

def get_screen_size():
    size = pyautogui.size()
    return size.width, size.height

def ask_permission(action: str):
    print(f"\nBot wants to: {action}")
    answer = input("Allow? (yes/no): ").strip().lower()
    return answer == "yes"

def execute_action(action: dict):
    action_type = action.get("type")

    if action_type == "search_and_open":
        app = action["app"]
        if ask_permission(f"Open application: {app}"):
            pyautogui.hotkey("win")
            time.sleep(1)
            pyautogui.typewrite(app, interval=0.05)
            time.sleep(1)
            pyautogui.press("enter")
            time.sleep(2)
            print(f"Done — opened {app}")

    elif action_type == "click":
        x, y = action["x"], action["y"]
        if ask_permission(f"Click at ({x}, {y}) — {action.get('reason', '')}"):
            pyautogui.click(x, y)
            print(f"Done — clicked at ({x}, {y})")

    elif action_type == "type":
        text = action["text"]
        if ask_permission(f"Type: {text}"):
            print("Refocusing target window in 3 seconds — do NOT click anything...")
            time.sleep(3)
            pyautogui.typewrite(text, interval=0.08)
            print(f"Done — typed: {text}")

    elif action_type == "type_special":
        text = action["text"]
        if ask_permission(f"Type (special chars): {text}"):
            print("Refocusing target window in 3 seconds — do NOT click anything...")
            time.sleep(3)
            pyautogui.hotkey("alt", "tab")
            time.sleep(0.5)
            import pyperclip
            pyperclip.copy(text)
            pyautogui.hotkey("ctrl", "v")
            print(f"Done — typed: {text}")

    elif action_type == "key":
        key = action["key"]
        if ask_permission(f"Press key: {key}"):
            pyautogui.press(key)
            print(f"Done — pressed: {key}")

    elif action_type == "hotkey":
        keys = action["keys"]
        if ask_permission(f"Press hotkey: {'+'.join(keys)}"):
            pyautogui.hotkey(*keys)
            print(f"Done — hotkey: {'+'.join(keys)}")

    elif action_type == "focus_window":
        window = action["window"]
        if ask_permission(f"Focus window: {window}"):
            print(f"Please click on {window} window now. Waiting 3 seconds...")
            time.sleep(3)
            print("Done — window focused")

    elif action_type == "wait":
        seconds = action.get("seconds", 1)
        print(f"Waiting {seconds} seconds...")
        time.sleep(seconds)
        print("Done — waited")

    elif action_type == "done":
        print(f"\nTask complete: {action.get('message', 'Done')}")
        return True

    time.sleep(0.5)
    return False

def plan_task(task: str):
    width, height = get_screen_size()

    prompt = f"""You are an AI agent controlling a Windows {width}x{height} computer.

Task: {task}

IMPORTANT RULES:
- Always use search_and_open to open any application
- After opening an app, always add a focus_window step so the app gets focus
- For typing text, always use the type action
- Keep steps simple and reliable

Available actions:
1. search_and_open — opens app via Windows search bar
2. focus_window — waits for user to click on the target window
3. click — clicks at x,y coordinates
4. type — types simple text (letters, numbers, spaces only)
5. key — presses single key: enter, escape, tab, backspace
6. hotkey — key combination like ctrl+s, ctrl+c, alt+tab
7. wait — waits for seconds
8. done — marks task complete

Example for "open notepad and type Hello World":
[
  {{"type": "search_and_open", "app": "notepad", "reason": "opening notepad"}},
  {{"type": "focus_window", "window": "Notepad", "reason": "making sure notepad has focus"}},
  {{"type": "type", "text": "Hello World", "reason": "typing the text"}},
  {{"type": "done", "message": "opened notepad and typed Hello World"}}
]

Now create the plan for: {task}

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
    print("SAFETY: Move mouse to top-left corner to stop anytime.")
    print("Bot will ask permission before every single action.")
    print("=" * 40)

    print("\nPlanning steps...")
    steps = plan_task(task)

    if not steps:
        print("Could not plan task. Try a simpler instruction.")
        return

    print(f"\nPlan ready — {len(steps)} steps:")
    for i, step in enumerate(steps):
        print(f"  {i+1}. {step.get('type')} — {step.get('reason', step.get('message', ''))}")

    confirm = input("\nExecute this plan? (yes/no): ").strip().lower()
    if confirm != "yes":
        print("Cancelled.")
        return

    print("\nExecuting...")
    for i, step in enumerate(steps):
        print(f"\nStep {i+1}/{len(steps)} — {step.get('type')}")
        done = execute_action(step)
        if done:
            break

    print("\nComputer use session ended.")

if __name__ == "__main__":
    print("=" * 40)
    print("  AI SWE Bot — Computer Use Agent")
    print("=" * 40)
    print("This bot will control your mouse and keyboard.")
    print("You must approve every action before it runs.")
    print("Move mouse to TOP-LEFT corner to emergency stop.")
    print()
    task = input("What do you want the bot to do? ")
    run_task(task)
