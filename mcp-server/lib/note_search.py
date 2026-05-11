from __future__ import annotations

import base64
from typing import Any


def extract_note_text(doc_ref: dict[str, Any]) -> str:
    content_list = doc_ref.get("content", [])
    for content in content_list:
        attachment = content.get("attachment", {})
        if "data" in attachment:
            try:
                decoded = base64.b64decode(attachment["data"]).decode("utf-8")
                return decoded[:4000]
            except Exception:
                continue
        if "url" in attachment:
            return f"[Attachment at {attachment['url']}]"

    text_block = doc_ref.get("text", {})
    if isinstance(text_block, dict) and "div" in text_block:
        return text_block["div"][:4000]

    return ""


def extract_resource_text(resource: dict[str, Any]) -> str:
    rt = resource.get("resourceType", "")

    if rt == "DocumentReference":
        return extract_note_text(resource)

    text_block = resource.get("text", {})
    if isinstance(text_block, dict) and "div" in text_block:
        return text_block["div"][:2000]

    for field in ("code", "valueCodeableConcept", "category", "medicationCodeableConcept"):
        val = resource.get(field)
        if isinstance(val, dict):
            coding = val.get("coding", [])
            if coding:
                return coding[0].get("display", coding[0].get("code", ""))
            if val.get("text"):
                return val["text"]

    if isinstance(resource.get("category"), list):
        for cat in resource["category"]:
            if isinstance(cat, dict) and cat.get("text"):
                return cat["text"]

    if "description" in resource:
        return str(resource["description"])[:2000]

    return ""


def summarize_resource(resource: dict[str, Any]) -> dict[str, Any]:
    return {
        "resourceType": resource.get("resourceType", "Unknown"),
        "id": resource.get("id", "unknown"),
        "date": (
            resource.get("date")
            or resource.get("effectiveDateTime")
            or resource.get("recordedDate")
            or resource.get("authoredOn")
            or resource.get("onsetDateTime")
            or resource.get("meta", {}).get("lastUpdated", "unknown")
        ),
        "text": extract_resource_text(resource),
    }
