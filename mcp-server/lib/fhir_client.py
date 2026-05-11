from __future__ import annotations

from typing import Any

import httpx

from .sharp_context import SharpContext


class FhirClient:
    def __init__(self, ctx: SharpContext) -> None:
        self._base_url = ctx.fhir_server_url
        self._headers: dict[str, str] = {
            "Accept": "application/fhir+json",
            **ctx.auth_header,
        }

    async def _get(self, path: str, params: dict[str, str] | None = None) -> dict | None:
        url = f"{self._base_url}/{path.lstrip('/')}"
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.get(url, headers=self._headers, params=params)
            if resp.status_code == 404:
                return None
            resp.raise_for_status()
            return resp.json()

    async def read(self, resource_type: str, resource_id: str) -> dict[str, Any] | None:
        return await self._get(f"{resource_type}/{resource_id}")

    async def search(
        self,
        resource_type: str,
        params: dict[str, str] | None = None,
    ) -> list[dict[str, Any]]:
        result = await self._get(resource_type, params=params)
        if not result or not result.get("entry"):
            return []
        return [e.get("resource", e) for e in result["entry"] if e.get("resource")]

    async def search_patient(
        self,
        resource_type: str,
        patient_id: str,
        extra_params: dict[str, str] | None = None,
    ) -> list[dict[str, Any]]:
        params = {"patient": patient_id}
        if extra_params:
            params.update(extra_params)
        return await self.search(resource_type, params)

    async def get_conditions(self, patient_id: str) -> list[dict[str, Any]]:
        return await self.search_patient("Condition", patient_id)

    async def get_observations(self, patient_id: str) -> list[dict[str, Any]]:
        return await self.search_patient(
            "Observation", patient_id,
            {"_sort": "-date", "_count": "100"},
        )

    async def get_medications(self, patient_id: str) -> list[dict[str, Any]]:
        return await self.search_patient("MedicationRequest", patient_id)

    async def get_procedures(self, patient_id: str) -> list[dict[str, Any]]:
        return await self.search_patient(
            "Procedure", patient_id,
            {"_sort": "-date", "_count": "50"},
        )

    async def get_document_references(self, patient_id: str) -> list[dict[str, Any]]:
        return await self.search_patient(
            "DocumentReference", patient_id,
            {"_sort": "-date", "_count": "50"},
        )

    async def get_consents(self, patient_id: str) -> list[dict[str, Any]]:
        return await self.search_patient("Consent", patient_id)

    async def get_care_plans(self, patient_id: str) -> list[dict[str, Any]]:
        return await self.search_patient("CarePlan", patient_id)
