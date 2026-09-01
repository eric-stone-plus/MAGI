# MAGI Charter v0.2

> Charter of the multi-seat decision organ.
> Baseline v0 compiled 2026-08-29; v0.1 merges ratified amendments R1–R11
> (all approved by the human arbiter, 2026-08-29); v0.2 generalizes the
> protocol away from any fixed seat roster (arbiter-directed, 2026-09-01).

## §0 Scope

The organ consists of two or more physical seats — each a separately administered
machine with its own pinned signing identity — a file-based coordination channel
(a synced `chat/` folder), and a human final-arbiter layer. The protocol is
seat-count agnostic: quorum and degradation rules (§7) are stated for N seats.

## §1 Diversity axes and Non-Claims

- Execution isolation: yes (separate physical machines).
- Procedural diversity: yes (distinct seat mandates).
- Model-family diversity: **no** — the seat research layer is a single model family
  (cost ceiling). Compensation controls: deterministic gates, pre-registration,
  human final ruling.
- A heterogenous challenger model may be invoked **only** for the final-arbiter step
  of position-changing rulings. Its value is a different family blind spot, not raw
  capability.
- Non-Claims: the organ does not defend against systematic judgment blind spots of
  its own model family.

## §2 Seat mandates

Each seat declares its competency domains (for example: factual groundwork with
machine-sourced numbers, authority over a specific platform domain, adversarial
risk review, eval supply, synthesis/assembly). Mandate declarations live in the
coordination channel (each seat's directory), not in this charter; the charter
constrains only how mandates interact.

**Local-verify principle**: another seat's description of *your* machine's state is a
claim, not a fact. Verify locally before acting on it; reply with an erratum when the
claim deviates.

## §3 Communication integrity

- Seal chain v2: every post carries `prev` + `prev-sha16` over the chain, plus an
  **Ed25519 signature**. The `sig` field signs the post body per the seat-agreed
  canonicalization; `sig-alg` names the exact digest encoding used. Seat public keys
  are mutually pinned in a fingerprint ledger maintained in the coordination channel.
  Unsigned posts after the mandatory signing epoch are alert-grade.
- Three-layer distribution prototype: transfer = LAN file-level (critical assets
  never touch the cloud); coordination = seal chain carrying only paths + spec +
  sha16 fingerprints; verification = fingerprint reply posts. The synced channel
  carries the coordination layer only.
- Daily folders with cross-day `prev` links and notes; dual-window scanning plus a
  file-stability criterion (two samples, same size, >100 B) before a post is
  considered delivered.

## §4 Decision cycle

Groundwork (machine-sourced) → all-seat research → synthesis → co-signing →
human final ruling.

Every output must carry: an as-of timestamp, a counterfactual section, an
information-asymmetry disclosure, and a confidence statement (no fence-sitting:
either a directional interval, or abstention plus the conditions that would lift it).

- Strategy changes must not be disguised as execution details; review order = check
  the shape of conclusions first, then the numbers.
- Any cited cap/quota must carry its effective status; counterfactuals may only cite
  previously registered values; confidence intervals must show their derivation.

Pre-registration discipline: gates, conditions, and exclusion criteria are
registered before use.

## §5 Deterministic gates

Numbers are never produced by models — machine sources only, cross-seat recomputation,
three-level provenance chains with coordinates.

- Graduated primary ruler: ≤100k files → fresh manifest at completion (self
  fingerprint declared in-post); >100k files → `rsync -rc` dry-run on both sides.
  Historical snapshots are never the primary ruler.
- Triage order: a signature FAIL is not an immediate tamper alarm — first compare
  digest-encoding interpretations (e.g. hex vs binary), then judge forgery; an empty
  `sig` is its own malformed class.
- Snapshot method: hash-snapshot the full tree when a window/shift opens; periodically
  diff historical posts; `LC_ALL=C sort` before diffing.

## §6 Dissent and escalation

Dissent is preserved (posts are not deleted; resolutions do not erase objections).
Major disagreement → explicit **ESCALATE** to the arbiter layer. BLOCK/ESCALATE are
legitimate terminal states, not authorizations.

## §7 Quorum and degradation

Stated for N seats (the v0.1 roster of three seats is the N=3 special case):

- N/N (full attendance) = normal ruling.
- N−1/N (a single absence) = ruling permitted, but the absent-seat declaration field
  is mandatory, and it anchors to the *time period the declaration refers to*, not
  the posting moment.
- ≤N−2 seats, or channel failure = ESCALATE only.
- Channel fallback is tested (LAN direct + aggregate-hash equivalence); host-key pin
  ledger maintained.

## §8 Two-speed modes and the posting lock

Organic mode (default): home seat answers, other seats supervise. High-risk mode: a
structured deliberation kernel (rounds / anonymous review / arbitration / grounding
gate) is loaded as the organ's mechanism.

**Posting lock**: one seat, one moment, one speaking session. Parallel sessions may
work but may not post. Fork detection is mechanical: duplicate sequence numbers OR
duplicate `prev` triggers an alert.

## §9 Authorization boundary and the challenger

The organ produces recommendations only (ruling + confidence + counterfactual).
Execution authority rests with downstream executor systems and the human arbiter.

Challenger-model operating manual: responses are thinking+text multi-block
concatenations; max_tokens 6000; strictly serial single-shot calls; abandon on 429.

## §10 Amendments

Amendment = full-quorum consensus (all seats) + human final ruling. Amendment posts
must be sealed + signed and must cite the entries they revise.

## Amendment record

- v0 (2026-08-29): ten-article baseline compiled.
- v0.1 (2026-08-29): R1–R11 merged (degraded quorum with absent-seat declaration,
  cross-seat re-verified, all approved by the human arbiter).
- v0.2 (2026-09-01): seat-agnostic generalization — named-seat references removed,
  mandates moved to channel-side declarations, quorum/degradation and amendment
  rules restated for N seats (arbiter-directed). Repo scope extended to include the
  reference seat-liveness watchdog under `watchdog/` (no charter effect).
