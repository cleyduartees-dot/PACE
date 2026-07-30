"""PACE's own engine version — the single source of truth referenced by
Engines (when writing a new instance) and the Kernel (when reasoning
about instance compatibility). Independent of SCHEMA_VERSION: the engine
can evolve without the Instance Contract changing, and vice versa.
"""

PACE_VERSION = "0.6.0"
