import os
import json
import base64
import pyautogui
from PIL import Image, ImageEnhance, ImageFilter
from io import BytesIO
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def image_to_base64(image: Image.Image) -> str:
    buffer = BytesIO()
    image.save(buffer, format="PNG")
    return base64.standard_b64encode(buffer.getvalue()).decode("utf-8")

def take_screenshot():
    screenshot = pyautogui.screenshot()
    return screenshot

def enhance_image(image: Image.Image) -> Image.Image:
    image = image.convert("RGB")
    enhancer = ImageEnhance.Contrast(image)
    image = enhancer.enhance(1.5)
    enhancer = ImageEnhance.Sharpness(image)
    image = enhancer.enhance(2.0)
    return image

def extract_text_from_image(image: Image.Image) -> str:
    try:
        import pytesseract
        text = pytesseract.image_to_string(image)
        return text.strip()
    except Exception as e:
        print(f"OCR error: {e}")
        return ""

def analyze_screenshot_for_bugs(screenshot: Image.Image = None) -> dict:
    if screenshot is None:
        print("Taking screenshot...")
        screenshot = take_screenshot()

    enhanced = enhance_image(screenshot)
    print("Extracting text from screenshot...")
    text = extract_text_from_image(enhanced)

    if not text:
        print("No text extracted from screenshot.")
        return {"bugs": [], "analysis": "No code found in screenshot"}

    print(f"Extracted {len(text)} characters from screen")
    print("Analyzing extracted code for bugs...")

    prompt = f"""You are an expert code analyzer. I extracted this text from a screenshot of a code editor.

Extracted text:
{text[:3000]}

Analyze this for:
1. Bugs and errors
2. Code quality issues
3. What the code is trying to do

Return ONLY a JSON object:
{{
    "code_detected": true,
    "language": "<detected language or unknown>",
    "total_bugs": <number>,
    "bugs": [
        {{
            "type": "<error type>",
            "description": "<what is wrong>",
            "severity": "<high, medium, or low>"
        }}
    ],
    "code_purpose": "<what this code does>",
    "quality_score": <0-100>
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
        return {"bugs": [], "analysis": "Could not analyze screenshot"}

def analyze_diagram(image_path: str) -> dict:
    print(f"Analyzing diagram: {image_path}")

    try:
        image = Image.open(image_path)
    except Exception as e:
        print(f"Could not open image: {e}")
        return {}

    text = extract_text_from_image(image)

    prompt = f"""You are an expert at reading technical diagrams and flowcharts.

I have a technical diagram. The text extracted from it is:
{text[:2000] if text else "No text could be extracted"}

Analyze what this diagram represents and provide insights.

Return ONLY a JSON object:
{{
    "diagram_type": "<flowchart, architecture, erd, uml, wireframe, or other>",
    "purpose": "<what this diagram shows>",
    "components": ["<component1>", "<component2>"],
    "relationships": ["<relationship1>", "<relationship2>"],
    "insights": ["<insight1>", "<insight2>"],
    "suggestions": ["<improvement1>", "<improvement2>"]
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
        return {}

def analyze_ui_screenshot(screenshot: Image.Image = None) -> dict:
    if screenshot is None:
        print("Taking screenshot...")
        screenshot = take_screenshot()

    text = extract_text_from_image(screenshot)

    prompt = f"""You are a UI/UX expert analyzing a screenshot of a user interface.

Text extracted from the UI:
{text[:2000] if text else "No text extracted"}

Analyze this UI and provide insights.

Return ONLY a JSON object:
{{
    "ui_type": "<web app, desktop app, mobile app, or other>",
    "elements_detected": ["<element1>", "<element2>"],
    "usability_score": <0-100>,
    "issues": [
        {{
            "type": "<usability, accessibility, design>",
            "description": "<what is wrong>",
            "fix": "<how to improve>"
        }}
    ],
    "strengths": ["<strength1>", "<strength2>"],
    "overall_assessment": "<one sentence summary>"
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
        return {}

def plan_from_mockup(image_path: str) -> dict:
    print(f"Planning implementation from mockup: {image_path}")

    try:
        image = Image.open(image_path)
        text = extract_text_from_image(image)
    except Exception as e:
        print(f"Could not open image: {e}")
        text = ""

    prompt = f"""You are an expert developer. I have a UI mockup or wireframe.

Text extracted from the mockup:
{text[:2000] if text else "No text could be extracted"}

Based on what you can interpret, create an implementation plan.

Return ONLY a JSON object:
{{
    "mockup_type": "<website, mobile app, desktop app, or other>",
    "components_needed": ["<component1>", "<component2>"],
    "tech_stack": {{
        "frontend": "<recommended frontend>",
        "backend": "<recommended backend>",
        "database": "<recommended database>"
    }},
    "implementation_steps": [
        {{
            "step": 1,
            "task": "<what to build>",
            "estimated_hours": <number>
        }}
    ],
    "total_estimated_hours": <number>,
    "complexity": "<low, medium, or high>"
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
        return {}

def visual_bug_detection():
    print("=" * 40)
    print("  Visual Bug Detection")
    print("  Taking screenshot of your screen...")
    print("=" * 40)
    print()
    print("Make sure your code editor is visible on screen.")
    print("Analyzing in 3 seconds...")

    import time
    time.sleep(3)

    screenshot = take_screenshot()
    result = analyze_screenshot_for_bugs(screenshot)

    print("\n" + "=" * 40)
    print("  VISUAL ANALYSIS RESULT")
    print("=" * 40)

    if result.get("code_detected"):
        print(f"\nLanguage detected: {result.get('language', 'unknown').upper()}")
        print(f"Quality score: {result.get('quality_score', 0)}/100")
        print(f"Code purpose: {result.get('code_purpose', 'unknown')}")
        print(f"Bugs found: {result.get('total_bugs', 0)}")

        bugs = result.get("bugs", [])
        if bugs:
            print("\nBugs detected from screen:")
            for bug in bugs:
                print(f"  [{bug['severity'].upper()}] {bug['type']}")
                print(f"  {bug['description']}")
    else:
        print("No code detected in screenshot.")
        print(result.get("analysis", ""))

    return result

if __name__ == "__main__":
    print("=" * 40)
    print("  Multi-Model AI Processing")
    print("=" * 40)
    print()
    print("1. Visual bug detection from screen")
    print("2. Analyze UI screenshot")
    print("3. Analyze diagram/flowchart")
    print("4. Plan from mockup image")
    print()
    choice = input("Choose (1-4): ").strip()

    if choice == "1":
        visual_bug_detection()

    elif choice == "2":
        print("Taking screenshot in 3 seconds...")
        import time
        time.sleep(3)
        screenshot = take_screenshot()
        result = analyze_ui_screenshot(screenshot)
        print(f"\nUI Type: {result.get('ui_type', 'unknown')}")
        print(f"Usability Score: {result.get('usability_score', 0)}/100")
        print(f"Assessment: {result.get('overall_assessment', 'N/A')}")
        if result.get("issues"):
            print("\nUI Issues:")
            for issue in result["issues"]:
                print(f"  [{issue['type'].upper()}] {issue['description']}")
                print(f"  Fix: {issue['fix']}")

    elif choice == "3":
        path = input("Image path: ").strip()
        result = analyze_diagram(path)
        print(f"\nDiagram type: {result.get('diagram_type', 'unknown')}")
        print(f"Purpose: {result.get('purpose', 'N/A')}")
        if result.get("insights"):
            print("\nInsights:")
            for insight in result["insights"]:
                print(f"  - {insight}")

    elif choice == "4":
        path = input("Mockup image path: ").strip()
        result = plan_from_mockup(path)
        print(f"\nMockup type: {result.get('mockup_type', 'unknown')}")
        print(f"Complexity: {result.get('complexity', 'unknown')}")
        print(f"Estimated hours: {result.get('total_estimated_hours', 0)}")
        if result.get("implementation_steps"):
            print("\nImplementation plan:")
            for step in result["implementation_steps"]:
                print(f"  {step['step']}. {step['task']} ({step['estimated_hours']}h)")
