# Agent Dispatch Table Audit — QUINTE v3.4

**Date:** 2026-06-23  
**Auditor:** Fr (kimi file-explorer pass)  
**Scope:** Verify every agent’s *claimed* model, invocation, and constraints against the *actual* configs/scripts.  
**Files read:**

- `~/.hermes/profiles/technical/skills/multi-agent-debate/scripts/cc_dispatch.py` (76 lines)
- `~/.hermes/profiles/technical/skills/multi-agent-debate/scripts/cw_dispatch.py` (81 lines)
- `~/.hermes/profiles/technical/skills/multi-agent-debate/scripts/omp_run.py` (78 lines)
- `~/.hermes/profiles/technical/skills/multi-agent-debate/scripts/magi_dispatch.py` (95 lines)
- `~/.hermes/profiles/technical/skills/multi-agent-debate/SKILL.md` (279 lines)
- `~/.hermes/profiles/technical/skills/multi-agent-debate/references/agent-dispatch-quickref.md` (73 lines)
- `~/.claude/settings.json` (86 lines)
- `~/.hermes/profiles/technical/memories/MEMORY.md` (49 lines)
- `~/.hermes/profiles/technical/memories/USER.md` (7 lines)
- `~/Public/hermes-core-rules-mac-x86/SOUL.md` (56 lines)

**Environment checks performed:** `which claude codewhale omp grok kimi mimo reasonix`; existence of `~/.codewhale/config.toml`, `/tmp/omp_ds_key.txt`, `~/.local/share/mimocode/auth.json`.

---

## Executive Summary

**23 distinct mismatches** found across the 7 audited agents. The most severe are:

1. **Constitutional contradiction:** SOUL §Agent Dispatch (L36) and SKILL.md (L82) explicitly forbid script wrappers, yet **cc/cw/omp/MAGI all have Python wrapper scripts** that are actively used.
2. **cc subagent lock ineffective:** Claimed anti-flash mechanism `CLAUDE_CODE_SUBAGENT_MODEL=deepseek-v4-pro` is **not enforced**; actual code/settings use `claude-opus-4-20250514`.
3. **MAGI Gold invocation is wrong in the wrapper:** `magi_dispatch.py` calls `grok -p`, while SKILL.md demands `grok build` and the quickref states `grok` has **no `-p` flag**.
4. **omp key source broken at runtime:** `omp_run.py` expects `/tmp/omp_ds_key.txt` (missing) or `OMP_DS_KEY`; documented sources (`~/.claude/settings.json`, inline proxy) are not used.
5. **rx has no dispatch script at all** — only documentation exists.

---

## Per-Agent Audit

### 1. hm (Hermes coordinator / self)

| Check | Claimed | Actual | Verdict |
|-------|---------|--------|---------|
| (1) Model | DeepSeek v4-pro (SKILL.md L26; USER.md L1: “DS v4-pro max (hm/omp/cw/rx)”) | **No standalone hm config or dispatch script found.** The running session is Kimi Code CLI, not a DeepSeek endpoint. | ⚠️ **Unverifiable / likely mismatch.** No artifact proves hm runs on DS v4-pro. |
| (2) Invocation | “self” (SKILL.md L26) | No wrapper; hm is the orchestrator. | ✅ Matches (no script expected). |
| (3) Constraint | “hm负责编排+最终合入……不负责实现代码” (MEMORY.md L25); post-QUINTE implementation MUST use MAGI (SKILL.md L52-L63). | No runtime gate prevents hm from writing implementation code. Enforcement is prompt/honor-system only. | ⚠️ **No mechanical enforcement.** |

**Mismatches:**
- hm’s claimed DS v4-pro model has no supporting config/script in the audited files.
- The “no solo implementation” rule is documented but not mechanically enforced.

---

### 2. cc (Claude Code / DeepSeek Anthropic-compat)

| Check | Claimed | Actual | Verdict |
|-------|---------|--------|---------|
| (1) Model | DeepSeek v4-pro via Anthropic-compat (`claude-opus-4` → `deepseek-v4-pro`) (SKILL.md L27; MEMORY.md L21; USER.md L1) | `settings.json` env sets `ANTHROPIC_MODEL: "deepseek-v4-pro"`, but `cc_dispatch.py` overrides it to `"claude-opus-4-20250514"` (L45). `settings.json` top-level `"model": "claude-opus-4-20250514"` (L76). | ⚠️ **Inconsistent model strings.** The runtime Anthropic-compat call uses the Anthropic model ID, not the DeepSeek name. |
| (2) Invocation | `python3 scripts/cc_dispatch.py "TASK: <prompt>" $AUDIT/cc_roundN.md 2>&1` (SKILL.md L93). Underlying: `claude -p --permission-mode bypassPermissions` (SKILL.md L27). | `cc_dispatch.py` runs `['claude','-p','--permission-mode','bypassPermissions','--effort','xhigh', prompt]` (L51-52). | ✅ CLI flags match; wrapper path matches. |
| (3) Constraint | `--effort max` + `CLAUDE_CODE_SUBAGENT_MODEL=deepseek-v4-pro` “anti-flash” (SKILL.md L92-93 comment). Key source: env `DEEPSEEK_API_KEY`, fallback `~/.codewhale/config.toml` (SKILL.md L91; MEMORY.md L21). | Script uses `--effort xhigh`, not `max` (L52). Sets `CLAUDE_CODE_SUBAGENT_MODEL=claude-opus-4-20250514` (L46), not `deepseek-v4-pro`. Key source is `ANTHROPIC_API_KEY` or `DEEPSEEK_API_KEY`, fallback `~/.codewhale/config.toml` (L28-36). | ❌ **Mismatch on effort flag, subagent model lock, and unclaimed `ANTHROPIC_API_KEY` source.** |

**Additional mismatches:**
- `agent-dispatch-quickref.md` L9 documents `python3 scripts/run_cc.py` — the actual file is `cc_dispatch.py`.
- `USER.md` L1 and `agent-dispatch-quickref.md` L32 claim cc key is read from `auth.json['xiaomi']['key']`; `cc_dispatch.py` does **not** read this file (it reads env/`~/.codewhale/config.toml`).
- `cc_dispatch.py` docstring says “Sub-agents locked to pro” (L4) but the code does not lock them to `deepseek-v4-pro`.

---

### 3. cw (codewhale)

| Check | Claimed | Actual | Verdict |
|-------|---------|--------|---------|
| (1) Model | DeepSeek v4-pro (SKILL.md L28) | No explicit model selection in `cw_dispatch.py`; `codewhale` itself selects the model. | ✅ No claim to contradict. |
| (2) Invocation | `codewhale exec --auto "TASK: <prompt>" > $AUDIT/cw_roundN.md 2>&1` (SKILL.md L95). `~/.local/bin/codewhale exec --auto ...` (quickref L10). | `cw_dispatch.py` runs `/Users/ericstone/.local/bin/codewhale exec --auto <prompt>` with `cwd=/tmp` (L50-53). | ✅ Binary and subcommand match; wrapper not mentioned in SKILL.md. |
| (3) Constraint | R1: “Do not execute shell commands, do not modify files, do not run git. Produce analysis after evidence collection.” (SKILL.md L148). R2: “Do NOT use tool calls… Return cross-examination in prose.” (SKILL.md L207). | `cw_dispatch.py` passes the raw prompt verbatim; it does **not** inject R1/R2 constraint prefixes or validate output format. | ❌ **Claimed constraint is not enforced by the wrapper; relies entirely on caller prompt.** |

**Additional mismatches:**
- `cw_dispatch.py` timeout default is 300 s (L47), while SKILL.md/SOUL.md set cw operational ceiling at **180 s** (SKILL.md L184; SOUL.md L40).
- `cw_dispatch.py` does not prepend `TASK:` to the prompt (SKILL.md dispatch command includes it).

---

### 4. omp

| Check | Claimed | Actual | Verdict |
|-------|---------|--------|---------|
| (1) Model | DeepSeek v4-pro (SKILL.md L29) | `omp_run.py` passes `--model deepseek/deepseek-v4-pro` (L53). | ✅ Matches. |
| (2) Invocation | `HTTPS_PROXY=http://127.0.0.1:37981 /usr/local/bin/omp -p "TASK: <prompt>" > $AUDIT/omp_roundN.md 2>&1` (SKILL.md L97). Quickref adds `HTTP_PROXY=...` and key (L11). | `omp_run.py` runs `omp -p --model deepseek/deepseek-v4-pro --thinking xhigh <prompt>` (L53), `cwd=/tmp`, **no proxy set**, no `TASK:` prefix, binary is bare `omp` not `/usr/local/bin/omp`. | ❌ **Proxy missing, extra `--thinking xhigh` flag undocumented, path/prefix differ.** |
| (3) Constraint | HTTPS_PROXY required; key required (SKILL.md L29; quickref L11). | Key loaded from `/tmp/omp_ds_key.txt` (does **not exist**) or `OMP_DS_KEY` env (L36-45). Quickref says restore key from `~/.claude/settings.json`, but `settings.json` contains an Anthropic/DeepSeek key, not an omp key, and `omp_run.py` never reads it. | ❌ **Documented key source does not match actual loader; proxy not enforced.** |

**Additional mismatches:**
- `/tmp/omp_ds_key.txt` is missing at runtime; without `OMP_DS_KEY` env, omp auth will fail.

---

### 5. rx (reasonix)

| Check | Claimed | Actual | Verdict |
|-------|---------|--------|---------|
| (1) Model | DeepSeek v4-pro (SKILL.md L30) | No rx config file found. | ⚠️ Unverifiable. |
| (2) Invocation | `reasonix run "TASK: <prompt>" > $AUDIT/rx_roundN.md 2>&1` (SKILL.md L106). Quickref: `reasonix run --model deepseek-v4-pro --effort max "[prompt + inline content]" > file.md 2>&1` (L15). | **No `rx_dispatch.py` or equivalent script exists.** Only documentation. | ❌ **Actual dispatch artifact missing.** |
| (3) Constraint | R2 only; cannot read files — embed content inline; `<1500 chars` or `<tool_call>` → discard, dispatch MAGI Gold substitute (SKILL.md L30, L165-L166). | No script exists to enforce inline-only prompts or to auto-substitute MAGI Gold on failure. | ❌ **No enforcement mechanism.** |

**Additional mismatches:**
- SKILL.md and quickref disagree on rx flags (`--model` / `--effort max` present only in quickref).

---

### 6. Gold (MAGI Gold / grok)

| Check | Claimed | Actual | Verdict |
|-------|---------|--------|---------|
| (1) Model | grok (SKILL.md L31; MEMORY.md L37, L39) | `magi_dispatch.py` maps Gold to `~/.local/bin/grok` (L12). | ✅ Matches. |
| (2) Invocation | `grok build "TASK: <prompt>" > $AUDIT/gold_roundN.md 2>&1` (SKILL.md L101). Quickref: `echo "TASK: ..." \| grok --always-approve --verbatim > file.md 2>&1` (L12), explicitly states `grok` has **no `-p` flag**. | `magi_dispatch.py` runs `~/.local/bin/grok -p <prompt>` (L66-67). | ❌ **Severe mismatch:** `grok -p` contradicts both SKILL.md (`grok build`) and the quickref (no `-p` flag; pipe + `--always-approve --verbatim`). |
| (3) Constraint | Grok-specific recovery: exit 143 = SIGTERM with persisted session → `--resume` (SKILL.md L181; `magi_dispatch.py` L15 comment). | `magi_dispatch.py` classifies exit 143 as `interrupted_recoverable` (L36-38) but does **not** auto-resume; it only returns a JSON hint. | ⚠️ **Recovery is advisory, not automated.** |

**Additional mismatches:**
- No `--always-approve --verbatim` flags (quickref) nor `build` subcommand (SKILL.md) in the actual wrapper.

---

### 7. Fr (MAGI Fr / kimi)

| Check | Claimed | Actual | Verdict |
|-------|---------|--------|---------|
| (1) Model | kimi (SKILL.md L32; MEMORY.md L37, L39) | `magi_dispatch.py` maps Fr to `~/.kimi-code/bin/kimi` (L18). | ✅ Matches. |
| (2) Invocation | `kimi -p "Read <paths>. Check for <issue>." > $AUDIT/fr_roundN.md 2>&1` (SKILL.md L102). Quickref: `kimi -y -p "TASK: ..." > file.md 2>&1` (L13). | `magi_dispatch.py` runs `~/.kimi-code/bin/kimi -p <prompt>` (L66-67). | ⚠️ **Missing `-y` auto-approve flag** (quickref warns forgetting `-y` causes interactive prompts); no `Read <paths>` prefix enforced. |
| (3) Constraint | “80% thinking tax, JSON at file tail, wait 120s before timeout” (`magi_dispatch.py` L21). | Timeout is 300 s (L20); no wait-before-timeout logic; no JSON sidecar append. | ❌ **Thinking-tax handling not implemented beyond a comment.** |

---

### 8. Myrrh (MAGI Myrrh / mimo)

| Check | Claimed | Actual | Verdict |
|-------|---------|--------|---------|
| (1) Model | mimo (SKILL.md L33; MEMORY.md L37, L39). Substitute: kimi when mimo unavailable. | `magi_dispatch.py` maps Myrrh to `~/.mimocode/bin/mimo` (L24). | ✅ Matches. |
| (2) Invocation | `mimo run --dangerously-skip-permissions "<prompt>" > $AUDIT/myrrh_roundN.md 2>&1` (SKILL.md L103). Quickref: `mimo run "TASK: ..." > file.md 2>&1` (L14). | `magi_dispatch.py` runs `~/.mimocode/bin/mimo run --dangerously-skip-permissions <prompt>` (L66-67). | ✅ Matches SKILL.md; ⚠️ **contradicts quickref** which omits `--dangerously-skip-permissions`. |
| (3) Constraint | Myrrh validates all `evidence_citations` resolve to real `file:line`; unresolvable → 0.5× weight; fake → reject (SKILL.md L120). | No validation logic in `magi_dispatch.py` or any other audited script. | ❌ **Evidence validation is not enforced.** |

---

## Cross-Cutting / Systemic Mismatches

1. **Script wrappers are forbidden but universally used.**
   - SOUL.md L36: “No merged processes, no script wrappers.”
   - SKILL.md L82: “Never wrap CLI calls in scripts. Each dispatch command must be independently traceable, killable, and timeoutable.”
   - Reality: `cc_dispatch.py`, `cw_dispatch.py`, `omp_run.py`, `magi_dispatch.py` are all Python wrappers around CLI calls. ❌

2. **Output-capture pattern mismatch.**
   - SKILL.md L109: “Output capture: `> file 2>&1` only.”
   - Reality: wrappers use `subprocess.run(capture_output=True)` and Python `open(...).write()`, not shell redirection. This hides output from `terminal` process logs and breaks the “independently traceable” requirement. ❌

3. **JSON sidecar requirement unenforced.**
   - SKILL.md L111-120: every MAGI output must end with a structured JSON block.
   - Reality: `magi_dispatch.py` writes only stdout; no sidecar is appended or validated. ❌

4. **Agent-patience timeout ceiling mismatch for cw.**
   - SKILL.md L184 / SOUL.md L40: cw ceiling = 180 s.
   - `cw_dispatch.py` default timeout = 300 s. ❌

5. **Archive path contradictions.**
   - SKILL.md L144: archive must be `~/Public/QUINTE/debates/YYYY-MM-DD/<topic-slug>/`; never `/tmp/quinte-audit/`.
   - SOUL.md L53 still references `/tmp/quinte-audit/<topic-slug>/` for session isolation.
   - The wrappers themselves accept any output path and set `cwd=/tmp`, making `/tmp` the effective working directory. ⚠️

6. **`--effort max` vs `--effort xhigh` inconsistency for cc.**
   - SKILL.md L92 comment says `--effort max`.
   - `cc_dispatch.py` and `settings.json` use `xhigh`.
   - MEMORY.md L21 resolves this: “--effort xhigh+ultracode(DS天花板,max=UI假象)”, so `max` is a placebo. SKILL.md comment is therefore misleading. ⚠️

7. **Model-string inconsistency in cc stack.**
   - `settings.json` env: `ANTHROPIC_MODEL=deepseek-v4-pro`.
   - `cc_dispatch.py`: `ANTHROPIC_MODEL=claude-opus-4-20250514` and `CLAUDE_CODE_SUBAGENT_MODEL=claude-opus-4-20250514`.
   - The Anthropic-compat endpoint may map the Anthropic ID to DeepSeek, but the **claimed** anti-flash subagent lock to `deepseek-v4-pro` is not what the code sets. ❌

8. **Delegate-task ban vs wrapper reality.**
   - SOUL.md L37 / SKILL.md L82 forbid `delegate_task` to preserve heterogeneity.
   - Using Python wrappers is functionally equivalent to wrapping CLI calls in scripts — the spirit of the rule (traceable, killable, no abstraction layer) is violated. ⚠️

---

## Complete Mismatch Register

| # | Agent | Category | Claim | Actual | Severity |
|---|-------|----------|-------|--------|----------|
| 1 | hm | model | DS v4-pro | no config/script; running on Kimi Code CLI | High |
| 2 | hm | enforcement | no solo implementation | honor-system only | Medium |
| 3 | cc | invocation | `scripts/run_cc.py` (quickref) | actual file is `cc_dispatch.py` | Low |
| 4 | cc | key source | `auth.json['xiaomi']['key']` (USER.md, quickref) | env/`~/.codewhale/config.toml` | High |
| 5 | cc | constraint | `--effort max` (SKILL.md comment) | `--effort xhigh` | Medium |
| 6 | cc | constraint | `CLAUDE_CODE_SUBAGENT_MODEL=deepseek-v4-pro` anti-flash | actual `claude-opus-4-20250514` | High |
| 7 | cc | key source | `DEEPSEEK_API_KEY` only (SKILL.md) | also reads `ANTHROPIC_API_KEY` | Low |
| 8 | cc | model strings | `deepseek-v4-pro` | Anthropic-compat ID `claude-opus-4-20250514` | Medium |
| 9 | cw | constraint | R1/R2 behavior constraints injected | raw prompt passed; no enforcement | High |
| 10 | cw | timeout | ceiling 180 s | default 300 s | Medium |
| 11 | cw | invocation | `TASK:` prefix in command | not prepended by wrapper | Low |
| 12 | omp | invocation | HTTPS_PROXY required | no proxy in `omp_run.py` | High |
| 13 | omp | invocation | `/usr/local/bin/omp` | bare `omp` | Low |
| 14 | omp | invocation | `-p` only | also `--thinking xhigh` | Low |
| 15 | omp | key source | `~/.claude/settings.json` (quickref) | `/tmp/omp_ds_key.txt` or `OMP_DS_KEY`; file missing | High |
| 16 | rx | invocation | `reasonix run ...` | no dispatch script exists | High |
| 17 | rx | constraint | inline-only, auto-substitute Gold | no enforcement script | High |
| 18 | rx | flags | `--model`/`--effort max` (quickref) absent in SKILL.md | internal doc conflict | Low |
| 19 | Gold | invocation | `grok build` (SKILL.md) or pipe + `--always-approve --verbatim` (quickref) | `grok -p` | Critical |
| 20 | Gold | invocation | no `-p` flag (quickref) | wrapper uses `-p` | Critical |
| 21 | Fr | invocation | `-y` auto-approve (quickref) | missing in wrapper | Medium |
| 22 | Fr | invocation | `Read <paths>` prefix (SKILL.md) | not enforced | Low |
| 23 | Myrrh | constraint | evidence-citation validation | not implemented | High |
| 24 | Myrrh | invocation | `--dangerously-skip-permissions` present (SKILL.md) | omitted in quickref | Low |
| 25 | all | architecture | no script wrappers | cc/cw/omp/MAGI all wrapped | Critical |
| 26 | all | output | shell `> file 2>&1` only | wrappers use Python capture/write | High |
| 27 | MAGI | output | JSON sidecar required | not appended/validated | High |
| 28 | constitution | paths | never `/tmp/quinte-audit/` | SOUL.md still references it; wrappers use `cwd=/tmp` | Medium |

---

## Recommendations

1. **Align cc model strings.** Decide whether `ANTHROPIC_MODEL`/`CLAUDE_CODE_SUBAGENT_MODEL` should be the Anthropic-compat ID or the DeepSeek name, then update `cc_dispatch.py`, `settings.json`, and documentation consistently.
2. **Enforce the subagent lock.** If the anti-flash rule is real, set `CLAUDE_CODE_SUBAGENT_MODEL=deepseek-v4-pro` (or the validated compat equivalent) and add a startup assertion.
3. **Fix Gold invocation.** Either update `magi_dispatch.py` to use `grok build` (per SKILL.md) or `echo ... | grok --always-approve --verbatim` (per quickref), and remove the contradictory `-p` usage.
4. **Add rx dispatch script.** Create `rx_dispatch.py` that enforces inline-content-only prompts and auto-substitutes MAGI Gold on failure.
5. **Repair omp key plumbing.** Make `omp_run.py` read from the documented key source or update documentation; ensure `/tmp/omp_ds_key.txt` is populated or remove that path.
6. **Implement MAGI sidecar & citation validation.** Append the JSON sidecar in `magi_dispatch.py` and have Myrrh validate `evidence_citations` before writing final output.
7. **Resolve the script-wrapper contradiction.** Either remove the wrappers and dispatch raw CLI commands per SOUL.md, or amend SOUL.md/SKILL.md to permit wrappers while keeping traceability (e.g., wrappers must log exact CLI invoked).
8. **Lower cw timeout default** from 300 s to 180 s to match the documented per-agent ceiling.
9. **Remove stale `/tmp/quinte-audit/` references** from SOUL.md or reconcile with SKILL.md archive path.

---

*End of audit.*
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   The user asked to output to that file. I should confirm completion and provide a brief summary in Chinese. The file has been written. I should mention the path and key mismatches. Keep it concise.

审计完成，结果已写入：

  `/Users/ericstone/Public/QUINTE/debates/2026-06-23/agent-dispatch-audit/fr_audit.md`

  核心发现（共 28 处不匹配，其中多处为严重）：

  - **cc**：实际 `CLAUDE_CODE_SUBAGENT_MODEL` 为 `claude-opus-4-20250514`，与文档宣称的 `deepseek-v4-pro` 反 flash 锁定不符；`USER.md` 和 quickref 声称的 `auth.json['xiaomi']['key']` 来源未被 `cc_dispatch.py` 使用。
  - **cw**：`cw_dispatch.py` 未注入 R1/R2 行为约束，仅透传 prompt；超时默认 300s，超出文档 cw 上限 180s。
  - **omp**：`omp_run.py` 未设置 `HTTPS_PROXY`；依赖的 `/tmp/omp_ds_key.txt` 不存在；比文档多了 `--thinking xhigh`。
  - **rx**：没有实际的调度脚本，仅存在文档。
  - **Gold**：`magi_dispatch.py` 使用 `grok -p`，与 SKILL.md 要求的 `grok build` 冲突，也与 quickref 明确声明的“grok 没有 `-p` flag”直接矛盾。
  - **Fr**：缺少 quickref 要求的 `-y` 自动确认标志。
  - **Myrrh**：未实现文档要求的 `evidence_citations` 校验。
  - **系统性矛盾**：SOUL.md/SKILL.md 明确禁止脚本包装，但 cc/cw/omp/MAGI 全部使用 Python wrapper；且 wrapper 使用 Python capture 而非文档要求的 shell `> file 2>&1`；MAGI JSON sidecar 也未被追加/校验。

  详细按 agent 的模型、调用方式、约束执行三维度逐项列出，并附行号引用，见上述文件。

To resume this session: kimi -r session_0103d035-29a1-41eb-803c-ddb0af6654a1
