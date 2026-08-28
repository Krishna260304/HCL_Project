"""
Text processing and normalization utilities.
"""

import re
from typing import List


def normalize_text(text: str) -> str:
    """Normalize whitespace and strip excess characters."""
    if not text:
        return ""
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def estimate_token_count(text: str) -> int:
    """Fast heuristic token estimation (~4 characters per token in English)."""
    if not text:
        return 0
    return max(1, len(text) // 4)


def extract_keywords(text: str, max_keywords: int = 10) -> List[str]:
    """Extract simple alphanumeric keyword tokens."""
    if not text:
        return []
    words = re.findall(r"\b[a-zA-Z0-9_-]{3,}\b", text.lower())
    stop_words = {
        "the", "and", "for", "with", "this", "that", "from", "have",
        "will", "about", "what", "which", "when", "where", "into", "more"
    }
    filtered = [w for w in words if w not in stop_words]
    # Unique preserve order
    seen = set()
    result = []
    for w in filtered:
        if w not in seen:
            seen.add(w)
            result.append(w)
            if len(result) >= max_keywords:
                break
    return result
