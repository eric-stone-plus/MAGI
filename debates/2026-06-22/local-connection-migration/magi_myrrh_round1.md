# QUINTE R1: Migration Safety Audit — SSH-to-Local

**Auditor**:[0m
[0m← [0mWrite magi_myrrh_round1.md
Wrote file successfully.
[0m
Now I'll write the analysis.
Analysis written to `magi_myrrh_round1.md`. Key findings:

- **Dual-connection strategy is sound** but needs awareness of workspace fingerprint splitting (two connections, same target, different caches).
- **Biggest hidden failure mode**: `Process()` inherits the GUI app's environment, not the user's shell environment. The "real PATH" claim is likely incomplete — `.zprofile`/`.zshrc` won't be sourced.
- **Other risks**: process orphaning on app quit, SSHTransport code path contamination (local logic lives inside SSH class), potential sandbox restrictions.
- **Verdict**: Migrate, but verify environment parity first by comparing `env`/`$PATH` output from both modes before committing.
en check the other and see stale state
- UI could show duplicate entries for the same physical workspace

**Mitigation**: During the dual-connection period, designate one as "primary" and only use the other for verification. Don't interleave operations.

### 1b. Which Connection Is Active?

The context doesn't specify how Hermes Desktop handles multiple connections to the same target. If there's no "active connection" concept, the user must mentally track which one they're using. This is a footgun during the transition period.

**Mitigation**: Label them clearly (the proposed "Local Hermes (Direct)" vs existing "Local Hermes" is good). Consider a visual indicator of which is in use.

---

## 2. Hidden Failure Modes

### 2a. Environment Inheritance (the big one)

`Process()` inherits the **app's environment**, not the user's Terminal environment. For a GUI app launched from Finder/Dock:

- PATH comes from `/etc/paths` + `/etc/paths.d/*` (via `path_helper`) + any `Info.plist` LSEnvironment entries
- `.zprofile`, `.zshrc`, `.bash_profile` are **not sourced**
- Custom environment variables (API keys, tool configs, virtual envs) are **not present**

The context claims local mode provides "real PATH, real HOME, real Python" — but this is the **app process's** environment, which is likely **less complete** than a user's interactive shell.

SSH-to-localhost has a similar problem (non-interactive SSH doesn't source shell profiles), but it's a **known, documented** problem with known workarounds (`~/.ssh/environment`, `PermitUserEnvironment`). Local mode's environment is a new unknown.

**Risk**: Commands that work via SSH (because SSH was previously tuned) may fail via local mode with cryptic "command not found" errors.

### 2b. `SSHTransport.execute()` — Code Path Contamination

The local code path lives **inside** `SSHTransport.execute()`, gated by `connection.kind == .local`. This means:

- SSH-specific error handling, cleanup, timeout logic, and retry mechanisms may apply to local execution unexpectedly
- If `SSHTransport` has SSH connection pooling, multiplexing, or socket cleanup, local mode could trigger irrelevant code paths
- Future SSH-specific changes could accidentally break local mode

This is a code smell, not a blocker — but it means local mode inherits SSH's baggage. Any bug in `SSHTransport`'s non-transport logic now affects local mode too.

### 2c. Process Orphaning

SSH sessions have well-defined lifecycle: when the SSH connection closes, child processes receive SIGHUP and (typically) terminate. `Process()` in a GUI app has different behavior:

- When Hermes Desktop quits, `Process()` may or may not send SIGTERM to children
- Long-running Hermes processes (daemons, watchers) could become orphans
- macOS app termination (Force Quit) definitely won't clean up children gracefully

**Risk**: Orphaned Hermes processes consuming resources, holding file locks, or conflicting with future sessions.

### 2d. macOS App Sandbox

If Hermes Desktop is distributed via the App Store or uses App Sandbox:

- `Process()` execution may be restricted to specific paths
- File access outside the sandbox container may fail
- Network operations from child processes may be blocked

The context doesn't mention sandboxing. If the app is sandboxed, this could be a **hard blocker** for local mode.

### 2e. stdin/stdout/stderr Behavior

SSH handles PTY allocation, line buffering, and terminal negotiation. Direct `Process()` may behave differently:

- Commands expecting a TTY may fail or produce different output
- Buffering differences could cause output to appear in different chunks
- Interactive commands (prompts, progress bars) may not render correctly

---

## 3. What Could Go Wrong?

| Scenario | Likelihood | Impact | Detection |
|----------|-----------|--------|-----------|
| PATH missing tools, "command not found" | High | Medium | Immediate — commands fail |
| Shell env vars missing (API keys, configs) | Medium | High | Subtle — commands run but behave wrong |
| Orphan processes on app quit | Medium | Medium | Delayed — resource consumption grows |
| Sandbox blocks Process() execution | Low (if not App Store) | Critical | Immediate — all commands fail |
| State divergence between dual connections | Medium | Medium | Subtle — stale data, confused user |
| SSHTransport code path leaks into local | Low | Medium | Unpredictable — varies by bug |
| TTY-dependent commands break | Low | Low | Immediate — output differs |

---

## 4. Recommendation

**Proceed with migration, but address the environment gap first.**

The dual-connection strategy is sound. The real risk isn't the migration mechanics — it's the environment inheritance problem. Before committing to local mode:

1. **Verify environment parity**: Run `env` and `echo $PATH` via both SSH and local mode. Compare. If they differ significantly, local mode will break things.
2. **Check sandbox status**: Confirm Hermes Desktop is not App Sandbox–restricted. If it is, local mode may be non-viable.
3. **Test process cleanup**: Start a long-running process via local mode, quit Hermes Desktop, check if the process terminates.
4. **Audit SSHTransport mixing**: Confirm that local execution in `SSHTransport.execute()` doesn't trigger SSH-specific side effects (socket creation, connection pooling, etc.).

If all four pass, the migration is safe. Keep SSH as fallback for 1–2 weeks as proposed. The PATH/environment difference is the most likely source of breakage — make it the first thing you test.

---

## 5. One-Line Verdict

**Migrate, but test environment parity first — the "real PATH" claim is unverified and likely incomplete for GUI-launched Process().**
