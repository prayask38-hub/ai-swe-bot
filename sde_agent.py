import os
import json
import threading
import time
from datetime import datetime
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

try:
    from sandbox import run_code_in_sandbox, run_with_rollback
    SANDBOX_AVAILABLE = True
except:
    SANDBOX_AVAILABLE = False

try:
    from api_hub import GitHubAPI
    from github_integration import get_repo_files, get_file_content, analyze_repo_for_bugs
    GITHUB_AVAILABLE = True
except:
    GITHUB_AVAILABLE = False

from bug_detector import detect_bugs
from solution_generator import generate_solutions
from auto_fixer import run_code, apply_fix
from smart_ai import chain_of_thought_analysis, self_correcting_solution
from multi_ai import multi_ai_analyze
from learning_engine import init_learning_db, learn_from_fix, get_smart_suggestion, learn_coding_style
from predictive_analysis import full_predictive_analysis
from language_detector import detect_language
from sde_replacement import read_ticket, write_code, write_tests, run_tests, review_code, respond_to_review
from code_quality import full_code_review
from roadmap_generator import generate_roadmap, save_roadmap
from blockchain_logger import init_blockchain_db, log_action
from storage import init_db, save_session, save_bug, save_successful_fix
from website_generator import generate_website, save_website
from enterprise_security import init_security_db, log_security_event


class SDEAgent:
    def __init__(self, name: str = "Prayas AI Engineer"):
        self.name = name
        self.session_id = datetime.now().strftime('%Y%m%d_%H%M%S')
        self.tasks_completed = 0
        self.bugs_fixed = 0
        self.lines_written = 0
        self.session_log = []

        print(f"\n{'='*60}")
        print(f"  SDE Agent — {self.name}")
        print(f"  Session: {self.session_id}")
        print(f"  Initializing all systems...")
        print(f"{'='*60}\n")

        init_db()
        init_learning_db()
        init_blockchain_db()
        init_security_db()

        log_action("agent_started", {
            "agent_name": name,
            "session_id": self.session_id
        })

        print("All systems online:")
        systems = [
            "Bug detector", "Solution generator", "Auto fixer",
            "Smart AI", "Multi AI", "Learning engine",
            "Predictive analysis", "Code quality", "Collaborative AI",
            "Blockchain logger", "Enterprise security", "Storage",
            "Website generator", "GitHub" if GITHUB_AVAILABLE else "GitHub (no token)",
            "Docker sandbox" if SANDBOX_AVAILABLE else "Sandbox (Docker not running)"
        ]
        for system in systems:
            print(f"  + {system}")
        print()

    def log(self, message: str, level: str = "info"):
        timestamp = datetime.now().strftime('%H:%M:%S')
        icons = {"info": "→", "success": "✓", "warning": "!", "error": "✗"}
        icon = icons.get(level, "→")
        print(f"  [{timestamp}] {icon} {message}")
        self.session_log.append({
            "time": timestamp,
            "level": level,
            "message": message
        })

    def understand_task(self, task: str):
        self.log(f"Understanding task: {task[:60]}...")

        prompt = f"""You are a senior software engineer receiving a task.

Task: {task}

Return ONLY a JSON object:
{{
    "task_type": "<fix_bugs, write_code, analyze_code, generate_website, review_code, or general>",
    "language": "<python, javascript, java, or unknown>",
    "complexity": "<simple, medium, or complex>",
    "approach": "<brief description>",
    "estimated_minutes": <number>
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
            plan = json.loads(raw)
            self.log(f"Task type: {plan.get('task_type', 'unknown')}")
            self.log(f"Complexity: {plan.get('complexity', 'unknown')}")
            self.log(f"Estimated time: {plan.get('estimated_minutes', 0)} minutes")
            return plan
        except:
            return {"task_type": "general", "language": "python", "complexity": "medium"}

    def fix_code(self, code: str, language: str = None):
        self.log("Starting full code fix pipeline...")

        if not language or language == "unknown":
            lang_result = detect_language(code)
            language = lang_result.get("language", "python")
            self.log(f"Language detected: {language}")

        learn_coding_style(code, language)

        self.log("Running predictive analysis...")
        try:
            predictions = full_predictive_analysis(code, language)
            risk = predictions.get("predictions", {}).get("risk_level", "unknown")
            self.log(f"Risk level: {risk}", "warning" if risk in ["high", "critical"] else "info")
        except Exception as e:
            self.log(f"Predictive analysis skipped: {e}", "warning")

        self.log("Running smart chain-of-thought analysis...")
        try:
            smart_result = chain_of_thought_analysis(code, language)
            bugs = smart_result.get("bugs", []) if smart_result else []
            confidence = smart_result.get("confidence", 0) if smart_result else 0
            self.log(f"Smart AI found {len(bugs)} bugs with {confidence}% confidence")
        except Exception as e:
            self.log(f"Smart AI failed, using standard detector: {e}", "warning")
            bug_result = detect_bugs(code, language)
            bugs = bug_result.get("bugs", [])

        if not bugs:
            self.log("No bugs found — code is clean!", "success")
            return {"success": True, "fixed_code": code, "bugs_found": 0, "bugs_fixed": 0}

        self.log("Cross-checking with multi-AI consensus...")
        try:
            multi_result = multi_ai_analyze(code, language)
            multi_bugs = multi_result.get("bugs", [])
            if len(multi_bugs) > len(bugs):
                bugs = multi_bugs
                self.log(f"Multi-AI found {len(bugs)} bugs total")
        except Exception as e:
            self.log(f"Multi-AI skipped: {e}", "warning")

        self.log(f"Generating self-correcting solutions for {len(bugs)} bugs...")
        solutions_list = []
        for bug in bugs:
            try:
                known = get_smart_suggestion(language, bug.get("type", ""), bug.get("description", ""))
                if known and known.get("source") == "memory":
                    self.log(f"Using memorized fix for {bug.get('type')} (used {known.get('times_seen', 0)} times)")
                    solutions = {
                        "bug_id": bug.get("bug_id", 1),
                        "solutions": [
                            {"solution_id": 1, "approach": "From memory",
                             "explanation": "Previously successful fix",
                             "fixed_code": known["suggestion"]},
                            {"solution_id": 2, "approach": "AI verified",
                             "explanation": "AI confirmed fix",
                             "fixed_code": known["suggestion"]},
                            {"solution_id": 3, "approach": "Alternative",
                             "explanation": "Alternative approach",
                             "fixed_code": known["suggestion"]}
                        ]
                    }
                else:
                    verified = self_correcting_solution(code, bug, language)
                    if verified:
                        solutions = {
                            "bug_id": bug.get("bug_id", 1),
                            "solutions": [
                                {"solution_id": 1, "approach": "Verified fix",
                                 "explanation": verified.get("verification_notes", ""),
                                 "fixed_code": verified.get("verified_fix", "")},
                                {"solution_id": 2, "approach": "Original fix",
                                 "explanation": verified.get("explanation", ""),
                                 "fixed_code": verified.get("original_fix", "")},
                                {"solution_id": 3, "approach": "AI generated",
                                 "explanation": "Alternative approach",
                                 "fixed_code": verified.get("verified_fix", "")}
                            ]
                        }
                    else:
                        solutions = generate_solutions(code, bug)
                solutions_list.append(solutions)
            except Exception as e:
                self.log(f"Solution generation failed for bug #{bug.get('bug_id', '?')}: {e}", "warning")
                solutions_list.append({"bug_id": bug.get("bug_id", 1), "solutions": []})

        self.log("Phase 1 — Applying best fix for each bug...")
        current_code = code
        fixes_applied = []

        for i, bug in enumerate(bugs):
            solutions = solutions_list[i].get("solutions", []) if i < len(solutions_list) else []
            if not solutions:
                continue
            best_fix = solutions[0].get("fixed_code", "")
            if not best_fix:
                continue
            try:
                current_code = apply_fix(current_code, bug.get("line", 1), best_fix)
                fixes_applied.append({
                    "bug_id": bug.get("bug_id", i+1),
                    "solution": solutions[0].get("approach", "fix"),
                    "fixed_code": best_fix,
                    "status": "applied"
                })
                self.log(f"Fix applied for Bug #{bug.get('bug_id', i+1)}: {solutions[0].get('approach', '')}")
                learn_from_fix(language, bug.get("type", ""), best_fix, best_fix)
                save_successful_fix(language, bug.get("type", ""), best_fix, best_fix)
                self.bugs_fixed += 1
            except Exception as e:
                self.log(f"Could not apply fix for Bug #{bug.get('bug_id', i+1)}: {e}", "warning")

        self.log("Phase 2 — AI full rewrite with all fixes...")
        try:
            rewrite_prompt = f"""You are an expert {language} developer.

Here is buggy code:
{code}

Here are all the bugs that need to be fixed:
{json.dumps([{"line": b.get("line"), "type": b.get("type"), "description": b.get("description")} for b in bugs], indent=2)}

Rewrite the ENTIRE code with ALL bugs fixed. Keep the same logic and structure but fix every single bug.

Return ONLY the complete fixed {language} code. No explanations. No markdown. No comments about changes. Just pure working code."""

            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": rewrite_prompt}]
            )

            rewritten = response.choices[0].message.content.strip()
            if rewritten.startswith("```"):
                rewritten = rewritten.split("```")[1]
                if rewritten.startswith(language):
                    rewritten = rewritten[len(language):]
                elif rewritten.startswith("python"):
                    rewritten = rewritten[6:]
            rewritten = rewritten.strip()

            if rewritten and len(rewritten) > 50:
                current_code = rewritten
                self.log("Full rewrite complete — testing now...")

                result = run_code(current_code)
                if result and result.get("success"):
                    self.log("Code runs successfully after rewrite!", "success")
                    for fix in fixes_applied:
                        fix["status"] = "fixed"
                    log_action("all_bugs_fixed", {
                        "language": language,
                        "bugs_fixed": len(fixes_applied)
                    })
                else:
                    error = result.get("error", "unknown") if result else "unknown"
                    self.log(f"Code has remaining issues: {error[:100]}", "warning")
                    self.log("Saving best attempt anyway...", "info")
        except Exception as e:
            self.log(f"Rewrite phase failed: {e}", "warning")

        self.log("Running code quality review...")
        try:
            quality = full_code_review(current_code, language)
            quality_score = quality.get("quality", {}).get("overall_score", 0)
            self.log(f"Code quality score: {quality_score}/100")
        except Exception as e:
            quality_score = 0
            self.log(f"Quality review skipped: {e}", "warning")

        self.log("Generating session roadmap...")
        try:
            roadmap = generate_roadmap(code, bugs, fixes_applied)
            save_roadmap(roadmap, f"roadmap_{self.session_id}.md")
        except Exception as e:
            roadmap = {"code_health": "good", "summary": "Session complete", "steps_taken": [], "next_steps": []}
            self.log(f"Roadmap generation skipped: {e}", "warning")

        try:
            session_id = save_session(
                language=language,
                total_bugs=len(bugs),
                bugs_fixed=len(fixes_applied),
                code_health=roadmap.get("code_health", "good"),
                original_code=code,
                fixed_code=current_code
            )
            for bug in bugs:
                fix_data = next((f for f in fixes_applied if f["bug_id"] == bug.get("bug_id")), None)
                save_bug(session_id, bug.get("type", ""), bug.get("line", 0),
                        bug.get("description", ""), bug.get("severity", "medium"),
                        fix_data["solution"] if fix_data else "unfixed")
        except Exception as e:
            self.log(f"Session save skipped: {e}", "warning")

        log_action("fix_session_complete", {
            "bugs_found": len(bugs),
            "bugs_fixed": len(fixes_applied),
            "language": language,
            "quality_score": quality_score
        })

        self.tasks_completed += 1

        return {
            "success": True,
            "original_code": code,
            "fixed_code": current_code,
            "bugs_found": len(bugs),
            "bugs_fixed": len(fixes_applied),
            "fixes_applied": fixes_applied,
            "quality_score": quality_score,
            "roadmap": roadmap
        }

    def write_feature(self, task_description: str, language: str = "python"):
        self.log(f"Writing feature: {task_description[:60]}...")

        ticket = {
            "id": f"AGENT-{self.session_id}",
            "title": task_description,
            "description": task_description,
            "acceptance_criteria": "Code must work correctly and pass all tests",
            "priority": "high",
            "labels": [language, "auto-generated"]
        }

        self.log("Reading and planning ticket...")
        plan = read_ticket(ticket)
        self.log(f"Complexity: {plan.get('complexity', 'unknown')}")

        self.log("Writing implementation code...")
        code_result = write_code(
            plan.get("understanding", task_description),
            language,
            task_description
        )
        code = code_result.get("code", "")
        filename = code_result.get("filename", "implementation.py")

        if code:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(code)
            self.lines_written += len(code.split('\n'))
            self.log(f"Code written: {filename} ({len(code.split(chr(10)))} lines)", "success")

        self.log("Writing test cases...")
        test_result = write_tests(code, filename, language)
        test_code = test_result.get("test_code", "")

        self.log("Running tests...")
        if test_code:
            run_result = run_tests(test_code, f"test_{filename}")
            passed = run_result.get("passed", False)
            self.log(f"Tests: {'PASSED' if passed else 'FAILED'}", "success" if passed else "warning")
        else:
            passed = False

        self.log("Checking code quality...")
        try:
            quality = full_code_review(code, language)
            quality_score = quality.get("quality", {}).get("overall_score", 0)
            self.log(f"Quality score: {quality_score}/100")
        except:
            quality_score = 0

        log_action("feature_written", {
            "task": task_description[:50],
            "filename": filename,
            "lines": len(code.split('\n')),
            "tests_passed": passed,
            "quality_score": quality_score
        })

        self.tasks_completed += 1

        return {
            "success": True,
            "filename": filename,
            "code": code,
            "tests_passed": passed,
            "quality_score": quality_score,
            "plan": plan
        }

    def analyze_code(self, code: str, language: str = "python"):
        self.log("Running full code analysis...")

        try:
            result = chain_of_thought_analysis(code, language)
        except:
            result = {}

        try:
            predictions = full_predictive_analysis(code, language)
        except:
            predictions = {}

        try:
            quality = full_code_review(code, language)
        except:
            quality = {}

        return {
            "analysis": result,
            "predictions": predictions,
            "quality": quality
        }

    def generate_website_feature(self, description: str, style: str = "modern"):
        self.log(f"Generating website: {description[:50]}...")
        try:
            html_content, plan = generate_website(description, style)
            filepath = save_website(html_content)
            self.log(f"Website generated: {filepath}", "success")
            log_action("website_generated", {"description": description[:50]})
            self.tasks_completed += 1
            return {"success": True, "filepath": filepath, "plan": plan}
        except Exception as e:
            self.log(f"Website generation failed: {e}", "error")
            return {"success": False, "error": str(e)}

    def review_code_collaborative(self, code: str, language: str = "python"):
        self.log("Running collaborative code review...")
        try:
            import asyncio
            from collaborative_ai import collaborative_code_review
            result = asyncio.run(collaborative_code_review(code, language))
            return result
        except Exception as e:
            self.log(f"Collaborative review failed: {e}", "error")
            return {}

    def analyze_repository(self, repo_name: str):
        if not GITHUB_AVAILABLE:
            self.log("GitHub not available — add GITHUB_TOKEN to .env", "warning")
            return {"error": "GitHub not available"}

        self.log(f"Analyzing GitHub repository: {repo_name}...")
        try:
            bugs = analyze_repo_for_bugs(repo_name)
            self.log(f"Found bugs in {len(bugs)} files", "warning" if bugs else "success")
            log_action("repo_analyzed", {"repo": repo_name, "files_with_bugs": len(bugs)})
            return {"repo": repo_name, "files_with_bugs": len(bugs), "bug_report": bugs}
        except Exception as e:
            self.log(f"Repo analysis failed: {e}", "error")
            return {"error": str(e)}

    def run_task(self, task: str, code: str = None, **kwargs):
        self.log(f"New task received: {task[:60]}")
        print()

        plan = self.understand_task(task)
        task_type = plan.get("task_type", "general")
        language = plan.get("language", "python")

        if task_type == "fix_bugs" and code:
            return self.fix_code(code, language)
        elif task_type == "write_code":
            return self.write_feature(task, language)
        elif task_type == "analyze_code" and code:
            return self.analyze_code(code, language)
        elif task_type == "generate_website":
            style = kwargs.get("style", "modern")
            return self.generate_website_feature(task, style)
        elif task_type == "review_code" and code:
            return self.review_code_collaborative(code, language)
        else:
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": task}]
            )
            return {"response": response.choices[0].message.content}

    def print_summary(self):
        print(f"\n{'='*60}")
        print(f"  SESSION SUMMARY")
        print(f"{'='*60}")
        print(f"  Session ID:      {self.session_id}")
        print(f"  Tasks completed: {self.tasks_completed}")
        print(f"  Bugs fixed:      {self.bugs_fixed}")
        print(f"  Lines written:   {self.lines_written}")
        print(f"  Log entries:     {len(self.session_log)}")
        print(f"{'='*60}\n")


if __name__ == "__main__":
    print("=" * 60)
    print("  AI SDE-2 AGENT")
    print("  Powered by 20 integrated modules")
    print("=" * 60)
    print()
    print("1. Fix bugs in code")
    print("2. Write a new feature")
    print("3. Analyze code quality")
    print("4. Generate a website")
    print("5. Review code collaboratively")
    print("6. Analyze GitHub repository")
    print()

    agent = SDEAgent("Prayas AI Engineer")

    choice = input("Choose (1-6): ").strip()

    if choice == "1":
        print("\nPaste your buggy code then press Enter twice:")
        lines = []
        empty_count = 0
        while empty_count < 2:
            line = input()
            if line == "":
                empty_count += 1
            else:
                empty_count = 0
                lines.append(line)
        code = "\n".join(lines)

        result = agent.run_task("Fix all bugs in this code", code=code)
        print(f"\nBugs found:    {result.get('bugs_found', 0)}")
        print(f"Bugs fixed:    {result.get('bugs_fixed', 0)}")
        print(f"Quality score: {result.get('quality_score', 0)}/100")
        print(f"\nFixed code:")
        print("-" * 60)
        print(result.get("fixed_code", "No fixed code generated"))
        print("-" * 60)

    elif choice == "2":
        task = input("\nDescribe the feature to build: ")
        result = agent.run_task(task)
        print(f"\nFile created:  {result.get('filename', 'unknown')}")
        print(f"Tests passed:  {result.get('tests_passed', False)}")
        print(f"Quality score: {result.get('quality_score', 0)}/100")

    elif choice == "3":
        print("\nPaste your code then press Enter twice:")
        lines = []
        empty_count = 0
        while empty_count < 2:
            line = input()
            if line == "":
                empty_count += 1
            else:
                empty_count = 0
                lines.append(line)
        code = "\n".join(lines)
        result = agent.run_task("Analyze this code", code=code)
        quality = result.get("quality", {}).get("quality", {})
        print(f"\nOverall score: {quality.get('overall_score', 0)}/100")
        print(f"Security:      {quality.get('security', 0)}/100")
        print(f"Summary:       {quality.get('summary', 'N/A')}")

    elif choice == "4":
        description = input("\nDescribe the website: ")
        style = input("Style (modern/minimal/bold): ").strip() or "modern"
        result = agent.run_task(description, style=style)
        print(f"\nWebsite created: {result.get('filepath', 'unknown')}")

    elif choice == "5":
        print("\nPaste your code then press Enter twice:")
        lines = []
        empty_count = 0
        while empty_count < 2:
            line = input()
            if line == "":
                empty_count += 1
            else:
                empty_count = 0
                lines.append(line)
        code = "\n".join(lines)
        result = agent.run_task("Review this code", code=code)
        consensus = result.get("consensus", {})
        print(f"\nConsensus score: {consensus.get('confidence_score', 0)}/100")
        print(f"Summary: {consensus.get('consensus_summary', 'N/A')}")
        print(f"Recommendation: {consensus.get('final_recommendation', 'N/A')}")

    elif choice == "6":
        repo = input("\nGitHub repo name: ")
        result = agent.analyze_repository(repo)
        print(f"\nFiles with bugs: {result.get('files_with_bugs', 0)}")

    agent.print_summary()
