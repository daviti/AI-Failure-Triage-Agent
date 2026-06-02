"""
Core triage agent: sends CI log / screenshot context to Claude Opus 4.8
with adaptive thinking, prompt caching, and structured output.
"""

import base64
from pathlib import Path

import anthropic

from qia.config import settings
from qia.models.triage import TriageReport

_client = anthropic.Anthropic(api_key=settings.anthropic_api_key)

_SYSTEM_PROMPT = """You are the Quality Intelligence Agent (QIA) — an expert in software quality
engineering, CI/CD systems, and automated test infrastructure.

Your job is to perform deep root cause analysis on test failures and CI pipeline errors.
You have expertise in:
- Android/iOS mobile automation (Appium, Espresso, XCTest)
- Web automation (Selenium, Playwright, Cypress)
- CI/CD platforms (GitHub Actions, Jenkins, CircleCI, Bitrise)
- Common failure patterns: flaky tests, environment issues, dependency problems
- Predicting which team or component owns a failure
- Assessing release risk

Analyze every failure thoroughly. Be specific — quote exact error messages, stack traces,
and log lines that support your conclusions. If you see a flaky pattern, say so explicitly."""


def _encode_image(path: Path) -> tuple[str, str]:
    """Return (base64_data, media_type) for an image file."""
    suffix = path.suffix.lower()
    media_map = {".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".gif": "image/gif", ".webp": "image/webp"}
    media_type = media_map.get(suffix, "image/png")
    data = base64.standard_b64encode(path.read_bytes()).decode()
    return data, media_type


def analyze(
    log_content: str,
    test_name: str | None = None,
    screenshot_path: Path | None = None,
    extra_context: str | None = None,
) -> TriageReport:
    """
    Analyze a CI failure and return a structured TriageReport.

    Uses prompt caching on the system prompt + large log content to reduce
    cost on repeated analyses against the same CI run.
    """
    user_content: list[dict] = []

    # Build the analysis request text
    request_parts = ["Analyze this CI failure and produce a complete triage report."]
    if test_name:
        request_parts.append(f"\n**Test / Job name:** {test_name}")
    if extra_context:
        request_parts.append(f"\n**Additional context:** {extra_context}")

    request_parts.append(f"\n\n**CI Log:**\n```\n{log_content}\n```")
    user_content.append({"type": "text", "text": "\n".join(request_parts)})

    # Attach screenshot if provided (vision analysis)
    if screenshot_path and screenshot_path.exists():
        img_data, media_type = _encode_image(screenshot_path)
        user_content.append(
            {
                "type": "image",
                "source": {"type": "base64", "media_type": media_type, "data": img_data},
            }
        )
        user_content.append(
            {"type": "text", "text": "The screenshot above was captured at the moment of failure."}
        )

    response = _client.messages.parse(
        model=settings.model,
        max_tokens=settings.max_tokens,
        thinking={"type": "adaptive"},
        output_config={
            "effort": settings.effort,
            "format": TriageReport.model_json_schema(),
        },
        system=[
            {
                "type": "text",
                "text": _SYSTEM_PROMPT,
                # Cache the system prompt — it never changes between calls
                "cache_control": {"type": "ephemeral"},
            }
        ],
        messages=[{"role": "user", "content": user_content}],
        output_format=TriageReport,
    )

    if response.parsed_output is None:
        raise ValueError("Claude returned an empty or unparseable structured response")

    return response.parsed_output
