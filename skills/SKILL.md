---
name: magi
description: Run or verify the headless MAGI triadic cross-family technical adjudication CLI. Use for high-risk architecture, irreversible decisions, SSH-only workflows, or requests needing three isolated Hermes review profiles, three complete single-family QUINTE dossiers, six anonymous cross-reviews, and a final PASS/BLOCK/ESCALATE product.
---

# MAGI Cross-Verification

Use the atomic, display-independent `magi` CLI. Do not invoke seats, QUINTE
lanes, reviewers, or the Final Adjudicator directly from this skill.

## Run

1. Prepare one Brief `1.1` with an explicit action binding and scope.
2. Initialize exactly `seat-m`, `seat-d`, and `seat-g`.
3. Run `magi build-dossiers TRIAL_DIR --config BUILDERS.json`.
4. Confirm all three dossiers are frozen before exchange.
5. Run `magi run TRIAL_DIR --config AGENTS.json`; completed output is Product
   Summary `1.0`, including exact final dissent.
6. Run `magi verify-product TRIAL_DIR` and retain the closed product summary.

Resume with the same commands and byte-identical configs. Configuration,
runtime, dossier, review, or verdict drift must fail closed.

## Boundaries

- Treat each internal QUINTE run as single-family across all seven roles.
- Require `auto_primary_arbiter=true` so every inner QUINTE product is headless.
- Use only native production carriers: MiMo=`mimo`, DeepSeek=`reasonix`,
  OpenAI=`codex`; never fall back to OMP or another excluded carrier.
- Keep profile diversity separate from model-family diversity.
- Require three distinct families, profile digests, and QUINTE run IDs.
- Require all six anonymous directed reviews.
- Require every reviewer to run through its frozen complete Hermes profile;
  reject a native model wrapper, changed profile path/digest, or undeclared
  methodology trace.
- Accept the final conclusion only after deterministic verification.
- Never treat a residual trace alone as a completed MAGI product.
- Never claim MAGI proves truth or a universal confidence percentage.
- Route external authorization and protected writes through HIGHBALL.

Read `../specs/PROTOCOL.md` only when contract details are needed.
