import os
import json
from groq import Groq
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def generate_website(description: str, style: str = "modern"):
    print(f"Generating website: {description}")
    print("Planning structure...")

    plan_prompt = f"""You are an expert web developer. Plan a website based on this description.

Description: {description}
Style: {style}

Return ONLY a JSON object:
{{
    "title": "<website title>",
    "pages": ["<page1>", "<page2>"],
    "sections": ["<section1>", "<section2>", "<section3>"],
    "color_scheme": {{
        "primary": "<hex color>",
        "secondary": "<hex color>",
        "background": "<hex color>",
        "text": "<hex color>"
    }},
    "features": ["<feature1>", "<feature2>"]
}}

Return ONLY the JSON. No extra text."""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": plan_prompt}]
    )

    raw = response.choices[0].message.content.strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    raw = raw.strip()

    try:
        plan = json.loads(raw)
        print(f"Plan ready: {plan['title']}")
        print(f"Sections: {plan['sections']}")
    except:
        plan = {
            "title": description,
            "sections": ["Hero", "About", "Features", "Contact"],
            "color_scheme": {
                "primary": "#6366f1",
                "secondary": "#8b5cf6",
                "background": "#0f172a",
                "text": "#f1f5f9"
            },
            "features": ["Responsive", "Modern design"]
        }

    print("\nGenerating HTML...")
    html_prompt = f"""You are an expert web developer. Create a complete, beautiful, modern single-page website.

Description: {description}
Title: {plan['title']}
Sections: {plan['sections']}
Colors: primary={plan['color_scheme']['primary']}, secondary={plan['color_scheme']['secondary']}, background={plan['color_scheme']['background']}, text={plan['color_scheme']['text']}

Requirements:
- Complete HTML file with embedded CSS and JavaScript
- Modern, professional design
- Fully responsive for mobile and desktop
- Smooth scrolling navigation
- Animated hero section
- Clean card layouts
- Google Fonts
- Font Awesome icons via CDN
- Hover effects and transitions
- Contact form with basic validation
- Footer with social links

Return ONLY the complete HTML code. No extra text. Start with <!DOCTYPE html>"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        max_tokens=4000,
        messages=[{"role": "user", "content": html_prompt}]
    )

    html = response.choices[0].message.content.strip()
    if html.startswith("```"):
        html = html.split("```")[1]
        if html.startswith("html"):
            html = html[4:]
    html = html.strip()

    return html, plan

def generate_landing_page(product_name: str, tagline: str, features: list):
    print(f"Generating landing page for: {product_name}")

    prompt = f"""You are an expert web developer. Create a stunning SaaS landing page.

Product: {product_name}
Tagline: {tagline}
Features: {', '.join(features)}

Create a complete HTML landing page with:
- Dark theme with purple/blue gradient accents
- Hero section with product name, tagline and CTA button
- Features section with icons and descriptions
- How it works section with numbered steps
- Pricing section with 3 tiers: Free, Pro $49/mo, Team $199/mo
- Testimonials section
- FAQ section
- CTA section
- Footer
- Smooth animations
- Google Fonts — use Inter
- Font Awesome icons
- Mobile responsive

Return ONLY complete HTML. No extra text. Start with <!DOCTYPE html>"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        max_tokens=4000,
        messages=[{"role": "user", "content": prompt}]
    )

    html = response.choices[0].message.content.strip()
    if html.startswith("```"):
        html = html.split("```")[1]
        if html.startswith("html"):
            html = html[4:]
    html = html.strip()

    return html

def save_website(html: str, filename: str = None):
    if not filename:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"website_{timestamp}.html"

    folder = "generated_websites"
    os.makedirs(folder, exist_ok=True)
    filepath = os.path.join(folder, filename)

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(html)

    print(f"\nWebsite saved to: {filepath}")
    return filepath

def open_website(filepath: str):
    import subprocess
    subprocess.Popen(["cmd", "/c", "start", filepath])
    print(f"Opening website in browser...")

if __name__ == "__main__":
    print("=" * 40)
    print("  Website Generator Test")
    print("=" * 40)
    print()
    print("1. Generate custom website")
    print("2. Generate AI SWE Bot landing page")
    print()
    choice = input("Choose (1 or 2): ").strip()

    if choice == "1":
        description = input("Describe your website: ")
        style = input("Style (modern/minimal/bold): ").strip() or "modern"
        html, plan = generate_website(description, style)
        filepath = save_website(html)
        open_website(filepath)

    elif choice == "2":
        print("\nGenerating AI SWE Bot landing page...")
        html = generate_landing_page(
            product_name="AI SWE Bot",
            tagline="Your AI Software Engineer — fixes bugs, writes code, works autonomously",
            features=[
                "Detects any bug in seconds",
                "Generates 3 solutions per bug",
                "Auto-fixes and tests code",
                "Works in 6 programming languages",
                "Computer use — controls your PC",
                "Voice commands — hands free",
                "Learns from every fix",
                "100% local and private"
            ]
        )
        filepath = save_website(html, "ai_swe_bot_landing.html")
        open_website(filepath)
        print("\nYour landing page is ready — this is what you show to VCs and beta users!")
