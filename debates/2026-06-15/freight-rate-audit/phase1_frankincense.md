# Phase 1 · Frankincense (乳香) — Synthesis

> "What does this MEAN?" — Hermeneutics

## Three Movements

### Movement I: The Architecture of Corruption

The report's errors are not random — they form a coherent pattern that points to a specific failure mode. Three distinct error types coexist:

**Type A: Systematic Number Truncation (affects 100% of freight rates)**
Every single freight rate in the document has its leading digit(s) removed. This is not a rounding error or a typo — it's a mechanical parsing failure. The pattern is consistent:
- 12.11 → ".1" or ".11" (tens digit '1' stripped)
- 8.35 → ".35" (tens digit '8' stripped)
- 10.37 → "0.4" (possibly "10.37" → "0.37" → rounded to "0.4")
- 7.23 → ".2" (tens digit '7' stripped)
- 5.50 → ".5" (tens digit '5' stripped)

This pattern is diagnostic: it looks like the numbers were exported from a system that formatted them as `X.Y` where X was a single digit, and when the actual values were `XX.YY`, the tens digit was lost. Possible causes:
1. Excel cell width too narrow — number displayed as "####" and someone typed the visible portion
2. CSV export with fixed-width column that truncated the integer part
3. Copy-paste from a PDF where the first digit was in a different formatting block
4. A programmatic export (e.g., Python/SQL) that used `%.1f` format on values >10

**Type B: COA/Spot Misclassification (affects 3 of 4 routes)**
The report systematically overcounts spot voyages and undercounts COA voyages:
- ADANG BAY: Report 25 COA + 15 spot → Actual 36 COA + 4 spot
- NEWCASTLE: Report ~45 COA + ~16 spot → Actual 34 COA + 28 spot
- KALIORANG: Report claims spot exists → Actual 0 spot

For ADANG BAY, the error is extreme: 11 COA voyages were misclassified as spot. This suggests the classification logic used by the report author differs from the ledger's "货类型" column. Possible causes:
1. The author used a different definition of "COA" (e.g., only "年度长协" vs all "长协" types)
2. The author classified by shipowner (e.g., only 中远海 = COA) rather than by cargo type
3. The author had a different data source or manually reclassified

For NEWCASTLE, the error is reversed: more spot than reported. This might mean the author undercounted spot or had a narrower definition.

**Type C: Fabricated Data (KALIORANG)**
The report claims KALIORANG has both COA and spot voyages. The ledger shows 3 COA voyages and 0 spot. The "spot" range ".5-8.3" appears to be the COA range (5.87~8.35) with digits stripped and misattributed to a non-existent category. This is the most troubling error — it creates data that doesn't exist.

### Movement II: What This Means for the Report's Conclusions

The report's four conclusions are:

1. **"运价离散度主要由BDI指数波动驱动"** — The directional argument is sound (BDI does drive freight), but the specific dispersion numbers (60-100%) are calculated from corrupted data. The actual dispersions are different.

2. **"COA长协运价系统性低于同期现货"** — This is FALSE for NEWCASTLE (where COA mean > spot mean due to 小长协). It's approximately true for ADANG BAY but the magnitude is different from what the report claims.

3. **"2026年同期同航线内部离散<3%"** — Cannot verify without 2026-specific data extraction, but given that all other numbers are wrong, this claim is suspect.

4. **"未发现运价异常偏高"** — This conclusion is built on corrupted data. With the correct numbers, the analysis might reach the same conclusion — but we cannot know, because the analysis was done on wrong data.

### Movement III: The Systemic Failure

This is not a case of one or two typos. It's a systemic failure where:
1. Every freight rate was corrupted (Type A)
2. Most voyage classifications were wrong (Type B)
3. At least one data category was fabricated (Type C)
4. The report was written, reviewed, and prepared for submission to a government inspection team without anyone catching these errors

The fact that no one noticed that "运价区间.0~2.1/吨" is meaningless (what unit? what currency? ".0" of what?) suggests the report was generated from a template or automated system and never manually reviewed against the source data.

## Five Key Insights

1. **The report is structurally unsound** — not just factually wrong, but the entire data pipeline from ledger to report is broken. Fixing individual numbers won't help; the whole document needs to be regenerated from the raw ledger.

2. **The errors are consistent with a specific technical failure** — number truncation + classification mismatch + category fabrication = a data export/processing pipeline that was never validated against the source. This points to an organizational failure in the report preparation process, not individual negligence.

3. **The "correct" story might still be defensible** — the actual ledger data does show that COA prices are generally lower than spot, that BDI drives freight rates, and that the spread is within market norms. The report's narrative might be right even though every number is wrong. But the narrative built on wrong numbers cannot be trusted by the inspection team.

4. **The KALIORANG fabrication is the most serious issue** — creating data that doesn't exist (spot voyages) crosses the line from "error" to "misrepresentation". Even if unintentional (likely the COA data was miscategorized), presenting non-existent spot data to inspectors is a compliance risk.

5. **The report undermines its own purpose** — it was written to demonstrate that "运价波动均有合理的市场依据" and that the company followed proper procedures. But by presenting corrupted data, it does the opposite: it raises questions about the company's data integrity and internal controls.

⚠️ 降级版 — Frankincense 由 hm 产出（非独立 agent）
