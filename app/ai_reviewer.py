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

Review this file:
{file_name}

Content:
{file_content}

Find:
- security issues
- misconfigurations
- bad practices

Return bullet points only.
"""

    payload = {
        "model": "llama3-8b-8192",
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

    if "error" in result:
        return f"Groq API Error: {result['error']['message']}"

    if "choices" not in result:
        return f"Unexpected response: {result}"

    return result["choices"][0]["message"]["content"]
