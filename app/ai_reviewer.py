import google.generativeai as genai
import os


genai.configure(
    api_key=os.environ["GEMINI_API_KEY"]
)

model = genai.GenerativeModel("gemini-1.5-flash")


def review_code(file_content, file_name):

    prompt = f"""
    You are a senior DevSecOps engineer.

    Review this file carefully.

    Check for:
    - security vulnerabilities
    - Terraform best practices
    - Kubernetes misconfigurations
    - dangerous settings
    - CI/CD issues

    File Name:
    {file_name}

    File Content:
    {file_content}

    Return concise bullet point findings.
    """

    response = model.generate_content(prompt)

    return response.text
