[0m
> build · glm-5.2
[0m
[0m$ [0mls -la ~/Public/HIGHBALL/specs/ 2>&1; echo "---README---"; ls -la ~/Public/HIGHBALL/ 2>&1
total 104
drwxr-xr-x@ 11 ericstone  staff    352 Jun 22 00:53 .
drwxr-xr-x@ 12 ericstone  staff    384 Jun 22 00:58 ..
-rw-r--r--@  1 ericstone  staff    987 Jun 17 01:35 cato-constraint.md
-rw-r--r--@  1 ericstone  staff    766 Jun 17 01:35 deadlock-record.md
-rw-r--r--@  1 ericstone  staff    879 Jun 17 01:35 kansa-two-domain.md
-rw-r--r--@  1 ericstone  staff   4387 Jun 22 00:51 kennomon-architecture-gate.md
-rw-r--r--@  1 ericstone  staff    731 Jun 17 01:35 post-mortem.md
-rw-r--r--@  1 ericstone  staff    815 Jun 17 01:35 riskclass-profiles.md
-rw-r--r--@  1 ericstone  staff    908 Jun 17 01:35 rubicon-aps.md
-rw-r--r--@  1 ericstone  staff   5730 Jun 19 05:28 storm-integration.md
-rw-r--r--@  1 ericstone  staff  11889 Jun 22 00:53 theoretical-foundation.md
---README---
total 64
drwxr-xr-x@ 12 ericstone  staff    384 Jun 22 00:58 .
drwxr-xr-x+ 14 ericstone  staff    448 Jun 23 21:27 ..
drwxr-xr-x@ 16 ericstone  staff    512 Jun 23 02:31 .git
-rw-r--r--@  1 ericstone  staff     18 Jun 17 22:49 .gitignore
drwxr-xr-x@  3 ericstone  staff     96 Jun 19 17:46 data
drwxr-xr-x@ 12 ericstone  staff    384 Jun 17 22:44 debates
drwxr-xr-x@  3 ericstone  staff     96 Jun 19 18:24 lib
-rw-r--r--@  1 ericstone  staff   1072 Jun 16 10:24 LICENSE
drwxr-xr-x   3 ericstone  staff     96 Jun 22 00:51 ontology
-rw-r--r--@  1 ericstone  staff  20536 Jun 22 00:53 README.md
drwxr-xr-x@  3 ericstone  staff     96 Jun 19 17:55 scripts
drwxr-xr-x@ 11 ericstone  staff    352 Jun 22 00:53 specs
[0m
I'll start by exploring the HIGHBALL repo structure and finding the SOUL.md files in parallel.
[0m$ [0mls -la ~/.hermes/profiles/technical/ 2>&1; echo "---hermes-core---"; ls -la ~/Public/hermes-core-rules-mac-x86/ 2>&1
total 1355024
drwx------@  59 ericstone  staff       1888 Jun 23 23:17 .
drwxr-xr-x@   4 ericstone  staff        128 May 27 03:57 ..
-rw-r--r--@   1 ericstone  staff       6148 May 20 19:00 .DS_Store
-rw-------@   1 ericstone  staff      20062 Jun 21 18:04 .env
drwxr-xr-x@  15 ericstone  staff        480 Jun 22 03:05 .git
-rw-r--r--@   1 ericstone  staff        491 Jun 22 02:38 .gitignore
-rw-r--r--@   1 ericstone  staff     520852 Jun 23 23:16 .hermes_history
-rw-r--r--@   1 ericstone  staff         70 Jun 23 20:25 .update_check
drwx------@   2 ericstone  staff         64 Jun 22 02:38 audio_cache
-rw-------@   1 ericstone  staff       6925 Jun 23 20:25 auth.json
-rw-r--r--@   1 ericstone  staff          0 May 18 13:04 auth.lock
drwxr-xr-x@   5 ericstone  staff        160 Jun  4 06:45 bin
drwxr-xr-x@   6 ericstone  staff        192 Jun 23 22:19 cache
-rw-------@   1 ericstone  staff        628 Jun 23 11:03 channel_directory.json
drwxr-xr-x@   3 ericstone  staff         96 May 18 14:30 checkpoints
-rw-------@   1 ericstone  staff      17973 Jun 21 18:12 config.yaml
-rw-------@   1 ericstone  staff      14485 May 27 12:22 config.yaml.bak
-rw-------@   1 ericstone  staff      14528 May 27 22:57 config.yaml.bak.20260601_120628
-rw-------@   1 ericstone  staff      16066 Jun  1 12:07 config.yaml.bak.20260601_120732
-rw-------@   1 ericstone  staff      17447 Jun 15 13:00 config.yaml.bak.20260616_085213
-rw-------@   1 ericstone  staff      17468 Jun 16 08:59 config.yaml.bak.20260616_085912
-rw-------@   1 ericstone  staff      17468 Jun 16 08:59 config.yaml.bak.20260616_090121
-rw-------@   1 ericstone  staff      17535 Jun 16 09:03 config.yaml.bak.20260616_090403
-rw-------@   1 ericstone  staff      16454 Jun 16 09:25 config.yaml.bak.20260616_175950
-rw-------@   1 ericstone  staff      17573 Jun 16 18:03 config.yaml.bak.20260616_194112
-rw-------@   1 ericstone  staff      16446 Jun 17 22:57 config.yaml.bak.20260619_101716
-rw-------@   1 ericstone  staff      17699 Jun 20 13:26 config.yaml.bak.20260621_180408
-rw-------@   1 ericstone  staff      17978 Jun 21 18:04 config.yaml.bak.20260621_181135
drwx------@   8 ericstone  staff        256 Jun 23 23:16 cron
-rw-r--r--@   1 ericstone  staff        160 Jun 22 11:42 desktop-build-stamp.json
-rw-------@   1 ericstone  staff        290 Jun 23 11:03 gateway_state.json
-rw-r--r--@   1 ericstone  staff        146 Jun 23 11:03 gateway.lock
-rwxr-xr-x@   1 ericstone  staff        146 Jun 23 11:03 gateway.pid
drwxr-xr-x@  30 ericstone  staff        960 Jun 11 16:57 home.bak.20260611
drwx------@   2 ericstone  staff         64 Jun 22 02:38 hooks
drwx------@   2 ericstone  staff         64 Jun 22 02:38 image_cache
-rw-r--r--@   1 ericstone  staff     367044 Jun 23 23:16 interrupt_debug.log
-rw-r--r--@   1 ericstone  staff       1072 Jun 11 18:51 LICENSE
drwx------@  17 ericstone  staff        544 Jun 22 12:02 logs
drwxr-xr-x@   6 ericstone  staff        192 May 28 01:40 lsp
drwx------@  21 ericstone  staff        672 Jun 23 23:14 memories
-rw-------@   1 ericstone  staff    2385025 Jun 23 22:32 models_dev_cache.json
-rw-------@   1 ericstone  staff        734 Jun 23 22:19 ollama_cloud_models_cache.json
drwx------@   2 ericstone  staff         64 Jun 22 02:38 pairing
drwxr-xr-x@ 218 ericstone  staff       6976 Jun 23 23:09 pastes
-rw-------@   1 ericstone  staff      12873 Jun 23 23:17 processes.json
-rw-------@   1 ericstone  staff       1969 Jun 23 22:19 provider_models_cache.json
-rw-r--r--@   1 ericstone  staff       3265 Jun 11 18:52 README.md
drwxr-xr-x@   3 ericstone  staff         96 Jun 22 03:06 sandboxes
drwxr-xr-x@   5 ericstone  staff        160 Jun 22 02:38 scripts
drwx------@ 617 ericstone  staff      19744 Jun 19 11:30 sessions
-rw-r--r--@   1 ericstone  staff          0 Jun  1 12:13 sessions.db
-rw-r--r--@   1 ericstone  staff       3931 Jun 20 14:43 SETUP.md
drwx------@  42 ericstone  staff       1344 Jun 23 23:15 skills
-rw-r--r--@   1 ericstone  staff       5223 Jun 23 23:12 SOUL.md
drwxr-xr-x@   3 ericstone  staff         96 Jun 22 11:41 state-snapshots
-rw-r--r--@   1 ericstone  staff  681775104 Jun 23 23:17 state.db
-rw-r--r--@   1 ericstone  staff      32768 Jun 23 11:04 state.db-shm
-rw-r--r--@   1 ericstone  staff    1273112 Jun 23 23:17 state.db-wal
---hermes-core---
total 72
drwxr-xr-x@ 12 ericstone  staff   384 Jun 23 22:43 .
drwxr-xr-x+ 14 ericstone  staff   448 Jun 23 21:27 ..
drwxr-xr-x@ 16 ericstone  staff   512 Jun 23 22:51 .git
-rw-r--r--@  1 ericstone  staff   491 Jun 22 03:07 .gitignore
-rw-r--r--@  1 ericstone  staff  5767 Jun 23 21:27 deepseek-cc-switch-verification.json
-rw-r--r--@  1 ericstone  staff  1072 Jun 18 00:40 LICENSE
drwxr-xr-x@  5 ericstone  staff   160 Jun 23 21:14 memories
-rw-r--r--@  1 ericstone  staff  5721 Jun 22 12:57 README.md
drwxr-xr-x@  3 ericstone  staff    96 Jun 23 21:13 scripts
-rw-r--r--@  1 ericstone  staff  3931 Jun 20 15:09 SETUP.md
drwxr-xr-x@ 32 ericstone  staff  1024 Jun 22 03:07 skills
-rw-r--r--@  1 ericstone  staff  5199 Jun 23 22:44 SOUL.md
[0m
[0m→ [0mRead /Users/ericstone/Public/HIGHBALL/README.md
[0m
[0m$ [0mls -la ~/.hermes/profiles/technical/SOUL.md 2>&1; echo "---"; ls -la ~/.hermes/SOUL.md 2>&1
-rw-r--r--@ 1 ericstone  staff  5223 Jun 23 23:12 /Users/ericstone/.hermes/profiles/technical/SOUL.md
---
-rw-------@ 1 ericstone  staff  513 May 27 15:41 /Users/ericstone/.hermes/SOUL.md
[0m
[0m→ [0mRead /Users/ericstone/Public/HIGHBALL/specs/kennomon-architecture-gate.md
HIGHBALL confirmed to have no `specs/PROTOCOL.md`. Let me read the HIGHBALL README, key constraint files, and locate the actual SOUL.md files (the `profiles/technical/` path may not exist).
[0m→ [0mRead /Users/ericstone/Public/HIGHBALL/specs/theoretical-foundation.md
[0m→ [0mRead /Users/ericstone/.hermes/profiles/technical/SOUL.md
[0m→ [0mRead /Users/ericstone/Public/hermes-core-rules-mac-x86/SOUL.md
[0m
[0m$ [0mls ~/Public/QUINTE/specs/PROTOCOL.md ~/Public/MAGI/specs/PROTOCOL.md 2>&1
/Users/ericstone/Public/MAGI/specs/PROTOCOL.md
/Users/ericstone/Public/QUINTE/specs/PROTOCOL.md
[0m
HIGHBALL confirmed: no `PROTOCOL.md`; its authoritative doc is `README.md` (comprehensive, 300 lines, covers KANSA/KENGEN/BANNIN/KOZO). Now let me read both SOUL.md files and grep all repos for broken references in parallel.
[0m✱ [0mGrep "HIGHBALL.{0,40}PROTOCOL\.md|HIGHBALL.{0,40}specs/PROTOCOL"[90m in /Users/ericstone/.hermes · 2 matches[0m
[0m✱ [0mGrep "HIGHBALL.{0,40}PROTOCOL\.md|HIGHBALL.{0,40}specs/PROTOCOL"[90m in /Users/ericstone/Public · 3 matches[0m
[0m→ [0mRead /Users/ericstone/Public/hermes-core-rules-win/SOUL.md[90m [limit=4][0m
Complete picture now. Findings:

**Confirmed:**
- `QUINTE/specs/PROTOCOL.md` ✓ exists
- `MAGI/specs/PROTOCOL.md` ✓ exists
- `HIGHBALL/specs/PROTOCOL.md` ✗ does NOT exist — HIGHBALL's authoritative doc is `README.md` (300 lines, comprehensive KANSA/KENGEN/BANNIN/KOZO spec, points to `specs/` for detail)

**Broken references (3 SOUL.md files):**
1. `~/.hermes/profiles/technical/SOUL.md:3`
2. `~/Public/hermes-core-rules-mac-x86/SOUL.md:3`
3. `~/Public/hermes-core-rules-win/SOUL.md:3` (found via grep — not in your list)

**Decision: Option B** (reference HIGHBALL `README.md`). HIGHBALL is a constraint layer, not a protocol — forcing it into the `specs/PROTOCOL.md` pattern is a category error. `README.md` is the real, maintained authority (updated Jun 22, self-describes as "the constraint layer for AI agent outputs"). Option A (stub `PROTOCOL.md` index) would just be fragile indirection that can itself go stale — the exact bug we're fixing.

Let me confirm the win file's exact text, then apply.
[0m→ [0mRead /Users/ericstone/Public/hermes-core-rules-mac-x86/memories/POSTMORTEM.md[90m [offset=115, limit=15][0m
[0m
[0m← [0mEdit /Users/ericstone/.hermes/profiles/technical/SOUL.md
Index: /Users/ericstone/.hermes/profiles/technical/SOUL.md
===================================================================
--- /Users/ericstone/.hermes/profiles/technical/SOUL.md
+++ /Users/ericstone/.hermes/profiles/technical/SOUL.md
@@ -1,7 +1,7 @@
 # Hermes Agent Constitution
 
-Constitutional files: SOUL · USER · MEMORY · SKILL · POSTMORTEM. Protocol authority: QUINTE / MAGI / HIGHBALL `specs/PROTOCOL.md`.
+Constitutional files: SOUL · USER · MEMORY · SKILL · POSTMORTEM. Protocol authority: QUINTE / MAGI `specs/PROTOCOL.md` · HIGHBALL `README.md` (specs/ for detail).
 
 ## ⛔ Iron Law — MAGI Before All (highest priority)
 
 **No MAGI, no QUINTE. No MAGI, no file modification.**

[0m
[0m← [0mEdit /Users/ericstone/Public/hermes-core-rules-mac-x86/SOUL.md
Index: /Users/ericstone/Public/hermes-core-rules-mac-x86/SOUL.md
===================================================================
--- /Users/ericstone/Public/hermes-core-rules-mac-x86/SOUL.md
+++ /Users/ericstone/Public/hermes-core-rules-mac-x86/SOUL.md
@@ -1,7 +1,7 @@
 # Hermes Agent Constitution
 
-Constitutional files: SOUL · USER · MEMORY · SKILL · POSTMORTEM. Protocol authority: QUINTE / MAGI / HIGHBALL `specs/PROTOCOL.md`.
+Constitutional files: SOUL · USER · MEMORY · SKILL · POSTMORTEM. Protocol authority: QUINTE / MAGI `specs/PROTOCOL.md` · HIGHBALL `README.md` (specs/ for detail).
 
 ## ⛔ Iron Law — MAGI Before All (highest priority)
 
 **No MAGI, no QUINTE. No MAGI, no file modification.**

[0m
All confirmed. The win file's line 3 has a slightly different prefix but the same broken `HIGHBALL \`specs/PROTOCOL.md\`` substring.

The POSTMORTEM.md lines (122, 124) are **historical audit records** describing the finding ("HIGHBALL/PROTOCOL.md referenced but doesn't exist") — not active broken references. I'll leave them as point-in-time records (editing postmortems to reflect current state is ahistorical) and flag them to you.

Applying the Option B fix to all 3 SOUL.md files:
[0m← [0mEdit /Users/ericstone/Public/hermes-core-rules-win/SOUL.md
Index: /Users/ericstone/Public/hermes-core-rules-win/SOUL.md
===================================================================
--- /Users/ericstone/Public/hermes-core-rules-win/SOUL.md
+++ /Users/ericstone/Public/hermes-core-rules-win/SOUL.md
@@ -1,7 +1,7 @@
 # Hermes Agent Constitution
 
-Constitutional files: SOUL.md · memories/USER.md · memories/MEMORY.md · skills/multi-agent-debate/SKILL.md · memories/POSTMORTEM.md. Protocol authority: QUINTE / MAGI / HIGHBALL `specs/PROTOCOL.md`.
+Constitutional files: SOUL.md · memories/USER.md · memories/MEMORY.md · skills/multi-agent-debate/SKILL.md · memories/POSTMORTEM.md. Protocol authority: QUINTE / MAGI `specs/PROTOCOL.md` · HIGHBALL `README.md` (specs/ for detail).
 
 ## Iron Law — MAGI Before All
 
 **No MAGI, no QUINTE. No MAGI, no file modification.**

[0m
[0m$ [0mecho "=== Verify line 3 of each SOUL.md ==="; rg -n "Protocol authority" ~/.hermes/profiles/technical/SOUL.md ~/Public/hermes-core-rules-mac-x86/SOUL.md ~/Public/hermes-core-rules-win/SOUL.md
=== Verify line 3 of each SOUL.md ===
/Users/ericstone/Public/hermes-core-rules-win/SOUL.md:3:Constitutional files: SOUL.md · memories/USER.md · memories/MEMORY.md · skills/multi-agent-debate/SKILL.md · memories/POSTMORTEM.md. Protocol authority: QUINTE / MAGI `specs/PROTOCOL.md` · HIGHBALL `README.md` (specs/ for detail).
/Users/ericstone/.hermes/profiles/technical/SOUL.md:3:Constitutional files: SOUL · USER · MEMORY · SKILL · POSTMORTEM. Protocol authority: QUINTE / MAGI `specs/PROTOCOL.md` · HIGHBALL `README.md` (specs/ for detail).
/Users/ericstone/Public/hermes-core-rules-mac-x86/SOUL.md:3:Constitutional files: SOUL · USER · MEMORY · SKILL · POSTMORTEM. Protocol authority: QUINTE / MAGI `specs/PROTOCOL.md` · HIGHBALL `README.md` (specs/ for detail).
[0m
All three applied. Now let me verify the edits and do a final sweep for any remaining broken references (broader patterns).
[0m✱ [0mGrep "HIGHBALL[ /]+(specs/)?PROTOCOL\.md|HIGHBALL.{0,20}PROTOCOL\.md"[90m in /Users/ericstone/.hermes · 1 match[0m
[0m✱ [0mGrep "HIGHBALL[ /]+(specs/)?PROTOCOL\.md|HIGHBALL.{0,20}PROTOCOL\.md"[90m in /Users/ericstone/Public · 1 match[0m
Done. Summary:

**Decision: Option B** — HIGHBALL is a constraint layer, not a protocol; its `README.md` (300 lines, updated Jun 22, self-describes as "the constraint layer for AI agent outputs") is the real authority. Option A would be a stub `PROTOCOL.md` indexing other files — fragile indirection that can itself go stale (the exact bug being fixed). `QUINTE`/`MAGI` keep `specs/PROTOCOL.md` (verified both exist).

**Fixed (3 SOUL.md files)** — line 3 now reads:
```
Protocol authority: QUINTE / MAGI `specs/PROTOCOL.md` · HIGHBALL `README.md` (specs/ for detail).
```
- `~/.hermes/profiles/technical/SOUL.md`
- `~/Public/hermes-core-rules-mac-x86/SOUL.md`
- `~/Public/hermes-core-rules-win/SOUL.md` ← 3rd found via grep, not in your list

**Left intact (2 files):** `memories/POSTMORTEM.md` line 122 in both `~/.hermes/profiles/technical/` and `~/Public/hermes-core-rules-mac-x86/` contain `HIGHBALL/PROTOCOL.md referenced but doesn't exist`. These are **historical audit records** (2026-06-23 MAGI cross-repo audit root-cause), not active references. Editing point-in-time postmortems to reflect the fix would be ahistorical. Say the word if you'd prefer them annotated/updated instead.

No other repos reference HIGHBALL's PROTOCOL.md.
