# MAGI Final Architecture — Full QUINTE Evidence

## Rules Under Audit (2026-06-18, all fixes applied)

### SOUL.md (core-rules)
```
MAGI: OCR v2.0. Gold: mimo-v2.5+kimi+DS v4-pro. Fr: mimo-v2.5-pro. Myrrh: DS v4-pro.
成本: kimi(Andante ¥49/月) > DS(按量) > mimo(Lite ¥39/月). 三模型全火力.
Pipeline: text-layer→zlib→DS / scanned→Tesseract→OCR gate→mimo Gold→confidence gate→DS text or batch kimi→merge→Fr+Myrrh→QUINTE
```

### MEMORY.md (core-rules)
```
MAGI Gold 田忌赛马: mimo-v2.5(Lite ¥39/月)对结构表单; kimi(Andante ¥49/月,thinking=high)对歧义视觉; DS v4-pro(max)对文本校验+对抗审计。
纯文本低置信→DS非kimi。OCR太差→跳过mimo直接kimi全文档。
校准≥95%。Circuit breaker:mimo故障→all-kimi。Fr:mimo-v2.5-pro。Myrrh:DS v4-pro。
```

### MAGI SKILL.md (Hermes local)
Full 858-line operational skill. Architecture section has tiered pipeline.
Gold dispatch: mimo-v2.5 primary → batch kimi escalation per-document.
Pitfalls: 0a/0a-ii/0a-iii with QUINTE blocking conditions.

### MAGI README.md (public repo)
Architecture diagram with model names (mimo-v2.5-pro, DeepSeek v4-pro).
Gold box: "mimo-v2.5 primary, kimi batch fallback".
Mac Deployment section: 田忌赛马 table + tiered pipeline diagram.

## Task

Final consistency audit across all four sources:
1. Any remaining contradictions?
2. Any coverage gaps?
3. Any ambiguity?
4. Is the architecture logically complete and deployable?
