# MAGI — Domain Applications & Extension Directions

> 2026-06-14 · From session analysis

## Already Proven: MAGI in Practice

### Crypto Trading Model (2026-06-14)

User said "magi crypto 看盘与交易模型" — full MAGI protocol executed:

| Phase | Duration | Output |
|-------|----------|--------|
| Phase 0 (Star) | ~10s | Problem decomposition, Gift assignment |
| Phase 1 (Offering) | Gold 36s, Frankincense 126s, Myrrh 40s | Three parallel analyses |
| Phase 2 (Journey) | ~60s | Spiral review cycle 1 |
| Phase 3 (Manger) | ~5s | Convergence evaluated |
| Phase 4 (Revelation) | ~15s | Confidence topology + action items |

Result: 3,686 lines of code + documentation produced.
MAGI worked as investigation → QUINTE-LITE worked as implementation.

## Domain Systems Designed for QUINTE-LITE (MAGI-compatible)

Four systems designed in session `20260614_004338_83ea4d`:

### 1. KAIKEI（会计）— Financial Cross-Audit

**Domain**: 财务勾稽审计
**Core concept**: Triple Ledger Mapping (三重映射)

```
横向映射 (Cross-Sectional): Same period, different accounts
  收入 → 应收账款 → 现金流入

纵向映射 (Temporal): Same account, different periods
  期初余额 + 本期发生 = 期末余额

斜向映射 (Diagonal): Cross-period, cross-account
  去年确认收入 → 今年回款率 vs 行业历史
```

**Significance model**: S = |actual - expected| / σ_historical
- S < 1.0 → normal
- 1.0 ≤ S < 2.0 → watch
- 2.0 ≤ S < 3.0 → warn
- S ≥ 3.0 → alert

**MAGI mapping**:
- Gold → RITORNO (复核者): Build cross-audit matrix
- Frankincense → KENSA (检查者): Reverse-verify from cash flow
- Myrrh → KAKUNIN (确认者): External benchmark validation

### 2. HANREI（判例）— Contract Clause Dependency

**Domain**: 合同条款关联与风险推演
**Core concept**: Clause Dependency Graph (条款依赖图)

```
4 edge types:
1. Direct reference ("按第X条执行")
2. Conceptual implication (definitions used by other clauses)
3. Condition trigger (breach → termination → damages)
4. Interest opposition (buyer's right vs seller's obligation)
```

**Dispute simulation**: For each fragile path in the graph,
construct a virtual dispute scenario:
- Party A's claim + clause path
- Party B's defense + clause path
- Tribunal's analysis + probable ruling + probability

**MAGI mapping**:
- Gold → BENGOSHI (法律推理者): Parse clauses, build dependency graph
- Frankincense → TEISHUTU (争端推演者): Construct dispute scenarios
- Myrrh → KANTOKU (监督者): Risk quantification + clause optimization

### 3. SENPAI（船配）— Vessel Nomination Risk

**Domain**: 宣船文件核对与风险筛查
**Core concept**: Confidence Decay Model (置信度衰减模型)

```
C = C₀ × e^(-λt)

C₀ = source confidence:
  Official (flag state/classification society) = 1.0
  Third-party (RightShip/DNV) = 0.9
  Owner-reported = 0.7
  Broker relay = 0.5
  No source = 0.3

λ = decay rate:
  PSC records: 0.005 (6-month half-life)
  Classification certificates: 0.001 (2-year half-life)
  Sanctions lists: 0.01 (real-time update required)
  RightShip ratings: 0.003

Rule: C < 0.6 → "pending verification", cannot be used as pass basis
```

**4-dimension risk assessment**:
- Compliance (30%): flag blacklist/PSC/sanctions
- Operational (25%): equipment/age/mooring
- Financial (25%): P&I/H&M/management
- Reputational (20%): sanctions association/age/PSC history

**MAGI mapping**:
- Gold → CHOSAKEN (调查者): Extract + standardize + compute confidence
- Frankincense → KENSAKEN (检查者): Compliance checklist verification
- Myrrh → FUDO (风险评估者): Composite risk score + historical benchmark

### 4. YOSOKU（预测）— Price Prediction Arena

**Domain**: 运价/煤炭价格预测模型拟合
**Core concept**: Adversarial Model Arena (对抗性模型竞技场)

```
Regime-Conditional Ensemble:
  R1: Trend up (BDI rising > X% for N weeks)
  R2: Trend down
  R3: Range-bound
  R4: Black swan (daily drop > 2σ or weekly rise > 3σ)
  R5: Structural shift (supply/demand fundamental change)

Each model M has independent weight w[M][R] per regime.
Weights computed from historical backtest MAPE + directional accuracy.

Meta-model:
  Ŷ_final = Σ_M [w(M, R_t) × Ŷ_M] × α(Q_t) + (1-α(Q_t)) × Ŷ_fundamental

  Q_t = data quality score
  α(Q) = Q² / (Q² + (1-Q)²) — S-curve transition
```

**MAGI mapping**:
- Gold → MODELER (建模者): Maintain model library + backtest engine
- Frankincense → JUDGE (裁判者): Regime identification + dynamic weighting
- Myrrh → ATTACKER (攻击者): Find each model's failure scenarios

## Integration with MAGI Protocol

All four systems are **MAGI-compatible** — they use the same three-agent
structure with differentiated roles:

```
MAGI Protocol (generic)
  ├── Gold: verification
  ├── Frankincense: synthesis
  └── Myrrh: adversarial

KAIKEI (financial)
  ├── Gold → RITORNO: cross-audit matrix
  ├── Frankincense → KENSA: reverse verification
  └── Myrrh → KAKUNIN: external benchmark

HANREI (legal)
  ├── Gold → BENGOSHI: clause parsing
  ├── Frankincense → TEISHUTU: dispute simulation
  └── Myrrh → KANTOKU: risk quantification

SENPAI (vessel)
  ├── Gold → CHOSAKEN: data extraction
  ├── Frankincense → KENSAKEN: compliance check
  └── Myrrh → FUDO: risk assessment

YOSOKU (prediction)
  ├── Gold → MODELER: backtest
  ├── Frankincense → JUDGE: regime + weighting
  └── Myrrh → ATTACKER: adversarial stress test
```

Each domain system is a **specialization** of the MAGI protocol —
same structure, domain-specific Gift prompts and output formats.

## Implications for MAGI Design

1. **MAGI is a protocol family**, not a single protocol.
   The Three Gifts structure is generic; each domain specializes it.

2. **Gift prompts should be swappable**.
   The engine loads domain-specific prompts (KAIKEI/Gold.md vs generic Gold.md).

3. **Output format is domain-specific**.
   KAIKEI produces cross-audit matrices. SENPAI produces confidence decay tables.
   YOSOKU produces regime-conditional predictions. All are "MAGI" but look different.

4. **Convergence criteria may differ by domain**.
   KAIKEI: all three mappings closed? SENPAI: all items C ≥ 0.6?
   The convergence gate should be configurable per domain.
