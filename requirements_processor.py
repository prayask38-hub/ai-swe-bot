import os
import json
from datetime import datetime
from groq import Groq
from dotenv import load_dotenv

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def process_requirements(raw_requirements: str):
    print("Processing requirements...")

    prompt = f"""You are a senior software engineer receiving vague product requirements.

Raw requirements:
{raw_requirements}

Analyze these requirements like a senior engineer would. Ask the questions that MUST be answered before writing a single line of code.

Return ONLY a JSON object:
{{
    "understood_goal": "<what you understand needs to be built>",
    "ambiguities": [
        {{
            "question": "<clarifying question>",
            "why_important": "<why this must be answered>",
            "default_assumption": "<what you will assume if not answered>"
        }}
    ],
    "assumptions_made": ["<assumption1>", "<assumption2>"],
    "out_of_scope": ["<what is NOT being built>"],
    "risks": ["<risk1>", "<risk2>"],
    "estimated_complexity": "<simple, medium, complex, or very complex>",
    "estimated_days": <number>
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

def generate_technical_spec(requirements: str, clarifications: dict = None):
    print("Generating technical specification...")

    context = ""
    if clarifications:
        context = f"\nClarifications provided:\n{json.dumps(clarifications, indent=2)}"

    prompt = f"""You are a senior software architect writing a technical design document.

Requirements:
{requirements}
{context}

Write a complete technical specification document.

Return ONLY a JSON object:
{{
    "title": "<feature title>",
    "version": "1.0",
    "date": "{datetime.now().strftime('%Y-%m-%d')}",
    "overview": "<2-3 sentence overview>",
    "technical_approach": "<how this will be built>",
    "architecture": {{
        "components": ["<component1>", "<component2>"],
        "data_flow": "<how data moves through the system>",
        "tech_stack": ["<technology1>", "<technology2>"]
    }},
    "api_endpoints": [
        {{
            "method": "<GET/POST/PUT/DELETE>",
            "path": "<endpoint path>",
            "description": "<what it does>",
            "request": "<request body>",
            "response": "<response body>"
        }}
    ],
    "database_schema": [
        {{
            "table": "<table name>",
            "columns": ["<col1 type>", "<col2 type>"],
            "indexes": ["<index1>"]
        }}
    ],
    "implementation_tasks": [
        {{
            "task_id": "T1",
            "title": "<task title>",
            "description": "<what to implement>",
            "estimated_hours": <number>,
            "dependencies": ["<T2>"],
            "assignee": "SDE-2"
        }}
    ],
    "testing_requirements": [
        {{
            "type": "<unit/integration/e2e>",
            "description": "<what to test>",
            "coverage_required": "<percentage>"
        }}
    ],
    "security_considerations": ["<consideration1>", "<consideration2>"],
    "performance_requirements": ["<requirement1>", "<requirement2>"],
    "total_estimated_days": <number>
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

def generate_tickets(spec: dict):
    print("Generating Jira-style tickets...")

    tasks = spec.get("implementation_tasks", [])
    if not tasks:
        return []

    tickets = []
    for task in tasks:
        ticket = {
            "id": f"TICKET-{task.get('task_id', '001')}",
            "title": task.get("title", ""),
            "type": "Story",
            "priority": "High",
            "description": task.get("description", ""),
            "acceptance_criteria": [
                f"Implementation complete for: {task.get('title','')}",
                "Unit tests written and passing",
                "Code reviewed and approved",
                "Documentation updated"
            ],
            "estimated_hours": task.get("estimated_hours", 0),
            "dependencies": task.get("dependencies", []),
            "labels": ["sde-2", "auto-generated"]
        }
        tickets.append(ticket)

    return tickets

def process_meeting_notes(notes: str):
    print("Processing meeting notes...")

    prompt = f"""You are a senior engineer who just attended a product meeting.

Meeting notes:
{notes}

Extract all actionable technical items from these notes.

Return ONLY a JSON object:
{{
    "meeting_summary": "<2 sentence summary>",
    "decisions_made": ["<decision1>", "<decision2>"],
    "action_items": [
        {{
            "what": "<what needs to be done>",
            "who": "<SDE-2, PM, Designer, etc>",
            "by_when": "<urgency: immediate, this week, this sprint>",
            "technical_details": "<any technical specifics mentioned>"
        }}
    ],
    "open_questions": ["<unresolved question1>", "<unresolved question2>"],
    "technical_risks_identified": ["<risk1>", "<risk2>"],
    "next_steps": ["<step1>", "<step2>", "<step3>"]
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

def save_spec_as_markdown(spec: dict, filename: str = None):
    if not filename:
        filename = f"spec_{spec.get('title','feature').replace(' ','_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"

    with open(filename, 'w', encoding='utf-8') as f:
        f.write(f"# Technical Specification: {spec.get('title','Feature')}\n\n")
        f.write(f"**Version:** {spec.get('version','1.0')}  \n")
        f.write(f"**Date:** {spec.get('date',datetime.now().strftime('%Y-%m-%d'))}  \n\n")
        f.write(f"---\n\n")
        f.write(f"## Overview\n{spec.get('overview','')}\n\n")
        f.write(f"## Technical Approach\n{spec.get('technical_approach','')}\n\n")

        arch = spec.get("architecture", {})
        if arch:
            f.write(f"## Architecture\n")
            f.write(f"**Tech Stack:** {', '.join(arch.get('tech_stack',[]))}\n\n")
            f.write(f"**Components:**\n")
            for c in arch.get("components", []):
                f.write(f"- {c}\n")
            f.write(f"\n**Data Flow:** {arch.get('data_flow','')}\n\n")

        endpoints = spec.get("api_endpoints", [])
        if endpoints:
            f.write(f"## API Endpoints\n")
            for ep in endpoints:
                f.write(f"### {ep.get('method','')} {ep.get('path','')}\n")
                f.write(f"{ep.get('description','')}\n\n")

        tasks = spec.get("implementation_tasks", [])
        if tasks:
            total = sum(t.get("estimated_hours", 0) for t in tasks)
            f.write(f"## Implementation Tasks ({total} hours total)\n\n")
            for task in tasks:
                f.write(f"### [{task.get('task_id','')}] {task.get('title','')}\n")
                f.write(f"**Hours:** {task.get('estimated_hours',0)}  \n")
                f.write(f"**Description:** {task.get('description','')}  \n\n")

        f.write(f"## Security Considerations\n")
        for s in spec.get("security_considerations", []):
            f.write(f"- {s}\n")
        f.write(f"\n## Total Estimate: {spec.get('total_estimated_days', 0)} days\n")

    print(f"Spec saved: {filename}")
    return filename

def print_spec(spec: dict):
    print("\n" + "=" * 50)
    print("  TECHNICAL SPECIFICATION")
    print("=" * 50)
    print(f"\nTitle:      {spec.get('title','')}")
    print(f"Complexity: {spec.get('total_estimated_days', 0)} days")
    print(f"\nOverview:")
    print(f"  {spec.get('overview','')}")
    print(f"\nTech stack: {', '.join(spec.get('architecture',{}).get('tech_stack',[]))}")

    tasks = spec.get("implementation_tasks", [])
    if tasks:
        total_hours = sum(t.get("estimated_hours", 0) for t in tasks)
        print(f"\nImplementation tasks: {len(tasks)} ({total_hours} hours)")
        for task in tasks:
            print(f"  [{task.get('task_id','')}] {task.get('title','')} — {task.get('estimated_hours',0)}h")

    security = spec.get("security_considerations", [])
    if security:
        print(f"\nSecurity considerations:")
        for s in security:
            print(f"  - {s}")

if __name__ == "__main__":
    print("=" * 40)
    print("  Requirements Processor")
    print("=" * 40)
    print()
    print("1. Process vague requirements")
    print("2. Process meeting notes")
    print("3. Generate full technical spec")
    print("4. Test with sample requirements")
    print()
    choice = input("Choose (1-4): ").strip()

    if choice == "1":
        print("\nPaste your requirements (Enter twice when done):")
        lines = []
        empty = 0
        while empty < 2:
            line = input()
            if line == "":
                empty += 1
            else:
                empty = 0
                lines.append(line)
        req = "\n".join(lines)
        result = process_requirements(req)
        print(f"\nUnderstood goal: {result.get('understood_goal','')}")
        print(f"\nClarifying questions:")
        for q in result.get("ambiguities", []):
            print(f"  Q: {q.get('question','')}")
            print(f"     Why: {q.get('why_important','')}")
            print(f"     Assuming: {q.get('default_assumption','')}")
        print(f"\nRisks:")
        for r in result.get("risks", []):
            print(f"  - {r}")

    elif choice == "2":
        print("\nPaste meeting notes (Enter twice when done):")
        lines = []
        empty = 0
        while empty < 2:
            line = input()
            if line == "":
                empty += 1
            else:
                empty = 0
                lines.append(line)
        notes = "\n".join(lines)
        result = process_meeting_notes(notes)
        print(f"\nSummary: {result.get('meeting_summary','')}")
        print(f"\nAction items:")
        for item in result.get("action_items", []):
            print(f"  [{item.get('who','')}] {item.get('what','')} — {item.get('by_when','')}")
        print(f"\nOpen questions:")
        for q in result.get("open_questions", []):
            print(f"  ? {q}")

    elif choice == "3":
        print("\nPaste requirements (Enter twice when done):")
        lines = []
        empty = 0
        while empty < 2:
            line = input()
            if line == "":
                empty += 1
            else:
                empty = 0
                lines.append(line)
        req = "\n".join(lines)
        spec = generate_technical_spec(req)
        tickets = generate_tickets(spec)
        filename = save_spec_as_markdown(spec)
        print_spec(spec)
        print(f"\nTickets generated: {len(tickets)}")
        for t in tickets:
            print(f"  {t['id']}: {t['title']} ({t['estimated_hours']}h)")

    elif choice == "4":
        sample = """
We need users to be able to log in with Google.
Also add a dashboard where they can see their activity.
Make it fast. Should work on mobile too.
The CEO wants this done by next Friday.
"""
        print(f"Sample requirement: {sample}")
        print("\nStep 1 — Processing requirements...")
        analysis = process_requirements(sample)
        print(f"Understood: {analysis.get('understood_goal','')}")
        print(f"Complexity: {analysis.get('estimated_complexity','')}")
        print(f"Clarifying questions: {len(analysis.get('ambiguities',[]))}")

        print("\nStep 2 — Generating technical spec...")
        spec = generate_technical_spec(sample)
        filename = save_spec_as_markdown(spec)
        print_spec(spec)

        print("\nStep 3 — Generating tickets...")
        tickets = generate_tickets(spec)
        print(f"Tickets created: {len(tickets)}")
        for t in tickets:
            print(f"  {t['id']}: {t['title']}")
