# Rebutter Agent — Setup Instructions

Step-by-step guide to configure the Rebutter agent natively in Prompt Opinion.

## Prerequisites

- A Prompt Opinion account (free tier is sufficient)
- The Rebutter MCP Server deployed and accessible (e.g., on HuggingFace Spaces)
- At least one test patient loaded into the platform's FHIR server

---

## Step 1: Register the MCP Server

1. Go to **Workspace Hub** in Prompt Opinion
2. Click **"Add MCP Server"**
3. Enter:
   - **Name:** `Rebutter MCP Server`
   - **URL:** `https://<your-hf-space>.hf.space/mcp`
   - **Description:** Evidence retrieval tools for clinical claim verification. Searches FHIR records for supporting/refuting evidence and documented patient preferences.
4. **Enable "Pass FHIR Token"** toggle — CRITICAL for SHARP header propagation
5. Save and verify the server connects (green status indicator)

## Step 2: Create the Rebutter Agent

1. Go to **Agent Builder** in Prompt Opinion
2. Click **"Create New Agent"**
3. Configure:
   - **Name:** `Rebutter`
   - **Description:** Second-opinion clinical claim verification agent. Independently checks claims from other agents against the patient's FHIR record and returns a verdict (CONCUR, REBUT, or INSUFFICIENT_EVIDENCE) grounded in cited FHIR resources.
   - **Type:** A2A Agent (Path 1 — native)
4. Paste the full system prompt from `system-prompt.md`

## Step 3: Attach MCP Tools

1. In the agent configuration, go to **"Tools"** section
2. Click **"Add Tools"**
3. Select the Rebutter MCP Server
4. Attach all four tools:
   - `SearchSupportingEvidence`
   - `SearchRefutingEvidence`
   - `ExtractDocumentedPreferences`
   - `CiteFhirResource`

## Step 4: Define Skills

1. In the agent configuration, go to **"Skills"** section
2. Add skills as defined in `skill-definitions.md`:
   - `verify_clinical_claim`
   - `check_patient_preferences`

## Step 5: Publish to Marketplace

1. Click **"Publish"** on the agent configuration
2. Fill in marketplace listing details:
   - **Category:** Clinical Decision Support
   - **Tags:** second-opinion, claim-verification, FHIR, patient-safety
   - See `../submission/marketplace-listings.md` for full listing text

## Step 6: Test the Agent

1. Open **General Chat** in Prompt Opinion
2. Select a test patient (e.g., Janet Williams)
3. Invoke the Rebutter agent via A2A with a test claim:
   - "The Prior Auth Agent recommends blood transfusion for this patient"
4. Verify:
   - SHARP headers propagate (check MCP server logs)
   - FHIR resources are queried and returned
   - Verdict is delivered with citations
   - Documented preferences are surfaced (e.g., religious objection to transfusion)

## Troubleshooting

- **"SHARP context not available"**: Ensure "Pass FHIR Token" is enabled in Workspace Hub
- **Empty evidence results**: Check that patient data is loaded in the FHIR server
- **LLM reasoning failures**: Verify ANTHROPIC_API_KEY is set in HuggingFace Spaces secrets
- **MCP server unreachable**: Confirm the HuggingFace Space is running (not sleeping)
