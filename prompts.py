import os
from typing import Dict, List

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

# Separated from the user message so the model treats it as a persistent instruction,
# not part of the content it is reasoning about.
_SYSTEM_PROMPT = (
    "You are a secure coding assistant. "
    "You will be given a code snippet and a numbered list of confirmed security findings. "
    "Suggest the minimal code changes needed to address each finding. "
    "Be concise and do not rewrite code unrelated to the findings."
)


def _format_findings(findings: List[Dict]) -> str:
    """Render findings as a numbered list so the model gets clean, readable context."""
    lines = []
    for i, f in enumerate(findings, 1):
        lines.append(
            f"{i}. [{f.get('severity', 'Unknown')}] {f.get('title', '')} "
            f"(line {f.get('line', '?')}): {f.get('explanation', '')}"
        )
    return "\n".join(lines)


def ai_suggestions(code: str, findings: List[Dict], language: str) -> str:
    """Return an AI-generated remediation suggestion for the confirmed findings.

    Degrades gracefully if the OpenAI SDK is absent or the API call fails.
    """
    if OpenAI is None:
        return "AI explanation unavailable (OpenAI SDK not installed)."

    user_message = (
        f"Language: {language}\n\n"
        f"Code:\n```\n{code}\n```\n\n"
        f"Confirmed findings:\n{_format_findings(findings)}\n\n"
        "Suggest a minimal fix for each finding above."
    )

    try:
        client = OpenAI()
        resp = client.chat.completions.create(
            model=os.environ.get("OPENAI_MODEL", "gpt-4o-mini"),
            messages=[
                {"role": "system", "content": _SYSTEM_PROMPT},
                {"role": "user", "content": user_message},
            ],
            temperature=0,   # remediation should be consistent, not creative
            max_tokens=400,
        )
        return resp.choices[0].message.content or ""
    except Exception:
        return "AI explanation unavailable."
