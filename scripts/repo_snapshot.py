#!/usr/bin/env python3
"""Read-only Git snapshot. File bodies are hashed, never included in output.

Requires Python 3.8+ and local Git. Ignored files are excluded.
The snapshot is not atomic: stop concurrent writers before capturing evidence.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import stat
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from urllib.parse import urlsplit, urlunsplit


def is_within(path, root):
    """Python 3.8-compatible lexical containment; callers resolve paths first."""
    try:
        path.relative_to(root)
        return True
    except ValueError:
        return False


def git(root, *args, optional=False):
    env = dict(os.environ, GIT_OPTIONAL_LOCKS="0", GIT_TERMINAL_PROMPT="0")
    for key in ("GIT_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE", "GIT_COMMON_DIR"):
        env.pop(key, None)
    result = subprocess.run(["git", "-c", "core.fsmonitor=false", "-C", str(root),
                             *args], stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE, env=env, check=False)
    if result.returncode and not optional:
        raise ValueError("Git command failed: " + " ".join(args[:2]))
    return result.stdout if result.returncode == 0 else b""


def repository(path):
    root = Path(path).resolve(strict=True)
    return Path(os.fsdecode(git(root, "rev-parse", "--show-toplevel")).strip()).resolve()


def redact_origin(value):
    if "://" in value:
        parts = urlsplit(value)
        return urlunsplit((parts.scheme, parts.netloc.rsplit("@", 1)[-1],
                           parts.path, "", ""))
    # SCP-style remotes may carry a username. Drop query/fragment credentials.
    value = value.split("?", 1)[0].split("#", 1)[0]
    return value.split("@", 1)[-1] if "@" in value else value


def fingerprint(root, relative):
    path = root / relative
    path.parent.resolve().relative_to(root)  # Never follow an escaping ancestor.
    try:
        info = path.lstat()
    except FileNotFoundError:
        return {"kind": "missing"}
    result = {"mode": stat.S_IMODE(info.st_mode)}
    if stat.S_ISLNK(info.st_mode):
        data = os.fsencode(os.readlink(path))
        result.update(kind="symlink", sha256=hashlib.sha256(data).hexdigest())
    elif stat.S_ISREG(info.st_mode):
        with path.open("rb") as stream:
            hasher = hashlib.sha256()
            for chunk in iter(lambda: stream.read(1024 * 1024), b""):
                hasher.update(chunk)
            digest = hasher.hexdigest()
        result.update(kind="file", size=info.st_size, sha256=digest)
    elif stat.S_ISDIR(info.st_mode):
        result.update(kind="directory")
    else:
        raise ValueError("Cannot fingerprint special file: " + relative)
    return result


def snapshot(root, depth=0):
    if depth > 32:
        raise ValueError("Submodule depth exceeds 32")
    commit = git(root, "rev-parse", "--verify", "HEAD").decode("ascii").strip()
    index = {}
    for item in git(root, "ls-files", "--stage", "-z").split(b"\0"):
        if item:
            meta, path = item.split(b"\t", 1)
            mode, oid, stage = meta.decode("ascii").split()
            index.setdefault(os.fsdecode(path), []).append(
                {"mode": mode, "oid": oid, "stage": int(stage)})
    raw = git(root, "status", "--porcelain=v1", "-z", "--untracked-files=all",
              "--ignore-submodules=none")
    items, records = iter(raw.split(b"\0")), []
    for item in items:
        if not item:
            continue
        xy, path = item[:2].decode("ascii"), os.fsdecode(item[3:])
        record = {"xy": xy, "path": path, "index": index.get(path, []),
                  "worktree": fingerprint(root, path)}
        if "R" in xy or "C" in xy:
            record["original_path"] = os.fsdecode(next(items))
        records.append(record)
    submodules = []
    for path, entries in sorted(index.items()):
        if any(entry["mode"] == "160000" for entry in entries):
            child = root / path
            child.resolve().relative_to(root)
            initialized = child.is_dir() and (child / ".git").exists()
            submodules.append({"path": path, "index": entries,
                               "initialized": initialized,
                               "snapshot": snapshot(child.resolve(), depth + 1)
                               if initialized else None})
    return {"commit": commit,
            "branch": os.fsdecode(git(root, "symbolic-ref", "--quiet", "--short",
                                       "HEAD", optional=True)).strip() or None,
            "origin": redact_origin(os.fsdecode(git(root, "config", "--get",
                                        "remote.origin.url", optional=True)).strip()) or None,
            "status": sorted(records, key=lambda row: row["path"]),
            "submodules": submodules}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("local_repo")
    parser.add_argument("--output", help="JSON destination outside the repository")
    args = parser.parse_args()
    try:
        root = repository(args.local_repo)
        output = Path(args.output).resolve() if args.output else None
        git_dir = Path(os.fsdecode(git(root, "rev-parse", "--absolute-git-dir")).strip()).resolve()
        common_dir = (root / os.fsdecode(git(root, "rev-parse", "--git-common-dir")).strip()).resolve()
        if output and any(is_within(output, folder) for folder in (root, git_dir, common_dir)):
            raise ValueError("--output must be outside the repository")
        result = {"schema_version": 1, "root": str(root),
                  "captured_at_utc": datetime.now(timezone.utc).isoformat(),
                  **snapshot(root)}
        data = json.dumps(result, ensure_ascii=True, indent=2) + "\n"
        if output:
            # Replacing a destination avoids modifying repository files via hardlinks.
            with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=output.parent,
                                             delete=False) as stream:
                temporary = Path(stream.name)
                stream.write(data)
            try:
                os.replace(temporary, output)
            finally:
                temporary.unlink(missing_ok=True)
        else:
            sys.stdout.write(data)
        return 0
    except (OSError, ValueError, RuntimeError) as error:
        print("repo_snapshot: " + str(error), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
