from groq import Groq
from dotenv import load_dotenv
import os
import json
import subprocess
import tempfile

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def run_code(code: str):
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(code)
        temp_path = f.name
    
    result = subprocess.run(
        ["python", temp_path],
        capture_output=True,
        text=True,
        timeout=10
    )
    
    os.unlink(temp_path)
    
    return {
        "success": result.returncode == 0,
        "output": result.stdout,
        "error": result.stderr
    }

def apply_fix(code: str, bug_line: int, fixed_line: str):
    lines = code.split('\n')
    
    # If fix is multi-line, replace the buggy line with all fix lines
    fix_lines = fixed_line.split('\n')
    
    # Remove the buggy line and insert fix lines in its place
    lines = lines[:bug_line - 1] + fix_lines + lines[bug_line:]
    
    return '\n'.join(lines)

def auto_fix_loop(code: str, bugs: list, solutions_list: list):
    print("Starting auto-fix loop...\n")
    current_code = code

    for i, bug in enumerate(bugs):
        print(f"Fixing Bug #{bug['bug_id']} — {bug['type']} on line {bug['line']}")
        solutions = solutions_list[i]['solutions']
        fixed = False

        for attempt, solution in enumerate(solutions):
            print(f"  Trying Solution {attempt + 1}: {solution['approach']}")
            
            test_code = apply_fix(current_code, bug['line'], solution['fixed_code'])
            result = run_code(test_code)

            if result['success']:
                print(f"  PASSED with Solution {attempt + 1}")
                current_code = test_code
                fixed = True
                break
            else:
                print(f"  FAILED — {result['error'].strip()[:80]}")

        if not fixed:
            print(f"  All solutions failed for Bug #{bug['bug_id']}")
        print()

    print("Final code after all fixes:")
    print("-" * 40)
    print(current_code)
    print("-" * 40)

    final_result = run_code(current_code)
    if final_result['success']:
        print(f"\nFinal output: {final_result['output']}")
        print("CODE IS FULLY FIXED AND WORKING.")
    else:
        print(f"\nSome bugs remain: {final_result['error']}")

    return current_code

# The buggy code
buggy_code = """def calculate_average(numbers):
    total = 0
    for num in numbers:
        total += num
    average = total / len(numbers)
    return average

result = calculate_average([10, 20, 30])
print("Average is: " + result)
"""

# Bugs and solutions from previous steps
bugs = [
    {"bug_id": 1, "line": 7, "type": "NameError", "description": "average should be average", "severity": "high"},
    {"bug_id": 2, "line": 9, "type": "TypeError", "description": "string + float concatenation", "severity": "medium"}
]

solutions_list = [
    {"solutions": [
        {"solution_id": 1, "approach": "Typo Fix", "fixed_code": "    return average"},
        {"solution_id": 2, "approach": "Variable Rename", "fixed_code": "    averge = total / len(numbers)"},
        {"solution_id": 3, "approach": "Output Type Fix", "fixed_code": "    return str(average)"}
    ]},
    {"solutions": [
        {"solution_id": 1, "approach": "str() function", "fixed_code": "print(\"Average is: \" + str(result))"},
        {"solution_id": 2, "approach": "f-string", "fixed_code": "print(f\"Average is: {result}\")"},
        {"solution_id": 3, "approach": "% operator", "fixed_code": "print(\"Average is: %s\" % result)"}
    ]}
]

auto_fix_loop(buggy_code, bugs, solutions_list)
