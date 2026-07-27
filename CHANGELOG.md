# Changelog

All notable changes to PACE are documented here. The format loosely follows
[Keep a Changelog](https://keepachangelog.com/). PACE tracks two independent
version lines: the engine (`PACE_VERSION`) and the instance Contract
(`SCHEMA_VERSION`).

## [0.4.0] — 2026-07-27 — "The Gatekeeper" (per-message enforcement)

### Added
- `pace check` — fast, quiet per-message verification: locates `.pace/`,
  reports the instance + engine version, and surfaces an update notice.
  Caches the PyPI check (memory/generated/) so per-message cost is ~0, and
  is silent when there is no `.pace/` — safe to run on every message.
- `pace agent install` — wire PACE into every client that can enforce it
  (REQUEST-0018): a Claude Code `UserPromptSubmit` hook that runs
  `pace check` on **every** message (real enforcement), a Cursor
  always-applied rule, and `AGENTS.md` (universal instruction). Idempotent;
  never clobbers existing settings.

## [0.3.1] — 2026-07-27 — external-feedback fixes

### Fixed
- `pace update` now retries with `--break-system-packages` when the plain
  upgrade is rejected by an externally-managed environment (Debian/Ubuntu
  PEP 668). Reported by an adopter whose update failed on a managed Python.
- `pace supersede` now stamps the prior version file `STATUS SUPERSEDED`
  and adds `SUPERSEDED_BY`, so each version file is self-describing instead
  of relying on `ACTIVE_VERSIONS.pdl` alone.

## [0.3.0] — 2026-07-27 — "Zero-touch Guardian"

### Added
- `pace hook install` / `uninstall` — a git pre-commit guardian that runs
  `pace doctor` on every commit and blocks commits that break the contract.
  Refuses to touch hooks PACE did not write.
- AGENTS.md auto-pointer (REQUEST-0013): the handoff engine writes an
  `AGENTS.md` at the repository root (only if absent) so AI clients that
  auto-read it load PACE's memory with zero user action.
- `pace update` (REQUEST-0014) — one-step self-update; the update notice now
  suggests it first.
- Update notice (REQUEST-0012): the handoff's Health checks now WARN when a
  newer `pace-engine` exists on PyPI, showing the exact command
  (`pip install --upgrade pace-engine`). Fail-silent: offline or slow
  network means no notice, never an error.

## [0.2.0] — 2026-07-27 · Contract 0.2.0 — "Active Guardian"

### Added
- `pace supersede <section> "..."` — update mission / vision / roadmap / sprint
  by creating a new version file; the previous file is kept and
  `ACTIVE_VERSIONS.pdl` is updated. Makes the contract's "never edit a
  protected section in place" rule impossible to break in the normal flow.
- Enriched `pace handoff` — now includes recent continuity notes and a
  **Health checks** section that WARNs on drift (placeholder sections,
  oversized continuity log).
- `rules/` section (Contract v0.2, **optional and backward-compatible**) — a
  home for approved, permanent governance rules an AI must obey.
- `pace condense` — archive old continuity notes to `CONTINUITY_ARCHIVE.md` so the working log stays lean; nothing is
  discarded and re-running is a no-op. The handoff health check points
  here once the log grows large.
- `pace rule add` / `pace rule list` — record and list rules by scope
  (PACE / ORGANIZATION / PROJECT). Approved rules render at the top of the
  handoff so an AI reads them first.

### Changed
- Kernel now understands Contract `0.1.0` and `0.2.0`. Optional sections do not
  invalidate older instances — a `.pace/` without `rules/` stays valid.

## [0.1.0] — 2026-07 — first public release

### Added
- **PACE Kernel** — locate and structurally validate a `.pace/` instance
  against the Instance Contract loaded at runtime.
- **CLI** — `pace init`, `pace create`, `pace doctor`, `pace context`,
  `pace handoff`, `pace remember`, `pace recall`.
- **Guided intake** — `pace init --guided` seeds mission / vision / roadmap /
  sprint from the owner's answers.
- **Working memory** — continuity notes so an AI keeps the thread across a long
  chat.
- **Self-hosting** — PACE's own repository is governed by a `.pace/` instance.
- Published to PyPI as **`pace-engine`**. Licensed under **BSL 1.1**.
