# Rebutter Test Data

Synthetic FHIR R4 test data for demonstrating the Rebutter second-opinion agent.

## Contents

### FHIR Bundles (`bundles/`)

Transaction bundles containing Patient, Condition, Observation, MedicationRequest, and other clinical resources for each test patient. These must be loaded first since the planted notes reference patient IDs from these bundles.

### Planted Notes (`planted-notes/`)

FHIR DocumentReference resources containing clinical note text (base64-encoded in `content[0].attachment.data`). These notes serve as evidence that Rebutter discovers when evaluating upstream claims.

| File | Patient | Date | Scenario |
|------|---------|------|----------|
| `janet_2023_religious_objection_transfusion.json` | Janet Williams | 2023-11-15 | Religious objection to blood transfusion (Jehovah's Witness). Rebutter should flag this if an upstream agent recommends transfusion. |
| `robert_2022_advance_directive_no_feeding_tube.json` | Robert Chen | 2022-08-20 | Advance directive declining feeding tube / artificial nutrition under all circumstances. Rebutter should flag this if PEG placement is recommended. |
| `maria_2024_goals_of_care_meeting.json` | Maria Santos | 2024-03-10 | Goals-of-care meeting where patient wants aggressive diabetes management and insulin intensification. Rebutter should CONCUR with claims recommending treatment escalation. |
| `david_2024_comfort_measures_only.json` | David Okonkwo | 2024-01-22 | Family meeting electing comfort measures only, DNR/DNI, hospice. Rebutter should flag this if aggressive treatment or chemotherapy is recommended. |

## Import Instructions

### Step 1: Load FHIR Bundles

POST each bundle to the Prompt Opinion FHIR server. You can use either the platform's import UI or the FHIR API directly:

```bash
# Via FHIR API
curl -X POST https://<fhir-server-url>/fhir \
  -H "Content-Type: application/fhir+json" \
  -H "Authorization: Bearer <access-token>" \
  -d @bundles/janet_williams_bundle.json

# Repeat for each patient bundle
```

Alternatively, use the platform's bulk import UI if available.

### Step 2: Upload Planted Notes

After bundles are imported (so patient references resolve), upload each DocumentReference:

```bash
curl -X POST https://<fhir-server-url>/fhir/DocumentReference \
  -H "Content-Type: application/fhir+json" \
  -H "Authorization: Bearer <access-token>" \
  -d @planted-notes/janet_2023_religious_objection_transfusion.json

# Repeat for each planted note
```

### Step 3: Verify Resources

Check that resources loaded correctly:

```bash
# Verify patient exists
curl https://<fhir-server-url>/fhir/Patient/patient-janet-williams \
  -H "Authorization: Bearer <access-token>"

# Verify DocumentReferences are searchable
curl "https://<fhir-server-url>/fhir/DocumentReference?patient=Patient/patient-janet-williams" \
  -H "Authorization: Bearer <access-token>"
```

Confirm each patient record shows the expected conditions, observations, and linked DocumentReferences in the platform UI.

## Expected Demo Scenarios

### Scenario 1: Janet Williams -- Religious Objection to Transfusion

- **Upstream claim**: "Patient should receive blood transfusion to treat iron-deficiency anemia"
- **Expected Rebutter verdict**: DISAGREE
- **Evidence**: Progress note from 2023-11-15 documents patient's Jehovah's Witness faith and explicit refusal of all blood products. Advance directive on file.
- **Key point**: The objection is in free-text narrative, not a structured code -- demonstrating why GenAI is needed.

### Scenario 2: Robert Chen -- Advance Directive Against Feeding Tube

- **Upstream claim**: "PEG tube placement is recommended for nutritional support"
- **Expected Rebutter verdict**: DISAGREE
- **Evidence**: Advance care planning note from 2022-08-20 documents explicit refusal of feeding tube under all circumstances. Daughter Susan Chen witnessed and supports.
- **Key point**: The directive predates the current encounter, requiring temporal reasoning across documents.

### Scenario 3: Maria Santos -- Supports Aggressive Diabetes Management

- **Upstream claim**: "Recommend insulin intensification with basal insulin glargine to improve glycemic control"
- **Expected Rebutter verdict**: CONCUR
- **Evidence**: Goals-of-care note from 2024-03-10 confirms patient actively wants aggressive management, is willing to start insulin, and has enrolled in education programs.
- **Key point**: Rebutter does not only disagree -- it can find evidence that supports a claim and concur with confidence.

### Scenario 4: David Okonkwo -- Comfort Measures Only

- **Upstream claim**: "Consider third-line chemotherapy regimen for disease control"
- **Expected Rebutter verdict**: DISAGREE
- **Evidence**: Family meeting note from 2024-01-22 documents patient and family election of comfort measures only, DNR/DNI, hospice referral, and explicit decline of further chemotherapy.
- **Key point**: Multiple decision points (CMO, DNR/DNI, no chemo, no ICU) are documented in a single narrative note.

## Disclaimer

All patient data in this directory is entirely synthetic and was created for hackathon demonstration purposes. No real patient information is included. Any resemblance to actual persons is coincidental.
