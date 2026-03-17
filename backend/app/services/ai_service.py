"""
Claude AI integration service. Handles all communication with the Anthropic API.
"""

import json
import anthropic

from app.core.config import settings
from app.prompts.templates import (
    DOCUMENT_CLASSIFICATION,
    STRUCTURED_DATA_EXTRACTION,
    WASTE_ANALYSIS,
    TREND_ANALYSIS,
)


def _get_client() -> anthropic.Anthropic:
    return anthropic.Anthropic(api_key=settings.anthropic_api_key)


def _call_claude(prompt: str) -> str:
    client = _get_client()
    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=4096,
        messages=[{"role": "user", "content": prompt}],
    )
    return message.content[0].text


def _parse_json_response(text: str) -> dict:
    """Extract JSON from Claude's response, handling markdown code fences."""
    cleaned = text.strip()
    if cleaned.startswith("```"):
        lines = cleaned.split("\n")
        # Drop first and last lines (the fences)
        lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        cleaned = "\n".join(lines)
    return json.loads(cleaned)


def classify_document(raw_text: str) -> dict:
    prompt = DOCUMENT_CLASSIFICATION % raw_text[:8000]
    response = _call_claude(prompt)
    return _parse_json_response(response)


def extract_structured_data(raw_text: str) -> dict:
    prompt = STRUCTURED_DATA_EXTRACTION % raw_text[:12000]
    response = _call_claude(prompt)
    return _parse_json_response(response)


def analyze_waste(structured_data: dict) -> dict:
    prompt = WASTE_ANALYSIS % json.dumps(structured_data, indent=2)
    response = _call_claude(prompt)
    return _parse_json_response(response)


def analyze_trends(historical_data: list) -> dict:
    prompt = TREND_ANALYSIS % json.dumps(historical_data, indent=2)
    response = _call_claude(prompt)
    return _parse_json_response(response)
