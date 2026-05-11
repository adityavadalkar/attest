# Feasibility Notes

Framing Attest for real-world deployment within existing healthcare infrastructure and regulatory constraints.

## Standards-Based Architecture

### FHIR R4 Resources

Attest operates entirely on standard FHIR R4 resources. No custom resource types or extensions are required.

Resources consumed:
- `Patient` -- demographics and identifiers
- `Condition` -- active problem list
- `Observation` -- lab results, vitals
- `MedicationRequest` -- active and historical medications
- `DocumentReference` -- clinical notes (base64-encoded text in attachments)
- `AllergyIntolerance` -- documented allergies
- `Procedure` -- surgical and procedural history
- `CarePlan` -- active care plans and goals

Any FHIR R4-compliant server (HAPI FHIR, Epic FHIR API, Cerner FHIR API, etc.) can serve as Attest's data source without modification.

### SHARP Headers for Security Context

Attest uses SHARP-on-MCP headers for authentication and authorization context. This approach avoids custom auth schemes:

- The access token is a standard SMART on FHIR token issued by the EHR's authorization server
- No additional credential exchange or registration is needed beyond what the upstream agent already has
- Patient scoping is enforced by the FHIR server's existing access controls

This means Attest can be added to an existing SMART on FHIR ecosystem without changes to the auth infrastructure.

## Regulatory Positioning

### Clinical Decision Support, Not Medical Device

Attest is positioned as a clinical decision support (CDS) tool, not a medical device:

- It does not make autonomous clinical decisions
- It does not directly order treatments, medications, or procedures
- It surfaces evidence from the patient's own medical record for clinician review
- The clinician retains full authority to accept, modify, or dismiss Attest's output

This positioning aligns with FDA guidance on Clinical Decision Support Software (CDS), specifically the criteria under Section 3060 of the 21st Century Cures Act for CDS functions that are not regulated as medical devices:

1. Not intended to acquire, process, or analyze a medical image or signal
2. Intended for the purpose of displaying, analyzing, or printing medical information
3. Intended for the purpose of supporting or providing recommendations to a health care professional
4. Intended for the purpose of enabling the health care professional to independently review the basis for the recommendations

Attest satisfies all four criteria: it analyzes text records (not images/signals), displays evidence, provides recommendations to clinicians, and enables independent review through its evidence citations and justification text.

### Safety Language

Throughout its output, Attest uses language that preserves clinician authority:

**Used (advisory):**
- "Evidence suggests..."
- "Consider reviewing..."
- "The following documentation may be relevant..."
- "This note surfaces a potential conflict..."
- "The patient's record contains..."

**Avoided (prescriptive):**
- ~~"The patient should not receive..."~~
- ~~"This treatment is contraindicated..."~~
- ~~"Do not proceed with..."~~
- ~~"This diagnosis is incorrect..."~~
- ~~"Prescribe X instead..."~~

The system highlights, surfaces, and flags -- it does not recommend, diagnose, or prescribe.

### Clinician-Attestable Next Steps

Every Attest verdict includes suggested next steps framed as actions the clinician can attest to:

- "Review the advance directive dated 2022-08-20 with the patient or proxy"
- "Confirm the patient's current transfusion preferences given the documented religious objection"
- "Verify that the comfort measures only election from 2024-01-22 remains current"
- "Consider discussing insulin initiation given the patient's documented enthusiasm for treatment intensification"

These next steps are designed to be:
1. Actionable by the clinician without additional tools
2. Documentable in the medical record
3. Non-prescriptive (the clinician decides whether to act)

## EHR Integration Pathways

### SMART on FHIR App

Attest could be deployed as a SMART on FHIR application:

- Launched from within the EHR context (Epic, Cerner, etc.)
- Receives the SMART launch context (patient ID, access token, FHIR server URL)
- Maps directly to SHARP headers
- Renders verdicts in a sidebar or modal within the EHR workflow

### CDS Hooks

Attest's evaluation could be triggered via CDS Hooks:

- Hook: `order-sign` -- evaluate claims when a clinician signs an order
- Hook: `patient-view` -- surface relevant notes when a chart is opened
- Response: CDS Hook cards with evidence summaries and suggested actions

### MCP Tool in Agent Workflows

The current architecture -- Attest as an MCP tool called by upstream agents -- is the primary deployment model for the hackathon. In production, the MCP server would sit behind the organization's API gateway with SMART on FHIR token validation.

## Scalability Considerations

- **Read-only FHIR access**: Attest never writes to the FHIR server, minimizing risk and simplifying permissions
- **Stateless processing**: No session state between requests; each evaluation is independent
- **Token-scoped queries**: FHIR queries are always scoped to a single patient, limiting data volume per request
- **Cacheable FHIR responses**: Patient data that does not change frequently (advance directives, historical notes) could be cached within a request to reduce FHIR server load

## Limitations and Honest Framing

- Attest's accuracy depends on the completeness of the FHIR record. If a relevant note was not uploaded or is in a system Attest cannot access, it will not be found.
- Free-text note interpretation is probabilistic. While GenAI performs well on clinical narrative, edge cases in unusual documentation styles may produce incorrect interpretations.
- Attest does not replace clinical judgment. It is a tool for surfacing evidence that a clinician might otherwise miss or not have time to review.
- The system requires FHIR R4 access. Organizations still on older FHIR versions (DSTU2, STU3) or proprietary APIs would need a FHIR facade or adapter.
