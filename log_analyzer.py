import os
import json
import re
from datetime import datetime
from groq import Groq
from dotenv import load_dotenv

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

LOG_PATTERNS = {
    "python_traceback": r"Traceback \(most recent call last\):",
    "python_error": r"(TypeError|ValueError|AttributeError|NameError|ImportError|KeyError|IndexError|RuntimeError|Exception):",
    "java_exception": r"(Exception|Error) in thread",
    "javascript_error": r"(TypeError|ReferenceError|SyntaxError|RangeError):",
    "http_error": r"HTTP/\d\.\d [45]\d\d",
    "database_error": r"(SQL|Database|Connection|Query) (Error|Exception|Failed)",
    "memory_error": r"(OutOfMemoryError|MemoryError|heap space)",
    "timeout": r"(TimeoutError|Connection timed out|Request timeout)",
    "null_pointer": r"(NullPointerException|NoneType|null pointer)",
    "permission": r"(PermissionError|Access denied|Permission denied)",
    "segfault": r"(Segmentation fault|SIGSEGV|core dumped)"
}

def parse_log_file(log_path: str):
    print(f"Reading log file: {log_path}")
    try:
        with open(log_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        lines = content.split('\n')
        print(f"Log lines: {len(lines):,}")
        return content, lines
    except Exception as e:
        print(f"Could not read log: {e}")
        return "", []

def parse_log_text(log_text: str):
    lines = log_text.split('\n')
    return log_text, lines

def detect_errors(content: str, lines: list):
    errors = []
    for i, line in enumerate(lines):
        for error_type, pattern in LOG_PATTERNS.items():
            if re.search(pattern, line, re.IGNORECASE):
                context_start = max(0, i - 3)
                context_end = min(len(lines), i + 8)
                context = '\n'.join(lines[context_start:context_end])
                errors.append({
                    "line_number": i + 1,
                    "type": error_type,
                    "line": line.strip(),
                    "context": context,
                    "timestamp": extract_timestamp(line)
                })
                break
    unique_errors = []
    seen = set()
    for err in errors:
        key = err["type"] + err["line"][:50]
        if key not in seen:
            seen.add(key)
            unique_errors.append(err)
    print(f"Detected {len(unique_errors)} unique errors")
    return unique_errors[:20]

def extract_timestamp(line: str):
    patterns = [
        r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}',
        r'\d{2}/\d{2}/\d{4} \d{2}:\d{2}:\d{2}',
        r'\w{3} \d{2} \d{2}:\d{2}:\d{2}',
        r'\d{2}:\d{2}:\d{2}'
    ]
    for pattern in patterns:
        match = re.search(pattern, line)
        if match:
            return match.group()
    return "unknown"

def extract_stack_trace(content: str):
    traces = []
    lines = content.split('\n')
    in_trace = False
    current_trace = []

    for line in lines:
        if 'Traceback (most recent call last):' in line or 'Exception in thread' in line:
            if current_trace:
                traces.append('\n'.join(current_trace))
            current_trace = [line]
            in_trace = True
        elif in_trace:
            current_trace.append(line)
            if re.match(r'\w+Error:|^\w+Exception:', line.strip()):
                traces.append('\n'.join(current_trace))
                current_trace = []
                in_trace = False
        if len(traces) >= 5:
            break

    if current_trace:
        traces.append('\n'.join(current_trace))

    return traces[:5]

def analyze_logs_with_ai(log_content: str, errors: list, stack_traces: list):
    print("Running AI log analysis...")

    error_summary = json.dumps([{
        "type": e["type"],
        "line": e["line"][:100],
        "context": e["context"][:200]
    } for e in errors[:10]], indent=2)

    traces_text = '\n\n'.join(stack_traces[:3]) if stack_traces else "No stack traces found"

    prompt = f"""You are a senior site reliability engineer debugging a production system.

Log errors detected:
{error_summary}

Stack traces:
{traces_text[:2000]}

Log sample:
{log_content[:1500]}

Analyze these logs and provide a complete root cause analysis.

Return ONLY a JSON object:
{{
    "root_cause": "<the main cause of the failure>",
    "severity": "<critical, high, medium, or low>",
    "affected_component": "<which part of the system failed>",
    "error_chain": ["<first thing that went wrong>", "<then this happened>", "<which caused this>"],
    "bugs": [
        {{
            "type": "<error type>",
            "description": "<what exactly went wrong>",
            "likely_file": "<which file probably caused this>",
            "likely_line": "<approximate line number or function>",
            "fix": "<exactly how to fix this>"
        }}
    ],
    "immediate_actions": ["<do this right now>", "<then this>"],
    "prevention": ["<how to prevent this in future>"],
    "estimated_downtime": "<how long this issue may have caused downtime>",
    "summary": "<one paragraph explaining what happened>"
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
            "root_cause": "Could not parse AI response",
            "severity": "unknown",
            "bugs": [],
            "immediate_actions": [],
            "summary": "Log analysis complete"
        }

def generate_fix_patch(bug: dict, codebase_path: str = None):
    prompt = f"""You are a senior engineer. Generate an exact code fix for this production bug.

Bug type: {bug.get('type', '')}
Description: {bug.get('description', '')}
Likely file: {bug.get('likely_file', '')}
Likely location: {bug.get('likely_line', '')}
Suggested fix: {bug.get('fix', '')}

Generate the exact code patch needed.

Return ONLY a JSON object:
{{
    "patch_description": "<what this patch does>",
    "before_code": "<the buggy code>",
    "after_code": "<the fixed code>",
    "explanation": "<why this fix works>",
    "test_case": "<a test to verify the fix works>"
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

def analyze_log(log_input: str, is_file: bool = False):
    print("=" * 50)
    print("  PRODUCTION LOG ANALYZER")
    print("=" * 50)
    print()

    if is_file:
        content, lines = parse_log_file(log_input)
    else:
        content, lines = parse_log_text(log_input)

    if not content:
        print("No log content found.")
        return {}

    errors = detect_errors(content, lines)
    stack_traces = extract_stack_trace(content)

    print(f"Stack traces found: {len(stack_traces)}")

    analysis = analyze_logs_with_ai(content, errors, stack_traces)

    report = {
        "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        "total_errors": len(errors),
        "stack_traces": len(stack_traces),
        "errors": errors,
        "analysis": analysis
    }

    report_file = f"log_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2)
    print(f"Report saved: {report_file}")

    return report

def print_analysis(report: dict):
    analysis = report.get("analysis", {})

    print("\n" + "=" * 50)
    print("  ROOT CAUSE ANALYSIS")
    print("=" * 50)
    print(f"\nSeverity:          {analysis.get('severity', 'unknown').upper()}")
    print(f"Affected component: {analysis.get('affected_component', 'unknown')}")
    print(f"Root cause:        {analysis.get('root_cause', 'unknown')}")
    print(f"Est. downtime:     {analysis.get('estimated_downtime', 'unknown')}")

    chain = analysis.get("error_chain", [])
    if chain:
        print(f"\nError chain:")
        for i, step in enumerate(chain):
            print(f"  {i+1}. {step}")

    bugs = analysis.get("bugs", [])
    if bugs:
        print(f"\nBugs identified: {len(bugs)}")
        for bug in bugs:
            print(f"\n  [{bug.get('type','?')}]")
            print(f"  File: {bug.get('likely_file', 'unknown')}")
            print(f"  Location: {bug.get('likely_line', 'unknown')}")
            print(f"  Problem: {bug.get('description', '')[:100]}")
            print(f"  Fix: {bug.get('fix', '')[:100]}")

    actions = analysis.get("immediate_actions", [])
    if actions:
        print(f"\nImmediate actions:")
        for action in actions:
            print(f"  → {action}")

    prevention = analysis.get("prevention", [])
    if prevention:
        print(f"\nPrevention:")
        for p in prevention:
            print(f"  - {p}")

    print(f"\nSummary:")
    print(f"  {analysis.get('summary', 'N/A')}")

if __name__ == "__main__":
    print("=" * 40)
    print("  Production Log Analyzer")
    print("=" * 40)
    print()
    print("1. Analyze a log file")
    print("2. Paste log text directly")
    print("3. Analyze sample crash log")
    print()
    choice = input("Choose (1-3): ").strip()

    if choice == "1":
        path = input("Log file path: ").strip()
        report = analyze_log(path, is_file=True)
        print_analysis(report)

    elif choice == "2":
        print("Paste your log (press Enter twice when done):")
        lines = []
        empty_count = 0
        while empty_count < 2:
            line = input()
            if line == "":
                empty_count += 1
            else:
                empty_count = 0
                lines.append(line)
        log_text = "\n".join(lines)
        report = analyze_log(log_text)
        print_analysis(report)

    elif choice == "3":
        sample_log = """
2026-03-21 09:15:23 ERROR Starting request processing
2026-03-21 09:15:24 INFO Processing user request id=4821
2026-03-21 09:15:24 ERROR Database connection failed: Connection refused
2026-03-21 09:15:24 ERROR Traceback (most recent call last):
  File "/app/api/handlers.py", line 142, in process_request
    result = db.execute(query, params)
  File "/app/db/connection.py", line 67, in execute
    cursor = self.connection.cursor()
AttributeError: 'NoneType' object has no attribute 'cursor'
2026-03-21 09:15:25 CRITICAL Service health check failed
2026-03-21 09:15:25 ERROR HTTP/1.1 500 Internal Server Error
2026-03-21 09:15:26 ERROR NullPointerException in UserService.getUser()
2026-03-21 09:15:27 ERROR Memory usage: 94% - approaching limit
2026-03-21 09:15:28 ERROR TimeoutError: Request timeout after 30s
2026-03-21 09:15:29 CRITICAL System entering degraded state
"""
        report = analyze_log(sample_log)
        print_analysis(report)
