import os
import json
import sqlite3
import psutil
import time
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

DB_PATH = "ai_swe_bot.db"

def get_system_metrics():
    cpu = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage('/')

    return {
        "cpu_percent": cpu,
        "memory_percent": memory.percent,
        "memory_used_gb": round(memory.used / 1024**3, 2),
        "memory_total_gb": round(memory.total / 1024**3, 2),
        "disk_percent": disk.percent,
        "disk_used_gb": round(disk.used / 1024**3, 2),
        "disk_total_gb": round(disk.total / 1024**3, 2),
        "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }

def get_bot_stats():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM sessions")
    total_sessions = cursor.fetchone()[0]

    cursor.execute("SELECT SUM(total_bugs) FROM sessions")
    total_bugs = cursor.fetchone()[0] or 0

    cursor.execute("SELECT SUM(bugs_fixed) FROM sessions")
    total_fixed = cursor.fetchone()[0] or 0

    cursor.execute("SELECT COUNT(*) FROM learned_fixes")
    learned_fixes = cursor.fetchone()[0]

    cursor.execute("""
        SELECT language, COUNT(*) as count
        FROM sessions
        GROUP BY language
        ORDER BY count DESC
    """)
    language_stats = cursor.fetchall()

    cursor.execute("""
        SELECT code_health, COUNT(*) as count
        FROM sessions
        GROUP BY code_health
        ORDER BY count DESC
    """)
    health_stats = cursor.fetchall()

    cursor.execute("""
        SELECT date, total_bugs, bugs_fixed, language
        FROM sessions
        ORDER BY id DESC
        LIMIT 10
    """)
    recent_sessions = cursor.fetchall()

    conn.close()

    fix_rate = round((total_fixed / total_bugs * 100), 1) if total_bugs > 0 else 0

    return {
        "total_sessions": total_sessions,
        "total_bugs_found": total_bugs,
        "total_bugs_fixed": total_fixed,
        "fix_rate": fix_rate,
        "learned_fixes": learned_fixes,
        "language_stats": [{"language": r[0], "count": r[1]} for r in language_stats],
        "health_stats": [{"health": r[0], "count": r[1]} for r in health_stats],
        "recent_sessions": [
            {
                "date": r[0],
                "bugs_found": r[1],
                "bugs_fixed": r[2],
                "language": r[3]
            } for r in recent_sessions
        ]
    }

def get_error_patterns():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT bug_type, COUNT(*) as count
        FROM bugs
        GROUP BY bug_type
        ORDER BY count DESC
        LIMIT 10
    """)
    patterns = cursor.fetchall()
    conn.close()

    return [{"type": p[0], "count": p[1]} for p in patterns]

def generate_html_dashboard():
    system = get_system_metrics()
    bot = get_bot_stats()
    patterns = get_error_patterns()

    recent_html = ""
    for s in bot["recent_sessions"]:
        recent_html += f"""
        <tr>
            <td>{s['date']}</td>
            <td>{s['language'].upper()}</td>
            <td>{s['bugs_found']}</td>
            <td>{s['bugs_fixed']}</td>
            <td>{"100%" if s['bugs_found'] == s['bugs_fixed'] else f"{round(s['bugs_fixed']/s['bugs_found']*100)}%" if s['bugs_found'] > 0 else "0%"}</td>
        </tr>"""

    language_html = ""
    colors = ["#6366f1", "#8b5cf6", "#06b6d4", "#10b981", "#f59e0b"]
    for i, lang in enumerate(bot["language_stats"]):
        color = colors[i % len(colors)]
        language_html += f'<div class="lang-bar"><span>{lang["language"].upper()}</span><div class="bar"><div class="bar-fill" style="width:{min(100, lang["count"]*20)}%;background:{color}"></div></div><span>{lang["count"]}</span></div>'

    pattern_html = ""
    for p in patterns[:5]:
        pattern_html += f'<div class="pattern-item"><span class="pattern-type">{p["type"]}</span><span class="pattern-count">{p["count"]}x</span></div>'

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta http-equiv="refresh" content="30">
<title>AI SWE Bot — Dashboard</title>
<style>
*{{box-sizing:border-box;margin:0;padding:0}}
body{{font-family:monospace;background:#0d0d0d;color:#e0e0e0;min-height:100vh}}
.header{{padding:20px 30px;border-bottom:1px solid #222;display:flex;align-items:center;gap:12px}}
.header h1{{font-size:18px;color:#fff}}
.dot{{width:8px;height:8px;border-radius:50%;background:#00ff88;animation:pulse 2s infinite}}
@keyframes pulse{{0%,100%{{opacity:1}}50%{{opacity:.3}}}}
.updated{{font-size:11px;color:#444;margin-left:auto}}
.grid{{display:grid;grid-template-columns:repeat(4,1fr);gap:16px;padding:20px}}
.grid2{{display:grid;grid-template-columns:1fr 1fr;gap:16px;padding:0 20px 20px}}
.grid3{{display:grid;grid-template-columns:1fr 1fr 1fr;gap:16px;padding:0 20px 20px}}
.card{{background:#111;border:1px solid #222;border-radius:8px;padding:16px}}
.card-title{{font-size:11px;color:#555;text-transform:uppercase;letter-spacing:.1em;margin-bottom:8px}}
.metric{{font-size:32px;font-weight:bold;color:#fff}}
.metric-sub{{font-size:12px;color:#555;margin-top:4px}}
.metric-green{{color:#00ff88}}
.metric-yellow{{color:#ffaa00}}
.metric-red{{color:#ff4444}}
.progress{{height:4px;background:#222;border-radius:2px;margin-top:8px;overflow:hidden}}
.progress-fill{{height:100%;border-radius:2px;transition:width .3s}}
.lang-bar{{display:flex;align-items:center;gap:8px;margin-bottom:8px;font-size:12px}}
.bar{{flex:1;height:6px;background:#222;border-radius:3px;overflow:hidden}}
.bar-fill{{height:100%;border-radius:3px}}
.pattern-item{{display:flex;justify-content:space-between;padding:6px 0;border-bottom:1px solid #1a1a1a;font-size:12px}}
.pattern-type{{color:#aaa}}
.pattern-count{{color:#00ff88;font-weight:bold}}
table{{width:100%;border-collapse:collapse;font-size:12px}}
th{{text-align:left;color:#555;font-weight:normal;padding:6px 0;border-bottom:1px solid #222}}
td{{padding:6px 0;border-bottom:1px solid #1a1a1a;color:#aaa}}
td:first-child{{color:#fff}}
.section-title{{font-size:13px;font-weight:bold;margin-bottom:12px;color:#fff}}
</style>
</head>
<body>
<div class="header">
  <div class="dot"></div>
  <h1>AI SWE Bot — Performance Dashboard</h1>
  <span class="updated">Auto-refreshes every 30s | Last updated: {system['timestamp']}</span>
</div>

<div class="grid">
  <div class="card">
    <div class="card-title">Total sessions</div>
    <div class="metric metric-green">{bot['total_sessions']}</div>
    <div class="metric-sub">debugging sessions run</div>
  </div>
  <div class="card">
    <div class="card-title">Bugs found</div>
    <div class="metric metric-yellow">{bot['total_bugs_found']}</div>
    <div class="metric-sub">across all sessions</div>
  </div>
  <div class="card">
    <div class="card-title">Bugs fixed</div>
    <div class="metric metric-green">{bot['total_bugs_fixed']}</div>
    <div class="metric-sub">auto-fixed by bot</div>
  </div>
  <div class="card">
    <div class="card-title">Fix rate</div>
    <div class="metric {'metric-green' if bot['fix_rate'] >= 80 else 'metric-yellow'}">{bot['fix_rate']}%</div>
    <div class="progress"><div class="progress-fill" style="width:{bot['fix_rate']}%;background:#00ff88"></div></div>
  </div>
</div>

<div class="grid">
  <div class="card">
    <div class="card-title">CPU usage</div>
    <div class="metric {'metric-green' if system['cpu_percent'] < 50 else 'metric-yellow' if system['cpu_percent'] < 80 else 'metric-red'}">{system['cpu_percent']}%</div>
    <div class="progress"><div class="progress-fill" style="width:{system['cpu_percent']}%;background:{'#00ff88' if system['cpu_percent'] < 50 else '#ffaa00' if system['cpu_percent'] < 80 else '#ff4444'}"></div></div>
  </div>
  <div class="card">
    <div class="card-title">Memory usage</div>
    <div class="metric {'metric-green' if system['memory_percent'] < 60 else 'metric-yellow' if system['memory_percent'] < 80 else 'metric-red'}">{system['memory_percent']}%</div>
    <div class="metric-sub">{system['memory_used_gb']} GB / {system['memory_total_gb']} GB</div>
    <div class="progress"><div class="progress-fill" style="width:{system['memory_percent']}%;background:{'#00ff88' if system['memory_percent'] < 60 else '#ffaa00'}"></div></div>
  </div>
  <div class="card">
    <div class="card-title">Disk usage</div>
    <div class="metric metric-yellow">{system['disk_percent']}%</div>
    <div class="metric-sub">{system['disk_used_gb']} GB / {system['disk_total_gb']} GB</div>
    <div class="progress"><div class="progress-fill" style="width:{system['disk_percent']}%;background:#ffaa00"></div></div>
  </div>
  <div class="card">
    <div class="card-title">Learned fixes</div>
    <div class="metric metric-green">{bot['learned_fixes']}</div>
    <div class="metric-sub">patterns in memory</div>
  </div>
</div>

<div class="grid2">
  <div class="card">
    <div class="section-title">Languages used</div>
    {language_html if language_html else '<div style="color:#444;font-size:12px">No sessions yet</div>'}
  </div>
  <div class="card">
    <div class="section-title">Top error patterns</div>
    {pattern_html if pattern_html else '<div style="color:#444;font-size:12px">No patterns yet</div>'}
  </div>
</div>

<div style="padding:0 20px 20px">
  <div class="card">
    <div class="section-title">Recent sessions</div>
    <table>
      <tr>
        <th>Date</th>
        <th>Language</th>
        <th>Bugs found</th>
        <th>Bugs fixed</th>
        <th>Fix rate</th>
      </tr>
      {recent_html if recent_html else '<tr><td colspan="5" style="color:#444">No sessions yet</td></tr>'}
    </table>
  </div>
</div>

</body>
</html>"""

    with open("dashboard.html", "w", encoding="utf-8") as f:
        f.write(html)

    print("Dashboard saved to dashboard.html")
    return "dashboard.html"

def open_dashboard():
    import subprocess
    filepath = generate_html_dashboard()
    subprocess.Popen(["cmd", "/c", "start", filepath])
    print("Dashboard opened in browser.")
    print("It auto-refreshes every 30 seconds.")

def print_terminal_dashboard():
    system = get_system_metrics()
    bot = get_bot_stats()

    print("\n" + "=" * 50)
    print("  AI SWE BOT — LIVE DASHBOARD")
    print("=" * 50)
    print(f"\n  Updated: {system['timestamp']}")
    print(f"\n  SYSTEM")
    print(f"  CPU:     {system['cpu_percent']}%")
    print(f"  Memory:  {system['memory_percent']}% ({system['memory_used_gb']}GB / {system['memory_total_gb']}GB)")
    print(f"  Disk:    {system['disk_percent']}%")
    print(f"\n  BOT PERFORMANCE")
    print(f"  Sessions:     {bot['total_sessions']}")
    print(f"  Bugs found:   {bot['total_bugs_found']}")
    print(f"  Bugs fixed:   {bot['total_bugs_fixed']}")
    print(f"  Fix rate:     {bot['fix_rate']}%")
    print(f"  Learned fixes:{bot['learned_fixes']}")
    if bot['language_stats']:
        print(f"\n  TOP LANGUAGES")
        for lang in bot['language_stats'][:3]:
            print(f"  {lang['language'].upper()}: {lang['count']} sessions")
    print("\n" + "=" * 50)

if __name__ == "__main__":
    print("=" * 40)
    print("  Performance Dashboard")
    print("=" * 40)
    print()
    print("1. Open web dashboard in browser")
    print("2. Print terminal dashboard")
    print("3. Live terminal monitoring")
    print()
    choice = input("Choose (1-3): ").strip()

    if choice == "1":
        open_dashboard()

    elif choice == "2":
        print_terminal_dashboard()

    elif choice == "3":
        print("Live monitoring — press Ctrl+C to stop")
        try:
            while True:
                print_terminal_dashboard()
                time.sleep(5)
        except KeyboardInterrupt:
            print("\nMonitoring stopped.")
