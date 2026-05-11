# Rebutter Architecture

## System Components

### 1. MCP Server (`rebutter-mcp-server`)

The Model Context Protocol server that exposes Rebutter's capabilities as tools. It receives claims from upstream agents and orchestrates evidence gathering and verdict synthesis.

**Responsibilities:**
- Accept incoming tool calls with claim text and patient context
- Extract SHARP headers (FHIR server URL, access token, patient ID) from the MCP request context
- Forward authenticated FHIR queries to gather evidence
- Invoke the Rebutter Agent for reasoning
- Return structured verdicts to the calling agent

### 2. Rebutter Agent (LLM-powered)

The GenAI reasoning core. Receives a claim, patient context, and retrieved evidence, then produces a structured verdict.

**Responsibilities:**
- Decompose upstream claims into verifiable assertions
- Evaluate each piece of evidence against the claim
- Weigh evidence strength, recency, and relevance
- Synthesize a verdict (CONCUR, DISAGREE, INSUFFICIENT_EVIDENCE)
- Generate clinician-readable justification text

### 3. Upstream Agent (caller)

Any clinical decision support agent that calls Rebutter for a second opinion. The upstream agent makes a clinical claim (e.g., "recommend blood transfusion") and receives a structured rebuttal or concurrence.

### 4. FHIR Server

A FHIR R4-compliant server (e.g., HAPI FHIR, Prompt Opinion platform) that stores patient records including structured resources (Conditions, Observations, MedicationRequests) and unstructured clinical notes (DocumentReferences).

## Data Flow

```
+------------------+       MCP Tool Call        +------------------+
|                  |  (claim + SHARP headers)   |                  |
|  Upstream Agent  | =========================> |  Rebutter MCP    |
|  (Caller)        |                            |  Server          |
|                  | <========================= |                  |
+------------------+    Structured Verdict      +--------+---------+
                                                         |
                                                         | 1. Extract SHARP headers
                                                         | 2. Query FHIR for evidence
                                                         |
                                                +--------v---------+
                                                |                  |
                                                |  FHIR Server     |
                                                |  (Patient data,  |
                                                |   DocumentRefs)  |
                                                |                  |
                                                +--------+---------+
                                                         |
                                                         | FHIR resources
                                                         | (Conditions, Notes, etc.)
                                                         |
                                                +--------v---------+
                                                |                  |
                                                |  Rebutter Agent  |
                                                |  (LLM Reasoning) |
                                                |                  |
                                                +------------------+
                                                         |
                                                         | Verdict:
                                                         |  - disposition (CONCUR/DISAGREE/INSUFFICIENT)
                                                         |  - justification
                                                         |  - evidence citations
                                                         |  - confidence score
                                                         v
```

## SHARP Header Propagation

SHARP-on-MCP headers travel through the entire call chain:

```
Upstream Agent
  |-- x-fhir-server-url: https://fhir.example.com/r4
  |-- x-fhir-access-token: eyJhbGciOi...
  |-- x-patient-id: patient-janet-williams
  |
  v
Rebutter MCP Server
  |-- Extracts headers from MCP request context
  |-- Uses x-fhir-access-token for all FHIR API calls
  |-- Scopes queries to x-patient-id
  |-- Never stores token beyond request lifecycle
  |
  v
FHIR Server
  |-- Validates token
  |-- Enforces FHIR scopes
  |-- Returns only authorized resources
```

## Tool Descriptions

### `rebutter_evaluate_claim`

Primary tool exposed by the MCP server.

**Input:**
- `claim` (string): The clinical assertion to evaluate (e.g., "Patient should receive blood transfusion")
- `context` (object, optional): Additional context from the upstream agent (e.g., reasoning, referenced resources)

**Output:**
- `verdict` (enum): CONCUR | DISAGREE | INSUFFICIENT_EVIDENCE
- `confidence` (number): 0.0 - 1.0
- `justification` (string): Clinician-readable explanation of the verdict
- `evidence` (array): List of evidence items with FHIR resource references, relevance scores, and excerpts
- `suggested_next_steps` (array): Clinician-attestable actions (phrased as "consider," "review," "verify")

### `rebutter_search_notes`

Internal tool used by the Rebutter Agent to search DocumentReferences.

**Input:**
- `patient_id` (string): FHIR patient ID
- `keywords` (array): Search terms derived from claim decomposition
- `date_range` (object, optional): Filter by date

**Output:**
- Array of DocumentReference resources with decoded note text

### `rebutter_get_patient_context`

Internal tool that retrieves structured clinical data for the patient.

**Input:**
- `patient_id` (string): FHIR patient ID
- `resource_types` (array): Which FHIR resources to retrieve (Condition, Observation, MedicationRequest, etc.)

**Output:**
- Bundled FHIR resources for the patient

## Verdict Synthesis

The Rebutter Agent follows a structured reasoning process:

1. **Claim Decomposition**: Break the upstream claim into discrete, verifiable assertions. For example, "Recommend blood transfusion for anemia" becomes:
   - The patient has anemia
   - Blood transfusion is clinically indicated
   - The patient can receive blood transfusion (no contraindications or refusals)

2. **Evidence Retrieval**: For each assertion, query FHIR for relevant resources:
   - Structured data (Conditions, Observations, lab results)
   - Unstructured notes (DocumentReferences -- decoded from base64)
   - Advance directives, goals-of-care documentation

3. **Evidence Evaluation**: For each piece of evidence, assess:
   - Relevance to the specific assertion
   - Recency (more recent documentation may supersede older)
   - Strength (explicit patient statement vs. incidental mention)
   - Direction (supports or contradicts the claim)

4. **Verdict Determination**:
   - **CONCUR**: Evidence supports the claim with no contradicting evidence found
   - **DISAGREE**: Evidence contradicts the claim (patient refusal, contraindication, conflicting directive)
   - **INSUFFICIENT_EVIDENCE**: Not enough evidence to confirm or deny the claim

5. **Justification Generation**: Produce a clinician-readable summary that cites specific evidence, explains the reasoning chain, and suggests attestable next steps.
