import asyncio
import os
import json
from playwright.async_api import async_playwright
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

async def search_web(query: str):
    print(f"Searching for: {query}")
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        await page.goto("https://www.google.com")
        await page.fill('textarea[name="q"]', query)
        await page.press('textarea[name="q"]', "Enter")
        await page.wait_for_load_state("networkidle")
        results = await page.query_selector_all("h3")
        search_results = []
        for result in results[:5]:
            text = await result.inner_text()
            if text:
                search_results.append(text)
        print(f"Found {len(search_results)} results:")
        for i, r in enumerate(search_results):
            print(f"  {i+1}. {r}")
        await browser.close()
        return search_results

async def fill_form(url: str, form_data: dict):
    print(f"Filling form at: {url}")
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        await page.goto(url)
        await page.wait_for_load_state("networkidle")
        for field, value in form_data.items():
            try:
                await page.fill(f'input[name="{field}"]', value)
                print(f"  Filled {field}: {value}")
            except:
                try:
                    await page.fill(f'input[placeholder*="{field}"]', value)
                    print(f"  Filled {field} by placeholder")
                except:
                    print(f"  Could not fill {field}")
        await asyncio.sleep(2)
        await browser.close()

async def test_website(url: str):
    print(f"Testing website: {url}")
    results = []
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        errors = []
        page.on("pageerror", lambda e: errors.append(str(e)))

        try:
            response = await page.goto(url, timeout=10000)
            status = response.status
            print(f"  Status: {status}")
            results.append({"check": "page_loads", "passed": status == 200, "status": status})
        except Exception as e:
            print(f"  Failed to load: {e}")
            results.append({"check": "page_loads", "passed": False, "error": str(e)})
            await browser.close()
            return results

        title = await page.title()
        print(f"  Title: {title}")
        results.append({"check": "has_title", "passed": len(title) > 0, "title": title})

        links = await page.query_selector_all("a")
        print(f"  Links found: {len(links)}")
        results.append({"check": "has_links", "passed": len(links) > 0, "count": len(links)})

        images = await page.query_selector_all("img")
        broken_images = 0
        for img in images[:10]:
            src = await img.get_attribute("src")
            if not src:
                broken_images += 1
        print(f"  Images: {len(images)} total, {broken_images} broken")
        results.append({"check": "images", "total": len(images), "broken": broken_images})

        if errors:
            print(f"  JS errors: {len(errors)}")
            results.append({"check": "no_js_errors", "passed": False, "errors": errors})
        else:
            print(f"  No JS errors")
            results.append({"check": "no_js_errors", "passed": True})

        await asyncio.sleep(2)
        await browser.close()
        return results

async def scrape_data(url: str, data_type: str = "text"):
    print(f"Scraping {data_type} from: {url}")
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        await page.goto(url)
        await page.wait_for_load_state("networkidle")

        if data_type == "text":
            content = await page.inner_text("body")
            words = content.split()[:200]
            result = " ".join(words)
            print(f"  Scraped {len(words)} words")

        elif data_type == "links":
            links = await page.query_selector_all("a")
            result = []
            for link in links[:20]:
                href = await link.get_attribute("href")
                text = await link.inner_text()
                if href and text:
                    result.append({"text": text.strip(), "url": href})
            print(f"  Found {len(result)} links")

        elif data_type == "images":
            images = await page.query_selector_all("img")
            result = []
            for img in images[:20]:
                src = await img.get_attribute("src")
                alt = await img.get_attribute("alt")
                if src:
                    result.append({"src": src, "alt": alt or ""})
            print(f"  Found {len(result)} images")

        elif data_type == "headings":
            headings = await page.query_selector_all("h1, h2, h3")
            result = []
            for h in headings:
                text = await h.inner_text()
                tag = await h.evaluate("el => el.tagName")
                if text:
                    result.append({"tag": tag, "text": text.strip()})
            print(f"  Found {len(result)} headings")

        else:
            result = await page.content()

        await browser.close()
        return result

async def automate_task(task: str):
    prompt = f"""You are a browser automation expert. Plan how to complete this task using a browser.

Task: {task}

Return ONLY a JSON array of steps:
[
    {{"action": "goto", "url": "<url to visit>"}},
    {{"action": "click", "selector": "<css selector>"}},
    {{"action": "fill", "selector": "<css selector>", "value": "<text to type>"}},
    {{"action": "press", "key": "Enter"}},
    {{"action": "wait", "seconds": 2}},
    {{"action": "screenshot", "filename": "<name.png>"}},
    {{"action": "done", "message": "<completion message>"}}
]

Return ONLY the JSON array. No extra text."""

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
        steps = json.loads(raw)
    except:
        print("Could not plan task.")
        return

    print(f"\nPlan: {len(steps)} steps")
    for i, step in enumerate(steps):
        print(f"  {i+1}. {step['action']}")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()

        for i, step in enumerate(steps):
            action = step.get("action")
            print(f"\nStep {i+1}: {action}")

            try:
                if action == "goto":
                    await page.goto(step["url"])
                    await page.wait_for_load_state("networkidle")
                    print(f"  Navigated to {step['url']}")

                elif action == "click":
                    await page.click(step["selector"])
                    print(f"  Clicked {step['selector']}")

                elif action == "fill":
                    await page.fill(step["selector"], step["value"])
                    print(f"  Filled {step['selector']} with {step['value']}")

                elif action == "press":
                    await page.keyboard.press(step["key"])
                    print(f"  Pressed {step['key']}")

                elif action == "wait":
                    await asyncio.sleep(step.get("seconds", 1))
                    print(f"  Waited {step.get('seconds', 1)} seconds")

                elif action == "screenshot":
                    filename = step.get("filename", "screenshot.png")
                    await page.screenshot(path=filename)
                    print(f"  Screenshot saved: {filename}")

                elif action == "done":
                    print(f"  Task complete: {step.get('message', 'Done')}")
                    break

            except Exception as e:
                print(f"  Error: {e}")

        await asyncio.sleep(2)
        await browser.close()

if __name__ == "__main__":
    print("=" * 40)
    print("  Browser Automation Test")
    print("=" * 40)
    print()
    print("1. Search Google")
    print("2. Test a website")
    print("3. Scrape data")
    print("4. Automate custom task")
    print()
    choice = input("Choose (1-4): ").strip()

    if choice == "1":
        query = input("Search for: ")
        asyncio.run(search_web(query))

    elif choice == "2":
        url = input("Website URL: ")
        results = asyncio.run(test_website(url))
        print("\nTest Results:")
        for r in results:
            status = "PASS" if r.get("passed") else "FAIL"
            print(f"  [{status}] {r['check']}")

    elif choice == "3":
        url = input("URL to scrape: ")
        print("Data type: text, links, images, headings")
        data_type = input("Type: ").strip() or "headings"
        result = asyncio.run(scrape_data(url, data_type))
        print(f"\nResult: {json.dumps(result, indent=2)[:500]}")

    elif choice == "4":
        task = input("What do you want to automate? ")
        asyncio.run(automate_task(task))
