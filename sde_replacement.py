import os
import json
import subprocess
from datetime import datetime
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def read_ticket(ticket: dict):
    prompt = f"""You are a senior software engineer reading a development ticket.

Ticket:
Title: {ticket.get('title', '')}
Description: {ticket.get('description', '')}
Acceptance criteria: {ticket.get('acceptance_criteria', '')}
Priority: {ticket.get('priority', 'medium')}
Labels: {ticket.get('labels', [])}

Analyze this ticket and create an implementation plan.

Return ONLY a JSON object:
{{
    "ticket_id": "{ticket.get('id', 'TICKET-001')}",
    "understanding": "<what needs to be built>",
    "complexity": "<low, medium, or high>",
    "estimated_hours": <number>,
    "implementation_plan": [
        {{
            "step": 1,
            "task": "<what to do>",
            "files_to_create": ["<file1.py>"],
            "files_to_modify": ["<file2.py>"]
        }}
    ],
    "technical_approach": "<how to implement this>",
    "potential_risks": ["<risk1>", "<risk2>"],
    "test_cases": ["<test1>", "<test2>", "<test3>"]
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

def write_code(task: str, language: str = "python", context: str = ""):
    prompt = f"""You are a senior software engineer. Write production-ready code for this task.

Task: {task}
Language: {language}
Context: {context}

Requirements:
- Clean, well-commented code
- Error handling included
- Follow best practices
- Include docstrings
- Write testable code

Return ONLY a JSON object:
{{
    "filename": "<appropriate_filename.py>",
    "code": "<complete production-ready code>",
    "explanation": "<what this code does>",
    "dependencies": ["<dep1>", "<dep2>"],
    "usage_example": "<how to use this code>"
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

def write_tests(code: str, filename: str, language: str = "python"):
    prompt = f"""You are a senior QA engineer. Write comprehensive tests for this code.

Code file: {filename}
Code:
{code[:2000]}

Write tests that cover:
- Happy path scenarios
- Edge cases
- Error conditions
- Boundary values

Return ONLY a JSON object:
{{
    "test_filename": "test_{filename}",
    "test_code": "<complete test code using unittest>",
    "test_cases_count": <number>,
    "coverage_areas": ["<area1>", "<area2>"]
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

def run_tests(test_code: str, test_filename: str):
    print(f"Running tests: {test_filename}")

    with open(test_filename, 'w', encoding='utf-8') as f:
        f.write(test_code)

    try:
        result = subprocess.run(
            ["python", "-m", "pytest", test_filename, "-v", "--tb=short"],
            capture_output=True,
            text=True,
            timeout=30
        )
        passed = result.returncode == 0
        output = result.stdout + result.stderr
        print(f"Tests {'PASSED' if passed else 'FAILED'}")
        return {"passed": passed, "output": output[:500]}
    except Exception as e:
        try:
            result = subprocess.run(
                ["python", "-m", "unittest", test_filename.replace('.py', '')],
                capture_output=True,
                text=True,
                timeout=30
            )
            passed = result.returncode == 0
            return {"passed": passed, "output": result.stdout + result.stderr}
        except:
            return {"passed": False, "output": str(e)}
    finally:
        if os.path.exists(test_filename):
            os.remove(test_filename)

def review_code(code: str, filename: str):
    prompt = f"""You are a senior engineer doing a code review.

File: {filename}
Code:
{code[:2000]}

Review this code thoroughly.

Return ONLY a JSON object:
{{
    "approval_status": "<approved, changes_requested, or needs_major_revision>",
    "score": <0-100>,
    "comments": [
        {{
            "type": "<suggestion, issue, or praise>",
            "severity": "<critical, major, minor, or info>",
            "comment": "<review comment>",
            "suggestion": "<how to improve>"
        }}
    ],
    "summary": "<overall review summary>",
    "ready_to_merge": <true or false>
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

def respond_to_review(review_comments: list, code: str):
    prompt = f"""You are a developer responding to code review comments.

Original code:
{code[:1500]}

Review comments:
{json.dumps(review_comments, indent=2)[:1000]}

Address each comment and update the code accordingly.

Return ONLY a JSON object:
{{
    "responses": [
        {{
            "comment": "<original comment>",
            "response": "<your response>",
            "action_taken": "<what you changed>"
        }}
    ],
    "updated_code": "<complete updated code addressing all comments>",
    "summary": "<summary of changes made>"
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

def generate_pr_description(ticket: dict, code_result: dict, test_result: dict, review_result: dict):
    return f"""## Pull Request — {ticket.get('title', 'Feature Implementation')}

**Ticket:** {ticket.get('id', 'TICKET-001')}
**Priority:** {ticket.get('priority', 'medium').upper()}

## Changes Made
{code_result.get('explanation', 'Implementation complete')}

## Files Changed
- {code_result.get('filename', 'main.py')} — New implementation

## Test Results
- Tests: {'PASSED' if test_result.get('passed') else 'FAILED'}
- Test cases: {test_result.get('test_count', 0)}

## Code Review Score
- Score: {review_result.get('score', 0)}/100
- Status: {review_result.get('approval_status', 'pending')}

## Usage
```python
{code_result.get('usage_example', '# See code for usage')}
```

---
*This PR was automatically generated by AI SWE Bot*
*Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}*"""

def full_sde_workflow(ticket: dict):
    print("\n" + "=" * 50)
    print("  AI SDE-2 REPLACEMENT — FULL WORKFLOW")
    print("=" * 50)

    print(f"\nTicket: {ticket['title']}")
    print("=" * 50)

    print("\nStep 1: Reading and analyzing ticket...")
    plan = read_ticket(ticket)
    print(f"Complexity: {plan.get('complexity', 'unknown')}")
    print(f"Estimated hours: {plan.get('estimated_hours', 0)}")
    print(f"Technical approach: {plan.get('technical_approach', 'N/A')[:100]}")

    print("\nStep 2: Writing implementation code...")
    task = plan.get('understanding', ticket['description'])
    code_result = write_code(task, "python", ticket.get('description', ''))
    filename = code_result.get('filename', 'implementation.py')
    code = code_result.get('code', '')

    if code:
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(code)
        print(f"Code written to: {filename}")
        print(f"Explanation: {code_result.get('explanation', 'N/A')[:100]}")

    print("\nStep 3: Writing test cases...")
    test_result = write_tests(code, filename)
    test_code = test_result.get('test_code', '')
    print(f"Test cases written: {test_result.get('test_cases_count', 0)}")

    print("\nStep 4: Running tests...")
    if test_code:
        run_result = run_tests(test_code, f"test_{filename}")
        test_passed = run_result.get('passed', False)
        print(f"Test result: {'PASSED' if test_passed else 'FAILED'}")
    else:
        run_result = {"passed": False, "output": "No tests generated"}
        test_passed = False

    print("\nStep 5: Code review...")
    review = review_code(code, filename)
    print(f"Review score: {review.get('score', 0)}/100")
    print(f"Status: {review.get('approval_status', 'unknown')}")
    print(f"Ready to merge: {review.get('ready_to_merge', False)}")

    if review.get('comments'):
        needs_changes = [c for c in review['comments'] if c.get('severity') in ['critical', 'major']]
        if needs_changes:
            print(f"\nStep 6: Addressing {len(needs_changes)} critical review comments...")
            updated = respond_to_review(review['comments'], code)
            if updated.get('updated_code'):
                code = updated['updated_code']
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(code)
                print("Code updated based on review feedback.")
                print(f"Summary: {updated.get('summary', 'Changes made')[:100]}")

    print("\nStep 7: Generating PR description...")
    pr_description = generate_pr_description(ticket, code_result, run_result, review)
    pr_filename = f"PR_{ticket.get('id', 'TICKET001')}.md"
    with open(pr_filename, 'w', encoding='utf-8') as f:
        f.write(pr_description)
    print(f"PR description saved: {pr_filename}")

    print("\n" + "=" * 50)
    print("  WORKFLOW COMPLETE")
    print("=" * 50)
    print(f"\nFiles created:")
    print(f"  - {filename} (implementation)")
    print(f"  - {pr_filename} (PR description)")
    print(f"\nSummary:")
    print(f"  Ticket: {ticket['title']}")
    print(f"  Code: {len(code)} characters written")
    print(f"  Tests: {'PASSED' if test_passed else 'FAILED'}")
    print(f"  Review score: {review.get('score', 0)}/100")
    print(f"  Ready to merge: {review.get('ready_to_merge', False)}")

    return {
        "ticket": ticket,
        "plan": plan,
        "code_file": filename,
        "tests_passed": test_passed,
        "review_score": review.get('score', 0),
        "pr_file": pr_filename
    }

if __name__ == "__main__":
    print("=" * 40)
    print("  SDE-2 Replacement Test")
    print("=" * 40)
    print()

    sample_ticket = {
        "id": "TICKET-042",
        "title": "Build user authentication system",
        "description": "Create a secure user authentication system with login, logout, and session management. Users should be able to register with email and password. Passwords must be hashed. Sessions should expire after 24 hours.",
        "acceptance_criteria": "1. User can register with email and password. 2. Passwords are securely hashed. 3. User can login and receive a session token. 4. Session expires after 24 hours. 5. User can logout.",
        "priority": "high",
        "labels": ["authentication", "security", "backend"]
    }

    result = full_sde_workflow(sample_ticket)
    print(f"\nWorkflow completed successfully.")
    print(f"Check {result['code_file']} and {result['pr_file']} for outputs.")
