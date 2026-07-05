# Kernel

Resolves where a project's `.pace/` instance lives (the way Git locates `.git/`), loads the bootstrap sequence, and negotiates schema version between the installed PACE engine and a given instance's declared `SCHEMA_VERSION`.

Implemented: [`kernel.py`](./kernel.py) — `locate_instance()` and `validate_instance()`, structural validation only against `contracts/INSTANCE_CONTRACT_0.1.0.pdl` (required fields, required sections, `SCHEMA_VERSION` support, no code/scripts inside `.pace/`). Deeper semantic validation is deferred to the future Doctor engine. Tested against a fixture in [`tests/`](./tests/) — run `python kernel/tests/test_kernel.py`. Not yet wrapped by a CLI.
