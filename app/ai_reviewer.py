import os
import requests

GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"


def review_code(file_content, file_name, max_retries=3):
    api_key = os.environ["GROQ_API_KEYsss"]
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    prompt = f"""
You are a senior DevSecOps engineer. Review this file for security issues,
misconfigurations, and bad practices.
File: {file_name}
Content:
{file_content}
Respond ONLY with valid JSON, no markdown fences, in this exact shape:
{{
  "findings": [
    {{"severity": "critical|high|medium|low", "issue": "short description", "recommendation": "fix"}}
  ],
  "overall_risk": "critical|high|medium|low|none"
}}
"""
    payload = {
        "model": "openai/gpt-oss-20b",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.1,
        "response_format": {"type": "json_object"},
    }

    response = requests.post(GROQ_API_URL, headers=headers, json=payload, timeout=30)

    if response.status_code != 200:
        raise RuntimeError(f"Groq API returned {response.status_code}: {response.text}")

    result = response.json()
    if "choices" not in result:
        raise RuntimeError(f"Unexpected Groq response: {result}")

    return result["choices"][0]["message"]["content"]
