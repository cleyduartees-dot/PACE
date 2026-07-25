# Kernel

Resolves where a project's `.pace/` instance lives (the way Git locates `.git/`), loads the bootstrap sequence, and negotiates schema version between the installed PACE engine and a given instance's declared `SCHEMA_VERSION`.

Implemented: [`kernel.py`](./kernel.py) — `locate_instance()` and `validate_instance()`, structural validation only, loading `contracts/INSTANCE_CONTRACT_0.1.0.pdl` live via `services/contract_loader.py` (required fields, required sections come from the actual file, not a hand transcription). `SCHEMA_VERSION` support and the forbidden-suffix list remain Kernel-owned, since neither can honestly come from the contract document itself. Deeper semantic validation is deferred to the future Doctor engine. Tested against a fixture in [`tests/`](./tests/) — run `python kernel/tests/test_kernel.py`. Not yet wrapped by a CLI.
