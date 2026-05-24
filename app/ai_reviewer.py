from google import genai
import os


client = genai.Client(
    api_key=os.environ["GEMINI_API_KEY"]
)


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

    try:

        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt
        )

        return response.text

    except Exception as error:

        print(f"Gemini API failed: {error}")

        return """
- AI review unavailable
- Gemini API quota exceeded or API failed
- Please verify API quota/billing
"""
