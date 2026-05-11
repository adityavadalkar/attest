from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Annotated

from mcp.server.fastmcp import Context
from pydantic import Field

from lib.fhir_client import FhirClient
from lib.llm_reasoning import decompose_claim, evaluate_evidence
from lib.note_search import summarize_resource
from lib.sharp_context import get_sharp_context


async def search_supporting_evidence(
    claim: Annotated[
        str,
        Field(description="The clinical claim to verify against the patient's record"),
    ],
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

    try:
        assertions = await decompose_claim(claim)
    except Exception as e:
        return json.dumps({
            "status": "error",
            "message": f"Failed to decompose claim: {e}",
            "retrieval_timestamp": retrieval_ts,
        })

    conditions = await fhir.get_conditions(pid)
    observations = await fhir.get_observations(pid)
    medications = await fhir.get_medications(pid)
    procedures = await fhir.get_procedures(pid)
    documents = await fhir.get_document_references(pid)

    all_resources = conditions + observations + medications + procedures + documents
    resource_summaries = [summarize_resource(r) for r in all_resources]

    all_evidence = []
    for assertion in assertions:
        try:
            evidence_items = await evaluate_evidence(assertion, resource_summaries, "supporting")
            for item in evidence_items:
                item["assertion"] = assertion
                item["retrieval_timestamp"] = retrieval_ts
            all_evidence.extend(evidence_items)
        except Exception:
            continue

    return json.dumps({
        "status": "success",
        "claim": claim,
        "patient_id": pid,
        "assertions_checked": assertions,
        "supporting_evidence": all_evidence,
        "evidence_count": len(all_evidence),
        "retrieval_timestamp": retrieval_ts,
    })
