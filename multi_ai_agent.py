import asyncio
import aiohttp
import json
import os
from datetime import datetime
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
client = Groq(api_key=GROQ_API_KEY)

TEAM = {
    "product_manager": {
        "model": "llama-3.3-70b-versatile",
        "role": "Product Manager",
        "responsibility": "Breaks down requirements into tasks and prioritizes work",
        "output": "sprint plan with prioritized tasks"
    },
    "architect": {
        "model": "llama-3.3-70b-versatile",
        "role": "Software Architect",
        "responsibility": "Designs system architecture and technical approach",
        "output": "technical design document"
    },
    "frontend_dev": {
        "model": "llama-3.1-8b-instant",
        "role": "Frontend Developer",
        "responsibility": "Builds user interfaces and client-side logic",
        "output": "frontend code and components"
    },
    "backend_dev": {
        "model": "llama-3.3-70b-versatile",
        "role": "Backend Developer",
        "responsibility": "Builds APIs, databases, and server-side logic",
        "output": "backend code and APIs"
    },
    "qa_engineer": {
        "model": "llama-3.1-8b-instant",
        "role": "QA Engineer",
        "responsibility": "Tests code and ensures quality standards",
        "output": "test cases and quality report"
    },
    "devops": {
        "model": "llama-3.1-8b-instant",
        "role": "DevOps Engineer",
        "responsibility": "Handles deployment, CI/CD, and infrastructure",
        "output": "deployment plan and scripts"
    },
    "tech_lead": {
        "model": "llama-3.3-70b-versatile",
        "role": "Tech Lead",
        "responsibility": "Reviews all work and makes final decisions",
        "output": "final approval and integration plan"
    }
}

async def agent_work(session: aiohttp.ClientSession, agent_name: str, agent_info: dict,
                     task: str, context: str = ""):
    print(f"  [{agent_info['role']}] Working...")

    prompt = f"""You are a {agent_info['role']} on a software development team.

Your responsibility: {agent_info['responsibility']}
Your expected output: {agent_info['output']}

Project task: {task}

{f'Context from team: {context[:500]}' if context else ''}

Complete your specific responsibility for this project.

Return ONLY a JSON object:
{{
    "agent": "{agent_name}",
    "role": "{agent_info['role']}",
    "work_completed": "<detailed description of what you did>",
    "deliverables": ["<deliverable1>", "<deliverable2>"],
    "decisions_made": ["<decision1>", "<decision2>"],
    "dependencies": ["<what other team members need to do>"],
    "estimated_time": "<time to complete>",
    "status": "<complete, in_progress, or blocked>"
}}

Return ONLY the JSON. No extra text."""

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": agent_info["model"],
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 1024
    }

    try:
        async with session.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers=headers,
            json=payload
        ) as response:
            data = await response.json()
            raw = data["choices"][0]["message"]["content"].strip()

            if raw.startswith("```"):
                raw = raw.split("```")[1]
                if raw.startswith("json"):
                    raw = raw[4:]
            raw = raw.strip()

            result = json.loads(raw)
            print(f"  [{agent_info['role']}] Done — {result.get('status', 'complete')}")
            return result

    except Exception as e:
        print(f"  [{agent_info['role']}] Error: {e}")
        return {
            "agent": agent_name,
            "role": agent_info["role"],
            "work_completed": "Could not complete work",
            "deliverables": [],
            "decisions_made": [],
            "dependencies": [],
            "estimated_time": "unknown",
            "status": "blocked"
        }

async def run_sprint(project: dict):
    print("\n" + "=" * 60)
    print("  AI DEVELOPMENT TEAM — SPRINT SIMULATION")
    print("=" * 60)
    print(f"\nProject: {project['name']}")
    print(f"Description: {project['description'][:100]}")
    print(f"\nTeam size: {len(TEAM)} agents")
    print("=" * 60)

    task = f"""
Project: {project['name']}
Description: {project['description']}
Requirements: {', '.join(project.get('requirements', []))}
Tech stack: {project.get('tech_stack', 'Python, React, SQLite')}
Deadline: {project.get('deadline', '2 weeks')}
"""

    print("\nPhase 1: Planning (PM + Architect working in parallel)...")
    async with aiohttp.ClientSession() as session:
        planning_tasks = [
            agent_work(session, "product_manager", TEAM["product_manager"], task),
            agent_work(session, "architect", TEAM["architect"], task)
        ]
        planning_results = await asyncio.gather(*planning_tasks)

    pm_result = planning_results[0]
    arch_result = planning_results[1]

    planning_context = f"""
PM Plan: {pm_result.get('work_completed', '')}
Architecture: {arch_result.get('work_completed', '')}
"""

    print("\nPhase 2: Development (Frontend + Backend working in parallel)...")
    async with aiohttp.ClientSession() as session:
        dev_tasks = [
            agent_work(session, "frontend_dev", TEAM["frontend_dev"], task, planning_context),
            agent_work(session, "backend_dev", TEAM["backend_dev"], task, planning_context)
        ]
        dev_results = await asyncio.gather(*dev_tasks)

    fe_result = dev_results[0]
    be_result = dev_results[1]

    dev_context = f"""
Frontend: {fe_result.get('work_completed', '')}
Backend: {be_result.get('work_completed', '')}
"""

    print("\nPhase 3: QA + DevOps (working in parallel)...")
    async with aiohttp.ClientSession() as session:
        qa_devops_tasks = [
            agent_work(session, "qa_engineer", TEAM["qa_engineer"], task, dev_context),
            agent_work(session, "devops", TEAM["devops"], task, dev_context)
        ]
        qa_devops_results = await asyncio.gather(*qa_devops_tasks)

    qa_result = qa_devops_results[0]
    devops_result = qa_devops_results[1]

    all_context = f"""
PM: {pm_result.get('work_completed', '')[:200]}
Architecture: {arch_result.get('work_completed', '')[:200]}
Frontend: {fe_result.get('work_completed', '')[:200]}
Backend: {be_result.get('work_completed', '')[:200]}
QA: {qa_result.get('work_completed', '')[:200]}
DevOps: {devops_result.get('work_completed', '')[:200]}
"""

    print("\nPhase 4: Tech Lead final review...")
    async with aiohttp.ClientSession() as session:
        lead_result = await agent_work(
            session, "tech_lead", TEAM["tech_lead"], task, all_context
        )

    all_results = {
        "product_manager": pm_result,
        "architect": arch_result,
        "frontend_dev": fe_result,
        "backend_dev": be_result,
        "qa_engineer": qa_result,
        "devops": devops_result,
        "tech_lead": lead_result
    }

    return all_results

def generate_sprint_report(project: dict, results: dict):
    report = f"""# Sprint Report — {project['name']}

**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M')}
**Project:** {project['name']}
**Team Size:** {len(results)} agents

---

## Team Deliverables

"""
    for agent_name, result in results.items():
        report += f"### {result.get('role', agent_name)}\n"
        report += f"**Status:** {result.get('status', 'unknown').upper()}\n"
        report += f"**Work:** {result.get('work_completed', 'N/A')[:200]}\n\n"

        deliverables = result.get('deliverables', [])
        if deliverables:
            report += "**Deliverables:**\n"
            for d in deliverables:
                report += f"- {d}\n"
            report += "\n"

    lead = results.get('tech_lead', {})
    report += f"""---

## Tech Lead Decision

{lead.get('work_completed', 'No decision recorded')}

## Next Steps

"""
    decisions = lead.get('decisions_made', [])
    for d in decisions:
        report += f"- {d}\n"

    report += f"\n---\n*Generated by AI SWE Bot Multi-Agent Team*"

    filename = f"sprint_report_{project['name'].replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(report)
    print(f"\nSprint report saved: {filename}")
    return filename

def print_team_summary(results: dict):
    print("\n" + "=" * 60)
    print("  SPRINT COMPLETE — TEAM SUMMARY")
    print("=" * 60)

    completed = sum(1 for r in results.values() if r.get('status') == 'complete')
    total = len(results)

    print(f"\nTeam completion rate: {completed}/{total} agents")
    print()

    for agent_name, result in results.items():
        status = result.get('status', 'unknown')
        role = result.get('role', agent_name)
        status_icon = "DONE" if status == 'complete' else "WORKING" if status == 'in_progress' else "BLOCKED"
        print(f"  [{status_icon}] {role}")

        deliverables = result.get('deliverables', [])
        for d in deliverables[:2]:
            print(f"    - {d}")

    lead = results.get('tech_lead', {})
    print(f"\nTech Lead Final Decision:")
    print(f"  {lead.get('work_completed', 'No decision')[:150]}")

if __name__ == "__main__":
    print("=" * 40)
    print("  Multi-Agent Team Simulation")
    print("=" * 40)
    print()

    project = {
        "name": "AI SWE Bot Dashboard",
        "description": "Build a real-time dashboard for the AI SWE Bot that shows live metrics, bug detection history, code quality scores, and system performance. Users should be able to paste code and see analysis results instantly.",
        "requirements": [
            "Real-time metrics display",
            "Code paste and analyze feature",
            "Bug history timeline",
            "Code quality score charts",
            "System performance monitoring",
            "Mobile responsive design"
        ],
        "tech_stack": "Python Flask, React, SQLite, Chart.js",
        "deadline": "2 weeks"
    }

    print(f"Simulating full dev team for: {project['name']}")
    print(f"Team: {', '.join([info['role'] for info in TEAM.values()])}")
    print()

    results = asyncio.run(run_sprint(project))
    print_team_summary(results)
    filename = generate_sprint_report(project, results)

    print(f"\nOpen {filename} to see the full sprint report.")
