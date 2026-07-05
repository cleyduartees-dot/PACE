# Engines

Each PACE capability lives in its own subfolder, with its own contract, version and lifecycle.

Day-1 priority: `bootstrap` (produces the AI-consumable project context), `doctor` (validate-only at first), `project-creator` (`init` mode only at first — attaches `.pace/` to an existing project).

Later, once a second real project creates the pressure for it: `registry` (multi-project), `migrator` (schema-version bridging), `knowledge-resolver`, `patch-engine`, `task-engine`, `continuity`, `auditor`.

No engine implemented yet.
