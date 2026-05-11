from mcp.server.fastmcp import FastMCP

from tools.search_supporting_evidence import search_supporting_evidence
from tools.search_refuting_evidence import search_refuting_evidence
from tools.extract_documented_preferences import extract_documented_preferences
from tools.cite_fhir_resource import cite_fhir_resource

mcp = FastMCP("Rebutter", stateless_http=True, host="0.0.0.0")

_original_get_capabilities = mcp._mcp_server.get_capabilities


def _patched_get_capabilities(notification_options, experimental_capabilities):
    caps = _original_get_capabilities(notification_options, experimental_capabilities)
    caps.model_extra["extensions"] = {
        "ai.promptopinion/fhir-context": {
            "scopes": [
                {"name": "patient/Patient.rs", "required": True},
                {"name": "patient/Condition.rs"},
                {"name": "patient/Observation.rs"},
                {"name": "patient/MedicationRequest.rs"},
                {"name": "patient/Procedure.rs"},
                {"name": "patient/DocumentReference.rs"},
                {"name": "patient/Consent.rs"},
                {"name": "patient/CarePlan.rs"},
            ]
        }
    }
    return caps


mcp._mcp_server.get_capabilities = _patched_get_capabilities

mcp.tool(
    name="SearchSupportingEvidence",
    description=(
        "Searches a patient's FHIR record for evidence that supports a given clinical claim. "
        "Decomposes the claim into verifiable assertions and checks Conditions, Observations, "
        "Medications, Procedures, and clinical notes. Returns structured evidence with FHIR "
        "resource citations and confidence weights."
    ),
)(search_supporting_evidence)

mcp.tool(
    name="SearchRefutingEvidence",
    description=(
        "Searches a patient's FHIR record for evidence that contradicts a given clinical claim. "
        "Checks structured data and clinical notes for conflicting diagnoses, documented preferences, "
        "prior decisions, or contradictory findings. Returns structured evidence with FHIR resource "
        "citations and confidence weights."
    ),
)(search_refuting_evidence)

mcp.tool(
    name="ExtractDocumentedPreferences",
    description=(
        "Extracts documented patient preferences from the FHIR record including advance directives, "
        "code status, religious objections, treatment refusals, and goals of care. Searches across "
        "DocumentReferences, Consents, CarePlans, and Conditions."
    ),
)(extract_documented_preferences)

mcp.tool(
    name="CiteFhirResource",
    description=(
        "Retrieves a specific FHIR resource by type and ID and returns a structured citation "
        "with the full resource, effective date, version ID, retrieval timestamp, and a summary "
        "excerpt suitable for inclusion in a Rebutter response."
    ),
)(cite_fhir_resource)
