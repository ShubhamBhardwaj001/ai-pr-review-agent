import os
import json
import traceback
from datetime import datetime, timezone
from github_client import get_github_client
from ai_reviewer import review_code
from utils import is_supported_file


SEVERITY_EMOJI = {
    "critical": "🔴",
    "high": "🟠",
    "medium": "🟡",
    "low": "🔵",
}


def write_failure_context(stage, error, extra=None):
    context = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "stage": stage,
        "error_type": type(error).__name__,
        "error_message": str(error),
        "traceback": traceback.format_exc(),
    }
    if extra:
        context.update(extra)
    with open("rca_context.json", "w") as f:
        json.dump(context, f, indent=2)


def format_review(ai_review_json, filename):
    try:
        data = json.loads(ai_review_json)
    except json.JSONDecodeError:
        # Model didn't return clean JSON — fall back to raw text so nothing is lost
        return f"## Review for `{filename}`\n{ai_review_json}"

    lines = [
        f"## Review for `{filename}`",
        f"**Overall risk:** {data.get('overall_risk', 'unknown')}\n",
    ]

    findings = data.get("findings", [])
    if not findings:
        lines.append("No issues found.")
    else:
        for f in findings:
            emoji = SEVERITY_EMOJI.get(f.get("severity", ""), "⚪")
            severity = f.get("severity", "unknown").upper()
            lines.append(f"- {emoji} **{severity}**: {f.get('issue')}")
            lines.append(f"  - Fix: {f.get('recommendation')}")

    return "\n".join(lines)


def main():
    try:
        github_client = get_github_client()
        repository_name = os.environ["GITHUB_REPOSITORY"]
        pr_number = int(os.environ["PR_NUMBER"])
        repo = github_client.get_repo(repository_name)
        pull_request = repo.get_pull(pr_number)
    except Exception as e:
        write_failure_context("github_setup", e)
        raise

    try:
        files = pull_request.get_files()
    except Exception as e:
        write_failure_context("fetch_pr_files", e, {"pr_number": pr_number})
        raise

    review_comments = []
    for file in files:
        filename = file.filename
        if not is_supported_file(filename):
            continue
        print(f"Reviewing {filename}")
        file_content = file.patch
        try:
            ai_review = review_code(file_content, filename)
        except Exception as e:
            write_failure_context("groq_review", e, {"filename": filename, "pr_number": pr_number})
            raise
        review_comments.append(format_review(ai_review, filename))

    if review_comments:
        try:
            final_comment = "\n\n".join(review_comments)
            pull_request.create_issue_comment(final_comment)
            print("PR comment posted successfully.")
        except Exception as e:
            write_failure_context("post_comment", e, {"pr_number": pr_number})
            raise
    else:
        print("No supported files found.")


if __name__ == "__main__":
    main()
