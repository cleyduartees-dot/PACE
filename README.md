# PACE

**An engineering operating system** — a versioned, installable engine that
preserves, organizes, governs and evolves the knowledge of any software
project, so any AI understands it in seconds.

> PACE does for a project's knowledge what Git did for its source code.

PACE is installed once and governs any number of independent projects. Each
project carries only its own `.pace/` memory — never a copy of PACE itself.
Bring your own AI: PACE is AI-agnostic and runs locally. No lock-in.

## The problem

Engineering knowledge lives scattered across ChatGPT and Claude chats,
Slack, Notion, READMEs, emails and the architect's memory. When the AI
changes, the team changes, or months pass, most of it disappears — and the
same question returns: *"explain the project to me again."* PACE exists so
that never happens again.

## Install

From source (PyPI packaging is on the roadmap):

```
pip install .
```

Or run it directly without installing:

```
python cli/pace.py <command> ...
```

## Quickstart

```
pace init --guided        # interview: seed mission, vision, roadmap, sprint
pace context              # print the project's full context (for any AI)
pace handoff              # (re)generate the AI-onboarding handoff
pace remember "<note>"    # add a continuity note (agreement, current state)
pace recall               # print the working memory (so the AI keeps the thread)
pace doctor               # validate the .pace/ instance structurally
pace create <path> ...    # generate a brand-new project governed by PACE
```

## The 4-level model

| Level | What it is |
|---|---|
| **PACE** | The engine. Code only, versioned, installable. Knows nothing of any specific project. |
| **Organization** | An adopting org's governance memory (authority, policies, project registry). |
| **Instance (`.pace/`)** | A single project's memory: mission, vision, roadmap, sprint, history, decisions, requests. |
| **Project** | The actual product codebase — it simply hosts a `.pace/` at its root. |

## Repository layout

- `kernel/` — locates and structurally validates a `.pace/` instance against the Contract.
- `services/` — PDL reading, contract loading, validation, versioning.
- `engines/` — Project Creator (`init`, `create`), Handoff, and working Memory.
- `cli/` — the `pace` command.
- `ontology/` — the fundamental categories (entities, relations, assertions).
- `contracts/` — the checkable physical shape a `.pace/` instance must have.
- `protocols/` — the PDL specification and the Learning Protocol.
- `standards/`, `policies/`, `governance/` — conventions, binding rules and the authority model.
- `.pace/` — PACE's own memory. **PACE is governed by PACE** — run `pace context` here.

## A `.pace/` instance

```
.pace/
  INSTANCE.pdl          identity (kind, name, slug, schema/pace version)
  ACTIVE_VERSIONS.pdl   which mission/vision/roadmap/sprint are current
  mission/ vision/ roadmap/ sprint/
  history/ decisions/ releases/ requests/
  handoff/              regenerable AI-onboarding view (HANDOFF.md)
  memory/               continuity notes + generated reports
```

## Status

PACE governs itself: this repository has its own `.pace/` instance, valid
under its own Kernel. See `.pace/roadmap/` for the phased plan
(foundation -> solid product -> launch -> adoption -> scale) and
`.pace/handoff/HANDOFF.md` for the current onboarding view.

## License

To be defined.
