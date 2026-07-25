# CLI

Thin command layer that delegates to the Kernel — no logic of its own.

Day-1 commands planned: `pace init`, `pace context` (or `bootstrap`), `pace doctor`.

Implemented: [`pace.py`](./pace.py) — `pace init`, `pace create`, `pace doctor`, `pace context`. Run as `python cli/pace.py <command> ...`; not yet packaged as a real `pace` executable. Tested end-to-end in [`tests/`](./tests/) — run `python cli/tests/test_cli.py`.
