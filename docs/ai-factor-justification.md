# AI Factor Justification

Why Rebutter requires generative AI and cannot be implemented as a rule-based system.

## The Core Problem

Rebutter evaluates arbitrary clinical claims against a patient's medical record, which includes both structured data (FHIR resources with coded values) and unstructured data (free-text clinical notes). The space of possible claims is open-ended, and the evidence that supports or contradicts them is expressed in natural language with clinical nuance.

## Capabilities That Require GenAI

### 1. Free-Text Clinical Note Understanding

Clinical notes contain critical information that exists only in narrative form -- not as structured codes or discrete data elements.

**Examples from Rebutter's test scenarios:**

- A progress note stating a patient is a Jehovah's Witness and declines blood transfusion. There is no ICD-10 code or FHIR flag for "religious objection to transfusion." The refusal is expressed in the physician's narrative documentation, including direct patient quotes, discussion of alternatives, and documentation of capacity.

- An advance directive note where a patient declines feeding tube placement. The nuances of the patient's wishes (declines even for potentially reversible conditions, accepts comfort feeding, daughter witnessed) are in free text.

- A goals-of-care note where a patient expresses motivation for aggressive treatment. The enthusiasm, self-advocacy, and family support are conveyed in narrative, not in a checkbox.

A rule-based system would need to enumerate every possible way a clinician might document a transfusion refusal, an advance directive preference, or a treatment goal -- across thousands of physicians' documentation styles, synonyms, and contextual framings.

### 2. Claim Decomposition Into Verifiable Assertions

When an upstream agent claims "the patient should receive a blood transfusion for iron-deficiency anemia," Rebutter must decompose this into sub-assertions:

- Does the patient have iron-deficiency anemia? (verifiable against labs and conditions)
- Is blood transfusion a valid treatment? (medical knowledge)
- Are there contraindications or refusals? (requires note search)
- Is this consistent with the patient's documented wishes? (requires advance directive review)

This decomposition is claim-dependent. A claim about insulin requires different sub-assertions than a claim about transfusion or chemotherapy. The decomposition logic cannot be pre-enumerated for all possible clinical claims.

### 3. Semantic Evidence Evaluation Against Natural Language Claims

Once evidence is retrieved, Rebutter must determine whether each piece of evidence is relevant to the claim and whether it supports or contradicts it.

**Example:** A note states the patient "does not want a tube put in my stomach." Rebutter must understand that:
- "tube in my stomach" refers to PEG tube / feeding tube (not an NG tube, not a chest tube)
- "does not want" is a refusal, not a description of a past event
- This is the patient speaking (quoted), not the physician speculating
- This applies to future situations, not just the current encounter

Semantic matching at this level -- understanding clinical context, speaker attribution, temporal scope, and intent -- is fundamentally a natural language understanding task.

### 4. Nuanced Reasoning About Evidence Weight and Relevance

Not all evidence is equal. Rebutter must weigh:

- **Recency**: A 2024 goals-of-care note may supersede a 2022 preference if the patient changed their mind. But a 2022 advance directive that was never revoked still applies.
- **Specificity**: A note about declining "all blood products" is stronger evidence than a general note about the patient's religious faith.
- **Source**: A documented conversation with the patient (with capacity assessment) carries more weight than a nursing intake note mentioning the patient's religion.
- **Scope**: A patient who declines chemotherapy may still accept palliative radiation. Rebutter must reason about the boundaries of a refusal.

This multi-factor weighing cannot be reduced to a scoring formula because the relevant factors change with every claim and every evidence document.

### 5. Open-Ended Claim Space

A rule-based system requires defining rules in advance for every scenario it might encounter. In clinical medicine, the space of possible claims is effectively unbounded:

- Treatment recommendations for any condition
- Medication interactions with patient preferences
- Procedural recommendations against advance directives
- Diagnostic suggestions that conflict with documented history
- Care escalation proposals that contradict comfort-care elections

No finite rule set can cover this space. Each new clinical scenario would require manual rule authoring, testing, and deployment. GenAI handles novel claim types without re-engineering because it reasons from the evidence rather than matching against pre-defined patterns.

## What Rule-Based Systems Can Do (and Where They Stop)

Rule-based systems are appropriate for:
- Checking structured allergy codes against medication codes (drug-allergy interaction alerts)
- Verifying lab value thresholds (critical value notifications)
- Enforcing formulary restrictions based on coded diagnoses

These work because both the input (structured code) and the rule (if-then logic) operate in the same discrete space. Rebutter's problem space includes unstructured text, open-ended claims, and contextual reasoning that falls outside this model.

## Summary

| Capability | Rule-Based | GenAI |
|-----------|------------|-------|
| Parse structured FHIR codes | Yes | Yes |
| Understand free-text clinical notes | No | Yes |
| Decompose novel claims into sub-assertions | No | Yes |
| Evaluate natural language evidence against natural language claims | No | Yes |
| Reason about evidence weight, recency, and scope | Limited | Yes |
| Handle claims never seen before without new rules | No | Yes |
