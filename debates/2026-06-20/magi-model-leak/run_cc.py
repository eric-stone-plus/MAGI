import json, subprocess, os
key = json.load(open(os.path.expanduser('~/.local/share/mimocode/auth.json')))['xiaomi']['key']
prompt = "Quick audit — the MAGI protocol spec is supposed to be model-agnostic: only Gold, Frankincense, Myrrh as roles, no concrete model names (grok, kimi, mimo, DeepSeek, etc). But some files still leak model names. I found 3 in README.md and theoretical-foundation.md.\n\nWe need to check: are there OTHER model name leaks in the MAGI repo that I missed? Beyond just grok/kimi/mimo — also 'grok-build', 'K2.7', 'v2.5-pro', 'DeepSeek v4-pro', 'DS v4-pro'. Where else might model names be hiding in protocol docs where they shouldn't be?"
env = os.environ.copy()
env['ANTHROPIC_BASE_URL'] = 'https://token-plan-cn.xiaomimimo.com'
env['ANTHROPIC_AUTH_TOKEN'] = key
env['ANTHROPIC_MODEL'] = 'mimo-v2.5-pro'
env['HOME'] = os.path.expanduser('~')
with open('/tmp/quinte-audit/magi-model-leak/cc_round1.md', 'w') as f:
    subprocess.run(['claude', '-p', '--permission-mode', 'bypassPermissions', '--effort', 'xhigh', prompt], env=env, stdout=f, stderr=subprocess.STDOUT, timeout=300)
