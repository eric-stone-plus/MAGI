[0m
> build · mimo-v2.5-pro
[0m
[0m→ [0mRead ../../.hermes/profiles/technical/skills/multi-agent-debate/scripts/magi_dispatch.py
Looking at the file — items 2-4 (Gold/Fr/Myrrh fixes) are already in place. I need to add the JSON sidecar appender (items 5-6).
[0m
[0m← [0mEdit ../../.hermes/profiles/technical/skills/multi-agent-debate/scripts/magi_dispatch.py
Index: /Users/ericstone/.hermes/profiles/technical/skills/multi-agent-debate/scripts/magi_dispatch.py
===================================================================
--- /Users/ericstone/.hermes/profiles/technical/skills/multi-agent-debate/scripts/magi_dispatch.py
+++ /Users/ericstone/.hermes/profiles/technical/skills/multi-agent-debate/scripts/magi_dispatch.py
@@ -77,9 +77,29 @@
 stdout_bytes = len(result.stdout.encode('utf-8')) if result.stdout else 0
 
 with open(output_path, 'w') as f:
     f.write(result.stdout or '')
-
+
+sidecar = {
+    "status": "ok" if result.returncode == 0 and stdout_bytes > 0 else "error",
+    "confidence": 1.0 if result.returncode == 0 and stdout_bytes > 0 else 0.0,
+    "reasoning_chain": [
+        f"doctor={doctor}",
+        f"exit_code={result.returncode}",
+        f"stdout_bytes={stdout_bytes}",
+        f"timeout={cfg['timeout']}s"
+    ],
+    "diff": {
+        "before": prompt[:512],
+        "after": (result.stdout or '')[:512]
+    },
+    "verdict": "success" if result.returncode == 0 and stdout_bytes > 0 else "failed"
+}
+with open(output_path, 'a') as f:
+    f.write("\n\n```json\n")
+    json.dump(sidecar, f, indent=2)
+    f.write("\n```\n")
+
 if result.returncode != 0 or stdout_bytes == 0:
     classification = classify_error(result.returncode, result.stderr or '', stdout_bytes, doctor)
     print(json.dumps(classification), file=sys.stderr)
     return result.returncode or 1

[0m
[0m→ [0mRead ../../.hermes/profiles/technical/skills/multi-agent-debate/scripts/magi_dispatch.py
Let me verify the result:
Quick syntax check:
[0m
[0m$ [0mpython3 -m py_compile /Users/ericstone/.hermes/profiles/technical/skills/multi-agent-debate/scripts/magi_dispatch.py && echo "OK"
OK
[0m
Done. Summary of changes to `magi_dispatch.py`:

| Bug | Status |
|-----|--------|
| Gold (grok): `--always-approve` | Already present (line 13) |
| Fr (kimi): `-y` | Already present (line 19) |
| Myrrh (mimo): `/usr/local/bin/mimo` | Already present (line 24) |
| JSON sidecar appender | **Added** (lines 82–100) |

The sidecar is appended as a fenced JSON block after stdout, containing `status`, `confidence`, `reasoning_chain`, `diff.before`/`diff.after` (prompt vs output, truncated to 512 chars), and `verdict`.
