# Attest MCP Server

SHARP-compliant MCP server providing evidence retrieval tools for clinical claim verification.

## Tools

- **SearchSupportingEvidence** — Find evidence supporting a clinical claim
- **SearchRefutingEvidence** — Find evidence contradicting a clinical claim
- **ExtractDocumentedPreferences** — Extract advance directives, religious objections, goals of care
- **CiteFhirResource** — Get full FHIR resource citation with provenance

## Deployment

### HuggingFace Spaces (recommended)

1. Create a new Space with Docker SDK
2. Upload all files from this directory
3. Set `ANTHROPIC_API_KEY` in Space secrets
4. Server starts on port 7860

### Local

```bash
pip install -r requirements.txt
export ANTHROPIC_API_KEY=your_key
uvicorn main:app --host 0.0.0.0 --port 7860
```

## SHARP Headers

The server expects these headers on every MCP tool call:

| Header | Purpose |
|--------|---------|
| `X-FHIR-Server-URL` | Base URL of the FHIR server |
| `X-Patient-ID` | Current patient context |
| `X-FHIR-Access-Token` | Bearer token for FHIR queries |

Enable "Pass FHIR Token" in Prompt Opinion Workspace Hub when registering.
