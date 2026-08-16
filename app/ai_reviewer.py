import os
import requests

GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"

def review_code(file_content, file_name):
    api_key = os.environ["bad-key-test"]
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
        "model": "openai/gpt-oss-20b",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.2
    }
    response = requests.post(GROQ_API_URL, headers=headers, json=payload, timeout=30)

    if response.status_code != 200:
        raise RuntimeError(f"Groq API returned {response.status_code}: {response.text}")

    result = response.json()
    if "choices" not in result:
        raise RuntimeError(f"Unexpected Groq response: {result}")

    return result["choices"][0]["message"]["content"]
