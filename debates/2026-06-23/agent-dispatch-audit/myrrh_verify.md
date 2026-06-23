[0m
> build · mimo-v2.5-pro
[0m
[0m$ [0mcat ~/.claude/settings.json 2>&1 | python3 -c 'import json,sys; d=json.load(sys.stdin); print("effort:", d.get("effortLevel"), "ultracode:", d.get("ultracode"), "model:", d.get("model"))' 2>&1
effort: xhigh ultracode: True model: claude-opus-4-20250514
[0m
[0m$ [0mwhich grok 2>&1 && grok --help 2>&1 | head -3 || echo "FAIL: grok not found"
/Users/ericstone/.local/bin/grok
Grok Build TUI

Usage: grok [OPTIONS] [PROMPT] [COMMAND]
[0m
[0m$ [0mwhich kimi 2>&1 && kimi --version 2>&1 || echo "FAIL: kimi not found"
/Users/ericstone/.kimi-code/bin/kimi
0.15.0
[0m
[0m$ [0mpython3 ~/.hermes/profiles/technical/skills/multi-agent-debate/scripts/cc_dispatch.py 'test' /tmp/cc_verify.md 2>&1
{"status": "ok", "class": "success", "retry": "none", "action": "none", "bytes": 187}
[0m
[0m$ [0mwhich mimo 2>&1 && mimo --version 2>&1 || echo "FAIL: mimo not found"
/usr/local/bin/mimo
0.1.1
[0m
[0m$ [0mwhich reasonix 2>&1 && reasonix --help 2>&1 | head -3 || echo "FAIL: reasonix not found"
/usr/local/bin/reasonix
Usage: reasonix [options] [command]

DeepSeek-native agent framework — built for cache hits and cheap tokens.
[0m
[0m$ [0mwhich codewhale 2>&1 && codewhale --help 2>&1 | head -3 || echo "FAIL: codewhale not found"
/Users/ericstone/.local/bin/codewhale
Usage: codewhale [OPTIONS] [PROMPT]
       codewhale [OPTIONS] <COMMAND> [ARGS]
[0m
Running all verification checks in parallel.
[0m$ [0mwhich omp 2>&1 && omp --help 2>&1 | head -3 || echo "FAIL: omp not found"
/usr/local/bin/omp
omp v16.1.16

USAGE
[0m
All 8 checks passed. Writing JSON verdict:
[0m$ [0mcat > /tmp/cc_verify.json << 'EOF'
{
  "verdict": "ALL_PASS",
  "timestamp": "2026-06-23T00:00:00Z",
  "checks": {
    "cc_dispatch.py": {
      "status": "ok",
      "evidence": "{\"status\":\"ok\",\"class\":\"success\",\"retry\":\"none\",\"action\":\"none\",\"bytes\":187}"
    },
    "claude_settings": {
      "status": "ok",
      "evidence": "effort: xhigh, ultracode: True, model: claude-opus-4-20250514"
    },
    "grok": {
      "status": "ok",
      "path": "/Users/ericstone/.local/bin/grok",
      "evidence": "Grok Build TUI — version info available"
    },
    "kimi": {
      "status": "ok",
      "path": "/Users/ericstone/.kimi-code/bin/kimi",
      "evidence": "version 0.15.0"
    },
    "mimo": {
      "status": "ok",
      "path": "/usr/local/bin/mimo",
      "evidence": "version 0.1.1"
    },
    "omp": {
      "status": "ok",
      "path": "/usr/local/bin/omp",
      "evidence": "omp v16.1.16"
    },
    "reasonix": {
      "status": "ok",
      "path": "/usr/local/bin/reasonix",
      "evidence": "DeepSeek-native agent framework"
    },
    "codewhale": {
      "status": "ok",
      "path": "/Users/ericstone/.local/bin/codewhale",
      "evidence": "codewhale CLI available"
    }
  },
  "failed": []
}
EOF
echo "Written to /tmp/cc_verify.json"
Written to /tmp/cc_verify.json
[0m
**Verdict: ALL_PASS** — 8/8 checks succeeded, 0 failures.

| # | Check | Result | Evidence |
|---|-------|--------|----------|
| 1 | cc_dispatch.py | OK | status=ok, class=success |
| 2 | claude settings | OK | effort=xhigh, ultracode=True, model=claude-opus-4-20250514 |
| 3 | grok | OK | `/Users/ericstone/.local/bin/grok` — Grok Build TUI |
| 4 | kimi | OK | `/Users/ericstone/.kimi-code/bin/kimi` — v0.15.0 |
| 5 | mimo | OK | `/usr/local/bin/mimo` — v0.1.1 |
| 6 | omp | OK | `/usr/local/bin/omp` — v16.1.16 |
| 7 | reasonix | OK | `/usr/local/bin/reasonix` — DeepSeek-native agent framework |
| 8 | codewhale | OK | `/Users/ericstone/.local/bin/codewhale` — CLI available |

JSON sidecar written to `/tmp/cc_verify.json`.
