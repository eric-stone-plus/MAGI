---
name: kansa-audit
description: >-
  QUINTE R3 KANSA audit — independent blind review of R1+R2 evidence,
  source code verification, contradiction resolution, structured verdict
  output. Trigger: KANSA, R3-B, independent audit, resolve contradictions
  from source, verify claims against code.
---

# KANSA Audit (QUINTE R3)

KANSA is the independent verification phase of QUINTE multi-agent debate.
An auditor (R3-B) blindly reviews all R1+R2 evidence, resolves flagged
contradictions from source code, and produces a structured verdict WITHOUT
reading the other auditor's R3-A findings.

## Workflow

### Phase 1: Read All Evidence

1. Read ALL R1 files first (typically 4: hermes, codewhale, claude, omp)
2. Read ALL R2 files next (typically 4: the same agents as synthesizers)
3. Do NOT read any R3-A verdict files — this is a blind audit
4. Take note of: consensus zones, contradictions flagged by R2s, claims
   each agent made, evidence gaps

### Phase 2: Identify Key Contradictions

R2 cross-audits typically flag:
- **HC (Hard Contradictions)**: Mutually exclusive claims between analysts
- **SD (Soft Discrepancies)**: Different framing, possibly both right
- **LG (Logical Gaps)**: Claims missing necessary support
- **UV (Unverified)**: Cannot confirm from R1 texts alone

Prioritize HC and LG items for source code verification.

### Phase 3: Source Code Verification

For each contradiction:
1. Locate the exact source file and line range cited by each analyst
2. Read the actual source code — trust NO analyst's description
3. Trace the full code path, including lines before and after the cited
   range (analysts often miss pre/post logic)
4. Document the specific lines that prove or disprove each claim
5. Identify which analyst is correct, which is wrong, and WHY

Critical: Analysts cite specific line numbers — verify those exact lines
AND the surrounding context. Claude R1's HC-1 error (claiming gateway
hygiene model was hardcoded) happened because it stopped at line 8469
and missed override code at lines 8482-8486.

### Phase 4: Produce Structured Verdict

Output sections:

1. **Contradiction Resolution** — One section per HC/SD, with:
   - Claim table (who said what)
   - Source evidence (exact code, line numbers)
   - Clear VERDICT with winner/loser

2. **Evidence Verification** — Claims confirmed by source:
   - Each claim with source file, lines, exact code
   - CONFIRMED or REFUTED

3. **Cross-Check** (blind): What the other auditor likely claimed
   - Based on R1+R2 evidence only
   - Mark as "likely claim" since R3-A was not read

4. **Errors in Other Analysts** — Source-verified errors:
   - Analyst, error description, severity, source evidence

5. **Final Independent Verdict**
   - Resolution table for all contradictions
   - Analyst reliability ratings
   - Source-verified truth for the central question

6. **Appendix**: Source code reference table with file, lines, and verification status

## Pitfalls

- **Trusting analyst line-number claims without verification.**
  Always read the actual source. Analysts cite correct line numbers
  but may miss override/fallback code a few lines away.
- **Missing pre/post logic.** When an analyst cites "line X does Y",
  read 20 lines before and after. Gateway hygiene model override (HC-1)
  was missed by Claude because the override was 16 lines after the
  initial default.
- **Reading R3-A during blind audit.** This contaminates independence.
  Declare "blind audit constraint maintained" and do not open the other
  auditor's file.
- **Accepting "both agents could be right" without source verification.**
  HC items are mutually exclusive by definition. Source code always
  picks one winner.
- **Overlooking configuration interaction.** When code has config
  overrides (lines that read from config.yaml), those overrides can
  change behavior without changing the code. Always trace config read
  paths.
- **Not distinguishing threshold from model.** Gateway hygiene has TWO
  independent properties: the threshold (0.85, hardcoded) and the model
  (overridable from config). Conflating them produces wrong conclusions.
- **Cross-document contradiction blindness.** When rules are distributed
  across multiple documents (PROTOCOL.md, SKILL.md, SOUL.md), analysts
  often verify each document in isolation and miss conflicts between them.
  Apply contract-review discipline: trace every rule on a subject across
  ALL documents before concluding consistency. See `references/contract-review-analogy.md`
  for the full pattern library (2026-06-19).

## Verification Steps

After producing the verdict:
1. Every contradiction has a source citation with exact line numbers
2. Every CONFIRMED claim has a source code reference
3. The verdict includes both winner and loser for each contradiction
4. No R3-A file was read (blind audit constraint maintained)
5. The final verdict answers the central question with source-verified facts
