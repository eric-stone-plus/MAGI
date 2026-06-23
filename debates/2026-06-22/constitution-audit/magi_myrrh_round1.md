# MAGI Myrrh (mimo-v2.5-pro) · Constitution Consistency Audit · Round 1

**Scope**: SOUL.md · USER.md · MEMORY.md · POSTMORTEM.md
**Date**: 2026-06-22
**Method**: Line-by-line cross-reference; findings tagged by category

---

## 1. Cross-file contradictions

### 1a. BLOCKER — MAGI quorum: "至少一人" vs "全发缺一不可"

SOUL.md L33:
> MAGI (Gold/Fr/Myrrh) **至少一人**必须已就位

MEMORY.md L31:
> MAGI = grok+kimi+mimo **全发缺一不可**，不限阶段

SOUL.md L46 itself defines MAGI as a **≥2/3 convergence gate** across three mode[0m
[0m← [0mWrite magi_myrrh_round1.md
Wrote file successfully.
[0m
Now I have all four source files and both prior MAGI audits (Gold, Fr). I'll produce the Myrrh (mimo) independent audit.
Written to `magi_myrrh_round1.md`. Key findings:

- **3 BLOCKERs**: MAGI quorum contradiction ("至少一人" vs "全发缺一不可"), KANSA B fallback matrix mismatch (SOUL vs MEMORY give different MAGI substitutes for cc/cw/omp), cc model routing conflict (MiMo in SOUL/USER vs Claude in MEMORY)
- **2 HIGHs**: "No light QUINTE" absolutism vs thermal exception, push mandatory vs push requires consent
- **Version mismatch**: SOUL.md carries QUINTE v3.3 in 3 places; USER.md says v3.4
- **~15 rule instances** misplaced across files; SOUL.md doing too much (OCR, Hermes config mixed with persona)
- **7 missing elements**: SKILL.md absent from audit, POSTMORTEM frozen 5 days behind, no constitution version/changelog, no conflict resolution hierarchy
S冲突)

Two files say MiMo, one says Claude. MEMORY's parenthetical "(macOS冲突)" suggests this was a deliberate override, but it's undated and unexplained. If Claude is correct, SOUL and USER are wrong. If MiMo is correct, MEMORY is stale.

### 1d. HIGH — "No light QUINTE" absolutism vs thermal exception

SOUL.md L93–95:
> ⛔ 不自判简化… 无"轻量 QUINTE"、无"快速 QUINTE"、无"简化 QUINTE"

SOUL.md L123–126 (Netsumon Phase 1):
> R1: hm + MAGI Gold **仅**（不派生 cc/cw/omp 全量）
> R2/R3: 推迟至热恢复后，或**轻量 MAGI vote**

Netsumon explicitly permits a reduced R1 and "轻量 MAGI vote" — direct contradiction of L95's absolutism. No cross-reference or exception clause exists.

### 1e. HIGH — Push mandatory vs push requires consent

SOUL.md L35:
> 五文件修改后 commit + **push** 到备份 repo

SOUL.md L142:
> 执行前须确认当前 session 中用户已明确授权

L35 reads like automatic push after constitution edits. L142 says every push needs fresh user consent. Whether `hermes-core-rules-mac-x86` is exempt is ambiguous.

### 1f. MEDIUM — "Don't interrupt user" vs thermal kill authorization

MEMORY.md L9:
> 绝对不擅自中断/停止/取消用户已在进行的进程

Same line:
> **例外 — KENGEN tier0 热控**: CPU_Speed_Limit<80 且进程匹配 CLI/agent 签名→hm有常设kill授权无需确认

SOUL.md L119:
> CLI/agent 签名进程→SIGTERM (2s)→SIGKILL

The exception is inline in MEMORY but the kill behavior is only fully specified in SOUL. An agent reading MEMORY alone sees "常設kill授权" but not the SIGTERM→SIGKILL escalation or the creative-app exemption.

### 1g. MEDIUM — Code generation model policy

SOUL.md L77: hm/omp/cw/rx on **DeepSeek v4-pro**
MEMORY.md L27: 代码类工作**不用DS写**——经济原因
MEMORY.md L27: 代码生成: **kimi+grok+mimo**三模型并行写

If hm/omp/cw/rx use DS v4-pro but code work must not use DS, does that mean hm/omp/cw/rx never do code work? Or is MEMORY overriding SOUL's model assignment for code tasks? Ambiguity.

---

## 2. Version number alignment

| Entity | SOUL.md | USER.md | MEMORY.md | POSTMORTEM.md | Status |
|--------|---------|---------|-----------|---------------|--------|
| QUINTE | **v3.3** (L44), "v3.3+" (L79, L85) | **v3.4** (L1) | "四repo specs是版本号唯一权威源" (L33) | — | **MISMATCH**: SOUL stale |
| MAGI | **v3.0** (L46) | — | — | — | No cross-check possible |
| Constitution set | — | — | — | — | **No version tag anywhere** |

SOUL.md carries QUINTE v3.3 in three places. USER.md says v3.4. MEMORY.md says repo specs are the authority but doesn't flag SOUL's stale version. An agent reading SOUL gets a version that's one behind.

---

## 3. Rules stated in wrong file

### 3a. MEMORY.md — operational rules that belong in SOUL

| Rule | MEMORY line | Should be in |
|------|-------------|--------------|
| delegate_task full use outside QUINTE/MAGI | L17 | SOUL (behavioral constraint) |
| Push authorization ("不累积不延续") | L13 | SOUL (already at L50, L142 — deduplicate) |
| Agent fail→MAGI fallback mapping | L29 | SOUL KANSA section (already at L150 — reconcile) |
| "file mod前MAGI必在场" | L31 | SOUL (already at L27, L83 — deduplicate) |
| cc_dispatch.py key extraction | L21 | SOUL or keep MEMORY (USER L1 has weaker version) |
| "四repo specs是版本号唯一权威源" | L33 | SOUL architecture preamble |

### 3b. USER.md — protocol rules mixed into preferences

USER.md L1 is a single `§`-separated line containing:
- Hermes provider config ✓ (belongs here)
- QUINTE v3.4 ✗ → SOUL
- delegate_task ban ✗ → SOUL
- R2 embed/no /tmp ✗ → SOUL
- cc stream-json ban ✗ → SOUL
- hm architecture constraint ✗ → SOUL
- cc_dispatch.py key ✗ → MEMORY (already better at MEMORY L21)

### 3c. SOUL.md — content that's wrong container type

| Content | Lines | Better home |
|---------|-------|-------------|
| OCR pipeline (分层校验, cost model, circuit breaker) | L172–197 | MEMORY or dedicated SKILL — this is operational knowledge, not persona |
| Hermes self-maintenance after update | L23–25 | USER (environment config) |
| deepseek-timeout-workaround skill | L19 | USER (provider-specific config) |
| Approvals smart mode | L21 | USER (environment config) |

### 3d. MEMORY.md — user preferences mixed with operational rules

| Content | MEMORY line | Should be in |
|---------|-------------|--------------|
| Ghostty palette / red-green colorblind | L25 | USER (accessibility preference) |
| 科幻笔法 / MAGI cultural anchors | L19 | USER (voice & style) |
| GitHub-dark theme for HTML | L3 | USER (presentation preference) |
| Mac hardware spec | L37 | USER (already at USER L7 — delete duplicate) |

### 3e. POSTMORTEM.md — permanent rules leaking from incidents

Key Learnings L53–57 restates rules already in SOUL L48/L50. POSTMORTEM should be narrative + root cause; extracted rules should be pointers to SOUL/MEMORY.

---

## 4. What's missing

### 4a. SKILL.md — the invisible 5th file

SOUL.md L29 explicitly names five constitution files: SOUL · USER · MEMORY · **SKILL** · POSTMORTEM. SOUL.md L99 says "update all five config files" after protocol changes. SKILL.md is not in this audit set. A constitution consistency check that omits 20% of the constitution is incomplete.

### 4b. POSTMORTEM.md — frozen at 2026-06-17

POSTMORTEM header: "2026-06-17 Four-Repo Audit & Push". SOUL/MEMORY reference rule changes through 2026-06-22:
- 2026-06-20: MAGI iron law strengthened (SOUL L27, L82)
- 2026-06-21: 熱門 Netsumon established (SOUL L112)
- 2026-06-21: DEGRADED abolished (SOUL L148)
- 2026-06-22: Hermes Desktop update SOP (MEMORY L35)

None of these have POSTMORTEM entries. POSTMORTEM is 5 days behind the live rules.

### 4c. No constitution version or changelog

No file declares a constitution version number. No file tracks which rules were added/modified when. SOUL has inline dates (e.g., "2026-06-20 确立") but no unified changelog. An agent can't tell whether MEMORY L35 (2026-06-22) or SOUL L27 (2026-06-20) is more recent for the same rule area without reading both.

### 4d. No conflict resolution hierarchy

MEMORY.md L33 says specs are authoritative for version numbers. Nothing says which file wins when SOUL and MEMORY contradict on behavioral rules. The MAGI quorum conflict (§1a) and fallback matrix conflict (§1b) are live examples where hierarchy absence causes ambiguity.

### 4e. No "last reviewed" dates on files

None of the four files declares when it was last reviewed or by whom. SOUL has inline dates for individual rules but no file-level metadata.

### 4f. Missing audit trail for "先读后写"

SOUL.md doesn't explicitly state "先读后写" (read before write), but MEMORY.md L11 does. This is a behavioral constraint that arguably belongs in SOUL's gate architecture. SOUL's 雨門 (ambiguity gate) and 鏡門 (mirror gate) cover pre-action checks but don't explicitly include read-before-write.

### 4g. No explicit rule on when POSTMORTEM entries are created

SOUL L99 says update five files after protocol changes, but doesn't say when to create POSTMORTEM entries. The incidents in POSTMORTEM were created reactively. No rule governs proactive incident documentation.

---

## Summary

| Category | Count | Severity |
|----------|-------|----------|
| Cross-file contradictions | 7 | 3 BLOCKER, 2 HIGH, 2 MEDIUM |
| Version mismatches | 1 (QUINTE: 3 occurrences in SOUL) | HIGH |
| Rules in wrong file | 5 categories (~15 rule instances) | MEDIUM |
| Missing elements | 7 | MEDIUM–HIGH (SKILL.md omission is structural) |

**Three blockers require immediate resolution before any sync pass:**
1. MAGI quorum: SOUL "至少一人" → should be "全发缺一不可"
2. KANSA B fallback matrix: reconcile SOUL L150–156 with MEMORY L29
3. cc model routing: resolve MiMo (SOUL/USER) vs Claude (MEMORY)

**Structural recommendation**: Declare SOUL.md as the single source of truth for behavioral rules. USER.md owns preferences/environment. MEMORY.md owns operational shorthand with pointers to SOUL. POSTMORTEM owns incident narratives only. This eliminates ~40% redundant text and prevents future drift.
