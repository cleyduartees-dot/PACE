"""Small, reusable validation helpers — generic enough for the Kernel
today and for a future Doctor/Validator engine, so validation logic
doesn't live inline inside any one caller."""

from pathlib import Path


def require_fields(data: dict, fields, context: str) -> list:
    violations = []
    for field in fields:
        if not data.get(field):
            violations.append(f"{context} missing required field {field}")
    return violations


def require_dirs(root: Path, paths, label: str = "missing required section") -> list:
    violations = []
    for path in paths:
        if not (root / path).is_dir():
            violations.append(f"{label} {path}/")
    return violations


def require_non_empty_dir(root: Path, path: str) -> list:
    directory = root / path
    if directory.is_dir() and not any(directory.iterdir()):
        return [f"{path}/ exists but has no founding entry"]
    return []


def forbid_file_suffixes(root: Path, suffixes) -> list:
    violations = []
    for path in root.rglob("*"):
        if path.is_file() and path.suffix in suffixes:
            violations.append(f"forbidden code/script file inside .pace/: {path.relative_to(root)}")
    return violations
