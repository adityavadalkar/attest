from __future__ import annotations

import json
import os
from typing import Any

import anthropic

_client: anthropic.AsyncAnthropic | None = None


def _get_client() -> anthropic.AsyncAnthropic:
    global _client
    if _client is None:
        _client = anthropic.AsyncAnthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    return _client


MODEL = "claude-sonnet-4-5-20250514"


def _parse_json_response(text: str) -> Any:
    text = text.strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[1].rsplit("```", 1)[0].strip()
    return json.loads(text)


async def decompose_claim(claim: str) -> list[str]:
    client = _get_client()
    resp = await client.messages.create(
        model=MODEL,
        max_tokens=1024,
        messages=[
            {
                "role": "user",
                "content": (
                    "Break the following clinical claim into a list of individually "
                    "verifiable factual assertions. Each assertion should be specific "
                    "enough to check against a patient's medical record. "
                    "Return ONLY a JSON array of strings, no other text.\n\n"
                    f"Claim: {claim}"
                ),
            }
        ],
    )
    return _parse_json_response(resp.content[0].text)


async def evaluate_evidence(
    assertion: str,
    resource_summaries: list[dict[str, Any]],
    mode: str,
) -> list[dict[str, Any]]:
    if not resource_summaries:
        return []

    client = _get_client()
    direction = "supports" if mode == "supporting" else "contradicts"

    resp = await client.messages.create(
        model=MODEL,
        max_tokens=2048,
        messages=[
            {
                "role": "user",
                "content": (
                    f'Given the assertion: "{assertion}"\n\n'
                    f"Review these FHIR resources and identify which ones {direction} "
                    f"this assertion. For each relevant resource, return a JSON array of objects with:\n"
                    f"- resource_type: the FHIR resource type\n"
                    f"- resource_id: the resource ID\n"
                    f"- excerpt: a brief excerpt from the resource that {direction} the assertion\n"
                    f"- weight: 'strong', 'moderate', or 'weak'\n"
                    f"- reasoning: one sentence explaining why\n\n"
                    f"If no resources are relevant, return an empty array [].\n"
                    f"Return ONLY the JSON array.\n\n"
                    f"Resources:\n{json.dumps(resource_summaries[:20], indent=2)}"
                ),
            }
        ],
    )
    return _parse_json_response(resp.content[0].text)


async def extract_preferences_from_notes(
    note_summaries: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    if not note_summaries:
        return []

    client = _get_client()
    resp = await client.messages.create(
        model=MODEL,
        max_tokens=2048,
        messages=[
            {
                "role": "user",
                "content": (
                    "Review these clinical documents and extract any documented patient "
                    "preferences, advance directives, code status decisions, religious "
                    "objections, treatment refusals, or goals of care.\n\n"
                    "Return a JSON array of objects with:\n"
                    "- preference_type: e.g. 'advance_directive', 'religious_objection', "
                    "'treatment_refusal', 'goals_of_care', 'code_status'\n"
                    "- description: what the preference is\n"
                    "- effective_date: when it was documented\n"
                    "- source_resource_type: FHIR resource type\n"
                    "- source_resource_id: FHIR resource ID\n"
                    "- excerpt: the relevant text from the document\n\n"
                    "If no preferences are found, return an empty array [].\n"
                    "Return ONLY the JSON array.\n\n"
                    f"Documents:\n{json.dumps(note_summaries[:15], indent=2)}"
                ),
            }
        ],
    )
    return _parse_json_response(resp.content[0].text)
