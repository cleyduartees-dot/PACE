# PACE

An engineering operating system: a versioned, installable engine that preserves, organizes, governs and evolves the architectural knowledge of software projects, in collaboration between people and AI.

PACE is not a library embedded inside a product. It is installed once and governs any number of independent projects, each carrying only its own `.pace/` memory — never a copy of PACE itself.

## Status

Founded 2026-07-06. This repository currently contains only this founding commit. The minimal day-1 skeleton (kernel, services, engines, ontology, protocols, governance, policies, standards, contracts, cli, history, docs) is the next step, not yet built.

## Founding principle

- **PACE** — the engine. Code only, versioned, installable. No knowledge of any specific organization or project.
- **Organización** — an adopting company's own governance memory (who holds authority, its own policies, its registry of projects), same recursive shape as a project instance, scoped one level up.
- **Instancia (`.pace/`)** — a single project's own memory: mission, vision, roadmap, sprint, handoff, history, decisions.
- **Proyecto** — the actual product codebase. Outside PACE's concern beyond hosting a `.pace/` folder at its root.

## Roadmap (founding sequence)

1. Crear el repositorio oficial PACE. — done
2. Implementar el esqueleto mínimo.
3. Implementar `pace init`.
4. Adoptar el primer proyecto gobernado por PACE.
5. Implementar `pace create`.
6. Crear el primer proyecto nuevo nacido desde PACE.
