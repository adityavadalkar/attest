from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Annotated

from mcp.server.fastmcp import Context
from pydantic import Field

from lib.fhir_client import FhirClient
from lib.llm_reasoning import extract_preferences_from_notes
from lib.note_search import summarize_resource
from lib.sharp_context import get_sharp_context


async def extract_documented_preferences(
    patientId: Annotated[
        str | None,
        Field(description="The patient ID. Optional if patient context exists via SHARP headers"),
    ] = None,
    ctx: Context = None,
) -> str:
    sharp = get_sharp_context(ctx)
    pid = patientId or sharp.patient_id
    fhir = FhirClient(sharp)
    retrieval_ts = datetime.now(timezone.utc).isoformat()

    documents = await fhir.get_document_references(pid)
    consents = await fhir.get_consents(pid)
    care_plans = await fhir.get_care_plans(pid)
    conditions = await fhir.get_conditions(pid)

    all_resources = documents + consents + care_plans + conditions
    if not all_resources:
        return json.dumps({
            "status": "success",
            "patient_id": pid,
            "preferences": [],
            "message": "No documents, consents, or care plans found for this patient",
            "retrieval_timestamp": retrieval_ts,
        })

    resource_summaries = [summarize_resource(r) for r in all_resources]

    try:
        preferences = await extract_preferences_from_notes(resource_summaries)
    except Exception as e:
        return json.dumps({
            "status": "error",
            "message": f"Failed to extract preferences: {e}",
            "retrieval_timestamp": retrieval_ts,
        })

    return json.dumps({
        "status": "success",
        "patient_id": pid,
        "preferences": preferences,
        "preferences_count": len(preferences),
        "resources_searched": len(all_resources),
        "retrieval_timestamp": retrieval_ts,
    })
