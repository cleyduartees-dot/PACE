# Services

Shared low-level infrastructure that Engines depend on: PDL parsing, filesystem I/O, git helpers. Plumbing, not user-facing capability.

Implemented: [`pdl.py`](./pdl.py) (flat grammar), [`pdl_nested.py`](./pdl_nested.py) (nested-section extraction, `PDL_SPECIFICATION_0.2.0`), [`contract_loader.py`](./contract_loader.py) (reads `contracts/INSTANCE_CONTRACT_0.1.0.pdl` live — no hardcoded transcription), [`fs.py`](./fs.py) (generic upward directory search, the way Git locates `.git/`), [`validate.py`](./validate.py) (reusable checks: required fields, required dirs, non-empty dir, forbidden suffixes). Tested in [`tests/`](./tests/). No git helper yet.
