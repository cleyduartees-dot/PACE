# Engines

Each PACE capability lives in its own subfolder, with its own contract, version and lifecycle.

Day-1 priority: `bootstrap` (produces the AI-consumable project context), `doctor` (validate-only at first), `project-creator` (`init` mode only at first — attaches `.pace/` to an existing project).

Later, once a second real project creates the pressure for it: `registry` (multi-project), `migrator` (schema-version bridging), `knowledge-resolver`, `patch-engine`, `task-engine`, `continuity`, `auditor`.

Implemented: [`project_creator.py`](./project_creator.py) — `init_instance()`, the `init` mode only (attaches a valid, structurally minimal `.pace/` to an existing project; writes placeholder mission/vision/roadmap/sprint content so `ACTIVE_VERSIONS.pdl` always points at something real). Generating a brand-new project from scratch (`pace create`) is a separate, later capability. Tested in [`tests/`](./tests/) — run `python engines/tests/test_project_creator.py`.
