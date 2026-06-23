# opencode Independent Review — MAGI/QUINTE v3.4 Audit (10 Issues)

> **Reviewer**: opencode (glm-5.2)
> **Date**: 2026-06-23
> **Scope**: Independent assessment of the 10 issues raised by the 7-agent audit comparing MAGI v3.4 and QUINTE v3.4.
> **Sources read**: `QUINTE/specs/PROTOCOL.md`, `QUINTE/README.md`, `QUINTE/specs/theoretical-foundation.md`, `MAGI/specs/PROTOCOL.md`. Cross-repo grep performed to verify KOZO and BANNIN definitions.

---

## Verdict Summary

| # | Issue | Agree? | Severity | Recommended Fix |
|---|-------|:------:|:--------:|-----------------|
| 1 | Convergence gate ownership | ✅ Agree | High | Reconcile wording; mechanical gate, not "adjudicate" |
| 2 | R2 agent count (3 vs 5) | ✅ Agree | High | Standardize on 5; specify panel selection |
| 3 | delegate_task contradiction | ⚠️ Partial | Medium | Clarify dual-use in README (not "remove") |
| 4 | timeout 120s vs 180s | ✅ Agree | High | Exempt MAGI from R1 120s, or align to 180s |
| 5 | Mode A/B not exhaustive | ✅ Agree | Medium | Add anytime/independent as 3rd deployment |
| 6 | confidence annotation | ✅ Agree | Medium | Narrow fix: remove MAGI "confidence annotation" claim only |
| 7 | BANNIN unimplemented | ✅ Agree | High | Downgrade Invariant #6 language; add interim enforcement |
| 8 | missing local cross-references | ✅ Agree | Low | Standardize on local relative paths; fix branch mismatch |
| 9 | theoretical-foundation v1.0 | ✅ Agree | Medium | Bump version + add v3.4 feature sections |
| 10 | KOZO undefined | ⚠️ Partial | Low | Add cross-ref to HIGHBALL (do NOT remove) |

**Bottom line**: 9 of 10 findings are valid. Issue #10 is valid as stated (KOZO is undefined *in MAGI/QUINTE specs*) but the correct fix is a cross-reference, not removal — KOZO is a real, ratified HIGHBALL component. Issue #3 is an apparent contradiction that resolves on close reading but still needs clarification. I **dispute** the `fr_changes.md` proposals to (a) remove KOZO entirely and (b) strip all `confidence` references from QUINTE — both overreach the underlying issues.

---

## Per-Issue Analysis

### Issue 1 — Convergence gate ownership: hm or self-converge?

**Agree: YES (real contradiction, High severity)**

The two specs contradict each other directly:

- `QUINTE/specs/PROTOCOL.md:66` — "hm retains veto over Phase outputs but does NOT adjudicate MAGI's internal convergence gate during R1 Mode B. MAGI delegates self-converge (≥2/3 gate)."
- `MAGI/specs/PROTOCOL.md:93` — "hm reads all three outputs. Binary decision"
- `MAGI/specs/PROTOCOL.md:97` — "≥2/3 agree → Converge → hm adopts answer."

QUINTE says hm does **not** adjudicate (delegates self-converge); MAGI says hm **reads all three** and makes a **binary decision** and **adopts** the answer. "Binary decision" + "adopts" reads as adjudication, contradicting "does NOT adjudicate."

**Root cause**: The specs use "adjudicate" to mean two different things. QUINTE means "hm does not apply judgment/override the gate." MAGI means "hm mechanically applies the ≥2/3 rule and adopts the converged output." Both can be true simultaneously, but the wording is genuinely contradictory as written.

**Recommended fix** (different from `fr_changes.md`): Align both specs on the *mechanical gate* framin[0m
[0m← [0mWrite /Users/ericstone/Public/MAGI/debates/2026-06-23/magi-quinte-fix/opencode_review.md
Wrote file successfully.
[0m
Review written to `/Users/ericstone/Public/MAGI/debates/2026-06-23/magi-quinte-fix/opencode_review.md`.

## Summary of my independent assessment

**9 of 10 findings agreed with; 2 with caveats.** Key conclusions:

| # | Verdict | Note |
|---|---------|------|
| 1 | ✅ Agree | Real contradiction; fix = mechanical-gate wording, keep §1.3 separation clause |
| 2 | ✅ Agree | Standardize on 5; thresholds → 3/5, 2/5, 1/5; also update Invariant #4 floor |
| 3 | ⚠️ Partial | Resolves on close reading (delegate_task used for sub-agents, forbidden for dispatch); fix = clarify, **don't delete** |
| 4 | ✅ Agree | Exempt MAGI from 120s; **don't** touch the kimi backoff timer (different semantics) |
| 5 | ✅ Agree | Non-exhaustive ≠ non-mutually-exclusive; add anytime as 3rd deployment |
| 6 | ✅ Agree | **Narrow fix only**: stop attributing confidence to MAGI; keep QUINTE's own JSON fields |
| 7 | ✅ Agree | Most severe — downgrade "No exceptions" + add interim git-hook enforcement |
| 8 | ✅ Agree | Local paths + fix `main`/`master` branch mismatch (latent broken link) |
| 9 | ✅ Agree | Bump version + add content (not just label) + fix duplicate §5 heading |
| 10 | ⚠️ Partial | KOZO **is defined** in HIGHBALL — add cross-ref, **don't remove** |

**Three disputes with the sibling `fr_changes.md` plan:**
1. It proposes **removing KOZO** — wrong; KOZO is a ratified HIGHBALL component (`HIGHBALL/README.md:151`). I recommend a cross-reference instead.
2. It proposes **stripping all `confidence` from QUINTE** — overreach; issue #6 is only about the MAGI contradiction. QUINTE's own JSON-sidecar confidence is unrelated.
3. It proposes **deleting `delegate_task` from README** — makes the README less accurate; the primitive is genuinely used (for sub-agents).

I also flagged an extra bug the audit missed: **duplicate §5 headings** in `theoretical-foundation.md` (two sections both numbered §5), and a latent broken cross-link from the `main`/`master` branch mismatch.
sfies Invariant #4's ≥1/3).
- **(B) Keep 3-agent panels, explain selection**: R2 has 5 participants; for each disputed claim a 3-agent panel is selected (rotating, with cross-model guarantee). Keep ≥2/3 tallies.

I lean toward **(A)** — it's simpler, matches the 5-pseudonym design, and removes the unexplained 3-from-5 selection. `fr_changes.md` also picks (A), so I agree there. But note: this changes Invariant #4's cross-model floor from "1/3" to "2/5", which should be updated in §5 Invariant #4 (`PROTOCOL.md:329`) for consistency.

---

### Issue 3 — delegate_task: PROTOCOL forbids, README depends

**Agree: PARTIAL (apparent contradiction, resolvable; Medium severity)**

- `QUINTE/specs/PROTOCOL.md:7` — "delegate_task is explicitly forbidden for QUINTE/MAGI dispatch (breaks model heterogeneity)."
- `QUINTE/README.md:99` — "It is not implementation-agnostic — it depends on Hermes-specific primitives (delegate_task, memory, skill persistence, cron, session_search)."

On close reading these are **not actually contradictory**: §1.2 of the PROTOCOL (`PROTOCOL.md:47`) shows `delegate_task` is used for *internal cc sub-agents* (Explore, Plan, general-purpose reviewers), while it is *forbidden for dispatching the heterogeneous debate participants* (cc/cw/omp/MAGI, which use `terminal`/bash). The README lists `delegate_task` as a Hermes primitive the protocol depends on (true, for sub-agents); the PROTOCOL forbids it *for cross-model dispatch* (also true).

**Root cause**: The README doesn't distinguish the two uses, so a reader reasonably sees a contradiction. This is a documentation-clarity issue, not a logical inconsistency.

**Recommended fix** (different from `fr_changes.md`): Do **not** simply remove `delegate_task` from the README — that loses true information (the protocol *does* depend on it for internal sub-agents per §1.2). Instead, clarify the scope: "depends on Hermes-specific primitives (terminal dispatch for heterogeneous agents, delegate_task for internal sub-agents, memory, skill persistence, cron, session_search)." This preserves both truths and removes the apparent conflict. The `fr_changes.md` plan to delete `delegate_task` from the primitive list would make the README *less* accurate, not more.

---

### Issue 4 — Timeout mismatch: 120s vs 180s

**Agree: YES (real inconsistency, High severity)**

- `QUINTE/specs/PROTOCOL.md:134` — "Timeout 120s → kill + shrink prompt + retry." (R1 discipline)
- `QUINTE/specs/PROTOCOL.md:279` — "Convergence gate timeout: 180s total." (MAGI)
- `QUINTE/specs/PROTOCOL.md:299` — "kimi 80% thinking tax: wait 120s" (timeout error class)
- `QUINTE/specs/PROTOCOL.md:313` — "180s deadline" (agent→MAGI substitution)
- `MAGI/specs/PROTOCOL.md:113` — "180s deadline" (substitution)

MAGI is one of the 5 R1 elements, yet its convergence-gate budget (180s) exceeds the R1 per-agent timeout (120s). Under the literal R1 rule (`PROTOCOL.md:134`), MAGI would be killed at 120s — before its own 180s convergence gate can complete. The 120s on line 299 (kimi thinking-tax wait) is a different concern but adds to the inconsistency: two different "120s" values with different semantics.

**Root cause**: MAGI's convergence gate (3 parallel delegates) was given 180s, but the generic R1 timeout wasn't updated to accommodate it. The substitution deadline (180s) and convergence-gate budget (180s) are consistent with each other, but the R1 discipline timeout (120s) is the outlier.

**Recommended fix**: Do **not** blindly change 120s→180s everywhere (as `fr_changes.md` proposes). The kimi thinking-tax wait (`PROTOCOL.md:299`) is a recovery backoff, not a dispatch deadline — changing it to 180s is semantically wrong. Instead:
- Exempt MAGI explicitly from the R1 120s deadline: "R1 per-agent timeout 120s (MAGI excepted — see §4.5 convergence-gate budget 180s)."
- Or raise the R1 timeout to 180s uniformly (simpler, but increases cost for all agents).
- Leave the kimi backoff at 120s (it's a backoff timer, not a dispatch deadline).

I prefer the explicit-exemption approach — it preserves the 120s cost discipline for the 4 non-MAGI agents while giving MAGI its needed 180s.

---

### Issue 5 — Mode A/B not exhaustive (MAGI v3.1 anytime deployment)

**Agree: YES (real omission, Medium severity)**

- `QUINTE/specs/PROTOCOL.md:70` — "MAGI operates in two mutually exclusive modes"
- `QUINTE/specs/PROTOCOL.md:80` — "Mode A and Mode B are mutually exclusive per session."
- `MAGI/specs/PROTOCOL.md:5` (v3.4 intro) — "Three doctors dispatchable anytime — Mode A (pre-verification), Mode B (QUINTE R1 embedded), or independent."
- `MAGI/specs/PROTOCOL.md:58` — "Mode A and Mode B cannot both be active in the same session."
- `MAGI/specs/PROTOCOL.md:165` (v3.1 changelog) — "Anytime deployment... Mode A/B remain but non-exhaustive."

MAGI v3.1 added a third "anytime/independent" deployment, and the v3.4 intro (`MAGI:5`) acknowledges "or independent." But §2.1a (`MAGI:53-58`) still frames only two modes, and QUINTE §1.4 (`QUINTE:70,80`) describes "two mutually exclusive modes" with no mention of anytime deployment. QUINTE's description of MAGI is stale relative to MAGI v3.1+.

**Important nuance**: "Mutually exclusive" (A and B can't both be active) is logically independent of "exhaustive" (A and B are the only options). The specs conflate the two. MAGI v3.1 correctly says A/B are non-exhaustive (there's also anytime/independent) while remaining mutually exclusive in the sense that A and B proper can't both run simultaneously. QUINTE's "two mutually exclusive modes" is wrong on exhaustiveness, not on mutual-exclusivity.

**Recommended fix**: In QUINTE §1.4, change "two mutually exclusive modes" → "two primary modes (Mode A standalone, Mode B embedded), plus anytime independent deployment (MAGI v3.1+)." Keep the A/B mutual-exclusivity clause (they *are* mutually exclusive with each other) but note non-exhaustiveness. Update MAGI §2.1a to formally document the third "anytime" deployment option (currently only in the changelog and intro). Both repos need the fix; `fr_changes.md` correctly targets both.

---

### Issue 6 — Confidence annotation: QUINTE claims MAGI has it, MAGI says no

**Agree: YES (real contradiction, Medium severity — but the fix must be narrow)**

- `QUINTE/specs/PROTOCOL.md:76` — "≥2/3 converge → answer with confidence annotation"
- `MAGI/specs/PROTOCOL.md:100` — "No weighted voting. No confidence score. Binary gate."
- `MAGI/specs/PROTOCOL.md:97` — "Annotates: `[MAGI 2/3]` or `[MAGI 3/3]`."

Direct contradiction: QUINTE says MAGI Mode A produces an "answer with confidence annotation"; MAGI explicitly states "No confidence score."

**Ambiguity**: "Confidence annotation" *could* be read as the `[MAGI N/3]` convergence-ratio annotation (3/3 is "higher confidence" than 2/3). But MAGI §2.4 (`MAGI:100`) says "No confidence score" — and a convergence ratio is a tally, not a score. The QUINTE wording strongly implies a numeric confidence output, which MAGI disclaims.

**Recommended fix** (disputing `fr_changes.md`): This is a **narrow** issue about the MAGI contradiction, **not** a mandate to strip all `confidence` from QUINTE. The correct fix is to change `QUINTE:76` from "answer with confidence annotation" → "answer with `[MAGI N/3]` convergence annotation." That removes the contradiction with MAGI's "no confidence score" while preserving MAGI's actual `[MAGI N/3]` annotation.

**I dispute the `fr_changes.md` plan to remove all `confidence` references from QUINTE.** QUINTE's JSON sidecar `confidence` field (`PROTOCOL.md:102`), the R1 schema `confidence` (`PROTOCOL.md:119`), and the evidence-validation gate's confidence weighting (`PROTOCOL.md:109,144`) are QUINTE's *own* design choices, unrelated to what MAGI outputs. Stripping them would gut QUINTE's evidence-weighting mechanism and break the JSON sidecar contract. The audit issue is specifically "QUINTE claims MAGI has confidence annotation but MAGI says no" — the fix is to stop claiming MAGI produces confidence, not to remove QUINTE's own confidence fields.

---

### Issue 7 — BANNIN unimplemented; push gate depends on spec-only component

**Agree: YES (real risk, High severity)**

- `QUINTE/specs/PROTOCOL.md:331` (Invariant #6) — "Push gate. Any push (code, config, docs) requires prior QUINTE (R1+R2+R3). No exceptions."
- `QUINTE/specs/PROTOCOL.md:346` — "BANNIN-enforced pre-write check: QUINTE verdict trail required."
- `QUINTE/specs/theoretical-foundation.md:121` — "BANNIN is specification-only (as of 2026-06-19). The Kennōmon architecture gate depends on this unimplemented component."

Invariant #6 asserts "No exceptions" and the 憲門 (Kennōmon) gate is "BANNIN-enforced," but BANNIN is spec-only. The push gate is therefore unenforced — it's aspirational, not operational. This is the most consequential finding: a "no exceptions" invariant backed by a component that doesn't exist.

**Recommended fix** (more than `fr_changes.md` proposes): Simply annotating "specification-only" (as `fr_changes.md` suggests) is necessary but insufficient — an unenforced "no exceptions" invariant is misleading. Two additional actions:
1. **Downgrade Invariant #6 language** until BANNIN ships: "Push gate (target): Any push should be preceded by prior QUINTE. Enforcement pending BANNIN implementation; interim enforcement via KENGEN git hook." Keep the aspiration, drop the false "No exceptions" claim.
2. **Add an interim enforcement mechanism**: a git `pre-push` hook (part of KENGEN) that checks for a QUINTE verdict trail before allowing pushes. This closes the gap until BANNIN is built.
3. The theoretical-foundation.md already flags this honestly (`theoretical-foundation.md:121-123`) — that's good; the PROTOCOL and README need the same honesty.

---

### Issue 8 — Missing / inconsistent local cross-references

**Agree: YES (real inconsistency, Low severity)**

Cross-references are inconsistent across the four files:
- `QUINTE/specs/theoretical-foundation.md:147-149` — uses **local relative paths** (`../../RASHOMON/...`, `../../MAGI/...`, `../../HIGHBALL/...`). These resolve correctly since the repos are siblings under `Public/`.
- `QUINTE/specs/PROTOCOL.md:82` — uses a **GitHub URL** to MAGI (`blob/main/specs/PROTOCOL.md`).
- `MAGI/specs/PROTOCOL.md:58` — uses a **GitHub URL** to QUINTE (`blob/master/specs/PROTOCOL.md`).
- `QUINTE/README.md:44` — uses GitHub URLs to RASHOMON and HIGHBALL.
- `QUINTE/README.md:79` — GitHub URL to MAGI.

Two concrete problems:
1. **Mixed schemes**: Some cross-refs are local relative paths, others are GitHub URLs. No consistency.
2. **Branch mismatch** (the sharper bug): QUINTE links to MAGI on `blob/main/` (`PROTOCOL.md:82`), but MAGI links to QUINTE on `blob/master/` (`MAGI:58`). If the repos use different default branches, one of these links is broken.

**Recommended fix**: Standardize on local relative paths for sibling-repo references (they're co-located on disk under `Public/`), keeping GitHub URLs as secondary/fallback. From `QUINTE/specs/PROTOCOL.md`, MAGI is at `../../MAGI/specs/PROTOCOL.md`; from `QUINTE/README.md`, MAGI is at `../MAGI/specs/PROTOCOL.md`. Verify and align the default branch name (`main` vs `master`) across both repos — this is a real latent broken-link bug, not just style.

---

### Issue 9 — theoretical-foundation still v1.0

**Agree: YES (stale doc, Medium severity)**

- `QUINTE/specs/theoretical-foundation.md:4` — "Version: 1.0 (2026-06-18) — Initial, post-QUINTE audit"
- `QUINTE/specs/theoretical-foundation.md:166` — "Version 1.0 — 2026-06-18"
- `QUINTE/specs/PROTOCOL.md:5` — "v3.4 (2026-06-20)"

The theoretical foundation is v1.0 dated 2026-06-18, two days before the protocol hit v3.4 (2026-06-20). v3.4 added substantial mechanisms — JSON sidecar + evidence validation gate, R2 anonymity + mind-change tracking, 6-tier error classification, agent→MAGI substitution, cross-repo consistency — none of which are reflected in the theoretical foundation. The doc even references "v3.4" in passing (e.g., `theoretical-foundation.md:33` "maintained in v3.4") but carries a v1.0 version stamp and pre-v3.4 date.

There's also a **duplicated section heading**: §5 "Current Limitations" (`theoretical-foundation.md:108`) and §5 "Minimum Evidence Requirements" (`theoretical-foundation.md:127`) — two sections numbered §5. This is an independent doc bug worth fixing in the same pass.

**Recommended fix**: Bump to v1.1 (or v2.0) dated 2026-06-20. Add a section covering the v3.4 additions (JSON sidecar/evidence validation, R2 anonymity, error classification, substitution) and their theoretical status. Fix the duplicate §5 heading (renumber the second to §6). Update the closing version line. `fr_changes.md` only bumps the version stamp without adding content — that's a version-label change, not a real update.

---

### Issue 10 — KOZO undefined

**Agree: PARTIAL (valid within scope; but fix is cross-ref, not removal; Low severity)**

- `MAGI/specs/PROTOCOL.md:98` — "≤1/3 agree → Diverge → Escalate to QUINTE. Disagreement pattern recorded for KOZO."
- KOZO is **not** defined anywhere in `MAGI/specs/PROTOCOL.md` or `QUINTE/specs/PROTOCOL.md`.

So within the two MAGI/QUINTE specs, KOZO is indeed undefined — the audit finding is correct *as scoped to these files*. **However**, my cross-repo grep shows KOZO is a real, ratified, well-defined HIGHBALL component:
- `HIGHBALL/README.md:11` — "KOZO | HIGHBALL measurement layer | Attention compliance + cross-detection sensitivity"
- `HIGHBALL/README.md:151` — "KOZO — Attention Quality & Cross-Detection Sensitivity" (full definition, 3 operational layers, CDA metric, Diversity score, Goodhart firewall)
- `HIGHBALL/ontology/highball-ontology.md:12` — "KOZO | 構造 | Attentive? | Measurement / meta-governance | Cross-phase"
- `RASHOMON/CONCEPTS.md:23` — "KOZO | kōzō (structure) | HIGHBALL attention quality measurement layer"
- `HIGHBALL/README.md:277` — "KOZO was ratified as a HIGHBALL component 2026-06-12 (5/5 QUINTE consensus)"

KOZO is the meta-governance/attention-quality measurement layer in HIGHBALL. It records divergence patterns (CDA — Cross-Detection Agreement) for post-hoc analysis. So MAGI §2.4's "Disagreement pattern recorded for KOZO" is a legitimate reference to a real system — it's just **not defined or cross-referenced** in the MAGI spec.

**Recommended fix** (disputing `fr_changes.md`): Do **NOT** remove the KOZO reference — that would delete a correct, meaningful hook into HIGHBALL's measurement layer. Instead, add a one-line definition + cross-reference in `MAGI/specs/PROTOCOL.md`: e.g., a footnote or §2.4 note: "KOZO (構造, HIGHBALL attention-quality measurement layer) records disagreement patterns for post-hoc audit; see [HIGHBALL spec](../../HIGHBALL/README.md#kozo--attention-quality--cross-detection-sensitivity)." This matches the pattern already used in `QUINTE/specs/theoretical-foundation.md:147-149` (cross-refs to sibling repos). The `fr_changes.md` plan to "remove `Disagreement pattern recorded for KOZO`" would silently drop a real integration point — I disagree with that approach.

---

## Where I Dispute the Sibling Fix Plans

I reviewed `fr_changes.md` and `gold_fixes.md` (the latter is an empty stub). The `fr_changes.md` plan has three proposals I consider **wrong** or overreaching:

1. **"KOZO: define or remove" → removes KOZO** (`fr_changes.md:75`). Wrong. KOZO is a defined, ratified HIGHBALL component (Attention Quality & Cross-Detection Sensitivity, `HIGHBALL/README.md:151`). Removing the reference breaks a real integration. Fix: add a cross-reference definition, not deletion.

2. **"Confidence: remove from QUINTE" → strips all confidence fields** (`fr_changes.md:46-61,128-136`). Overreach. Issue #6 is specifically about QUINTE *claiming MAGI produces a confidence annotation* that MAGI disclaims. The fix is to stop attributing confidence output to MAGI (`PROTOCOL.md:76`), not to delete QUINTE's own JSON-sidecar `confidence` field, R1 schema confidence, and evidence-validation weighting — those are QUINTE's independent design choices. Stripping them would break the JSON sidecar contract and the evidence-weighting mechanism.

3. **"delegate_task: remove from README"** (`fr_changes.md:11,169`). Partially wrong. delegate_task IS a real dependency (for internal cc sub-agents per `PROTOCOL.md:47`), just forbidden for cross-model dispatch. Removing it from the README's primitive list makes the README *less* accurate. Fix: clarify scope (terminal for heterogeneous dispatch, delegate_task for internal sub-agents), don't delete.

Additionally, `fr_changes.md` proposes changing the kimi thinking-tax backoff (`PROTOCOL.md:299`) from 120s→180s as part of issue #4. That's a semantic error — the 120s there is a recovery backoff timer, not a dispatch deadline. Only the R1 dispatch timeout (`PROTOCOL.md:134`) needs reconciliation with MAGI's 180s convergence budget.

---

## Recommended Fix Priority

| Priority | Issue | Rationale |
|----------|-------|-----------|
| P0 | #7 (BANNIN/push gate) | "No exceptions" invariant backed by non-existent component — actively misleading |
| P0 | #4 (timeout) | MAGI killed at 120s before its 180s gate can complete — functional breakage |
| P1 | #1 (gate ownership) | Core protocol contradiction between the two canonical specs |
| P1 | #2 (R2 count) | Refutation tallies don't match declared R2 participants |
| P2 | #6 (confidence annotation) | Narrow MAGI contradiction; quick fix on one line |
| P2 | #5 (Mode A/B) | Stale QUINTE description of MAGI; non-exhaustive |
| P2 | #9 (theoretical-foundation v1.0) | Stale + duplicate §5 heading |
| P3 | #3 (delegate_task) | Clarification only; resolvable on close reading |
| P3 | #8 (cross-refs) | Style + latent broken branch link (`main` vs `master`) |
| P3 | #10 (KOZO) | Add cross-reference to HIGHBALL; do not remove |

---

## Cross-Repo Verification Performed

To independently assess issues #7 and #10, I grepped `KOZO` and `BANNIN` across `/Users/ericstone/Public/`:
- **KOZO**: 100+ matches. Defined in `HIGHBALL/README.md:151` (Attention Quality & Cross-Detection Sensitivity), `HIGHBALL/ontology/highball-ontology.md:12`, `RASHOMON/CONCEPTS.md:23`. Ratified 2026-06-12 per `HIGHBALL/README.md:277`. Scripts exist (`HIGHBALL/scripts/kozo_baseline.py`). KOZO is real and implemented — it's just undefined *within the MAGI/QUINTE specs*.
- **BANNIN**: Defined in HIGHBALL as the runtime session-level guard (`hermes-core-rules-mac-x86` / `hermes-core-rules-win` reference it). `QUINTE/specs/theoretical-foundation.md:121` correctly flags it as spec-only as of 2026-06-19. No runtime implementation found in the grepped paths — confirms issue #7.

---

*Independent assessment by opencode (glm-5.2). sine ira et studio.*
