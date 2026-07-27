# Changelog

All notable changes to PACE are documented here. The format loosely follows
[Keep a Changelog](https://keepachangelog.com/). PACE tracks two independent
version lines: the engine (`PACE_VERSION`) and the instance Contract
(`SCHEMA_VERSION`).

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
