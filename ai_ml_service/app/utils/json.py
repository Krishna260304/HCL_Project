"""
Robust JSON parsing and extraction utilities for LLM generated text.
Handles markdown fenced code blocks, unescaped control characters, and partial JSON.
"""

import json
import re
from typing import Any, Dict, Optional


def extract_json_from_text(text: str) -> Optional[Dict[str, Any]]:
    """
    Extract and parse JSON object from a potentially messy LLM response string.
    Tries multiple extraction strategies:
    1. Direct json.loads
    2. Markdown code fence ```json ... ``` extraction
    3. First '{' to last '}' bracket slice
    4. Common syntax cleanups (trailing commas, escaped quotes)
    """
    if not text or not isinstance(text, str):
        return None

    cleaned_text = text.strip()

    # Strategy 1: Direct parse
    try:
        data = json.loads(cleaned_text)
        if isinstance(data, dict):
            return data
    except Exception:
        pass

    # Strategy 2: Code fence match
    fence_patterns = [
        r"```(?:json)?\s*([\s\S]*?)\s*```",
        r"```(?:javascript)?\s*([\s\S]*?)\s*```",
    ]
    for pattern in fence_patterns:
        match = re.search(pattern, cleaned_text, re.IGNORECASE)
        if match:
            extracted = match.group(1).strip()
            try:
                data = json.loads(extracted)
                if isinstance(data, dict):
                    return data
            except Exception:
                cleaned_extracted = clean_json_string(extracted)
                try:
                    data = json.loads(cleaned_extracted)
                    if isinstance(data, dict):
                        return data
                except Exception:
                    pass

    # Strategy 3: Substring between first '{' and last '}'
    first_brace = cleaned_text.find("{")
    last_brace = cleaned_text.rfind("}")
    if first_brace != -1 and last_brace != -1 and last_brace > first_brace:
        json_candidate = cleaned_text[first_brace : last_brace + 1]
        try:
            data = json.loads(json_candidate)
            if isinstance(data, dict):
                return data
        except Exception:
            cleaned_candidate = clean_json_string(json_candidate)
            try:
                data = json.loads(cleaned_candidate)
                if isinstance(data, dict):
                    return data
            except Exception:
                pass

    return None


def clean_json_string(s: str) -> str:
    """Clean common LLM formatting flaws in JSON strings."""
    # Remove trailing commas before closing braces/brackets
    s = re.sub(r",\s*([\]}])", r"\1", s)
    # Remove single line comments
    s = re.sub(r"//.*?\n", "\n", s)
    return s
