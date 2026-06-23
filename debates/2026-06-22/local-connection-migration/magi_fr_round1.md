# magi R1 Analysis: SSHTransport.swift Local Code Path Safety

## Scope
Review the new v1.2.0 direct-local code path in `SSHTransport.swift`, specifically:
- Does the `Process()`-based local execution look safe?
- What are the implications of `Process()` inheriting Hermes Desktop's environment?

Source reviewed: `/Users/ericstone/hermes-desktop/Sources/HermesDesktop/Services/SSH/SSHTransport.swift` (lines 61-76, 162-201, 484-568) and `ConnectionProfile.swift` (lines 202-219, 226-243, 309-365).

## Local Code Path Summary

When `connection.kind == .local`, `execute(...)` bypasses `/usr/bin/ssh` and runs the same generated shell command directly via `/bin/sh -c <remoteCommand>` (SSHTransport.swift L67-76). The command string is produced by `ConnectionProfile.remoteServiceCommand(...)`, which wraps the caller's command with:

```sh
export HERMES_HOME="..."
export PATH="<hermes-venv>:$HOME/.local/bin:$HOME/.hermes/hermes-agent/venv/bin:$HOME/.cargo/bin:/opt/homebrew/bin:/usr/local/bin:$PATH"
exec /bin/sh -c "<escaped command>"
```

For terminal sessions, `terminalLaunch(...)` returns a `ProcessLaunch` using `localTerminalEnvironment()` (L183-201), which copies `ProcessInfo.processInfo.environment` and explicitly sets/falls-back `HOME`, `USER`, `LOGNAME`, `SHELL`, `PATH`, `TERM`, and `COLORTERM`.

## Safety Assessment

### 1. `Process()` Environment Inheritance

`FoundationSSHProcessRunner.run()` (L491) creates a `Process()` and **does not set** `process.environment`. Therefore the spawned `/bin/sh` inherits Hermes Desktop's own environment (the same behavior as if you launched `/bin/sh` from the app).

**Concern:** If Hermes Desktop is launched from Finder / Launch Services, its `PATH` is typically the macOS default (`/usr/bin:/bin:/usr/sbin:/sbin`), which is much smaller than an interactive zsh shell's PATH. The same concern applies to other inherited env vars (e.g., `PYENV_ROOT`, `NVM_DIR`, `JAVA_HOME`) that the user may rely on in their `.zshrc`/`.zprofile`.

**Mitigation in the code:** The `remoteServiceCommand(...)` explicitly exports a new `PATH` that prepends the profile's Hermes venv, common user binary locations (`$HOME/.local/bin`, `$HOME/.cargo/bin`, `/opt/homebrew/bin`, `/usr/local/bin`), and the inherited `$PATH`. So `python3`, `hermes`, and other core tools should be discoverable even if the parent app's PATH is minimal. `HERMES_HOME` is also explicitly exported, so commands do not depend on inherited `HOME` being correct.

**Verdict on environment inheritance:** Acceptable for the intended use case. The explicit PATH/HERMES_HOME exports make the local path *more* predictable than a raw inherited environment, and no more dependent on shell dotfiles than the existing non-interactive SSH path (which also runs `/bin/sh -c` without sourcing `.zshrc`).

### 2. Command Injection / Unsafe Input Handling

The local branch executes `remoteCommand` via `/bin/sh -c`. That command string is built from user-provided inputs (`hermesProfile`, `customHermesHomePath`).

- `hermesProfile` is validated: cannot contain `/`, `.`, `..`, whitespace, or control characters (ConnectionProfile.swift L346-353).
- `customHermesHomePath` is validated: must start with `~/` or `/`, no control characters (L355-362).
- Both values are shell-escaped when interpolated (`escapedForDoubleQuotedShellArgument`).

**Verdict:** Injection risk is low; inputs are validated and escaped before reaching the shell command.

### 3. Error Handling

- Local failures use `describeLocalFailure(...)` (L252-264), which extracts structured JSON errors or prints a plain local failure message. It does not incorrectly blame SSH.
- `validateSuccessfulExit(...)` distinguishes local vs. remote failures (L218-226), though it still throws `.remoteFailure` in the local case (a minor naming wart, not a functional bug).

### 4. Terminal Environment

`localTerminalEnvironment()` (L183-201) explicitly builds a sane environment for local terminal tabs:
- Copies parent environment from `ProcessInfo.processInfo.environment`.
- Sets/falls back `HOME`, `USER`, `LOGNAME`, `SHELL`, `PATH`, `TERM`, `COLORTERM`.

This is appropriate because terminal tabs are meant to feel like the user's normal shell. The fallback `SHELL` is `/bin/zsh` and `PATH` falls back to a reasonable macOS default if missing.

### 5. Minor Issues / Watch-Outs

1. **No explicit `process.environment` for service commands.** The code relies on the shell command's `export` statements. This is fine in practice because `/bin/sh` inherits `HOME`, `USER`, etc. from the app, but it means the effective environment is "app env + explicit exports". If a future caller passes a `remoteCommand` that needs an env var not in the app env and not exported, it will fail. This is consistent with the SSH path, however.

2. **Working directory is inherited.** `Process()` is not given a `currentDirectoryURL`, so `/bin/sh` starts in Hermes Desktop's working directory. None of the Hermes commands appear to depend on cwd (they use `$HERMES_HOME` and absolute paths), so this is not a current risk.

3. **No TTY allocation for service commands.** The local path ignores `allocateTTY` and always runs non-interactively. This matches the SSH service path (`-T`), so it is intentional.

4. **Test coverage.** `SSHTransportTests.swift` verifies that local execution invokes `/bin/sh -c` with the correct arguments and that terminal launch builds the right `ProcessLaunch`, but there is no test asserting environment contents for service commands. Adding a test that records `Process.environment` (or the resulting exported PATH) would harden this against future regressions.

## Conclusion

The new local code path in `SSHTransport.swift` is **safe to use**. The `Process()` environment-inheritance concern is real but is adequately mitigated by:
- Explicit `export PATH=...` in every local service command, covering common macOS binary locations.
- Explicit `export HERMES_HOME=...`, removing dependence on inherited `HOME`.
- `localTerminalEnvironment()` for terminal sessions, providing full `HOME`/`USER`/`SHELL`/`PATH` fallbacks.

The migration from SSH-to-localhost to direct local mode is low-risk from a code-safety perspective, with the same dual-connection fallback strategy recommended in the migration plan.

**Recommendations:**
1. Proceed with the dual-connection migration plan (add local, keep SSH fallback).
2. Consider adding a unit test that asserts the local service command's exported PATH contains the expected Hermes venv and fallback directories.
3. Optionally rename the `.remoteFailure` thrown for local failures to `.localFailure` for clarity, though this is cosmetic.
