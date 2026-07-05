# Services

Shared low-level infrastructure that Engines depend on: PDL parsing, filesystem I/O, git helpers. Plumbing, not user-facing capability.

Implemented: [`pdl.py`](./pdl.py) (parses `protocols/PDL_SPECIFICATION_0.1.0.pdl`'s grammar), [`fs.py`](./fs.py) (generic upward directory search, the way Git locates `.git/`). No git helper yet.
