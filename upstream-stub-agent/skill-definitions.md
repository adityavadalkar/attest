# Prior Authorization Agent — Skill Definitions

## Skill: Evaluate Prior Authorization

- **Name:** `evaluate_prior_auth`
- **Description:** Evaluates a prior authorization request for a patient based on their clinical record. Produces an authorization decision with clinical justification.
- **Input Schema:**
  ```json
  {
    "type": "object",
    "properties": {
      "treatment": {
        "type": "string",
        "description": "The treatment or procedure being requested"
      },
      "urgency": {
        "type": "string",
        "enum": ["routine", "urgent", "emergent"],
        "description": "Urgency level of the request"
      }
    },
    "required": ["treatment"]
  }
  ```
- **Output:** Authorization decision with clinical justification citing relevant diagnoses and lab values.
