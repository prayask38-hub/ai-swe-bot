import os
import json
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from groq import Groq
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

OUTPUT_FOLDER = "creative_output"
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

def ai_design_plan(description: str, design_type: str):
    prompt = f"""You are a creative director and graphic designer.

Design request: {description}
Design type: {design_type}

Create a detailed design plan.

Return ONLY a JSON object:
{{
    "title": "<design title>",
    "style": "<minimalist, bold, elegant, playful, corporate, or modern>",
    "color_palette": {{
        "primary": "<hex color>",
        "secondary": "<hex color>",
        "accent": "<hex color>",
        "background": "<hex color>",
        "text": "<hex color>"
    }},
    "typography": {{
        "heading_size": <number 24-72>,
        "body_size": <number 12-24>,
        "style": "<bold, italic, or regular>"
    }},
    "layout": "<description of layout>",
    "elements": ["<element1>", "<element2>", "<element3>"],
    "tagline": "<short catchy tagline if applicable>"
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
        return {
            "title": description,
            "style": "modern",
            "color_palette": {
                "primary": "#6366f1",
                "secondary": "#8b5cf6",
                "accent": "#00ff88",
                "background": "#0d0d0d",
                "text": "#ffffff"
            },
            "typography": {"heading_size": 48, "body_size": 18, "style": "bold"},
            "layout": "centered",
            "elements": ["title", "subtitle", "cta button"],
            "tagline": description
        }

def hex_to_rgb(hex_color: str):
    hex_color = hex_color.lstrip('#')
    if len(hex_color) == 3:
        hex_color = ''.join([c*2 for c in hex_color])
    try:
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    except:
        return (100, 100, 100)

def generate_logo(company_name: str, tagline: str = "", style: str = "modern"):
    print(f"Generating logo for: {company_name}")

    plan = ai_design_plan(f"Logo for {company_name} — {tagline}", "logo")

    width, height = 800, 400
    bg_color = hex_to_rgb(plan["color_palette"]["background"])
    primary_color = hex_to_rgb(plan["color_palette"]["primary"])
    accent_color = hex_to_rgb(plan["color_palette"]["accent"])
    text_color = hex_to_rgb(plan["color_palette"]["text"])

    img = Image.new("RGB", (width, height), bg_color)
    draw = ImageDraw.Draw(img)

    draw.rectangle([0, 0, width, height], fill=bg_color)

    symbol_x, symbol_y = 80, height // 2
    symbol_size = 60
    draw.ellipse(
        [symbol_x - symbol_size, symbol_y - symbol_size,
         symbol_x + symbol_size, symbol_y + symbol_size],
        fill=primary_color, outline=accent_color, width=3
    )

    inner_size = symbol_size - 15
    draw.polygon([
        (symbol_x, symbol_y - inner_size),
        (symbol_x + inner_size, symbol_y + inner_size // 2),
        (symbol_x - inner_size, symbol_y + inner_size // 2)
    ], fill=accent_color)

    try:
        font_large = ImageFont.truetype("arial.ttf", plan["typography"]["heading_size"])
        font_small = ImageFont.truetype("arial.ttf", plan["typography"]["body_size"])
    except:
        font_large = ImageFont.load_default()
        font_small = ImageFont.load_default()

    text_x = symbol_x + symbol_size + 30
    draw.text((text_x, height // 2 - 40), company_name, fill=text_color, font=font_large)

    if tagline:
        draw.text((text_x, height // 2 + 30), tagline, fill=hex_to_rgb(plan["color_palette"]["accent"]), font=font_small)

    draw.line([(0, height - 4), (width, height - 4)], fill=accent_color, width=4)

    filename = os.path.join(OUTPUT_FOLDER, f"logo_{company_name.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png")
    img.save(filename)
    print(f"Logo saved: {filename}")
    return filename

def generate_banner(title: str, subtitle: str = "", cta: str = "Get Started"):
    print(f"Generating banner: {title}")

    plan = ai_design_plan(f"Banner for {title}", "banner")

    width, height = 1200, 400
    bg_color = hex_to_rgb(plan["color_palette"]["background"])
    primary_color = hex_to_rgb(plan["color_palette"]["primary"])
    accent_color = hex_to_rgb(plan["color_palette"]["accent"])
    text_color = hex_to_rgb(plan["color_palette"]["text"])

    img = Image.new("RGB", (width, height), bg_color)
    draw = ImageDraw.Draw(img)

    for i in range(0, width, 40):
        alpha = int(30 * (i / width))
        draw.rectangle([i, 0, i + 20, height],
                       fill=(primary_color[0], primary_color[1], primary_color[2]))

    draw.rectangle([0, 0, width, height], fill=bg_color)
    draw.rectangle([0, 0, 6, height], fill=accent_color)
    draw.rectangle([0, 0, width, 6], fill=primary_color)
    draw.rectangle([0, height-6, width, height], fill=primary_color)

    try:
        font_title = ImageFont.truetype("arial.ttf", 64)
        font_sub = ImageFont.truetype("arial.ttf", 28)
        font_cta = ImageFont.truetype("arial.ttf", 24)
    except:
        font_title = ImageFont.load_default()
        font_sub = ImageFont.load_default()
        font_cta = ImageFont.load_default()

    draw.text((80, 100), title, fill=text_color, font=font_title)

    if subtitle:
        draw.text((80, 195), subtitle, fill=hex_to_rgb(plan["color_palette"]["accent"]), font=font_sub)

    btn_x, btn_y = 80, 280
    btn_w, btn_h = 200, 55
    draw.rounded_rectangle([btn_x, btn_y, btn_x + btn_w, btn_y + btn_h],
                           radius=8, fill=accent_color)
    draw.text((btn_x + 20, btn_y + 14), cta, fill=bg_color, font=font_cta)

    for i in range(5):
        cx = width - 150 + (i % 3) * 50
        cy = 80 + (i // 3) * 50
        r = 20 + i * 8
        draw.ellipse([cx-r, cy-r, cx+r, cy+r],
                    outline=primary_color, width=2)

    filename = os.path.join(OUTPUT_FOLDER, f"banner_{title.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png")
    img.save(filename)
    print(f"Banner saved: {filename}")
    return filename

def generate_ui_mockup(app_name: str, screen_type: str = "dashboard"):
    print(f"Generating UI mockup: {app_name} — {screen_type}")

    plan = ai_design_plan(f"{screen_type} screen for {app_name}", "ui mockup")

    width, height = 1280, 800
    bg_color = hex_to_rgb(plan["color_palette"]["background"])
    primary_color = hex_to_rgb(plan["color_palette"]["primary"])
    accent_color = hex_to_rgb(plan["color_palette"]["accent"])
    text_color = hex_to_rgb(plan["color_palette"]["text"])
    secondary_color = hex_to_rgb(plan["color_palette"]["secondary"])

    img = Image.new("RGB", (width, height), bg_color)
    draw = ImageDraw.Draw(img)

    sidebar_w = 220
    draw.rectangle([0, 0, sidebar_w, height],
                   fill=(max(0, bg_color[0]-15), max(0, bg_color[1]-15), max(0, bg_color[2]-15)))
    draw.rectangle([sidebar_w, 0, sidebar_w+1, height], fill=primary_color)

    draw.rectangle([0, 0, sidebar_w, 60], fill=primary_color)

    try:
        font_nav = ImageFont.truetype("arial.ttf", 14)
        font_title = ImageFont.truetype("arial.ttf", 22)
        font_metric = ImageFont.truetype("arial.ttf", 32)
        font_small = ImageFont.truetype("arial.ttf", 12)
    except:
        font_nav = ImageFont.load_default()
        font_title = ImageFont.load_default()
        font_metric = ImageFont.load_default()
        font_small = ImageFont.load_default()

    draw.text((20, 18), app_name, fill=text_color, font=font_title)

    nav_items = ["Dashboard", "Analytics", "Projects", "Settings", "Help"]
    for i, item in enumerate(nav_items):
        y = 80 + i * 50
        if i == 0:
            draw.rectangle([0, y-5, sidebar_w, y+35], fill=primary_color)
        draw.rectangle([15, y+5, 25, y+25], fill=accent_color)
        draw.text((35, y+5), item, fill=text_color, font=font_nav)

    header_y = 0
    draw.rectangle([sidebar_w, header_y, width, 60], fill=(max(0, bg_color[0]-8), max(0, bg_color[1]-8), max(0, bg_color[2]-8)))
    draw.text((sidebar_w + 20, 18), f"{screen_type.title()} Overview", fill=text_color, font=font_title)
    draw.rectangle([width-120, 12, width-20, 42], fill=accent_color, outline=accent_color)
    draw.text((width-110, 18), "+ New Item", fill=bg_color, font=font_small)

    metrics = [("Total Users", "2,847", accent_color),
               ("Revenue", "$48.2K", primary_color),
               ("Growth", "+23%", (0, 200, 100)),
               ("Tasks Done", "142", secondary_color)]

    card_w = (width - sidebar_w - 80) // 4
    for i, (label, value, color) in enumerate(metrics):
        x = sidebar_w + 20 + i * (card_w + 15)
        y = 80
        draw.rounded_rectangle([x, y, x+card_w, y+100],
                               radius=8,
                               fill=(max(0, bg_color[0]+10), max(0, bg_color[1]+10), max(0, bg_color[2]+10)))
        draw.rectangle([x, y, x+4, y+100], fill=color)
        draw.text((x+15, y+15), label, fill=(150, 150, 150), font=font_small)
        draw.text((x+15, y+45), value, fill=text_color, font=font_metric)

    chart_x = sidebar_w + 20
    chart_y = 200
    chart_w = int((width - sidebar_w - 60) * 0.65)
    chart_h = 250

    draw.rounded_rectangle([chart_x, chart_y, chart_x+chart_w, chart_y+chart_h],
                           radius=8,
                           fill=(max(0, bg_color[0]+10), max(0, bg_color[1]+10), max(0, bg_color[2]+10)))
    draw.text((chart_x+15, chart_y+15), "Performance Chart", fill=text_color, font=font_nav)

    import random
    random.seed(42)
    bar_data = [random.randint(40, 180) for _ in range(12)]
    bar_w = (chart_w - 60) // 12
    for i, val in enumerate(bar_data):
        bx = chart_x + 30 + i * bar_w
        by = chart_y + chart_h - 40
        draw.rectangle([bx, by - val, bx + bar_w - 4, by], fill=primary_color)

    table_x = chart_x + chart_w + 20
    table_y = 200
    table_w = width - table_x - 20
    table_h = 250

    draw.rounded_rectangle([table_x, table_y, table_x+table_w, table_y+table_h],
                           radius=8,
                           fill=(max(0, bg_color[0]+10), max(0, bg_color[1]+10), max(0, bg_color[2]+10)))
    draw.text((table_x+15, table_y+15), "Recent Activity", fill=text_color, font=font_nav)

    activities = ["Bug fixed in app.py", "New user registered", "Deploy completed", "PR merged", "Test passed"]
    for i, activity in enumerate(activities):
        ay = table_y + 50 + i * 36
        draw.rectangle([table_x+15, ay+8, table_x+25, ay+18], fill=accent_color)
        draw.text((table_x+35, ay+5), activity, fill=(180, 180, 180), font=font_small)

    bottom_y = 480
    panel_w = (width - sidebar_w - 60) // 3

    for i in range(3):
        px = sidebar_w + 20 + i * (panel_w + 15)
        draw.rounded_rectangle([px, bottom_y, px+panel_w, bottom_y+200],
                               radius=8,
                               fill=(max(0, bg_color[0]+10), max(0, bg_color[1]+10), max(0, bg_color[2]+10)))
        labels = ["Code Quality", "Security Score", "Performance"]
        scores = ["87/100", "94/100", "91/100"]
        score_colors = [accent_color, (0, 200, 100), primary_color]
        draw.text((px+15, bottom_y+15), labels[i], fill=text_color, font=font_nav)
        draw.text((px+15, bottom_y+60), scores[i], fill=score_colors[i], font=font_metric)
        bar_fill = int(panel_w * 0.8 * (int(scores[i].split('/')[0]) / 100))
        draw.rounded_rectangle([px+15, bottom_y+120, px+panel_w-15, bottom_y+135],
                               radius=4, fill=(50, 50, 50))
        draw.rounded_rectangle([px+15, bottom_y+120, px+15+bar_fill, bottom_y+135],
                               radius=4, fill=score_colors[i])

    filename = os.path.join(OUTPUT_FOLDER, f"mockup_{app_name.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png")
    img.save(filename)
    print(f"UI mockup saved: {filename}")
    return filename

def generate_pdf_report(title: str, content: dict):
    print(f"Generating PDF report: {title}")

    filename = os.path.join(OUTPUT_FOLDER, f"report_{title.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf")

    c = canvas.Canvas(filename, pagesize=A4)
    width, height = A4

    c.setFillColor(colors.HexColor('#6366f1'))
    c.rect(0, height-80, width, 80, fill=1, stroke=0)
    c.setFillColor(colors.white)
    c.setFont("Helvetica-Bold", 24)
    c.drawString(40, height-55, title)
    c.setFont("Helvetica", 12)
    c.drawString(40, height-75, f"Generated by AI SWE Bot — {datetime.now().strftime('%Y-%m-%d %H:%M')}")

    y = height - 120
    c.setFillColor(colors.black)

    for section, text in content.items():
        c.setFillColor(colors.HexColor('#6366f1'))
        c.setFont("Helvetica-Bold", 14)
        c.drawString(40, y, section)
        y -= 25

        c.setFillColor(colors.black)
        c.setFont("Helvetica", 11)

        if isinstance(text, list):
            for item in text:
                if y < 60:
                    c.showPage()
                    y = height - 60
                c.drawString(55, y, f"• {str(item)[:80]}")
                y -= 18
        else:
            words = str(text).split()
            line = ""
            for word in words:
                if len(line + " " + word) < 85:
                    line += " " + word
                else:
                    if y < 60:
                        c.showPage()
                        y = height - 60
                    c.drawString(40, y, line.strip())
                    y -= 18
                    line = word
            if line:
                c.drawString(40, y, line.strip())
                y -= 18

        y -= 15

        if y < 80:
            c.showPage()
            y = height - 60

    c.setFillColor(colors.HexColor('#6366f1'))
    c.rect(0, 0, width, 30, fill=1, stroke=0)
    c.setFillColor(colors.white)
    c.setFont("Helvetica", 9)
    c.drawString(40, 10, "AI SWE Bot — Automated Report")
    c.drawRightString(width-40, 10, f"Page 1")

    c.save()
    print(f"PDF report saved: {filename}")
    return filename

def generate_3d_model_plan(object_description: str):
    print(f"Planning 3D model: {object_description}")

    prompt = f"""You are a 3D modeling expert. Create a detailed plan for modeling this object.

Object: {object_description}

Return ONLY a JSON object:
{{
    "object_name": "<name>",
    "modeling_approach": "<polygon, nurbs, or sculpting>",
    "complexity": "<low, medium, or high>",
    "estimated_polygons": <number>,
    "components": [
        {{
            "name": "<component name>",
            "shape": "<basic shape: cube, sphere, cylinder, cone>",
            "dimensions": "<approximate dimensions>",
            "material": "<material type>"
        }}
    ],
    "textures_needed": ["<texture1>", "<texture2>"],
    "animation_potential": "<static, rigged, or animated>",
    "tools_recommended": ["<tool1>", "<tool2>"],
    "modeling_steps": ["<step1>", "<step2>", "<step3>", "<step4>", "<step5>"]
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

if __name__ == "__main__":
    print("=" * 40)
    print("  Creative Suite")
    print("=" * 40)
    print()
    print("1. Generate logo")
    print("2. Generate banner")
    print("3. Generate UI mockup")
    print("4. Generate PDF report")
    print("5. Plan 3D model")
    print()
    choice = input("Choose (1-5): ").strip()

    if choice == "1":
        name = input("Company name: ").strip()
        tagline = input("Tagline (optional): ").strip()
        filename = generate_logo(name, tagline)
        print(f"\nLogo created: {filename}")

    elif choice == "2":
        title = input("Banner title: ").strip()
        subtitle = input("Subtitle (optional): ").strip()
        cta = input("CTA button text (default: Get Started): ").strip() or "Get Started"
        filename = generate_banner(title, subtitle, cta)
        print(f"\nBanner created: {filename}")

    elif choice == "3":
        app_name = input("App name: ").strip()
        screen = input("Screen type (dashboard/login/profile): ").strip() or "dashboard"
        filename = generate_ui_mockup(app_name, screen)
        print(f"\nUI mockup created: {filename}")

    elif choice == "4":
        title = input("Report title: ").strip()
        filename = generate_pdf_report(title, {
            "Executive Summary": "This report was automatically generated by AI SWE Bot.",
            "Key Findings": ["Bug detection accuracy: 95%", "Auto-fix success rate: 87%", "Average fix time: 2.3 seconds"],
            "Recommendations": ["Deploy to production", "Add more test coverage", "Monitor performance metrics"],
            "Conclusion": "The AI SWE Bot has demonstrated exceptional performance across all metrics."
        })
        print(f"\nPDF created: {filename}")

    elif choice == "5":
        description = input("Describe the 3D object: ").strip()
        plan = generate_3d_model_plan(description)
        print(f"\nObject: {plan.get('object_name', 'unknown')}")
        print(f"Approach: {plan.get('modeling_approach', 'unknown')}")
        print(f"Complexity: {plan.get('complexity', 'unknown')}")
        print(f"Estimated polygons: {plan.get('estimated_polygons', 0)}")
        if plan.get('modeling_steps'):
            print("\nModeling steps:")
            for i, step in enumerate(plan['modeling_steps']):
                print(f"  {i+1}. {step}")
