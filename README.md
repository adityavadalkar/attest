# Attest

**Second-opinion clinical claim verification for healthcare AI agents.**

Attest independently checks clinical claims from other AI agents against the patient's FHIR record and returns an evidence-grounded verdict: **CONCUR**, **REBUT**, or **INSUFFICIENT_EVIDENCE** — each backed by cited FHIR resources.

Built for the [Agents Assemble](https://agents-assemble.devpost.com/) hackathon on the [Prompt Opinion](https://promptopinion.ai) platform.

## How It Works

```
Upstream Agent (e.g., Prior Auth)
  → produces confident clinical claim
    → Attest Agent (A2A consultation)
      → Attest MCP Server (SHARP-compliant tool calls)
        → FHIR Server (queries with forwarded token)
      ← Evidence results
    ← Verdict with FHIR citations
```

**Example:** A Prior Auth Agent approves a blood transfusion based on lab values. Attest searches the full chart and finds a 2023 progress note documenting the patient's religious objection to transfusion. Verdict: **REBUT** — with the exact DocumentReference citation and a recommended action: "Confirm current patient preference regarding transfusion alternatives before proceeding."

## Components

### Path 2: Attest MCP Server (`mcp-server/`)

Python/FastMCP server exposing 4 tools:

| Tool | Purpose |
|------|---------|
| `SearchSupportingEvidence` | Find evidence supporting a clinical claim |
| `SearchRefutingEvidence` | Find evidence contradicting a clinical claim |
| `ExtractDocumentedPreferences` | Extract advance directives, religious objections, treatment refusals |
| `CiteFhirResource` | Get full FHIR resource citation with provenance |

Deployed on HuggingFace Spaces. SHARP-compliant — receives FHIR context via standard headers.

### Path 1: Attest Agent (`attest-agent-config/`)

Native A2A agent configured in Prompt Opinion. No code — system prompt + skill definitions + MCP tool attachments.

## Quick Start

### Deploy the MCP Server

```bash
# Clone this repo
git clone https://github.com/<your-username>/attest.git
cd attest/mcp-server

# Set your Anthropic API key
export ANTHROPIC_API_KEY=your_key_here

# Run locally
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 7860

# Or build with Docker
docker build -t attest-mcp .
docker run -p 7860:7860 -e ANTHROPIC_API_KEY=$ANTHROPIC_API_KEY attest-mcp
```

### Deploy to HuggingFace Spaces

1. Create a new Space (Docker type)
2. Upload the `mcp-server/` contents
3. Set `ANTHROPIC_API_KEY` in Space secrets
4. The server starts automatically on port 7860

### Configure the Agent

Follow the step-by-step instructions in [`attest-agent-config/setup-instructions.md`](attest-agent-config/setup-instructions.md).

### Load Test Data

See [`test-data/README.md`](test-data/README.md) for importing synthetic patients with planted evidence.

## Project Structure

```
attest/
├── mcp-server/              # FastMCP server (Path 2)
│   ├── server.py            # Tool registration + FHIR scope declaration
│   ├── main.py              # FastAPI entry point
│   ├── tools/               # 4 MCP tools
│   └── lib/                 # SHARP context, FHIR client, LLM reasoning
├── attest-agent-config/   # Agent configuration (Path 1)
│   ├── system-prompt.md     # The agent's brain
│   ├── skill-definitions.md # A2A skills
│   └── setup-instructions.md
├── upstream-stub-agent/     # Demo helper: Prior Auth stub
├── test-data/               # Synthetic patients + planted notes
├── demo/                    # Video script + shot list
├── submission/              # Devpost writeup + marketplace listings
└── docs/                    # Architecture, SHARP compliance, AI factor
```

## Tech Stack

- **Runtime:** Python 3.13, FastMCP, FastAPI
- **LLM:** Anthropic Claude (Sonnet 4.5)
- **Data:** FHIR R4
- **Auth:** SHARP-on-MCP (header-based context propagation)
- **Hosting:** HuggingFace Spaces (Docker)
- **Platform:** Prompt Opinion

## Judging Criteria

- **AI Factor:** Free-text clinical note understanding, claim decomposition, semantic evidence evaluation — none of this is rule-based.
- **Potential Impact:** Prevents preference-violating clinical decisions by surfacing the full chart context that first-pass agents miss.
- **Feasibility:** Standard FHIR R4, SHARP headers, CDS positioning, safety language, clinician-attestable outputs. Could exist in a real healthcare system today.

## License

MIT
