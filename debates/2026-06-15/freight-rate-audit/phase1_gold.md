# Phase 1 · Gold (金) — Verification

> "Is this TRUE?" — Empiricism

## Verification Protocol

Each claim from the report is checked against the ledger. Status: CONFIRMED / REFUTED / UNVERIFIABLE.
Severity: HIGH = material misstatement affecting 巡视组 judgment / MEDIUM = numerical error but directionally correct / LOW = minor discrepancy.

---

## Claim 1: "核查覆盖我司全部进口煤炭运输航次556条"

- ACTUAL: Ledger has 555 valid data rows (row 0 is header). 556 is close.
- STATUS: ⚠️ UNVERIFIABLE (off by 1, may include header count or a row I filtered)
- SEVERITY: LOW

## Claim 2: "ADANG BAY → 珠电（40航次）"

- ACTUAL: 40 voyages with discharge port containing "珠电"
- STATUS: ✅ CONFIRMED
- SEVERITY: N/A

## Claim 3: "该航线以中远海COA长协为主（25航次），辅以现货采购（15航次）"

- ACTUAL: COA (长协) = 36 voyages, Spot (现货) = 4 voyages. Total = 40.
- STATUS: 🛑 REFUTED
- EVIDENCE: Report says COA 25 + Spot 15 = 40. Actual is COA 36 + Spot 4 = 40. The COA/spot split is wrong by 11 voyages in each direction.
- SEVERITY: HIGH — misclassifies 11 voyages, inflating spot count by 275% and deflating COA count by 31%.

## Claim 4: "运价区间.0~2.1/吨" (ADANG BAY COA)

- ACTUAL: COA freight range is 3.96 ~ 12.11 USD/ton.
- STATUS: 🛑 REFUTED
- EVIDENCE: ".0~2.1" is nonsensical. The ".0" likely represents 12.11 truncated to ".1" or ".0". The "2.1" likely represents 12.11 truncated. Every number has its integer part stripped.
- SEVERITY: HIGH — all freight rate numbers are corrupted.

## Claim 5: "COA运价.0对应市场低谷（BDI<1000），.1对应市场高位"

- ACTUAL: COA lowest is 3.96 (2022, likely BDI low), highest is 12.11 (2024, likely BDI high).
- STATUS: 🛑 REFUTED
- EVIDENCE: The directional logic is correct (low BDI = low freight), but the numbers ".0" and ".1" are meaningless. Actual range 3.96~12.11 is a 206% spread, not "100% dispersion".
- SEVERITY: HIGH

## Claim 6: "现货.5~12.1的更大波动" (ADANG BAY spot)

- ACTUAL: Spot range is 6.88 ~ 10.78. Only 4 voyages.
- STATUS: 🛑 REFUTED
- EVIDENCE: ".5~12.1" doesn't match. Actual 6.88~10.78 is a 56.7% spread, not "86% dispersion". With only 4 spot voyages, statistical dispersion is meaningless anyway.
- SEVERITY: HIGH

## Claim 7: "NEWCASTLE → 珠电（61航次）"

- ACTUAL: 62 voyages.
- STATUS: 🛑 REFUTED (off by 1)
- SEVERITY: MEDIUM

## Claim 8: "COA长协 ~45航次, 运价区间 0.4~6.0/吨, 离散度 60%" (NEWCASTLE)

- ACTUAL: COA = 34 voyages, freight 10.37 ~ 20.38.
- STATUS: 🛑 REFUTED
- EVIDENCE: Voyage count off by 11. "0.4~6.0" is completely wrong — actual is 10.37~20.38. The "0.4" might be 10.37 with the "10" stripped. "6.0" might be 16.0 or 20.38 truncated.
- SEVERITY: HIGH — voyage count, freight range, and dispersion all wrong.

## Claim 9: "现货/2026 ~16航次, 5.0~0.4/吨, 离散度 36%" (NEWCASTLE spot)

- ACTUAL: Spot = 28 voyages (not ~16), freight 10.37 ~ 17.55.
- STATUS: 🛑 REFUTED
- EVIDENCE: "5.0~0.4" is incoherent (low > high?). Actual 10.37~17.55. Spot count is 28, not ~16.
- SEVERITY: HIGH

## Claim 10: "2026年H1运价9.9-20.4/吨" (NEWCASTLE)

- ACTUAL: Need to verify 2026 H1 specifically.
- STATUS: ⚠️ UNVERIFIABLE without year-level breakdown (not in current evidence extraction)
- SEVERITY: MEDIUM — cannot confirm or deny specific year range.

## Claim 11: "TABONEO → 珠电（19航次）"

- ACTUAL: 19 voyages.
- STATUS: ✅ CONFIRMED
- SEVERITY: N/A

## Claim 12: "该航线以海昌COA长协为主（10航次），运价区间.5~1.7/吨"

- ACTUAL: COA = 14 voyages (not 10), freight 5.50 ~ 11.70.
- STATUS: 🛑 REFUTED
- EVIDENCE: "海昌COA长协为主（10航次）" — 海昌 is only 1 of multiple COA shipowners. Total COA is 14, not 10. ".5~1.7" truncated from 5.50~11.70.
- SEVERITY: HIGH

## Claim 13: 海昌 2025 specific voyages (TABONEO)

Report lists:
| Vessel | Report Rate | Actual Rate | Match? |
|--------|------------|-------------|--------|
| XIN DONG GUAN 11 | .2 | 7.23 | ❌ |
| HC ENERGY | .6 | 7.58 | ❌ |
| HC SUNSHINE | .8 | 7.82 | ❌ |
| HC SUNSHINE | .0 | 7.97 | ❌ |
| DA TANG 712 | .0 | 8.03 | ❌ |
| HC ENERGY | .2 | 9.19 | ❌ |

- STATUS: 🛑 REFUTED — ALL 6 numbers are wrong.
- EVIDENCE: Same truncation pattern. ".2" could be 7.23→".23"→".2", ".6" could be 7.58→".58"→".6", etc.
- SEVERITY: HIGH — specific vessel-level data presented to 巡视组 is fabricated.

## Claim 14: "海昌COA在2025年内运价从.2逐步升至.2（28%波动）"

- ACTUAL: 海昌 2025 range is 7.23 ~ 9.19, which is a 27.1% increase. The 28% is approximately correct.
- STATUS: ⚠️ PARTIALLY CONFIRMED — percentage is approximately right, but the base numbers ".2→.2" are meaningless.
- SEVERITY: MEDIUM

## Claim 15: "KALIORANG → 珠电（3航次）"

- ACTUAL: 3 voyages.
- STATUS: ✅ CONFIRMED
- SEVERITY: N/A

## Claim 16: ".9（COA）与.5-8.3（现货）的分层" (KALIORANG)

- ACTUAL: ALL 3 voyages are COA. NO spot voyages exist. COA range: 5.87 ~ 8.35.
- STATUS: 🛑 REFUTED
- EVIDENCE: Report fabricates spot voyages that don't exist in the ledger. ".9" might be 8.35 truncated. ".5-8.3" might be 5.87~8.35 with digits stripped, but attributed to a non-existent "spot" category.
- SEVERITY: HIGH — fabricates data category (spot) that has zero basis in the ledger.

## Claim 17: "BDI振幅达6.8倍（500→3400）"

- STATUS: ⚠️ UNVERIFIABLE — BDI data not in the ledger. BDI did reach lows ~500 in 2020 and highs ~3400 in 2021-2022, so this is plausible but not verifiable from the provided data.
- SEVERITY: LOW (market data, not company data)

## Claim 18: "VLSFO燃油价格波动2.2倍（00→100/吨）"

- STATUS: 🛑 REFUTED (data corrupted)
- EVIDENCE: "00→100/吨" is clearly truncated. VLSFO was ~$400-600/ton in 2022 and ~$500-700/ton in 2024-2025. The "2.2倍" might be approximately correct but the base numbers are unreadable.
- SEVERITY: MEDIUM

## Claim 19: "COA长协运价系统性低于同期现货15-40%"

- ACTUAL: For ADANG BAY: COA mean ~6.9, Spot mean ~8.3, difference ~17%. For NEWCASTLE: COA mean ~15.2, Spot mean ~13.8 — COA is actually HIGHER than spot (because 小长协 at 15-16 pulls up).
- STATUS: 🛑 REFUTED for NEWCASTLE (COA > spot), ⚠️ PARTIALLY CONFIRMED for ADANG BAY
- SEVERITY: HIGH — the claim "COA系统性低于现货" is false for NEWCASTLE.

## Claim 20: "COA运价始终低于现货-3/吨"

- STATUS: ⚠️ UNVERIFIABLE — "-3/吨" is truncated. Could be "3" or "13" or "23".
- SEVERITY: MEDIUM

## Claim 21: "2025年Q4的ADANG BAY运价（.7-8.1）高于Q1（.2-6.2）"

- STATUS: 🛑 REFUTED (numbers truncated)
- EVIDENCE: ".7-8.1" and ".2-6.2" are unreadable. Need to verify seasonality claim.
- SEVERITY: MEDIUM

## Claim 22: "未发现因未履行比价程序而导致运价异常偏高的情况"

- STATUS: 🛑 REFUTED by implication
- EVIDENCE: The report that makes this conclusion contains systematically corrupted data. The conclusion cannot be trusted because the underlying analysis is based on wrong numbers. Specifically:
  - COA/spot classification is wrong (routes 1, 2, 4)
  - Freight rates are all truncated
  - KALIORANG spot data is fabricated
  - The conclusion is built on a foundation of errors.
- SEVERITY: HIGH — this is the report's core finding, and it's undermined by the data errors.

---

## Verification Summary

| Category | Count | Severity |
|----------|-------|----------|
| Claims verified | 3/22 (14%) | — |
| Claims REFUTED | 15/22 (68%) | — |
| Claims UNVERIFIABLE | 4/22 (18%) | — |
| HIGH severity errors | 11 | Material misstatement |
| MEDIUM severity errors | 4 | Numerical corruption |
| LOW severity errors | 2 | Minor |

**Conclusion**: The report fails verification. 68% of claims are directly contradicted by the ledger data. The systematic number truncation affects every freight rate in the document. The COA/spot classification errors are structural, not random. The KALIORANG spot data is fabricated.

⚠️ 降级版 — Gold 由 hm 产出（非独立 agent）
