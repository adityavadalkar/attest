from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Annotated

from mcp.server.fastmcp import Context
from pydantic import Field

from lib.fhir_client import FhirClient
from lib.note_search import extract_resource_text
from lib.sharp_context import get_sharp_context


async def cite_fhir_resource(
    resourceType: Annotated[
        str,
        Field(description="The FHIR resource type (e.g. Condition, Observation, DocumentReference)"),
    ],
    resourceId: Annotated[
        str,
        Field(description="The FHIR resource ID"),
    ],
    ctx: Context = None,
) -> str:
    sharp = get_sharp_context(ctx)
    fhir = FhirClient(sharp)
    retrieval_ts = datetime.now(timezone.utc).isoformat()

    resource = await fhir.read(resourceType, resourceId)
    if not resource:
        return json.dumps({
            "status": "not_found",
            "resource_type": resourceType,
            "resource_id": resourceId,
            "retrieval_timestamp": retrieval_ts,
        })

    effective_date = (
        resource.get("date")
        or resource.get("effectiveDateTime")
        or resource.get("recordedDate")
        or resource.get("authoredOn")
        or resource.get("onsetDateTime")
        or resource.get("period", {}).get("start")
        or resource.get("meta", {}).get("lastUpdated")
    )

    version_id = resource.get("meta", {}).get("versionId")

    summary_text = extract_resource_text(resource)

    return json.dumps({
        "status": "success",
        "resource_type": resourceType,
        "resource_id": resourceId,
        "version_id": version_id,
        "effective_date": effective_date,
        "retrieval_timestamp": retrieval_ts,
        "summary": summary_text[:1000] if summary_text else None,
        "resource": resource,
    })
