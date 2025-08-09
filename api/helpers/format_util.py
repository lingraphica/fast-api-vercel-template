import re


def strip_markdown_code_fences(text: str) -> str:
    # Remove ```json ... ``` or ``` ... ```
    text = re.sub(r"```(?:json)?\s*([\s\S]*?)\s*```", r"\1", text, flags=re.IGNORECASE)
    text = re.sub(r"```json", "", text, flags=re.IGNORECASE)
    text = re.sub(r"```", "", text, flags=re.IGNORECASE)
    return text.strip()
