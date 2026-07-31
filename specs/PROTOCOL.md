# MAGI Protocol

## Scope

MAGI is a triadic cross-verification runtime. It creates three independent seat
products, subjects each to the other two review seats, and produces an
actionable final adjudication. It is not a majority vote, a generic answer
aggregator, or a substitute for direct execution evidence.

## Invariants

1. Exactly three distinct, immutable technical review profiles and exactly
   three distinct declared model families participate.
2. Every seat forms its thesis before seeing another seat's output.
3. Every seat runs a complete QUINTE product with one family across five
   parties, Counterpart Arbiter, and Primary Arbiter.
4. Profile diversity and model-family diversity are separately digest-bound.
5. Dossiers are frozen before exchange and cannot contain symlinks.
6. Three QUINTE run IDs and result digests are unique.
7. Review aliases hide seat, family, provider, model, and route identity.
8. All six directed reviewer-subject pairs complete exactly once.
9. Final adjudication cites only valid source and evidence references.
10. Every source `HIGH`, `CRITICAL`, or `P0` finding is represented with the
    exact highest cited source severity; final closure evidence must be
    inherited from cited sources, never invented.
11. `PASS` cannot coexist with open/blocked/unresolved high risk or material
    dissent. `BLOCK` requires at least one high-risk `open` or evidence-backed
    `blocked` finding.
12. Stored state, configuration, artifacts, trace, and product summary remain
    digest-bound and are revalidated on resume and status.

## Stages

### Independent formation

Each isolated Hermes runtime receives the same immutable original brief and one
immutable profile. It returns Thesis `1.0`; tools and external actions are not
available during this phase.

### Same-family adversarial review

The thesis is incorporated into a derived QUINTE brief without changing the
original question, action scope, affected paths, or action-binding digest.
QUINTE produces Result `2.1` and Manifest `2.0`, including explicit seven-role
seat bindings.

### Freeze

Dossier `1.0` binds the original brief, profile, complete composed Hermes
reviewer-profile tree, thesis, derived brief, QUINTE manifest, and QUINTE
result. MAGI validates the source in a temporary tree and
atomically freezes it. Partial or symlink-containing sources fail closed.

### Anonymous exchange

MAGI creates an immutable alias map after all dossiers are frozen. Each seat
reviews both other dossiers through the same complete immutable Hermes profile
that produced its thesis, without receiving subject identity metadata. Cross
Review `1.1` binds the reviewer profile spec/tree and thesis digests; it must
record concrete use of at least one declared profile method and one declared
failure check, while preserving source references, evidence references,
uncertainty, and dissent. Bare native-model review is invalid.

### Final adjudication

The Final Adjudicator receives the three anonymous dossiers and six reviews and
returns Final Verdict `1.0`: `PASS`, `BLOCK`, or `ESCALATE`. This is a synthesis
of the three independently profiled theses, three complete single-family
QUINTE dossiers, and six reviews—not a vote tally or residual concatenation.
The verdict's top-level dissent is the exact canonical union of anonymized
QUINTE-result dissent and cross-review dissent.

### Deterministic verification

The verifier reconstructs the source universe and rejects invented references,
omitted high risk, severity downgrades, untyped or unsupported closure,
suppressed dissent, and an unsafe decision. It deterministically reconstructs
the HIGHBALL/RASHOMON-compatible Trace `1.1`.

## Product

`magi verify-product TRIAL_DIR` revalidates the closed state and emits Product
Summary `1.0`, binding:

- runtime, builder, agent, and original-brief digests;
- question, action scope, affected paths, and action binding;
- final verdict and residual trace;
- exact final dissent;
- three distinct family/profile/thesis/dossier/QUINTE products;
- six distinct directed cross-reviews;
- canonical product identity digest.

Only this verified product boundary may be consumed as completed MAGI evidence.

## Failure Semantics

Contract failure exits distinctly from agent failure and runtime I/O failure.
Resume begins at the first missing valid artifact; it never silently accepts a
changed configuration or runtime. `BLOCK` and `ESCALATE` are valid final MAGI
products but are non-authorizing at the HIGHBALL boundary.

## Non-Claims

MAGI does not prove truth, statistical independence, or a universal confidence
percentage. Containers reduce state contamination; profiles create method
diversity; distinct foundation-model families reduce one important source of
correlated error. Shared training data, protocol structure, original evidence,
and the final adjudicator remain declared contamination risks.
