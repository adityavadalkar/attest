from __future__ import annotations

from dataclasses import dataclass

import jwt
from mcp.server.fastmcp import Context

FHIR_SERVER_URL_HEADER = "x-fhir-server-url"
FHIR_ACCESS_TOKEN_HEADER = "x-fhir-access-token"
PATIENT_ID_HEADER = "x-patient-id"


@dataclass(frozen=True)
class SharpContext:
    fhir_server_url: str
    patient_id: str
    access_token: str | None = None

    @property
    def auth_header(self) -> dict[str, str]:
        if self.access_token:
            return {"Authorization": f"Bearer {self.access_token}"}
        return {}


def get_sharp_context(ctx: Context) -> SharpContext:
    req = ctx.request_context.request
    url = req.headers.get(FHIR_SERVER_URL_HEADER)
    if not url:
        raise ValueError("Missing X-FHIR-Server-URL header — SHARP context not available")
    token = req.headers.get(FHIR_ACCESS_TOKEN_HEADER)
    patient_id = _extract_patient_id(req, token)
    if not patient_id:
        raise ValueError("Missing patient context — no X-Patient-ID header or patient claim in token")
    return SharpContext(fhir_server_url=url.rstrip("/"), patient_id=patient_id, access_token=token)


def _extract_patient_id(req, token: str | None) -> str | None:
    if token:
        try:
            claims = jwt.decode(token, options={"verify_signature": False})
            patient = claims.get("patient")
            if patient:
                return str(patient)
        except Exception:
            pass
    return req.headers.get(PATIENT_ID_HEADER)
