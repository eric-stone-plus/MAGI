# AGENTS.md — MAGI repo rules

> Global/workspace rules live outside this repo. This file governs only this repo.

## What this repo is

The public home of the MAGI multi-seat decision-organ charter, plus the reference
seat-liveness watchdog (`watchdog/`, POSIX shell — no build system, no dependencies
beyond coreutils/openssl-level tooling).

## Rules

- English only in published files. (Operational seat traffic in the coordination
  channel stays bilingual; it is not part of this repo.)
- `CHARTER.md` semantics change only through the charter's own §10 amendment
  procedure (full-quorum consensus + human final ruling). Editorial fixes
  (typos, clarity, formatting) that do not change semantics are fine.
- No internal status narratives, handoffs, retrospectives, or dated progress logs in
  published files — the operational devlog lives locally in `devlog/` (gitignored).
- No credentials, private hostnames, or user-specific absolute paths in published
  files. The watchdog ships with `__HOME__` placeholders; substitute at install.
- The darwin watchdog variant is field-tested; the systemd variant is a reference
  template until a linux seat reports adoption. Keep that status honest in
  `watchdog/README.md`.
- Local checkout: `~/Public/MAGI`. Remote is the backup; local is the source of
  truth.
