import speech_recognition as sr
import pyttsx3
import os
import json
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

engine = pyttsx3.init()
engine.setProperty("rate", 180)
engine.setProperty("volume", 1.0)

voices = engine.getProperty("voices")
for voice in voices:
    if "female" in voice.name.lower() or "zira" in voice.name.lower():
        engine.setProperty("voice", voice.id)
        break

def speak(text: str):
    print(f"Bot: {text}")
    engine.say(text)
    engine.runAndWait()

def listen():
    recognizer = sr.Recognizer()
    recognizer.energy_threshold = 3000
    recognizer.pause_threshold = 1

    with sr.Microphone() as source:
        print("\nListening... (speak now)")
        recognizer.adjust_for_ambient_noise(source, duration=1)
        try:
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=10)
            print("Processing speech...")
            text = recognizer.recognize_google(audio)
            print(f"You said: {text}")
            return text.lower()
        except sr.WaitTimeoutError:
            print("No speech detected.")
            return None
        except sr.UnknownValueError:
            print("Could not understand audio.")
            return None
        except sr.RequestError as e:
            print(f"Speech recognition error: {e}")
            return None

def process_command(command: str):
    prompt = f"""You are an AI assistant for a software engineering bot.

The user said: "{command}"

Classify this command and extract the intent.

Return ONLY a JSON object:
{{
    "intent": "<one of: fix_code, open_app, write_document, search_web, run_task, create_file, git_command, general_question, stop>",
    "action": "<brief description of what to do>",
    "app": "<app name if relevant, else null>",
    "content": "<any text content mentioned, else null>"
}}

Examples:
- "fix the bug in my code" → intent: fix_code
- "open word and write a letter" → intent: open_app, app: word
- "search for python tutorials" → intent: search_web
- "stop listening" or "exit" or "quit" → intent: stop

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
        return {"intent": "general_question", "action": command, "app": None, "content": None}

def handle_intent(intent_data: dict, original_command: str):
    intent = intent_data.get("intent")
    action = intent_data.get("action")
    app = intent_data.get("app")
    content = intent_data.get("content")

    if intent == "stop":
        speak("Goodbye Prayas. Shutting down voice control.")
        return False

    elif intent == "fix_code":
        speak("I will help you fix the code. Please paste your code in the web interface and click analyze bugs.")

    elif intent == "open_app":
        speak(f"Opening {app} now.")
        from smart_computer_use import run_task
        run_task(original_command)

    elif intent == "search_web":
        speak(f"Searching for {content or action} in Chrome.")
        from smart_computer_use import run_task
        run_task(f"open chrome and search for {content or action}")

    elif intent == "write_document":
        speak(f"Opening Word to write your document.")
        from smart_computer_use import run_task
        run_task(f"open word and write {content or action}")

    elif intent == "run_task":
        speak(f"Running task: {action}")
        from smart_computer_use import run_task
        run_task(original_command)

    elif intent == "git_command":
        speak("Git commands need to be run in terminal. Opening terminal now.")
        from smart_computer_use import run_task
        run_task("open cmd")

    elif intent == "general_question":
        speak("Let me think about that.")
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": original_command}]
        )
        answer = response.choices[0].message.content
        sentences = answer.split(".")[:2]
        short_answer = ".".join(sentences)
        speak(short_answer)

    return True

def run_voice_assistant():
    speak("Hello Prayas. AI SWE Bot voice control is ready. How can I help you?")

    while True:
        command = listen()

        if command is None:
            speak("I did not hear anything. Please try again.")
            continue

        speak(f"You said: {command}. Processing now.")

        intent_data = process_command(command)
        print(f"Intent: {intent_data}")

        should_continue = handle_intent(intent_data, command)

        if not should_continue:
            break

    print("Voice assistant stopped.")

if __name__ == "__main__":
    print("=" * 40)
    print("  AI SWE Bot — Voice Control")
    print("=" * 40)
    print()
    print("Commands you can say:")
    print("  'fix the bug in my code'")
    print("  'open word and write a letter'")
    print("  'search for python tutorials'")
    print("  'open excel and create a spreadsheet'")
    print("  'stop listening' to exit")
    print()
    print("Make sure your microphone is connected.")
    print()
    run_voice_assistant()
