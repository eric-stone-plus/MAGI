# AGENTS.md — MAGI repo rules

> Global/workspace rules live outside this repo. This file governs only this repo.

## What this repo is

The public home of the MAGI three-seat decision-organ charter. Documentation-only;
no code, no build, no tests.

## Rules

- English only in published files. (Operational seat traffic in the coordination
  channel stays bilingual; it is not part of this repo.)
- `CHARTER.md` semantics change only through the charter's own §10 amendment
  procedure (three-seat consensus + human final ruling). Editorial fixes
  (typos, clarity, formatting) that do not change semantics are fine.
- No internal status narratives, handoffs, retrospectives, or dated progress logs in
  published files — the operational devlog lives locally in `devlog/` (gitignored).
- No credentials, machine paths, or private hostnames in published files.
- Local checkout: `~/Documents/Development/public-repos/MAGI`. Remote is the backup;
  local is the source of truth.
