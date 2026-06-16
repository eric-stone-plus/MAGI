# MAGI Ontology

> Structural ontology of the MAGI dialectical spiral protocol. Conceptual foundation in [RASHOMON ontology](../../RASHOMON/ontology/rashomon-ontology.md).

## Entity Catalog

### Gift (三博士の贈り物)

| Gift | Agent | Cognitive Mode | Core Question | Output Format |
|------|-------|---------------|---------------|---------------|
| Gold (金) | delegate A | Verification | "Is this TRUE?" | Verification tables + confidence levels |
| Frankincense (乳香) | delegate B | Synthesis | "What does this MEAN?" | Narrative synthesis |
| Myrrh (沒藥) | hm | Adversarial | "Where does this BREAK?" | Risk maps + fragility points |

**Constraint**: 3 agents only (hm + 2 delegates). Each Gift has unique structural output format → mismatch = drift detection.

### Phase (五段階)

| # | Name | Function | Duration |
|---|------|----------|----------|
| 0 | The Star (星) | hm structures problem, assigns Gifts | ~10s |
| 1 | The Offering (獻禮) | Three parallel analyses | Gold 36s, Frankincense 126s, Myrrh 40s |
| 2 | The Journey (旅路) | Dialectical spiral (each reviews previous) | ~60s/cycle |
| 3 | The Manger (馬槽) | Convergence gate (≥0.7 = pass) | ~5s |
| 4 | The Revelation (啟示) | Final verdict with confidence topology | ~15s |

**Constraint**: Max 3 spiral cycles (9 total reviews). Max 2 convergence restarts.

### Convergence Gate

| Dimension | Weight | Measures |
|-----------|:------:|----------|
| Factual alignment | 0.4 | Claim overlap across Gifts |
| Interpretive alignment | 0.3 | Narrative coherence |
| Risk alignment | 0.3 | Fragility point agreement |

**Threshold**: ≥0.7 → pass. Below → divergent → output with divergence map.

## Relation Catalog

| Relation | From | To | Cardinality |
|----------|------|----|-------------|
| carries_gift | agent | Gift | 1:1 per session |
| structures | hm (Star) | problem decomposition | 1:1 |
| analyzes | delegate | evidence (parallel) | Phase 1 |
| reviews | delegate_X | delegate_Y output (X≠Y) | Phase 2 spiral |
| converges | hm (Manger) | 3-dimension score | Phase 3 |
| reveals | hm | confidence topology | Phase 4 |

## Constraint Catalog

| Constraint | Value | Rationale |
|-----------|-------|-----------|
| Agents | 3 (hm + 2 delegates) | Three Gifts, three epistemological stances |
| Model | Agent-provided; DeepSeek recommended | Provider-agnostic; MiMo deprecated |
| Max spiral cycles | 3 | Diminishing returns |
| Max restarts | 2 | Divergent → output with divergence |
| Delegate timeout | 300s | Free tier latency |
| Total timeout | 1800s (30 min) | Hard cap |
| Convergence threshold | ≥0.7 | Below = insufficient alignment |

## Failure Mode Catalog

| Mode | Symptom | Detection | Recovery |
|------|---------|-----------|----------|
| Gift Confusion | Wrong output format | Structural mismatch | Flag, kill, retry with reinforced prompt |
| hm Self-Exemption | Myrrh output missing "Risk Map" | Check Phase 1 format | Reinforce Gift role |
| Spiral Stall | All delegates agree prematurely | Low tension score | Inject adversarial prompt |
| Convergence Cheating | Delegate inflates convergence score | Scores approach 1.0 unnaturally | Cross-check with raw claim overlap |
| Same-Model Blind Spot | All 3 delegates miss same issue | Single-model limitation, no cross-model diversity | Flag in verdict: "same-model limitation" |
| Delegate Timeout | Delegate exceeds 300s phase limit | 300s timeout per phase | Kill delegate, retry with reduced prompt |
| Spiral Oscillation | Delegates flip-flop between positions | Alternating agreement/disagreement | Hard stop at cycle 3, output with divergence |

## Domain Mapping to QUINTE/RASHOMON

| MAGI Concept | QUINTE/RASHOMON Concept |
|-------------|------------------------|
| Three Gifts (Gold/Frankincense/Myrrh) | Five Agents (hm/cc/cw/omp/rx) |
| Dialectical Spiral | Adversarial Cross-Review |
| Convergence Gate (Manger) | QUINTE Phase 5 Convergence |
| Confidence Topology | Binary Verdict (PASS/FAIL) |
| Gift Confusion | 閂門 Anti-Drift |
| hm Self-Exemption | 鏡門 Kyōmon (hm directional error) |
| Star (problem structuring) | Phase -1 Four Gates |

## Positioning

| | QUINTE | MAGI |
|-|--------|------|
| Approach | Parallel then cross (flat) | Parallel then spiral (directed) |
| Agents | 5 (cross-model) | 3 (same-model) |
| Output | Binary verdict | Confidence topology |
| Cost | Heavy (~10min) | Light (~3min) |
| When | High-stakes decisions | Investigation, analysis, iteration |
