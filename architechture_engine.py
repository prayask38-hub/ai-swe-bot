import os
import json
from datetime import datetime
from groq import Groq
from dotenv import load_dotenv

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def evaluate_architecture_decision(question: str, context: str = ""):
    print(f"Evaluating: {question[:60]}...")

    prompt = f"""You are a principal software architect with 20 years of experience at Google, Meta and Amazon.

Architecture decision needed:
{question}

Context:
{context if context else "Early stage startup, team of 5 engineers, Python backend"}

Evaluate ALL options and make a definitive recommendation like a senior architect would.

Return ONLY a JSON object:
{{
    "decision_title": "<short title for this ADR>",
    "options_evaluated": [
        {{
            "option": "<option name>",
            "pros": ["<pro1>", "<pro2>", "<pro3>"],
            "cons": ["<con1>", "<con2>", "<con3>"],
            "best_for": "<when this is the right choice>",
            "worst_for": "<when never use this>",
            "companies_using": ["<company1>", "<company2>"],
            "score": <0-100>
        }}
    ],
    "recommended_option": "<the best choice>",
    "recommendation_reason": "<detailed explanation of why>",
    "tradeoffs_accepted": ["<tradeoff1>", "<tradeoff2>"],
    "implementation_steps": ["<step1>", "<step2>", "<step3>"],
    "when_to_revisit": "<conditions that would change this decision>",
    "estimated_effort": "<hours or days to implement>",
    "risks": ["<risk1>", "<risk2>"],
    "verdict": "<one definitive sentence recommendation>"
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

def generate_adr(decision: dict, question: str):
    filename = f"ADR_{decision.get('decision_title','decision').replace(' ','_')}_{datetime.now().strftime('%Y%m%d')}.md"

    with open(filename, 'w', encoding='utf-8') as f:
        f.write(f"# ADR: {decision.get('decision_title','')}\n\n")
        f.write(f"**Date:** {datetime.now().strftime('%Y-%m-%d')}  \n")
        f.write(f"**Status:** Accepted  \n")
        f.write(f"**Decision:** {decision.get('recommended_option','')}  \n\n")
        f.write(f"---\n\n")
        f.write(f"## Context\n{question}\n\n")
        f.write(f"## Decision\n{decision.get('recommendation_reason','')}\n\n")
        f.write(f"## Options Considered\n\n")

        for opt in decision.get("options_evaluated", []):
            f.write(f"### {opt.get('option','')} (Score: {opt.get('score',0)}/100)\n")
            f.write(f"**Best for:** {opt.get('best_for','')}\n\n")
            f.write(f"**Pros:**\n")
            for p in opt.get("pros", []):
                f.write(f"- {p}\n")
            f.write(f"\n**Cons:**\n")
            for c in opt.get("cons", []):
                f.write(f"- {c}\n")
            f.write(f"\n**Used by:** {', '.join(opt.get('companies_using',[]))}\n\n")

        f.write(f"## Consequences\n")
        f.write(f"**Tradeoffs accepted:**\n")
        for t in decision.get("tradeoffs_accepted", []):
            f.write(f"- {t}\n")
        f.write(f"\n**Risks:**\n")
        for r in decision.get("risks", []):
            f.write(f"- {r}\n")
        f.write(f"\n## Implementation Steps\n")
        for i, step in enumerate(decision.get("implementation_steps", []), 1):
            f.write(f"{i}. {step}\n")
        f.write(f"\n## When to Revisit\n{decision.get('when_to_revisit','')}\n")

    print(f"ADR saved: {filename}")
    return filename

def system_design(requirements: str):
    print("Running system design analysis...")

    prompt = f"""You are a principal engineer designing a system from scratch.

Requirements:
{requirements}

Design the complete system architecture.

Return ONLY a JSON object:
{{
    "system_name": "<name>",
    "scale_estimate": {{
        "users": "<expected users>",
        "requests_per_second": <number>,
        "data_storage": "<GB or TB>"
    }},
    "components": [
        {{
            "name": "<component name>",
            "type": "<frontend, backend, database, cache, queue, etc>",
            "technology": "<specific technology>",
            "responsibility": "<what it does>",
            "scaling_strategy": "<how it scales>"
        }}
    ],
    "data_flow": "<how a request flows through the system>",
    "bottlenecks": ["<potential bottleneck1>", "<potential bottleneck2>"],
    "single_points_of_failure": ["<spof1>", "<spof2>"],
    "scaling_plan": {{
        "phase_1": "<0 to 10k users>",
        "phase_2": "<10k to 100k users>",
        "phase_3": "<100k to 1M users>"
    }},
    "estimated_monthly_cost": "<AWS/GCP cost estimate>",
    "tech_stack_summary": ["<tech1>", "<tech2>", "<tech3>"]
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

def evaluate_tech_debt(codebase_description: str):
    print("Evaluating technical debt...")

    prompt = f"""You are a senior architect evaluating technical debt.

Codebase description:
{codebase_description}

Evaluate the technical debt and provide a remediation plan.

Return ONLY a JSON object:
{{
    "debt_score": <0-100>,
    "debt_level": "<low, medium, high, or critical>",
    "debt_categories": [
        {{
            "category": "<code quality, architecture, security, performance, testing>",
            "severity": "<low, medium, high>",
            "description": "<what the debt is>",
            "remediation": "<how to fix it>",
            "effort_days": <number>
        }}
    ],
    "total_remediation_days": <number>,
    "priority_order": ["<fix this first>", "<then this>", "<then this>"],
    "quick_wins": ["<easy fix1>", "<easy fix2>"],
    "summary": "<overall assessment>"
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

def print_decision(decision: dict):
    print("\n" + "=" * 50)
    print("  ARCHITECTURAL DECISION")
    print("=" * 50)
    print(f"\nDecision: {decision.get('decision_title','')}")
    print(f"Verdict:  {decision.get('verdict','')}")
    print(f"Recommended: {decision.get('recommended_option','').upper()}")
    print(f"Effort: {decision.get('estimated_effort','')}")

    options = decision.get("options_evaluated", [])
    if options:
        print(f"\nOptions evaluated:")
        for opt in options:
            bar = "█" * (opt.get('score', 0) // 10) + "░" * (10 - opt.get('score', 0) // 10)
            print(f"  {opt.get('option',''):20} [{bar}] {opt.get('score',0)}/100")

    print(f"\nWhy {decision.get('recommended_option','')}:")
    print(f"  {decision.get('recommendation_reason','')[:200]}")

    tradeoffs = decision.get("tradeoffs_accepted", [])
    if tradeoffs:
        print(f"\nTradeoffs accepted:")
        for t in tradeoffs:
            print(f"  - {t}")

    steps = decision.get("implementation_steps", [])
    if steps:
        print(f"\nImplementation steps:")
        for i, s in enumerate(steps, 1):
            print(f"  {i}. {s}")

    print(f"\nRevisit when: {decision.get('when_to_revisit','')}")

if __name__ == "__main__":
    print("=" * 40)
    print("  Architectural Decision Engine")
    print("=" * 40)
    print()
    print("1. Evaluate architecture decision")
    print("2. Design a system from scratch")
    print("3. Evaluate technical debt")
    print("4. Test with sample decisions")
    print()
    choice = input("Choose (1-4): ").strip()

    if choice == "1":
        print("\nWhat architecture decision do you need to make?")
        question = input("> ").strip()
        context = input("Context (optional): ").strip()
        decision = evaluate_architecture_decision(question, context)
        adr_file = generate_adr(decision, question)
        print_decision(decision)
        print(f"\nADR saved: {adr_file}")

    elif choice == "2":
        print("\nDescribe the system to design:")
        req = input("> ").strip()
        design = system_design(req)
        print(f"\nSystem: {design.get('system_name','')}")
        print(f"Scale: {design.get('scale_estimate',{}).get('users','')} users")
        print(f"RPS: {design.get('scale_estimate',{}).get('requests_per_second',0)}/sec")
        print(f"Cost: {design.get('estimated_monthly_cost','')}/month")
        print(f"\nComponents:")
        for c in design.get("components", []):
            print(f"  {c.get('name','')} — {c.get('technology','')} ({c.get('type','')})")
        print(f"\nTech stack: {', '.join(design.get('tech_stack_summary',[]))}")
        print(f"\nScaling plan:")
        plan = design.get("scaling_plan", {})
        for phase, desc in plan.items():
            print(f"  {phase}: {desc}")

    elif choice == "3":
        print("\nDescribe your codebase:")
        desc = input("> ").strip()
        debt = evaluate_tech_debt(desc)
        print(f"\nDebt score: {debt.get('debt_score',0)}/100")
        print(f"Debt level: {debt.get('debt_level','').upper()}")
        print(f"Remediation: {debt.get('total_remediation_days',0)} days")
        print(f"\nQuick wins:")
        for w in debt.get("quick_wins", []):
            print(f"  - {w}")
        print(f"\nPriority order:")
        for i, p in enumerate(debt.get("priority_order", []), 1):
            print(f"  {i}. {p}")

    elif choice == "4":
        questions = [
            ("Should we use PostgreSQL or MongoDB for our user data?",
             "SaaS app, 100k users, complex queries needed, team knows SQL"),
            ("Should we build a monolith or microservices architecture?",
             "5 person team, early stage startup, need to ship fast"),
            ("Should we use Redis or Memcached for caching?",
             "Python backend, need pub/sub, complex data structures")
        ]

        for question, context in questions:
            print(f"\nQuestion: {question}")
            print(f"Context: {context}")
            decision = evaluate_architecture_decision(question, context)
            print(f"Recommendation: {decision.get('recommended_option','').upper()}")
            print(f"Verdict: {decision.get('verdict','')}")
            adr_file = generate_adr(decision, question)
            print()
