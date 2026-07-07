"""Guardrail checks applied to user input before it reaches any agent, MCP call,
or LLM prompt. This is where BabaTree's "input validation on city/name" security
criterion actually lives.
"""
from __future__ import annotations

import re

_ALLOWED_CHARS = re.compile(r"^[A-Za-zÀ-ɏ؀-ۿ\s\-'.]+$")
MAX_NAME_LENGTH = 80
MAX_CITY_LENGTH = 80


class GuardrailError(ValueError):
    """Raised when user-supplied input fails a pre-agent guardrail check."""


def sanitize_name(raw_name: str) -> str:
    name = raw_name.strip()
    if not name:
        raise GuardrailError("Name must not be empty.")
    if len(name) > MAX_NAME_LENGTH:
        raise GuardrailError(f"Name must be {MAX_NAME_LENGTH} characters or fewer.")
    if not _ALLOWED_CHARS.match(name):
        raise GuardrailError("Name contains characters that aren't allowed.")
    return name


def sanitize_city(raw_city: str) -> str:
    city = raw_city.strip()
    if not city:
        raise GuardrailError("City must not be empty.")
    if len(city) > MAX_CITY_LENGTH:
        raise GuardrailError(f"City must be {MAX_CITY_LENGTH} characters or fewer.")
    if not _ALLOWED_CHARS.match(city):
        raise GuardrailError("City contains characters that aren't allowed.")
    return city
