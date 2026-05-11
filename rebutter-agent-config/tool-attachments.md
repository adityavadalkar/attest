# Rebutter Agent — Tool Attachments

## MCP Tools to Attach

The Rebutter agent requires the following MCP tools from the **Rebutter MCP Server**:

| Tool Name | Purpose |
|-----------|---------|
| `SearchSupportingEvidence` | Searches patient FHIR record for evidence supporting a clinical claim |
| `SearchRefutingEvidence` | Searches patient FHIR record for evidence contradicting a clinical claim |
| `ExtractDocumentedPreferences` | Extracts advance directives, religious objections, treatment refusals, goals of care |
| `CiteFhirResource` | Retrieves full FHIR resource citation with provenance |

## Configuration

In the Prompt Opinion Workspace Hub:

1. Register the Rebutter MCP Server endpoint (HuggingFace Spaces URL)
2. Enable **"Pass FHIR Token"** toggle — this is critical for SHARP context propagation
3. All four tools should be attached to the Rebutter agent
4. The MCP server declares FHIR scopes via capabilities:
   - `patient/Patient.rs` (required)
   - `patient/Condition.rs`
   - `patient/Observation.rs`
   - `patient/MedicationRequest.rs`
   - `patient/Procedure.rs`
   - `patient/DocumentReference.rs`
   - `patient/Consent.rs`
   - `patient/CarePlan.rs`
