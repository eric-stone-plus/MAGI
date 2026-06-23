I'll read `r1_context.md` and trace how local mode vs SSH are implemented so the verdict is grounded in the actual code.
I'll read the other analysis files in the workspace for a fuller picture.
I'll locate and read the actual `SSHTransport.swift` implementation to verify the safety analysis.
I'll trace how service commands are built and whether tests cover the local path.
## Verdict: **Migrate — use local as primary, keep SSH as fallback for ~2 weeks**

After reading `r1_context.md` and the v1.2.0 source (`SSHTransport.swift`, `ConnectionProfile.swift`, tests), local mode is the right default for a same-Mac Hermes setup. The implementation is small and deliberate, not a risky rewrite.

---

### Is the new code path safe?

**Yes, for your use case.** The local branch is ~10 lines in `execute()`:

```67:76:/Users/ericstone/hermes-desktop/Sources/HermesDesktop/Services/SSH/SSHTransport.swift
        if connection.kind == .local {
            if let validationError = connection.validationError {
                throw SSHTransportError.invalidConnection(validationError)
            }
            return try await processRunner.run(
                executableURL: URL(fileURLWithPath: "/bin/sh"),
                arguments: ["-c", remoteCommand],
                standardInput: standardInput
            )
        }
```

What makes it safe:

1. **Same command pipeline** — Callers still pass `connection.remoteServiceCommand(...)`, which exports `HERMES_HOME` and a curated `PATH` (Hermes venv, `~/.local/bin`, Homebrew, etc.) before running the actual command. Only the transport changes (`/bin/sh` instead of `/usr/bin/ssh`).

2. **Tests exist** — Unit tests cover local launch, terminal bootstrap, and profile fingerprints. `LocalHermesIntegrationTests` runs a full discovery/files/skills/cron/kanban smoke test when `HERMES_RUN_LOCAL_INTEGRATION=1`.

3. **Backward compatible** — Connections without `kind` decode as `.ssh`, so your existing SSH entry keeps working.

4. **Security posture improves** — SSH-to-localhost needs Remote Login, `sshd`, and key management for work that never leaves the machine. Local mode runs as your macOS user via `Process()` with no network hop. Same effective privilege, less attack surface.

---

### Hidden risks: Process() vs SSH

| Concern | SSH localhost (current) | Local Process() |
|---|---|---|
| **PATH / python3** | Non-interactive SSH often has a stripped PATH — Hermes even has dedicated error messages for this | `remoteServiceCommand` sets PATH explicitly; avoids the classic SSH localhost pitfall |
| **Environment** | Opaque login-shell behavior over SSH | Service calls inherit the GUI app env, but HERMES_HOME/PATH are set in the shell wrapper anyway |
| **Terminal sessions** | SSH PTY + bootstrap | `localTerminalEnvironment()` sets HOME, USER, SHELL, PATH, TERM explicitly — more predictable than SSH loopback |
| **Latency** | ~50ms per roundtrip (negligible) | Direct subprocess, slightly faster |
| **User identity** | Can SSH as a different user | Always current macOS user — fine for "this Mac, my profile" |
| **Code maturity** | Battle-tested | New in v1.2.0, but narrow surface area |

**Real edge cases to watch:**

- **`.zshrc` / `.zprofile` noise** — Both paths use non-interactive `/bin/sh -c`. If startup files print text, JSON discovery can break. Hermes detects this and surfaces a clear error. Unlikely to bite you if SSH already works cleanly.
- **Service `execute()` doesn't set Process environment** — Only terminal launch does via `localTerminalEnvironment()`. Mitigated because every service command self-exports HERMES_HOME and PATH in the shell string.
- **Minor buglet** — Local failures are thrown as `SSHTransportError.remoteFailure` (misnamed, not unsafe).

For your `technical` profile on this Mac, local mode should be **more reliable** than SSH loopback, mainly because it sidesteps SSH PATH issues.

---

### Should you keep SSH as fallback?

**Yes, temporarily — not forever.**

Recommended approach (matches the proposed plan in `r1_context.md`):

1. **Add** a local connection alongside the existing SSH one — don't delete SSH yet.
2. **Switch active** to local and run your real workflow: Overview refresh, discovery, sessions, files, cron, terminal tab.
3. **Keep SSH for 1–2 weeks** as instant rollback (flip active connection in `connections.json`).
4. **Remove SSH localhost** once local is proven — you can disable Remote Login and drop the loopback SSH config.

Keep the **SSH connection type** in Hermes generally; you'll want it if you ever connect to a remote Mac, Pi, or VPS. Only the *localhost SSH workaround* becomes redundant.

Proposed local entry:

```json
{"id": "<new-uuid>", "kind": "local", "label": "Local Hermes (Direct)", "hermesProfile": "technical"}
```

---

### Bottom line

| Question | Answer |
|---|---|
| Migrate to local mode? | **Yes** |
| Is it safe? | **Yes** — simpler, well-tested, same command layer |
| Hidden Process() risks? | **Low** — mostly env/PATH, already handled by `remoteServiceCommand` |
| Keep SSH fallback? | **Yes, short term** — delete localhost SSH after validation, keep SSH type for remotes |

This is a low-risk, high-benefit change. The dual-connection rollout removes rollback risk entirely. I'd make local primary today and retire SSH-to-localhost once you've exercised your normal Hermes Desktop workflow for a week or two.
