from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
import os
import json
from bug_detector import detect_bugs
from solution_generator import generate_solutions
from auto_fixer import run_code, apply_fix
from roadmap_generator import generate_roadmap, save_roadmap
from language_detector import detect_language
from storage import init_db, save_session, save_bug, save_successful_fix, print_stats

load_dotenv()
app = Flask(__name__)
init_db()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    data = request.json
    code = data.get('code', '')

    lang_result = detect_language(code)
    language = lang_result['language']

    bugs = detect_bugs(code, language)

    all_solutions = []
    for bug in bugs['bugs']:
        solutions = generate_solutions(code, bug)
        all_solutions.append(solutions)

    return jsonify({
        'language': language,
        'framework': lang_result['framework'],
        'bugs': bugs['bugs'],
        'solutions': all_solutions
    })

@app.route('/fix', methods=['POST'])
def fix():
    data = request.json
    code = data.get('code', '')
    bugs = data.get('bugs', [])
    solutions_list = data.get('solutions', [])
    language = data.get('language', 'python')

    current_code = code
    fixes_applied = []

    for i, bug in enumerate(bugs):
        solutions = solutions_list[i]['solutions']
        for solution in solutions:
            test_code = apply_fix(current_code, bug['line'], solution['fixed_code'])
            result = run_code(test_code)
            if result['success']:
                current_code = test_code
                fixes_applied.append({
                    'bug_id': bug['bug_id'],
                    'solution': solution['approach'],
                    'fixed_line': solution['fixed_code'],
                    'status': 'fixed'
                })
                save_successful_fix(language, bug['type'], solution['fixed_code'], solution['fixed_code'])
                break

    roadmap = generate_roadmap(code, bugs, fixes_applied)
    save_roadmap(roadmap, 'roadmap.md')

    session_id = save_session(
        language=language,
        total_bugs=len(bugs),
        bugs_fixed=len(fixes_applied),
        code_health=roadmap['code_health'],
        original_code=code,
        fixed_code=current_code
    )

    for bug in bugs:
        fix = next((f for f in fixes_applied if f['bug_id'] == bug['bug_id']), None)
        save_bug(session_id, bug['type'], bug['line'], bug['description'], bug['severity'], fix['solution'] if fix else 'unfixed')

    return jsonify({
        'fixed_code': current_code,
        'fixes_applied': fixes_applied,
        'roadmap': roadmap
    })

@app.route('/stats')
def stats():
    from storage import get_all_sessions
    sessions = get_all_sessions()
    return jsonify({
        'sessions': [{'id': s[0], 'date': s[1], 'language': s[2], 'bugs': s[3], 'fixed': s[4], 'health': s[5]} for s in sessions]
    })

if __name__ == '__main__':
    app.run(debug=True)