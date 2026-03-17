import asyncio
import aiohttp
import json
import os
from datetime import datetime
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

AGENTS = {
    "architect": {
        "model": "llama-3.3-70b-versatile",
        "role": "Software architect who plans the overall solution structure",
        "specialty": "system design, architecture, planning"
    },
    "debugger": {
        "model": "llama-3.3-70b-versatile",
        "role": "Expert debugger who finds and fixes bugs",
        "specialty": "bug detection, error analysis, fixes"
    },
    "reviewer": {
        "model": "llama-3.1-8b-instant",
        "role": "Code reviewer who checks quality and best practices",
        "specialty": "code quality, best practices, standards"
    },
    "optimizer": {
        "model": "llama-3.1-8b-instant",
        "role": "Performance optimizer who improves code efficiency",
        "specialty": "performance, optimization, efficiency"
    },
    "security": {
        "model": "llama-3.3-70b-versatile",
        "role": "Security expert who finds vulnerabilities",
        "specialty": "security, vulnerabilities, safe coding"
    }
}

async def ask_agent(session: aiohttp.ClientSession, agent_name: str, agent_info: dict, task: str, context: str = ""):
    print(f"  Agent {agent_name.upper()} thinking...")

    prompt = f"""You are a {agent_info['role']}.
Your specialty: {agent_info['specialty']}

Task: {task}

{f'Context from other agents: {context}' if context else ''}

Provide your expert analysis. Be specific and actionable.

Return ONLY a JSON object:
{{
    "agent": "{agent_name}",
    "specialty": "{agent_info['specialty']}",
    "analysis": "<your detailed analysis>",
    "findings": ["<finding1>", "<finding2>", "<finding3>"],
    "recommendations": ["<recommendation1>", "<recommendation2>"],
    "confidence": "<high, medium, or low>"
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
            print(f"  Agent {agent_name.upper()} done — confidence: {result.get('confidence', 'unknown')}")
            return result

    except Exception as e:
        print(f"  Agent {agent_name} error: {e}")
        return {
            "agent": agent_name,
            "specialty": agent_info["specialty"],
            "analysis": "Could not complete analysis",
            "findings": [],
            "recommendations": [],
            "confidence": "low"
        }

async def run_parallel_agents(task: str, agents_to_use: list = None):
    if not agents_to_use:
        agents_to_use = list(AGENTS.keys())

    print(f"\nDeploying {len(agents_to_use)} AI agents in parallel...")
    print(f"Agents: {', '.join(agents_to_use)}")
    print()

    start_time = datetime.now()

    async with aiohttp.ClientSession() as session:
        tasks = [
            ask_agent(session, name, AGENTS[name], task)
            for name in agents_to_use
            if name in AGENTS
        ]
        results = await asyncio.gather(*tasks)

    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    print(f"\nAll agents completed in {duration:.1f} seconds")

    return results

async def consensus_decision(results: list, original_task: str):
    print("\nBuilding consensus from all agents...")

    all_findings = []
    all_recommendations = []

    for result in results:
        all_findings.extend(result.get("findings", []))
        all_recommendations.extend(result.get("recommendations", []))

    combined = {
        "task": original_task,
        "agent_count": len(results),
        "all_findings": all_findings,
        "all_recommendations": all_recommendations,
        "agent_results": results
    }

    client = Groq(api_key=GROQ_API_KEY)

    prompt = f"""You are a consensus builder. Multiple AI agents analyzed a task and provided their findings.

Task: {original_task}

Agent findings and recommendations:
{json.dumps(combined, indent=2)[:3000]}

Build a consensus decision by:
1. Finding common themes across agents
2. Prioritizing the most important issues
3. Creating a unified action plan

Return ONLY a JSON object:
{{
    "consensus_summary": "<overall summary>",
    "agreed_issues": ["<issue all agents agree on>"],
    "priority_actions": [
        {{
            "action": "<what to do>",
            "agent_support": "<which agents recommended this>",
            "priority": "<high, medium, or low>"
        }}
    ],
    "confidence_score": <0-100>,
    "final_recommendation": "<the single most important thing to do>"
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
            "consensus_summary": "Multiple agents analyzed the code",
            "agreed_issues": all_findings[:3],
            "priority_actions": [{"action": r, "agent_support": "multiple", "priority": "high"} for r in all_recommendations[:3]],
            "confidence_score": 75,
            "final_recommendation": all_recommendations[0] if all_recommendations else "Review the code manually"
        }

async def collaborative_code_review(code: str, language: str = "python"):
    task = f"""Review this {language} code and provide your expert analysis:
```{language}
{code}
```

Find bugs, security issues, performance problems, and suggest improvements."""

    print("=" * 50)
    print("  COLLABORATIVE AI NETWORK")
    print("  5 agents working in parallel")
    print("=" * 50)

    results = await run_parallel_agents(task)
    consensus = await consensus_decision(results, task)

    return {
        "agent_results": results,
        "consensus": consensus
    }

def print_collaborative_report(report: dict):
    results = report.get("agent_results", [])
    consensus = report.get("consensus", {})

    print("\n" + "=" * 50)
    print("  COLLABORATIVE AI REPORT")
    print("=" * 50)

    print(f"\nAgents deployed: {len(results)}")
    for result in results:
        print(f"\n  [{result['agent'].upper()}] — {result['specialty']}")
        print(f"  Confidence: {result.get('confidence', 'unknown')}")
        findings = result.get("findings", [])
        if findings:
            print(f"  Key findings:")
            for f in findings[:2]:
                print(f"    - {f}")

    print("\n" + "-" * 50)
    print("  CONSENSUS DECISION")
    print("-" * 50)
    print(f"\nSummary: {consensus.get('consensus_summary', 'N/A')}")
    print(f"Confidence: {consensus.get('confidence_score', 0)}/100")
    print(f"\nFinal recommendation:")
    print(f"  {consensus.get('final_recommendation', 'N/A')}")

    priority_actions = consensus.get("priority_actions", [])
    if priority_actions:
        print(f"\nPriority actions:")
        for action in priority_actions:
            print(f"  [{action['priority'].upper()}] {action['action']}")
            print(f"  Supported by: {action['agent_support']}")

    agreed = consensus.get("agreed_issues", [])
    if agreed:
        print(f"\nAll agents agree on:")
        for issue in agreed:
            print(f"  - {issue}")

if __name__ == "__main__":
    print("=" * 40)
    print("  Collaborative AI Network Test")
    print("=" * 40)
    print()

    sample_code = """
def process_payment(user_id, amount, card_number):
    import sqlite3
    conn = sqlite3.connect("payments.db")
    cursor = conn.cursor()

    query = "SELECT * FROM users WHERE id = " + str(user_id)
    user = cursor.execute(query).fetchone()

    if amount > 0:
        if user:
            if card_number:
                cursor.execute(
                    "INSERT INTO payments VALUES (?, ?, ?)",
                    (user_id, amount, card_number)
                )
                conn.commit()
                return True
    return False

def calculate_discount(price, discount):
    return price - (price * discount / 100)

def send_receipt(email, amount):
    print(f"Receipt sent to {email} for ${amount}")
"""

    report = asyncio.run(collaborative_code_review(sample_code, "python"))
    print_collaborative_report(report)

    print("\nSaving results...")
    with open("collaborative_report.json", "w") as f:
        json.dump(report, f, indent=2)
    print("Report saved to collaborative_report.json")
