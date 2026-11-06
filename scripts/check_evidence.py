#!/usr/bin/env python3
"""Check source identity and line anchors, not semantic correctness.

Evidence JSON (UTF-8, optional BOM): {"commit": "FULL_HASH", "records":
[{"id": "E1", "path": "src/a.py", "symbol": "function_name", "start": 1,
  "end": 4, "sha256": "RAW_FILE_SHA256"}]}.
Source must decode as UTF-8; ranges are inclusive, 1-based, split with splitlines().
Optional excerpt_sha256 hashes selected lines joined by LF with no final LF.
"""
import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath, PureWindowsPath
import re
import sys

# Reuse read-only Git plumbing without creating __pycache__ in an installed skill.
sys.dont_write_bytecode = True
from repo_snapshot import git, is_within, repository


def check_record(root, record, seen):
    if not isinstance(record, dict):
        raise ValueError("record must be an object")
    for field in ("id", "path", "symbol"):
        if not isinstance(record.get(field), str) or not record[field].strip():
            raise ValueError(field + " must be a nonempty string")
    if record["id"] in seen:
        raise ValueError("duplicate evidence id")
    seen.add(record["id"])
    relative = record["path"]
    path = PurePosixPath(relative)
    if ("\\" in relative or path.is_absolute() or PureWindowsPath(relative).drive
            or ".." in path.parts or str(path) != relative or relative == "."):
        raise ValueError("path must be normalized, relative, and use '/' separators")
    source = (root / relative).resolve(strict=True)
    if not is_within(source, root):
        raise ValueError("path escapes repository, possibly through a symlink")
    raw = source.read_bytes()
    expected = record.get("sha256")
    if not isinstance(expected, str) or not re.fullmatch(r"[0-9a-f]{64}", expected):
        raise ValueError("sha256 must be a lowercase 64-character hex digest")
    if hashlib.sha256(raw).hexdigest() != expected:
        raise ValueError("file sha256 mismatch")
    lines = raw.decode("utf-8").splitlines()
    start, end = record.get("start"), record.get("end")
    if (type(start) is not int or type(end) is not int
            or not 1 <= start <= end <= len(lines)):
        raise ValueError("invalid inclusive 1-based line range")
    if "excerpt_sha256" in record:
        excerpt = "\n".join(lines[start - 1:end]).encode("utf-8")
        if hashlib.sha256(excerpt).hexdigest() != record["excerpt_sha256"]:
            raise ValueError("excerpt_sha256 mismatch")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", required=True)
    parser.add_argument("--evidence", required=True)
    args = parser.parse_args()
    try:
        root = repository(args.repo)
        evidence = json.loads(Path(args.evidence).read_text(encoding="utf-8-sig"))
        if (not isinstance(evidence, dict)
                or not isinstance(evidence.get("records"), list)
                or not evidence["records"]):
            raise ValueError("evidence must be an object with a nonempty records array")
        actual = git(root, "rev-parse", "--verify", "HEAD").decode("ascii").strip()
        if evidence.get("commit") != actual:
            raise ValueError("commit mismatch: evidence must name the full current HEAD")
        failures, seen = [], set()
        for number, record in enumerate(evidence["records"], 1):
            try:
                check_record(root, record, seen)
            except (OSError, ValueError, RuntimeError) as error:
                failures.append({"record": number, "error": str(error)})
        print(json.dumps({"ok": not failures, "checked": len(evidence["records"]),
                          "failures": failures}, ensure_ascii=True, indent=2))
        return 1 if failures else 0
    except (OSError, ValueError, RuntimeError) as error:
        print("check_evidence: " + str(error), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
