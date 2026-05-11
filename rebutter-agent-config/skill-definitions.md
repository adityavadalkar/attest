# Rebutter Agent — Skill Definitions

These are the A2A skills to configure in the Prompt Opinion UI for the Rebutter agent.

## Skill 1: Verify Clinical Claim

- **Name:** `verify_clinical_claim`
- **Description:** Independently verifies a clinical claim against the patient's FHIR record. Searches for supporting and refuting evidence, checks documented patient preferences, and returns a verdict (CONCUR, REBUT, or INSUFFICIENT_EVIDENCE) with cited FHIR resources.
- **Input Schema:**
  ```json
  {
    "type": "object",
    "properties": {
      "claim": {
        "type": "string",
        "description": "The clinical claim to verify (e.g., 'Patient is a candidate for blood transfusion')"
      },
      "originating_agent": {
        "type": "string",
        "description": "Name or identifier of the agent that produced the claim"
      }
    },
    "required": ["claim"]
  }
  ```
- **Output:** Structured verdict with supporting evidence, refuting evidence, documented preferences, reasoning, and recommended action — all with FHIR resource citations.

## Skill 2: Check Patient Preferences

- **Name:** `check_patient_preferences`
- **Description:** Extracts all documented patient preferences from the FHIR record including advance directives, religious objections, treatment refusals, code status, and goals of care.
- **Input Schema:**
  ```json
  {
    "type": "object",
    "properties": {
      "context": {
        "type": "string",
        "description": "Optional context for what preferences to focus on (e.g., 'transfusion-related preferences')"
      }
    }
  }
  ```
- **Output:** List of documented preferences with source FHIR resources, effective dates, and excerpts.
