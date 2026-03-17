import os
import json
import socket
import subprocess
import psutil
from datetime import datetime
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def get_network_info():
    info = {}
    hostname = socket.gethostname()
    info["hostname"] = hostname

    try:
        info["local_ip"] = socket.gethostbyname(hostname)
    except:
        info["local_ip"] = "unknown"

    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        info["active_ip"] = s.getsockname()[0]
        s.close()
    except:
        info["active_ip"] = "unknown"

    interfaces = {}
    for name, addrs in psutil.net_if_addrs().items():
        interfaces[name] = []
        for addr in addrs:
            interfaces[name].append({
                "family": str(addr.family),
                "address": addr.address,
                "netmask": addr.netmask
            })
    info["interfaces"] = interfaces

    stats = psutil.net_io_counters()
    info["bytes_sent"] = stats.bytes_sent
    info["bytes_recv"] = stats.bytes_recv
    info["packets_sent"] = stats.packets_sent
    info["packets_recv"] = stats.packets_recv

    return info

def get_wifi_info():
    try:
        result = subprocess.run(
            ["netsh", "wlan", "show", "interfaces"],
            capture_output=True, text=True
        )
        output = result.stdout

        wifi_info = {}
        for line in output.split("\n"):
            line = line.strip()
            if "SSID" in line and "BSSID" not in line:
                wifi_info["ssid"] = line.split(":")[-1].strip()
            elif "Signal" in line:
                wifi_info["signal"] = line.split(":")[-1].strip()
            elif "Receive rate" in line:
                wifi_info["receive_rate"] = line.split(":")[-1].strip()
            elif "Transmit rate" in line:
                wifi_info["transmit_rate"] = line.split(":")[-1].strip()
            elif "State" in line:
                wifi_info["state"] = line.split(":")[-1].strip()
            elif "Radio type" in line:
                wifi_info["radio_type"] = line.split(":")[-1].strip()

        return wifi_info
    except Exception as e:
        return {"error": str(e)}

def scan_open_ports(host: str = "localhost", ports: list = None):
    if ports is None:
        ports = [80, 443, 8080, 8443, 3000, 5000, 5001, 8765, 3306, 5432, 27017, 6379, 22, 21, 25]

    print(f"Scanning {len(ports)} ports on {host}...")
    open_ports = []
    closed_ports = []

    for port in ports:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(0.5)
            result = sock.connect_ex((host, port))
            if result == 0:
                open_ports.append(port)
            else:
                closed_ports.append(port)
            sock.close()
        except:
            closed_ports.append(port)

    return {
        "host": host,
        "open_ports": open_ports,
        "closed_ports": closed_ports,
        "total_scanned": len(ports)
    }

def check_internet_connection():
    print("Checking internet connection...")
    hosts = [
        ("8.8.8.8", 53, "Google DNS"),
        ("1.1.1.1", 53, "Cloudflare DNS"),
        ("208.67.222.222", 53, "OpenDNS")
    ]

    results = []
    for host, port, name in hosts:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)
            result = sock.connect_ex((host, port))
            connected = result == 0
            sock.close()
            results.append({"host": name, "connected": connected})
            status = "OK" if connected else "FAIL"
            print(f"  {name}: {status}")
        except:
            results.append({"host": name, "connected": False})
            print(f"  {name}: FAIL")

    connected = any(r["connected"] for r in results)
    return {
        "internet_available": connected,
        "results": results,
        "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }

def network_speed_test():
    print("Testing network speed...")
    try:
        import time
        start = time.time()
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        sock.connect(("8.8.8.8", 53))
        latency = (time.time() - start) * 1000
        sock.close()

        stats_before = psutil.net_io_counters()
        import urllib.request
        test_url = "http://speedtest.ftp.otenet.gr/files/test1Mb.db"
        try:
            start = time.time()
            urllib.request.urlretrieve(test_url, os.devnull)
            duration = time.time() - start
            stats_after = psutil.net_io_counters()
            bytes_received = stats_after.bytes_recv - stats_before.bytes_recv
            speed_mbps = round((bytes_received * 8) / (duration * 1000000), 2)
        except:
            speed_mbps = 0

        return {
            "latency_ms": round(latency, 2),
            "download_mbps": speed_mbps,
            "status": "good" if latency < 100 else "slow"
        }
    except Exception as e:
        return {"error": str(e), "latency_ms": 0, "download_mbps": 0}

def ai_network_diagnosis(network_info: dict, wifi_info: dict, port_scan: dict):
    prompt = f"""You are a network security and troubleshooting expert.

Network information:
{json.dumps(network_info, indent=2)[:1000]}

WiFi information:
{json.dumps(wifi_info, indent=2)}

Open ports scan:
{json.dumps(port_scan, indent=2)}

Analyze this network configuration and provide:
1. Security assessment
2. Performance assessment
3. Any issues found
4. Recommendations

Return ONLY a JSON object:
{{
    "security_score": <0-100>,
    "performance_score": <0-100>,
    "issues": [
        {{
            "type": "<security, performance, or configuration>",
            "severity": "<high, medium, or low>",
            "description": "<what is wrong>",
            "fix": "<how to fix>"
        }}
    ],
    "open_port_risks": [
        {{
            "port": <port number>,
            "risk": "<what this port could expose>",
            "recommendation": "<what to do>"
        }}
    ],
    "recommendations": ["<rec1>", "<rec2>", "<rec3>"],
    "summary": "<one sentence overall assessment>"
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

def auto_troubleshoot():
    print("Running automated network troubleshoot...")
    issues = []
    fixes = []

    internet = check_internet_connection()
    if not internet["internet_available"]:
        issues.append("No internet connection")
        fixes.append("Check WiFi connection or restart router")

    wifi = get_wifi_info()
    if "signal" in wifi:
        signal = wifi["signal"].replace("%", "").strip()
        try:
            if int(signal) < 50:
                issues.append(f"Weak WiFi signal: {signal}%")
                fixes.append("Move closer to router or use ethernet")
        except:
            pass

    ports = scan_open_ports()
    risky_ports = [21, 22, 23, 3306, 5432]
    open_risky = [p for p in ports["open_ports"] if p in risky_ports]
    if open_risky:
        issues.append(f"Risky ports open: {open_risky}")
        fixes.append(f"Close or firewall these ports: {open_risky}")

    if not issues:
        print("No network issues found. Everything looks good.")
    else:
        print(f"\nFound {len(issues)} issues:")
        for i, (issue, fix) in enumerate(zip(issues, fixes)):
            print(f"\n  Issue {i+1}: {issue}")
            print(f"  Fix: {fix}")

    return {"issues": issues, "fixes": fixes}

def print_network_report(info: dict, wifi: dict, diagnosis: dict):
    print("\n" + "=" * 50)
    print("  NETWORK MANAGEMENT REPORT")
    print("=" * 50)

    print(f"\nHostname: {info.get('hostname', 'unknown')}")
    print(f"Local IP: {info.get('local_ip', 'unknown')}")
    print(f"Active IP: {info.get('active_ip', 'unknown')}")

    print(f"\nData transferred:")
    sent_mb = round(info.get('bytes_sent', 0) / 1024 / 1024, 2)
    recv_mb = round(info.get('bytes_recv', 0) / 1024 / 1024, 2)
    print(f"  Sent: {sent_mb} MB")
    print(f"  Received: {recv_mb} MB")

    if wifi and "ssid" in wifi:
        print(f"\nWiFi:")
        print(f"  Network: {wifi.get('ssid', 'unknown')}")
        print(f"  Signal: {wifi.get('signal', 'unknown')}")
        print(f"  State: {wifi.get('state', 'unknown')}")

    if diagnosis:
        print(f"\nSecurity Score: {diagnosis.get('security_score', 0)}/100")
        print(f"Performance Score: {diagnosis.get('performance_score', 0)}/100")
        print(f"Summary: {diagnosis.get('summary', 'N/A')}")

        issues = diagnosis.get("issues", [])
        if issues:
            print(f"\nIssues found: {len(issues)}")
            for issue in issues:
                print(f"  [{issue['severity'].upper()}] {issue['type']}")
                print(f"  {issue['description']}")
                print(f"  Fix: {issue['fix']}")

        recs = diagnosis.get("recommendations", [])
        if recs:
            print(f"\nRecommendations:")
            for rec in recs:
                print(f"  - {rec}")

if __name__ == "__main__":
    print("=" * 40)
    print("  Network Manager")
    print("=" * 40)
    print()
    print("1. Full network report")
    print("2. Check internet connection")
    print("3. Scan open ports")
    print("4. WiFi information")
    print("5. Auto troubleshoot")
    print("6. Network speed test")
    print()
    choice = input("Choose (1-6): ").strip()

    if choice == "1":
        print("\nGathering network information...")
        info = get_network_info()
        wifi = get_wifi_info()
        ports = scan_open_ports()
        print("\nRunning AI diagnosis...")
        diagnosis = ai_network_diagnosis(info, wifi, ports)
        print_network_report(info, wifi, diagnosis)

    elif choice == "2":
        result = check_internet_connection()
        print(f"\nInternet: {'CONNECTED' if result['internet_available'] else 'DISCONNECTED'}")

    elif choice == "3":
        result = scan_open_ports()
        print(f"\nOpen ports: {result['open_ports']}")
        print(f"Closed ports: {len(result['closed_ports'])} ports closed")

    elif choice == "4":
        wifi = get_wifi_info()
        print("\nWiFi Information:")
        for key, value in wifi.items():
            print(f"  {key}: {value}")

    elif choice == "5":
        auto_troubleshoot()

    elif choice == "6":
        result = network_speed_test()
        print(f"\nLatency: {result.get('latency_ms', 0)} ms")
        print(f"Download: {result.get('download_mbps', 0)} Mbps")
        print(f"Status: {result.get('status', 'unknown')}")
