# SHARP-on-MCP Compliance

How Attest implements the SHARP (Secure Healthcare Agent Relay Protocol) header specification for MCP-based clinical tool chains.

## Headers Used

Attest expects the following SHARP headers to be propagated via the MCP request context:

| Header | Required | Description |
|--------|----------|-------------|
| `x-fhir-server-url` | Yes | Base URL of the FHIR R4 server (e.g., `https://fhir.example.com/r4`) |
| `x-fhir-access-token` | Yes | Bearer token for authenticating FHIR API requests. Typically a SMART on FHIR access token. |
| `x-patient-id` | Yes | FHIR Patient resource ID that scopes all queries (e.g., `patient-janet-williams`) |

## Token Handling

### Never Stored, Only Forwarded

The `x-fhir-access-token` is treated as a transient credential:

- Extracted from the incoming MCP request context at the start of each tool invocation
- Used exclusively for FHIR API calls within that single request lifecycle
- Never written to disk, logs, databases, or any persistent storage
- Never cached between requests
- Discarded when the tool invocation completes

### Per-Request Forwarding

Each FHIR API call made by Attest includes the token as a standard Authorization header:

```
GET /fhir/DocumentReference?patient=Patient/patient-janet-williams
Host: fhir.example.com
Authorization: Bearer <x-fhir-access-token value>
```

The token is forwarded verbatim -- Attest does not exchange, refresh, or modify the token. If the token expires mid-request, the FHIR server returns a 401 and Attest propagates the error to the caller.

## Patient ID Extraction

### From MCP Headers

The primary source of patient ID is the `x-patient-id` SHARP header, set by the upstream agent.

### From JWT Claims (Validation)

When available, Attest validates the `x-patient-id` header against the `patient` claim in the JWT access token:

```json
{
  "iss": "https://auth.example.com",
  "sub": "practitioner-12345",
  "patient": "patient-janet-williams",
  "scope": "patient/DocumentReference.read patient/Condition.read",
  "exp": 1700000000
}
```

If the `patient` claim in the JWT does not match the `x-patient-id` header, Attest rejects the request with a 403 error. This prevents a compromised upstream agent from querying data for a patient outside the token's authorized scope.

### Scope Verification

Attest inspects the `scope` claim in the JWT to verify that the token grants sufficient FHIR permissions for the resources it needs to query. If scopes are insufficient, the request is rejected before any FHIR calls are made.

## FHIR Scopes Declared in Capabilities

Attest's MCP server declares the following FHIR scopes in its capability manifest. These represent the minimum access needed for second-opinion evaluation:

```json
{
  "fhir_scopes": [
    "patient/Patient.read",
    "patient/Condition.read",
    "patient/Observation.read",
    "patient/MedicationRequest.read",
    "patient/DocumentReference.read",
    "patient/AllergyIntolerance.read",
    "patient/Procedure.read",
    "patient/CarePlan.read"
  ]
}
```

All scopes are read-only. Attest never writes to the FHIR server.

## Context Propagation Through the MCP Tool Chain

### Single-Hop Propagation

In the simplest case, the upstream agent calls Attest directly:

```
Upstream Agent --> [SHARP headers] --> Attest MCP Server --> FHIR Server
```

### Multi-Hop Propagation

If Attest is part of a longer tool chain (e.g., an orchestrator calls a clinical agent which calls Attest), SHARP headers must be propagated through each hop:

```
Orchestrator --> Agent A --> [SHARP headers] --> Attest --> FHIR Server
```

Each intermediate agent is responsible for forwarding the SHARP headers unchanged. No agent in the chain may:
- Modify the access token
- Substitute a different patient ID
- Cache or store the token beyond its request lifecycle
- Use the token for requests outside the current tool invocation

### Error Propagation

FHIR authentication and authorization errors are propagated back through the chain with clear error codes:

| Error | Meaning |
|-------|---------|
| `SHARP_MISSING_HEADER` | Required SHARP header not present in MCP context |
| `SHARP_TOKEN_EXPIRED` | The FHIR access token has expired |
| `SHARP_PATIENT_MISMATCH` | `x-patient-id` does not match JWT `patient` claim |
| `SHARP_INSUFFICIENT_SCOPE` | Token scopes do not cover required FHIR resources |
| `FHIR_UNAUTHORIZED` | FHIR server rejected the token (401) |
| `FHIR_FORBIDDEN` | FHIR server denied access to the requested resource (403) |
