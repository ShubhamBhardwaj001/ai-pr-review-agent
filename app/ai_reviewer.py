import os
import requests

GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"


def review_code(file_content, file_name):

    api_key = os.environ["GROQ_API_KEY"]

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    prompt = f"""
You are a senior DevSecOps engineer.

Review this file and find:
- security issues
- bad practices
- misconfigurations
- CI/CD issues

File: {file_name}

Content:
{file_content}

Return bullet points only.
"""

    payload = {
        "model": "llama-3.1-70b-versatile",
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.2
    }

    response = requests.post(
        GROQ_API_URL,
        headers=headers,
        json=payload
    )

    result = response.json()

    return result["choices"][0]["message"]["content"]
