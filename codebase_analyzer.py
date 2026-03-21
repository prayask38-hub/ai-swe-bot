import os
import json
import hashlib
from pathlib import Path
from groq import Groq
from dotenv import load_dotenv
from typing import Optional

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

SUPPORTED_EXTENSIONS = {
    '.py': 'python', '.js': 'javascript', '.ts': 'typescript',
    '.java': 'java', '.cpp': 'cpp', '.c': 'c', '.go': 'go',
    '.rs': 'rust', '.rb': 'ruby', '.php': 'php', '.cs': 'csharp'
}

IGNORE_DIRS = {
    '.git', '.venv', 'node_modules', '__pycache__', '.idea',
    'venv', 'env', 'dist', 'build', '.next', 'vendor'
}

def scan_codebase(root_path: str, max_files: int = 100):
    print(f"Scanning codebase: {root_path}")
    files = []
    root = Path(root_path)

    for path in root.rglob("*"):
        if any(ignored in path.parts for ignored in IGNORE_DIRS):
            continue
        if path.is_file() and path.suffix in SUPPORTED_EXTENSIONS:
            try:
                size = path.stat().st_size
                if size > 500000:
                    continue
                rel_path = str(path.relative_to(root))
                files.append({
                    "path": rel_path,
                    "full_path": str(path),
                    "language": SUPPORTED_EXTENSIONS[path.suffix],
                    "size": size,
                    "lines": 0
                })
            except:
                continue
        if len(files) >= max_files:
            break

    print(f"Found {len(files)} files")
    return files

def read_file_content(file_info: dict):
    try:
        with open(file_info["full_path"], 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            file_info["lines"] = len(content.split('\n'))
            file_info["content"] = content[:3000]
            file_info["full_content"] = content
            return file_info
    except Exception as e:
        file_info["content"] = ""
        file_info["full_content"] = ""
        return file_info

def extract_dependencies(content: str, language: str):
    dependencies = []
    lines = content.split('\n')

    for line in lines:
        line = line.strip()
        if language == 'python':
            if line.startswith('import ') or line.startswith('from '):
                dependencies.append(line)
        elif language in ['javascript', 'typescript']:
            if 'require(' in line or line.startswith('import '):
                dependencies.append(line)
        elif language == 'java':
            if line.startswith('import '):
                dependencies.append(line)
        elif language == 'go':
            if line.startswith('import ') or '"' in line:
                dependencies.append(line)

    return dependencies[:20]

def extract_functions(content: str, language: str):
    functions = []
    lines = content.split('\n')

    for i, line in enumerate(lines):
        line_stripped = line.strip()
        if language == 'python':
            if line_stripped.startswith('def ') or line_stripped.startswith('class '):
                functions.append({"line": i+1, "signature": line_stripped[:80]})
        elif language in ['javascript', 'typescript']:
            if 'function ' in line_stripped or '=>' in line_stripped or line_stripped.startswith('class '):
                functions.append({"line": i+1, "signature": line_stripped[:80]})
        elif language == 'java':
            if 'public ' in line_stripped or 'private ' in line_stripped or 'protected ' in line_stripped:
                functions.append({"line": i+1, "signature": line_stripped[:80]})
        elif language == 'go':
            if line_stripped.startswith('func '):
                functions.append({"line": i+1, "signature": line_stripped[:80]})

    return functions[:15]

def build_dependency_graph(files: list):
    print("Building dependency graph...")
    graph = {}

    for file_info in files:
        path = file_info["path"]
        content = file_info.get("full_content", "")
        deps = extract_dependencies(content, file_info["language"])
        functions = extract_functions(content, file_info["language"])

        cross_file_deps = []
        for other_file in files:
            if other_file["path"] == path:
                continue
            other_name = Path(other_file["path"]).stem
            if other_name in content and other_name != "__init__":
                cross_file_deps.append(other_file["path"])

        graph[path] = {
            "language": file_info["language"],
            "lines": file_info.get("lines", 0),
            "imports": deps,
            "functions": functions,
            "cross_file_dependencies": cross_file_deps[:10]
        }

    return graph

def analyze_codebase_with_ai(files: list, graph: dict, query: str = "Find all bugs"):
    print(f"Running AI analysis: {query}")

    file_summaries = []
    for f in files[:15]:
        content = f.get("content", "")[:500]
        deps = graph.get(f["path"], {}).get("cross_file_dependencies", [])
        functions = graph.get(f["path"], {}).get("functions", [])
        file_summaries.append({
            "path": f["path"],
            "language": f["language"],
            "lines": f.get("lines", 0),
            "preview": content,
            "depends_on": deps,
            "functions": [fn["signature"] for fn in functions[:5]]
        })

    prompt = f"""You are a senior software engineer analyzing a codebase.

Query: {query}

Codebase structure:
{json.dumps(file_summaries, indent=2)[:4000]}

Dependency graph summary:
- Total files: {len(files)}
- Languages: {list(set(f['language'] for f in files))}
- Cross-file dependencies found: {sum(len(g.get('cross_file_dependencies',[])) for g in graph.values())}

Analyze this codebase and provide:
1. Overall architecture assessment
2. Cross-file dependency issues
3. Bugs that span multiple files
4. Security vulnerabilities
5. Improvement recommendations

Return ONLY a JSON object:
{{
    "architecture": {{
        "pattern": "<mvc, microservices, monolith, etc>",
        "quality": "<poor, fair, good, excellent>",
        "description": "<architecture description>"
    }},
    "cross_file_bugs": [
        {{
            "bug_id": 1,
            "files_involved": ["<file1>", "<file2>"],
            "type": "<bug type>",
            "description": "<what is wrong>",
            "severity": "<critical, high, medium, low>",
            "fix": "<how to fix>"
        }}
    ],
    "security_issues": [
        {{
            "file": "<filename>",
            "type": "<security issue>",
            "severity": "<critical, high, medium, low>",
            "description": "<details>"
        }}
    ],
    "recommendations": ["<rec1>", "<rec2>", "<rec3>"],
    "complexity_score": <0-100>,
    "maintainability_score": <0-100>,
    "summary": "<overall codebase assessment>"
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
        return {"summary": "Analysis complete", "cross_file_bugs": [], "recommendations": []}

def find_cross_file_bugs(files: list, graph: dict):
    print("Finding cross-file bugs...")
    bugs = []

    for path, info in graph.items():
        for dep_path in info.get("cross_file_dependencies", []):
            if dep_path not in graph:
                bugs.append({
                    "type": "MissingDependency",
                    "file": path,
                    "depends_on": dep_path,
                    "severity": "high",
                    "description": f"{path} depends on {dep_path} which may not exist or be importable"
                })

    file_contents = {f["path"]: f.get("full_content", "") for f in files}

    for path, content in file_contents.items():
        if not content:
            continue
        language = graph.get(path, {}).get("language", "python")

        if language == "python":
            lines = content.split('\n')
            for i, line in enumerate(lines):
                if 'from ' in line and ' import ' in line:
                    parts = line.strip().split('from ')
                    if len(parts) > 1:
                        module = parts[1].split(' import ')[0].strip()
                        if module.startswith('.') or not module.startswith(('os', 'sys', 'json', 'datetime', 'typing', 'pathlib', 'groq', 'flask', 'dotenv')):
                            module_file = module.replace('.', '/') + '.py'
                            if not any(module in f["path"] for f in files):
                                bugs.append({
                                    "type": "PotentialImportError",
                                    "file": path,
                                    "line": i + 1,
                                    "severity": "medium",
                                    "description": f"Import '{module}' on line {i+1} — verify module exists"
                                })

    return bugs[:20]

def generate_codebase_report(root_path: str, query: str = "Find all bugs and issues"):
    print("=" * 50)
    print("  CODEBASE ANALYZER")
    print("=" * 50)
    print()

    files = scan_codebase(root_path)
    if not files:
        print("No code files found.")
        return {}

    print("Reading file contents...")
    files = [read_file_content(f) for f in files]

    graph = build_dependency_graph(files)

    print("Finding cross-file bugs...")
    cross_bugs = find_cross_file_bugs(files, graph)

    print("Running AI analysis...")
    ai_analysis = analyze_codebase_with_ai(files, graph, query)

    report = {
        "root_path": root_path,
        "total_files": len(files),
        "languages": list(set(f["language"] for f in files)),
        "total_lines": sum(f.get("lines", 0) for f in files),
        "dependency_graph": graph,
        "cross_file_bugs": cross_bugs,
        "ai_analysis": ai_analysis,
        "timestamp": __import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }

    report_file = "codebase_report.json"
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2)
    print(f"Report saved: {report_file}")

    return report

def print_report(report: dict):
    ai = report.get("ai_analysis", {})
    arch = ai.get("architecture", {})
    cross_bugs = report.get("cross_file_bugs", [])
    ai_bugs = ai.get("cross_file_bugs", [])
    security = ai.get("security_issues", [])

    print("\n" + "=" * 50)
    print("  CODEBASE ANALYSIS REPORT")
    print("=" * 50)
    print(f"\nFiles analyzed:  {report.get('total_files', 0)}")
    print(f"Total lines:     {report.get('total_lines', 0):,}")
    print(f"Languages:       {', '.join(report.get('languages', []))}")
    print(f"\nArchitecture:    {arch.get('pattern', 'unknown').upper()}")
    print(f"Quality:         {arch.get('quality', 'unknown').upper()}")
    print(f"Complexity:      {ai.get('complexity_score', 0)}/100")
    print(f"Maintainability: {ai.get('maintainability_score', 0)}/100")
    print(f"\nSummary: {ai.get('summary', 'N/A')}")

    all_bugs = cross_bugs + ai_bugs
    if all_bugs:
        print(f"\nCross-file bugs: {len(all_bugs)}")
        for bug in all_bugs[:5]:
            print(f"\n  [{bug.get('severity','?').upper()}] {bug.get('type','Bug')}")
            print(f"  File: {bug.get('file', bug.get('files_involved', ['?'])[0] if bug.get('files_involved') else '?')}")
            print(f"  {bug.get('description', '')[:100]}")
            if bug.get('fix'):
                print(f"  Fix: {bug.get('fix', '')[:80]}")

    if security:
        print(f"\nSecurity issues: {len(security)}")
        for issue in security[:3]:
            print(f"  [{issue.get('severity','?').upper()}] {issue.get('type','?')} in {issue.get('file','?')}")

    recs = ai.get("recommendations", [])
    if recs:
        print(f"\nRecommendations:")
        for rec in recs:
            print(f"  - {rec}")

if __name__ == "__main__":
    print("=" * 40)
    print("  Multi-File Codebase Analyzer")
    print("=" * 40)
    print()
    print("1. Analyze this project")
    print("2. Analyze a custom path")
    print()
    choice = input("Choose (1-2): ").strip()

    if choice == "1":
        path = r"c:\Users\praya\OneDrive\Desktop\ai-swe-bot"
        query = input("What to analyze? (default: Find all bugs): ").strip() or "Find all bugs and architectural issues"
        report = generate_codebase_report(path, query)
        print_report(report)

    elif choice == "2":
        path = input("Enter codebase path: ").strip()
        query = input("What to analyze? (default: Find all bugs): ").strip() or "Find all bugs"
        report = generate_codebase_report(path, query)
        print_report(report)
