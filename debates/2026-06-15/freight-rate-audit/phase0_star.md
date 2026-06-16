# Phase 0 · The Star (星) — Evidence Package

> "We have seen his star in the east, and are come to worship him." — Matthew 2:2

## Subject

Audit of document "关于进口煤炭运输航线运价波动情况的说明" (运价波动情况说明), prepared by 广州珠江电力燃料有限公司 航运部, dated June 2026, intended for submission to 巡视组 (government inspection team).

The report claims to have analyzed 556 voyages (2022-2026) across 4 main routes, asserting that all freight rate fluctuations have "合理的市场依据" and that no "运价异常偏高" was found.

## Source Documents

1. **Report**: 运价波动情况说明.docx — 4 sections: scope/method, results (4 routes), analysis (4 factors), conclusion
2. **Ledger**: 海运外贸台账-20260615.xls — 555 data rows, 47 columns, single sheet "外贸船台账"

## Key Columns in Ledger

| Col | Field | Notes |
|-----|-------|-------|
| 0 | 年 | Year |
| 1 | 月 | Month |
| 2 | 货类型 | Cargo type: 年度长协/季度长协/小长协/长协/现货/市场 |
| 7 | 装港 | Loading port |
| 8 | 卸港 | Discharge port |
| 9 | 船东 | Shipowner |
| 10 | 船名 | Vessel name |
| 14 | 运价（船东口径） | Freight rate (shipowner basis), USD/ton |
| 17 | 货量 | Cargo quantity (tons) |

## Report Claims vs Ledger Data — Summary Matrix

### Route 1: ADANG BAY → 珠电

| Metric | Report | Ledger | Delta |
|--------|--------|--------|-------|
| Total voyages | 40 | 40 | ✅ Match |
| COA voyages | 25 | 36 | ❌ -11 |
| Spot voyages | 15 | 4 | ❌ +11 |
| COA range | ".0~.1/吨" | 3.96~12.11 | ❌ Truncated |
| Spot range | ".5~2.1/吨" | 6.88~10.78 | ❌ Truncated |
| COA dispersion | 100% | 97.6% (3.96~12.11) | ~Match concept, wrong numbers |
| Spot dispersion | 86% | 44.5% (6.88~10.78) | ❌ |
| COA shipowner | "中远海COA长协为主（25航次）" | 中远海（长协）20 + 中远海 8 + 恒达 5 + 海昌 1 + 德运 1 + 时代 1 | ❌ 中远海 total=28, not 25 |

### Route 2: NEWCASTLE → 珠电

| Metric | Report | Ledger | Delta |
|--------|--------|--------|-------|
| Total voyages | 61 | 62 | ❌ -1 |
| COA voyages | ~45 | 34 | ❌ -11 |
| Spot voyages | ~16 | 28 | ❌ +12 |
| COA range | "0.4~6.0/吨" | 10.37~20.38 | ❌ Completely wrong |
| Spot range | "5.0~0.4/吨" | 10.37~17.55 | ❌ Completely wrong |
| COA dispersion | 60% | 65.6% (10.37~20.38) | Close concept |
| Spot dispersion | 36% | 51.6% (10.37~17.55) | ❌ |

### Route 3: TABONEO → 珠电

| Metric | Report | Ledger | Delta |
|--------|--------|--------|-------|
| Total voyages | 19 | 19 | ✅ Match |
| COA voyages | 10 | 14 | ❌ -4 |
| COA range | ".5~1.7/吨" | 5.50~11.70 | ❌ Truncated |
| 海昌 2025 data | .2/.6/.8/.0/.0/.2 | 8.03/7.23/7.82/7.58/7.97/9.19 | ❌ All wrong |

### Route 4: KALIORANG → 珠电

| Metric | Report | Ledger | Delta |
|--------|--------|--------|-------|
| Total voyages | 3 | 3 | ✅ Match |
| Spot exists | "现货.5-8.3" | 0 spot voyages | ❌ Fabricated |
| COA range | ".9" | 5.87~8.35 | ❌ Truncated |

## Systematic Error Pattern

ALL freight rate numbers in the report have their tens digit(s) stripped:
- 12.11 → ".1" (first digit '1' removed)
- 8.35 → ".35" (first digit '8' removed)
- 10.37 → "0.4" (rounding? or '10' → '0')
- 5.50 → ".5" (first digit '5' removed)
- 8.03 → ".0" (first digit '8' removed)
- 9.19 → ".2" (rounding + truncation)

This is NOT random — it's a systematic parsing/formatting error affecting every single freight rate number in the document.

## Risk Context

This document is intended for 巡视组 (government inspection team). Submitting a document with:
1. Systematically corrupted freight rate numbers
2. Wrong COA/spot voyage classifications
3. Fabricated spot data for KALIORANG
4. Would constitute a material misstatement in a government inspection response

## Degradation Notice

⚠️ 降级版 — MAGI hm-solo（三个 Gift 全由 hm 产出）。delegate_task 返回 401（mimo credential pool 路径不匹配）。
