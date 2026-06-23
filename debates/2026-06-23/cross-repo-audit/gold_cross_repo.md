**Cross-repo architecture audit: hermes-core-rules-mac-x86 (live Mac constitution), hermes-core-rules-win (Win mirror), RASHOMON, HIGHBALL, QUINTE, MAGI.** Date context ~2026-06-23. Brutally honest findings follow. All paths relative to `/Users/ericstone/Public/`.

### Executive Summary (Core Contradictions)
- **RASHOMON/HIGHBALL anchor QUINTE/MAGI directionally but not precisely on gates.** RASHOMON and HIGHBALL correctly position themselves as "why" (philosophy) and "constraints" (KANSA/KENGEN/BANNIN/KOZO). QUINTE and MAGI cross-reference them. However, gate definitions (the 4 + the 5th) are misaligned and stale across the board.
- **Mac vs Win constitutions disagree on MAGI model mappings and violate invariants.** Mac is heterogeneous (grok/kimi/mimo). Win uses kimi + kimi + mimo (same base model for Gold/Fr). MAGI spec forbids this.
- **HIGHBALL's gates (incl. Kennomon/憲門) are not consistently reflected in QUINTE protocol or RASHOMON.** Constitutions claim "5-gate cardinality sync" and list 5 under Gate Precedence. QUINTE (authority) and RASHOMON still document 4.
- **MAGI >=2/3 convergence gate is consistent** across MAGI, QUINTE, constitutions, and SKILLs. This one thing holds.
- **Stale references, version skew, and internal contradictions are widespread.** Win README claims "three public repos" while listing four. RASHOMON/GATES.md frozen at v3.1. Win has an ancient magi/SKILL.md (v1.2, 5-stage theology). HIGHBALL kennomon is "Draft". QUINTE PROTOCOL still says "Four Gates" despite v3.4 changelog/constitution claims. BANNIN/Kennomon enforcement noted as "specification-only" in some QUINTE specs.

No single source of truth is fully authoritative. The "live constitution" (mac) is closest to reality but still drifts from the four public repos' specs.

### 1. Mac vs Win Constitutions — MAGI Model Mappings (Gold/Fr/Myrrh)
**Mac (hermes-core-rules-mac-x86):**
- SOUL.md:9-10, 22: "Gold (grok) + Fr (kimi) + Myrrh (mimo)"; "Gold→grok, Fr→kimi, Myrrh→mimo; >=2/3 gate".
- skills/multi-agent-debate/SKILL.md:31-33, 101-104: Explicit table and dispatch: `grok ... gold`, `kimi ... fr`, `mimo ... myrrh`.
- memories/MEMORY.md:37, 39: Same mapping. Gold=grok for engineering judgment.
- skills/magi/SKILL.md:40-43: Confirms grok/kimi/mimo.
- Heterogeneous (different providers: grok + kimi + mimo).

**Win (hermes-core-rules-win):**
- SOUL.md:13, 22: "On this machine: Gold=kimi, Fr=kimi, Myrrh=mimo (grok unreachable)"; explicitly labels it "heterogeneous pre-verification".
- USER.md:1: "MAGI three-model (Gold=kimi, Fr=kimi, Myrrh=mimo...)".
- MEMORY.md:37, 45: "kimi(Gold)+kimi(Fr)+mimo(Myrrh)".
- skills/multi-agent-debate/SKILL.md:133-135, 261-270: "grok→kimi on Win", Gold uses `kimi -p "Gold role: ..."`, Fr also kimi.
- skills/multi-agent-debate/magi/SKILL.md:3 (old v1.2): Still claims "Gold→grok, Fr→kimi..." (stale even internally).

**Violation**: MAGI/ontology/magi-ontology.md:15 and MAGI/specs/PROTOCOL.md:62, §3: "**No two delegates may use the same base model**. Three different training distributions required." Win directly violates the invariant that MAGI/QUINTE specs and RASHOMON philosophy require for "genuine heterogeneity" (see RASHOMON/README.md:31-33 on correlated errors).

Mac is correct per spec. Win is a pragmatic hack documented as if it satisfies the architecture. This is a material contradiction.

**Other Mac/Win diffs**:
- Mac README: "Four public repos". Win README:51: "**Three public repos** define..." (then lists the table with MAGI anyway). Stale text.
- Gate romanization: Mac uses macrons (Kyōmon, Shōmon, Kennōmon). Win drops them (Kyomon etc.). Minor but visible drift.
- Firepower/patience/KENGEN wording has small platform deltas but core rules align.
- Both claim "v3.4 alignment: 憲門 gate added, MAGI embedded R1, 5-gate cardinality sync" (mac README:91, win:91) but specs lag.

### 2. Gates: Amamon / Kyomon / Shomon / Kan'nukimon / Kennomon (HIGHBALL vs QUINTE)
**HIGHBALL** (source of the 5th):
- specs/kennomon-architecture-gate.md: Draft 2026-06-19. Defines 憲門 Kennōmon as BANNIN-enforced architecture gate on README/specs/ontology in the four public repos + SOUL.md. Pre-write lock + KENGEN push tie-in. "BANNIN, NOT hm."
- ontology/highball-ontology.md and README: Position KANSA (inside QUINTE), KENGEN/BANNIN, KOZO. KOZO described as "not a fifth gate" and "orthogonal to the four gates" (multiple places, e.g. HIGHBALL/README:157, 168, 243). Still references the old four when talking Phase -1.

**RASHOMON**:
- GATES.md: "QUINTE v3.1's four mandatory gates." Documents only Amamon (雨門), Kyōmon (鏡門), Shōmon (證門), Kan'nukimon (閂門). No Kennomon. Footer claims v3.4 but content is v3.1 (serial→parallel Shomon layers etc.). Stale.
- CONCEPTS.md:14 lists only the four.
- README and ontology correctly describe philosophy and MAGI as "Temple" (Gold/Fr/Myrrh) invited into QUINTE "Senate."

**QUINTE** (claimed protocol authority):
- specs/PROTOCOL.md:88: "Phase -1: Four Gates (hm, parallel)". Section 6: "## 6. The Four Gates" (lists Amamon, Kyōmon, Shōmon, Kan'nukimon; cross-repo check added v3.4 but no 5th).
- ontology/quinte-ontology.md:34, 45: "Four Gates", Phase -1 table has only four (雨門·鏡門·證門·閂門).
- CHANGELOG.md mentions 憲門. specs/security-assumptions.md and theoretical-foundation.md acknowledge Kennōmon as HIGHBALL/BANNIN (and note BANNIN is "specification-only" as of 2026-06-19; self-execution paradox).

**Constitutions** (both):
- Treat as unified precedence 1-5: 1. Amamon (ambiguity), 2. Kyōmon/Kyomon (mirror/comparative), 3. Shōmon/Shomon (testimony/full QUINTE), 4. Kan'nukimon, 5. Kennōmon/Kennomon (architecture/BANNIN on public repo critical paths + SOUL).
- Mac SOUL.md:26-32 (detailed with macrons). Win SOUL.md:26-32 (simpler, no macrons).
- Mac README:55 explicitly "five gates (雨門→鏡門→證門→閂門→憲門)".

**Inconsistency**: The four are hm Phase -1 input/anti-drift gates. Kennomon is a separate BANNIN tool-level guard (later addition). Constitutions + key decisions (2026-06-22) present them as a 5-cardinality list and claim sync. QUINTE (the spec) and RASHOMON do not reflect the update. HIGHBALL kennomon doc is draft and self-execution risks are openly noted. "Full QUINTE required for architecture changes" is text in SOUL but enforcement is aspirational/spec-only in places.

**HIGHBALL vs QUINTE protocol consistency on gates**: Partial. HIGHBALL correctly layers KANSA inside QUINTE Phase 6/R3. The input gates match at the name level but cardinality and Kennomon integration do not. KOZO is properly "measurement, not gate."

### 3. MAGI Convergence Gate (>=2/3)
Consistent and well-matched:
- MAGI/specs/PROTOCOL.md:96-98, §2.4: Binary `>=2/3` converge (annotate [MAGI N/3]) or `<=1/3` diverge → escalate. Markdown primary for gate; JSON sidecar separate (Myrrh evidence validation gate).
- MAGI/README.md:50-55, ontology:21-22: Same.
- QUINTE/specs/PROTOCOL.md:30, 80, 96, 107, 141: "internal convergence gate ACTIVE (≥2/3)", MAGI as one collective R1 element, output annotated, rx does not see inside.
- Constitutions: Explicit `>=2/3` (or ≥2/3) in SOUL and SKILLs for both platforms.
- SKILLs (mac multi-agent-debate + magi, win equivalents): Repeatedly state the gate.
- Mode A (standalone pre-verif) and Mode B (embedded R1) both use it; mutually exclusive.

No mismatch here. The gate is one of the few clean invariants.

### 4. Cross-References and Anchoring (RASHOMON/HIGHBALL → QUINTE/MAGI)
**Generally correct directionally**:
- QUINTE/README.md:44, ontology:184-188: References RASHOMON (why), HIGHBALL (constraints/KANSA), MAGI (embedded).
- MAGI/README.md:57-69, ontology:54-58, specs:134-138: MAGI as antechamber + R1 senator; links to QUINTE and RASHOMON.
- HIGHBALL/ontology:109-113, README:16: Explicitly positions against RASHOMON/QUINTE/MAGI. Cross-refs correct.
- RASHOMON/ontology:86, README:46-47: "The Temple (MAGI)" invited into "the Senate (QUINTE)"; references the three gifts.

**But**:
- Gate details lag (see above).
- MAGI defers model routing to "Hermes profile" (constitutions) — which then violates MAGI's own heterogeneity rule on Win.
- Some QUINTE docs (theoretical-foundation, security-assumptions) treat BANNIN/Kennomon as not-yet-operational.
- RASHOMON has rich debates/ but core GATES.md and CONCEPTS.md not updated for v3.4 5-gate or full MAGI embedding.
- No evidence of systematic link-rot or wrong repo names, but "specs/ unified" claim in constitutions is aspirational when gate sections diverge.

### 5. Other Stale References, Version Mismatches, Minor Issues
- Win README ecosystem text: "Three" vs table + reality (four repos).
- Win dedicated magi/SKILL.md: v1.2, old 5-stage Star/Offering/Journey/Manger/Revelation, still assumes grok for Gold. Contradicts the main multi-agent-debate/SKILL.md updates.
- RASHOMON/GATES.md: v3.1 content, "four gates", no Kennomon.
- QUINTE/PROTOCOL.md: Still "Four Gates" in Phase -1 and dedicated section despite 2026-06-22 claims of 5-gate sync and 憲門 addition in constitutions/CHANGELOG.
- HIGHBALL/kennomon: Draft status; multiple HIGHBALL files still say "four gates" when describing KOZO.
- Constitutions reference "specs/PROTOCOL.md" (QUINTE/MAGI) as authority, but then override/add gates.
- Both constitutions have detailed "after QUINTE" and Netsumon/KENGEN rules that align with HIGHBALL intent.
- Substitution tables (agent→MAGI and KANSA B fallbacks) are mostly consistent (cc→Myrrh etc.) but Win platform notes differ.
- Cross-repo consistency checks (v3.4, website/ sub-repo) mentioned in QUINTE but not uniformly enforced in all SKILLs.
- Old debates in all repos contain historical alignment work (e.g. 2026-06-08 to 06-22); current state has not fully absorbed it into the canonical .md files.

### Recommendations (Brutal)
1. **Fix heterogeneity or document the exception.** Win cannot claim "heterogeneous" with two kimi. Either route Gold to a different model (even if weaker) or update MAGI/QUINTE specs to allow platform-degraded mode with explicit penalty (e.g. lower weight, mandatory extra review).
2. **Decide on gates.** Either (a) make Kennomon the official 5th and update QUINTE PROTOCOL + RASHOMON GATES.md (and mark BANNIN as live), or (b) keep four Phase-1 gates + separate architecture enforcement and rewrite constitutions to stop listing "five gates" as a flat list.
3. **Sync the four repos' core docs.** The "specs/" are not unified while GATES.md, PROTOCOL.md Phase -1, and kennomon draft disagree on cardinality and enforcement.
4. **Clean Win README and its internal magi/SKILL.md.** Remove "three repos" lie. Either delete or mark the v1.2 magi skill obsolete.
5. **Enforce the claim "after protocol change, update all five constitutional files + re-QUINTE cross-audit."** The drift (especially gates + Win mappings) shows this process is not catching everything.
6. **Make BANNIN/Kennomon status explicit.** If it is still spec-only, constitutions claiming it as hard precedence overstate the guard.

The architecture intent (RASHOMON cross-detection + MAGI heterogeneity + QUINTE adversarial rounds + HIGHBALL constraints) is sound and mostly coherently referenced. The implementation of that intent in the live documents is not. Mac is the least broken; Win has platform reality colliding with invariants; the philosophy/constraint/protocol repos have not been fully updated for the "v3.4" claims made in June 2026.

This is the current state. Run a full QUINTE (with real MAGI) on the four key spec files + both SOULs to ratify fixes.
