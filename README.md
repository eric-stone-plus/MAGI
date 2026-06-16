<div align="center">

<img src="assets/magi-cover.svg?v=3" alt="MAGI" width="100%">

# MAGI (マギ) Protocol

**Three-agent dialectical spiral protocol for grounded inquiry.**

Single-model AI hits a confidence ceiling. MAGI breaks through — three apostles carry distinct epistemological gifts (Gold, Frankincense, Myrrh) through a dialectical spiral, converging on a confidence topology.

---

[![mimo](https://img.shields.io/badge/mimo-v2.5--pro-4B6BFB?style=flat)](https://xiaomi.com)
[![Protocol](https://img.shields.io/badge/protocol-v1.1-blue?style=flat)](spec/PROTOCOL.md)
[![License](https://img.shields.io/badge/license-MIT-green?style=flat)](LICENSE)

</div>

---

## What is MAGI?

MAGI is a **protocol** for multi-agent adversarial grounded inquiry, named for the Three Magi who followed the star to Bethlehem (Matthew 2:1-12). It defines:

- **3 agents** (hm + 2 apostles, all mimo-v2.5-pro)
- **5 phases** (Star → Offering → Journey → Manger → Revelation)
- **3 epistemological gifts** (Gold = verification, Frankincense = synthesis, Myrrh = risk)

> 📖 **Read the spec**: [spec/PROTOCOL.md](spec/PROTOCOL.md)

### Design Philosophy

MAGI exists to solve the same problem as QUINTE — when a single perspective cannot be trusted — but through a different metaphor. Where QUINTE uses the Roman Republic (checks and balances), MAGI uses Bethlehem (Three Magi, three gifts, one convergence). See [QUINTE](https://github.com/eric-stone-plus/QUINTE) for the full five-agent protocol.

## Architecture

```
Phase 0 · The Star (星)         — "We have seen his star"
Phase 1 · The Offering (獻禮)   — "They opened their treasures"
Phase 2 · The Journey (旅路)    — "They departed another way"
Phase 3 · The Manger (馬槽)     — "They fell down and worshipped"
Phase 4 · The Revelation (啟示) — "The truth shall set you free"
```

### The Three Gifts

| Gift | Apostle | Stance | Question |
|------|---------|--------|----------|
| **Gold** (金) | delegate A | Verification | "Is this true?" |
| **Frankincense** (乳香) | delegate B | Synthesis | "What does this mean?" |
| **Myrrh** (沒藥) | hm | Risk | "Where does this break?" |

Three persons, one substance. Three gifts, one truth.

### Convergence Gate (The Manger)

| Dimension | Weight | Criterion |
|-----------|--------|-----------|
| Factual | 0.4 | All Gifts agree on verified facts |
| Interpretive | 0.3 | Frankincense's synthesis uncontested |
| Risk | 0.3 | Myrrh's risks addressed |

Score ≥0.7 → converged → Revelation.

## Quick Start

```bash
git clone https://github.com/eric-stone-plus/MAGI.git
cd MAGI

# Read the protocol
cat spec/PROTOCOL.md

# Run the engine (from a Hermes session)
python3 lib/magi.py "your question here"
```

## For Implementors

| Path | What |
|------|------|
| [spec/PROTOCOL.md](spec/PROTOCOL.md) | Canonical protocol specification |
| [lib/magi.py](lib/magi.py) | Reference orchestrator engine |
| [prompts/](prompts/) | Gift prompt templates (Gold, Frankincense, Myrrh) |
| [concepts/CONCEPTS.md](concepts/CONCEPTS.md) | Theological and philosophical foundations |

## Relationship to QUINTE

| | QUINTE | MAGI |
|-|--------|------|
| Metaphor | Roman Republic | Bethlehem · Matthew 2 |
| Agents | 5 (DeepSeek v4-pro) | 3 (mimo-v2.5-pro) |
| Output | Binary verdict | Confidence topology |

MAGI investigates, QUINTE authorizes.

## License

MIT — the protocol and orchestration layer.
