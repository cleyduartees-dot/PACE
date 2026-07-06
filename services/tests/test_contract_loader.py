"""Proves the loader reads the real Instance Contract, not a fixture
standing in for it. Run directly: python services/tests/test_contract_loader.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from services.contract_loader import load_instance_contract

CONTRACT_PATH = (
    Path(__file__).resolve().parents[2] / "contracts" / "INSTANCE_CONTRACT_0.1.0.pdl"
)

EXPECTED_SECTIONS = {
    "mission", "vision", "roadmap", "sprint", "handoff", "history",
    "releases", "decisions", "requests", "memory/generated", "memory/persistent",
}


def test_contract_version_is_read_from_the_file():
    contract = load_instance_contract(CONTRACT_PATH)
    assert contract["contract_version"] == "0.1.0", contract["contract_version"]


def test_instance_pdl_required_fields_match_the_real_contract_text():
    contract = load_instance_contract(CONTRACT_PATH)
    fields = contract["root_manifest"][".pace/INSTANCE.pdl"]
    assert fields == [
        "KIND", "NAME", "SLUG", "SCHEMA_VERSION", "PACE_VERSION", "ORG_REF", "CREATED_AT",
    ], fields



def test_active_versions_pdl_required_fields_match_the_real_contract_text():
    contract = load_instance_contract(CONTRACT_PATH)
    fields = contract["root_manifest"][".pace/ACTIVE_VERSIONS.pdl"]
    assert fields == ["ACTIVE_MISSION", "ACTIVE_VISION", "ACTIVE_ROADMAP", "ACTIVE_SPRINT"], fields


def test_all_eleven_sections_are_found():
    contract = load_instance_contract(CONTRACT_PATH)
    assert set(contract["sections"]) == EXPECTED_SECTIONS, set(contract["sections"])


if __name__ == "__main__":
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for test in tests:
        test()
        print(f"PASS {test.__name__}")
    print(f"\n{len(tests)} tests passed")
