# Phase 1 · Myrrh (沒藥) — Risk Analysis

> "Where does this BREAK?" — Critical Rationalism

## Risk Matrix

### Risk 1: 巡视组信任崩塌 (Severity: CRITICAL)

**Trigger**: 巡视组发现运价数字明显不合理（如".0~2.1/吨"——什么货币？什么单位？".0"是什么？）

**Mechanism**: 巡视组不会逐行核对台账，但任何有基本常识的审查者都会注意到"运价区间.0~2.1/吨"是无意义的数字。一旦发现一处数字异常，会对整份报告的所有数据产生怀疑。

**Impact**: 报告不仅不能证明"运价合理"，反而会引发对公司数据管理能力的全面质疑。巡视组可能要求扩大核查范围，增加对公司其他财务报告的审查。

**Probability**: HIGH — 数字截断太明显，任何有基本财务常识的人都能看出。

**Mitigation**: 必须在提交前重新生成报告，所有数字从台账原始数据提取，逐行核对。

### Risk 2: KALIORANG 现货数据造假指控 (Severity: HIGH)

**Trigger**: 巡视组核对台账发现 KALIORANG 无现货航次，但报告声称有"现货.5-8.3"

**Mechanism**: 台账显示 KALIORANG 全部3个航次均为长协（通利2 + 海昌1），无任何现货航次。报告却说"COA.9与现货.5-8.3的分层符合COA低于现货的正常商业逻辑"——这个"分层"是凭空编造的。

**Impact**: 即使是无意的（可能是把长协数据错误归类），在巡视组眼中这就是"编造数据"。可能被定性为"提供虚假材料"。

**Probability**: MEDIUM — 取决于巡视组是否逐航线核对台账。但 KALIORANG 只有3航次，很容易被抽查到。

**Mitigation**: 删除 KALIORANG 现货相关描述，如实说明仅有3个长协航次。

### Risk 3: COA/现货分类错误暴露比价程序缺陷 (Severity: HIGH)

**Trigger**: 巡视组发现 ADANG BAY 实际36个COA + 4个现货，但报告写成25+15

**Mechanism**: 报告的分类错误可能被解读为：(a) 数据管理混乱——连自己有多少COA/现货都分不清；或 (b) 故意混淆——把COA说成现货来掩盖某些问题。无论哪种解读，都对公司不利。

**Impact**: 如果巡视组进一步追问"为什么分类会错"，可能牵扯出采购流程、合同管理等更深层问题。

**Probability**: MEDIUM

**Mitigation**: 重新按台账"货类型"字段准确分类，解释清楚分类标准。

### Risk 4: NEWCASTLE COA > 现货的事实推翻报告结论 (Severity: HIGH)

**Trigger**: 报告声称"COA系统性低于现货15-40%"，但 NEWCASTLE 航线 COA 均价高于现货均价

**Mechanism**: NEWCASTLE COA 包含4个"小长协"（运价15.07~16.33），拉高了COA均价。实际 COA 均价约15.2，现货均价约13.8——COA反而比现货贵。这直接推翻了"以量换价"的核心论点。

**Impact**: 报告的核心商业逻辑（"COA以量换价机制有效运行"）在 NEWCASTLE 航线上不成立。如果巡视组发现这一点，会质疑整个COA采购策略。

**Probability**: MEDIUM — 需要巡视组做均价计算

**Mitigation**: 区分不同类型的长协（年度长协 vs 小长协），分别计算均价。小长协可能有不同的定价逻辑。

### Risk 5: 运价数字截断导致无法复现分析 (Severity: MEDIUM)

**Trigger**: 巡视组要求提供运价分析的计算过程

**Mechanism**: 由于所有运价数字都被截断，报告中引用的离散度（100%、86%、60%等）无法从报告中的数字推导出来。巡视组无法验证报告的计算过程。

**Impact**: 报告的分析方法论看起来合理，但无法被独立验证。

**Probability**: LOW — 除非巡视组有专业的数据分析人员

### Risk 6: 季节性分析数据损坏 (Severity: MEDIUM)

**Trigger**: 报告称"2025年Q4的ADANG BAY运价（.7-8.1）高于Q1（.2-6.2）"

**Mechanism**: 季节性论点本身合理（Q4冬季储煤旺季运价确实通常更高），但具体数字".7-8.1"和".2-6.2"是截断的，无法验证。

**Impact**: 如果巡视组核对台账发现数字不对，会认为公司在操纵季节性数据。

**Probability**: LOW

### Risk 7: VLSFO 燃油数据损坏 (Severity: LOW)

**Trigger**: "VLSFO燃油价格波动2.2倍（00→100/吨）"

**Mechanism**: "00→100/吨"明显是截断。实际 VLSFO 价格区间大约是 $400-700/吨。2.2倍的说法可能近似正确，但基础数字不可读。

**Impact**: 低——燃油是辅助论点，不是核心。

**Probability**: LOW

### Risk 8: 报告被退回重写导致时间压力 (Severity: MEDIUM)

**Trigger**: 巡视组发现错误后要求重写

**Mechanism**: 如果报告被退回，公司需要在巡视组的时间框架内重新准备，可能来不及做充分的分析和内部审核。

**Impact**: 匆忙重写可能产生新的错误，形成恶性循环。

**Probability**: HIGH — 如果提交当前版本，几乎必然被退回

## Risk Summary

| # | Risk | Severity | Probability | Impact |
|---|------|----------|-------------|--------|
| 1 | 巡视组信任崩塌 | CRITICAL | HIGH | 全面扩大审查 |
| 2 | KALIORANG 造假指控 | HIGH | MEDIUM | 定性为虚假材料 |
| 3 | COA/分类错误暴露 | HIGH | MEDIUM | 牵扯采购流程 |
| 4 | NEWCASTLE COA>现货 | HIGH | MEDIUM | 推翻核心论点 |
| 5 | 无法复现分析 | MEDIUM | LOW | 方法论质疑 |
| 6 | 季节性数据损坏 | MEDIUM | LOW | 数据操纵嫌疑 |
| 7 | VLSFO 数据损坏 | LOW | LOW | 辅助论点失效 |
| 8 | 报告被退回重写 | MEDIUM | HIGH | 时间压力 |

**Bottom line**: 如果以当前版本提交，Risk 1 (信任崩塌) 几乎必然触发。报告必须重写。

⚠️ 降级版 — Myrrh 由 hm 产出（非独立 agent）
