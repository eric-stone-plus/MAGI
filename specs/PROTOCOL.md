# MAGI Protocol Specification

> Hermes Agent Protocol for triadic independent inquiry.

## 0. Scope

MAGI is a Hermes Agent Protocol for structured review by three independent
perspectives. It defines inquiry shape, convergence handling, and dissent
preservation. It is not a mixture-of-agents answer aggregator: MAGI does not
blend candidate answers into a smoother final answer. It records what
independent perspectives converge on, what they cannot support, and what
dissent remains material. No models, tools, delegates, providers, or fixed role
assignments are defined here.

Out of scope:

- concrete tools
- provider or model choices
- command lines
- host authorization policy
- process supervision
- implementation-specific fallback behavior

## 1. Triadic Structure

MAGI uses three independent perspectives:

- Perspective A produces its own claim set, evidence, and uncertainty.
- Perspective B produces its own claim set, evidence, and uncertainty.
- Perspective C produces its own claim set, evidence, and uncertainty.

The perspectives are protocol slots, not fixed identities. A concrete
implementation may bind them to people, tools, models, procedures, or other
review mechanisms, but that binding is outside this specification.

## 2. Independence

Each perspective should be formed before reading the other perspectives'
outputs. The framework is invalid when one perspective merely paraphrases
another or when a coordinator silently simulates all three positions.

Required evidence shape:

- Claim: what the perspective asserts.
- Evidence: why the claim should be considered.
- Uncertainty: what could make the claim wrong or incomplete.
- Boundary: what the perspective did not inspect.

## 3. Convergence

MAGI treats convergence as a signal of stability, not as proof of truth.

- If all three materially agree, adopt the shared claim with evidence and stated limits.
- If two materially agree and one dissents, adopt only the shared portion and preserve dissent.
- If there is no material convergence, mark unresolved and do not force closure.

No weighted voting. No confidence-score arithmetic. No hidden majority override.

## 4. Residual Trace

MAGI's required output is a convergence/divergence residual trace. It is lighter
than QUINTE's adversarial ledger, but it uses the same RASHOMON field meanings
so HIGHBALL or a host runtime can reason about action boundaries.

Minimum trace:

```json
{
  "trace_version": "1.0",
  "question": "string",
  "instrument": "MAGI",
  "residuals": [{
    "id": "MAGI-001",
    "severity": "MEDIUM",
    "type": "evidence_gap",
    "source": "Perspective A",
    "finding": "string",
    "affected_paths": ["path or glob"],
    "error_signature": "literal string, regex, command, or null",
    "evidence": "file:line, command output, source, or null",
    "disposition": "unresolved",
    "required_closure": "human_review",
    "closure_state": "open",
    "closure_evidence": ["file:line, command output, source, waiver, or null"],
    "scope": "what action this closure covers"
  }],
  "trial_manifest": {
    "manifest_version": "1.0",
    "base_model_relation": "mixed",
    "perspective_count": 3,
    "perspectives": [{
      "id": "Perspective A",
      "role": "independent inquiry perspective",
      "route": "implementation-bound route or null",
      "artifact": "artifact path or null",
      "prompt_hash": "hash or null",
      "independent_first_pass": true
    }],
    "perturbation_axes": ["role", "evidence_boundary"],
    "independence_controls": ["independent_first_pass", "separate_output_artifacts"],
    "contamination_risks": ["same_model_error_correlation"],
    "cost": {
      "total_tokens": null,
      "wall_time_seconds": null,
      "tool_calls": null,
      "human_minutes": null
    }
  },
  "action_boundary": "reversible",
  "highball_decision": "not_applicable"
}
```

The trace must validate against RASHOMON
`schemas/residual-trace.schema.json`. MAGI may be lighter than QUINTE in
pressure, but it must not rename or omit trace fields.
MAGI should include enough evidence, uncertainty, and scope for host-side
residual quality metrics to be derived. It should not self-certify trace
quality; the consumer computes quality from the trace.
MAGI should include `trial_manifest` when a conclusion is action-relevant. The
manifest records perspective artifacts, prompt hashes, perturbation axes,
independence controls, contamination risks, and cost so convergence can be
judged as trial-conditioned stability rather than proof.
Earlier MAGI outputs may lack this trace. Treat them as historical evidence
and scan them for adoption; do not rewrite old outputs solely to improve
metrics.

MAGI should normally set `highball_decision` to `not_applicable`; HIGHBALL owns
the runtime decision. If MAGI detects that its conclusion affects code,
protocol, production, money movement, legal exposure, or another protected
boundary, it should mark the relevant residual as `escalated` and leave
`closure_state` as `open` unless direct evidence or human waiver is present.
HIGHBALL residual routing decides when MAGI is sufficient and when the task
must escalate to QUINTE, direct evidence, human review, or block.
When HIGHBALL builds an Action Packet, MAGI's trace is the convergence or
divergence trace component, not the packet's route or authorization decision.
If later evidence confirms, contradicts, or complicates the trace, that
follow-up belongs in a HIGHBALL outcome ledger. MAGI does not rewrite the trace
or self-certify route success after the fact.

When MAGI is evaluated as a future default route for a class of work, that
evaluation belongs in HIGHBALL route experiment artifacts: a pre-run manifest
and a post-run review against calibration, baseline, and outcome evidence. MAGI
produces convergence and divergence residuals; it does not certify that its own
route earned policy status.

## 5. Failure Modes

- Simulated plurality: one actor writes all perspectives without independent formation.
- Role fixation: historical tool bindings are treated as permanent protocol facts.
- False convergence: agreement is reported while evidence or boundaries diverge.
- Suppressed dissent: minority disagreement is omitted from synthesis.
- Evidence collapse: claims are merged without preserving source evidence.
- Trace collapse: final synthesis lacks residual ids, source evidence, or closure state.

## 6. Invariants

1. MAGI is a Hermes Agent Protocol, not a current tool route.
2. The three perspectives are abstract slots.
3. Concrete implementations must be specified outside this repository.
4. Dissent remains visible.
5. Convergence does not override missing evidence.
6. Cultural anchors are non-runtime context.
7. Any action-relevant output must preserve a residual trace.
