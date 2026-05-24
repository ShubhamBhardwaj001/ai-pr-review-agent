import os

from github_client import get_github_client
from ai_reviewer import review_code
from utils import is_supported_file


def main():

    github_client = get_github_client()

    repository_name = os.environ["GITHUB_REPOSITORY"]

    pr_number = int(os.environ["PR_NUMBER"])

    repo = github_client.get_repo(repository_name)

    pull_request = repo.get_pull(pr_number)

    files = pull_request.get_files()

    review_comments = []

    for file in files:

        filename = file.filename

        if not is_supported_file(filename):
            continue

        print(f"Reviewing {filename}")

        file_content = file.patch

        ai_review = review_code(
            file_content,
            filename
        )

        review_comments.append(
            f"## Review for {filename}\n{ai_review}"
        )

    if review_comments:

        final_comment = "\n\n".join(review_comments)

        pull_request.create_issue_comment(
            final_comment
        )

        print("PR comment posted successfully.")

    else:
        print("No supported files found.")


if __name__ == "__main__":
    main()
