import os
import json
import requests
from datetime import datetime
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

class GitHubAPI:
    def __init__(self):
        self.token = os.getenv("GITHUB_TOKEN")
        self.headers = {
            "Authorization": f"token {self.token}",
            "Accept": "application/vnd.github.v3+json"
        }
        self.base_url = "https://api.github.com"

    def get_repos(self):
        response = requests.get(f"{self.base_url}/user/repos", headers=self.headers)
        if response.status_code == 200:
            repos = response.json()
            return [{"name": r["name"], "url": r["html_url"], "language": r["language"]} for r in repos]
        return []

    def create_issue(self, repo: str, title: str, body: str):
        username = self.get_username()
        url = f"{self.base_url}/repos/{username}/{repo}/issues"
        data = {"title": title, "body": body}
        response = requests.post(url, headers=self.headers, json=data)
        if response.status_code == 201:
            issue = response.json()
            print(f"Issue created: {issue['html_url']}")
            return issue
        return None

    def get_username(self):
        response = requests.get(f"{self.base_url}/user", headers=self.headers)
        if response.status_code == 200:
            return response.json()["login"]
        return None

    def get_commits(self, repo: str, limit: int = 5):
        username = self.get_username()
        url = f"{self.base_url}/repos/{username}/{repo}/commits"
        response = requests.get(url, headers=self.headers, params={"per_page": limit})
        if response.status_code == 200:
            commits = response.json()
            return [{"sha": c["sha"][:7], "message": c["commit"]["message"], "date": c["commit"]["author"]["date"]} for c in commits]
        return []

    def create_pull_request(self, repo: str, title: str, body: str, head: str, base: str = "main"):
        username = self.get_username()
        url = f"{self.base_url}/repos/{username}/{repo}/pulls"
        data = {"title": title, "body": body, "head": head, "base": base}
        response = requests.post(url, headers=self.headers, json=data)
        if response.status_code == 201:
            pr = response.json()
            print(f"PR created: {pr['html_url']}")
            return pr
        return None

class SlackAPI:
    def __init__(self):
        self.token = os.getenv("SLACK_TOKEN")
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }

    def send_message(self, channel: str, message: str):
        if not self.token:
            print("No Slack token — skipping")
            return None
        url = "https://slack.com/api/chat.postMessage"
        data = {"channel": channel, "text": message}
        response = requests.post(url, headers=self.headers, json=data)
        if response.status_code == 200:
            print(f"Slack message sent to {channel}")
            return response.json()
        return None

    def send_bug_report(self, channel: str, bug: dict, file_path: str):
        message = f"""*AI SWE Bot — Bug Report*
        
*File:* {file_path}
*Type:* {bug.get('type', 'Unknown')}
*Severity:* {bug.get('severity', 'Unknown').upper()}
*Line:* {bug.get('line', 'Unknown')}

*Description:* {bug.get('description', 'No description')}

_Auto-detected by AI SWE Bot at {datetime.now().strftime('%Y-%m-%d %H:%M')}_"""

        return self.send_message(channel, message)

class NotionAPI:
    def __init__(self):
        self.token = os.getenv("NOTION_TOKEN")
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
            "Notion-Version": "2022-06-28"
        }

    def create_page(self, database_id: str, title: str, content: str):
        if not self.token:
            print("No Notion token — skipping")
            return None
        url = "https://api.notion.com/v1/pages"
        data = {
            "parent": {"database_id": database_id},
            "properties": {
                "Name": {
                    "title": [{"text": {"content": title}}]
                }
            },
            "children": [
                {
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {
                        "rich_text": [{"type": "text", "text": {"content": content}}]
                    }
                }
            ]
        }
        response = requests.post(url, headers=self.headers, json=data)
        if response.status_code == 200:
            print(f"Notion page created")
            return response.json()
        return None

class AWSAPI:
    def __init__(self):
        self.access_key = os.getenv("AWS_ACCESS_KEY")
        self.secret_key = os.getenv("AWS_SECRET_KEY")
        self.region = os.getenv("AWS_REGION", "us-east-1")

    def test_connection(self):
        if not self.access_key:
            print("No AWS credentials — skipping")
            return False
        try:
            import boto3
            session = boto3.Session(
                aws_access_key_id=self.access_key,
                aws_secret_access_key=self.secret_key,
                region_name=self.region
            )
            sts = session.client('sts')
            identity = sts.get_caller_identity()
            print(f"AWS connected: {identity['Account']}")
            return True
        except Exception as e:
            print(f"AWS error: {e}")
            return False

def ai_decide_action(task: str, available_services: list):
    prompt = f"""You are an AI assistant managing integrations.

Task: {task}
Available services: {', '.join(available_services)}

Decide which service to use and what action to take.

Return ONLY a JSON object:
{{
    "service": "<github, slack, notion, aws, or none>",
    "action": "<specific action to take>",
    "parameters": {{
        "<param1>": "<value1>",
        "<param2>": "<value2>"
    }},
    "reason": "<why this service and action>"
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
        return None

def run_integration_hub(task: str):
    print(f"\nTask: {task}")
    print("=" * 40)

    github = GitHubAPI()
    slack = SlackAPI()
    notion = NotionAPI()
    aws = AWSAPI()

    available = []
    if github.token:
        available.append("github")
    if slack.token:
        available.append("slack")
    if notion.token:
        available.append("notion")
    if aws.access_key:
        available.append("aws")

    print(f"Available services: {available}")

    decision = ai_decide_action(task, available)
    if not decision:
        print("Could not decide action.")
        return

    print(f"\nAI decided: use {decision['service']} — {decision['action']}")
    print(f"Reason: {decision['reason']}")

    service = decision["service"]
    params = decision.get("parameters", {})

    if service == "github":
        action = decision["action"]
        if "issue" in action.lower():
            repo = params.get("repo", "ai-swe-bot")
            title = params.get("title", task)
            body = params.get("body", f"Auto-created by AI SWE Bot\n\nTask: {task}")
            github.create_issue(repo, title, body)
        elif "commit" in action.lower() or "repo" in action.lower():
            repos = github.get_repos()
            print(f"Your repos: {[r['name'] for r in repos]}")

    elif service == "slack":
        channel = params.get("channel", "#general")
        message = params.get("message", f"AI SWE Bot update: {task}")
        slack.send_message(channel, message)

    elif service == "notion":
        database_id = params.get("database_id", "")
        title = params.get("title", task)
        content = params.get("content", f"Created by AI SWE Bot: {task}")
        notion.create_page(database_id, title, content)

    elif service == "aws":
        aws.test_connection()

    else:
        print("No matching service found for this task.")

if __name__ == "__main__":
    print("=" * 40)
    print("  API Integration Hub")
    print("=" * 40)
    print()
    print("Services supported:")
    print("  GitHub — repos, issues, PRs, commits")
    print("  Slack  — messages, bug reports")
    print("  Notion — pages, databases")
    print("  AWS    — cloud services")
    print()
    print("Add tokens to .env file:")
    print("  GITHUB_TOKEN=...")
    print("  SLACK_TOKEN=...")
    print("  NOTION_TOKEN=...")
    print("  AWS_ACCESS_KEY=...")
    print("  AWS_SECRET_KEY=...")
    print()

    github = GitHubAPI()
    if github.token:
        print("Testing GitHub connection...")
        repos = github.get_repos()
        print(f"Connected — {len(repos)} repos found")
        if repos:
            print(f"Repos: {[r['name'] for r in repos]}")

        print("\nTesting commit history...")
        commits = github.get_commits("ai-swe-bot", limit=3)
        if commits:
            print("Recent commits:")
            for c in commits:
                print(f"  {c['sha']} — {c['message'][:50]}")
        else:
            print("No commits found or repo not found.")
    else:
        print("No GitHub token found in .env")

    print("\nAPI Integration Hub ready.")
    print("Add more service tokens to .env to enable them.")
