import os
import json
import requests
from datetime import datetime, timezone
from github import Github

GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"


def load_failure_context():
    if os.path.exists("rca_context.json"):
        with open("rca_context.json") as f:
            return json.load(f)
    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "stage": "unknown",
        "error_type": "Unknown",
        "error_message": "No detailed context captured — check the workflow run logs directly.",
        "traceback": "N/A",
    }


def generate_rca_text(context, run_url):
    api_key = os.environ["GROQ_API_KEY"]
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    prompt = f"""
You are a senior DevOps engineer writing a Root Cause Analysis (RCA) for your team.

Failure details:
- Stage: {context.get('stage')}
- Error type: {context.get('error_type')}
- Error message: {context.get('error_message')}
- Traceback:
{context.get('traceback')}
- Workflow run: {run_url}

Write the RCA in Markdown with exactly these sections:
## Incident Summary
## Root Cause
## Impact
## Resolution Steps
## Preventive Actions

Be concise and actionable. Do not invent facts beyond what's given above.
"""
    payload = {
        "model": "openai/gpt-oss-20b",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.2,
    }
    response = requests.post(GROQ_API_URL, headers=headers, json=payload, timeout=30)

    if response.status_code != 200:
        return (
            f"## Incident Summary\nAI PR Review failed, and RCA generation via Groq "
            f"also failed ({response.status_code}: {response.text}).\n\n"
            f"## Root Cause\n{context.get('error_message')}\n\n"
            f"## Resolution Steps\nCheck the workflow logs: {run_url}"
        )

    result = response.json()
    return result["choices"][0]["message"]["content"]


def create_rca_issue(rca_body, context, run_url):
    token = os.environ["GITHUB_TOKEN"]
    repo_name = os.environ["GITHUB_REPOSITORY"]
    pr_number = os.environ.get("PR_NUMBER", "N/A")

    client = Github(token)
    repo = client.get_repo(repo_name)

    title = f"RCA: AI PR Review failed (stage: {context.get('stage')}) — PR #{pr_number}"
    body = f"""{rca_body}

---
**Workflow run:** {run_url}
**Failed stage:** {context.get('stage')}
**PR:** #{pr_number}
**Detected at:** {context.get('timestamp')}
"""
    try:
        issue = repo.create_issue(title=title, body=body, labels=["rca", "automated"])
    except Exception:
        # Falls back if the "rca"/"automated" labels don't exist yet in the repo
        issue = repo.create_issue(title=title, body=body)

    print(f"RCA issue created: {issue.html_url}")


def main():
    context = load_failure_context()
    server_url = os.environ.get("GITHUB_SERVER_URL", "https://github.com")
    repo_name = os.environ["GITHUB_REPOSITORY"]
    run_id = os.environ["RUN_ID"]
    run_url = f"{server_url}/{repo_name}/actions/runs/{run_id}"

    rca_body = generate_rca_text(context, run_url)
    create_rca_issue(rca_body, context, run_url)


if __name__ == "__main__":
    main()
