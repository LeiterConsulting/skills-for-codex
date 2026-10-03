#!/usr/bin/env python3
"""Review caller-reported release evidence and verify selected local file hashes."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import stat
import sys

ID = re.compile(r"[A-Za-z][A-Za-z0-9_-]{0,63}\Z")
SHA = re.compile(r"[A-Fa-f0-9]{64}\Z")
RESERVED = re.compile(r"(?:con|prn|aux|nul|com[1-9]|lpt[1-9])(?:\..*)?\Z", re.I)
TIERS = ("source", "build", "package", "vendor", "installed", "live", "physical", "multiplayer", "soak")
STATUSES = ("passed", "failed", "not_run", "running", "needs_review", "not_applicable")
MAX_RECORD = 1024 * 1024
MAX_FILE = 2 * 1024 * 1024 * 1024
MAX_TOTAL = 4 * 1024 * 1024 * 1024
MAX_SELECTED = 256


class InputError(ValueError):
    pass


def require(condition, message):
    if not condition:
        raise InputError(message)


def fields(value, expected, label):
    require(isinstance(value, dict) and set(value) == set(expected),
            label + " must contain exactly the documented fields.")


def text(value, label, maximum=8192, nullable=False):
    if nullable and value is None:
        return
    require(isinstance(value, str) and 0 < len(value) <= maximum and value == value.strip(),
            label + " must be trimmed nonempty text within its size limit.")
    require(all(ord(c) >= 32 and ord(c) != 127 and not 0xD800 <= ord(c) <= 0xDFFF for c in value),
            label + " contains unsupported characters.")


def digest(value, nullable=False):
    require((nullable and value is None) or (isinstance(value, str) and SHA.fullmatch(value)),
            "Digest must be 64 hexadecimal characters.")


def identifier(value):
    require(isinstance(value, str) and ID.fullmatch(value), "Unsupported identifier.")


def relative_path(value):
    text(value, "Selected path", 240)
    path = PurePosixPath(value)
    require(not path.is_absolute() and value == path.as_posix() and bool(path.parts),
            "Selected paths must be canonical relative POSIX paths.")
    for part in path.parts:
        require(part not in (".", "..") and not any(c in part for c in '<>:"\\|?*')
                and not part.endswith((" ", ".")) and not RESERVED.fullmatch(part),
                "Unsupported or nonportable selected path.")


def reject_links(path):
    for component in (path, *path.parents):
        try:
            info = component.lstat()
        except FileNotFoundError:
            continue
        require(not stat.S_ISLNK(info.st_mode) and not getattr(info, "st_file_attributes", 0) & 0x400,
                "Linked/reparse paths are unsupported.")


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, "Duplicate JSON fields are unsupported.")
        result[key] = value
    return result


def load_record(path):
    path = path.absolute()
    reject_links(path)
    require(path.is_file() and path.stat().st_size <= MAX_RECORD, "Invalid record file or size.")
    try:
        return json.loads(path.read_text(encoding="utf-8-sig"), object_pairs_hook=unique_object)
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise InputError("Invalid UTF-8 JSON record.") from exc


def validate_record(record):
    fields(record, ("schema_version", "candidate", "artifacts", "checks"), "Record")
    require(type(record["schema_version"]) is int and record["schema_version"] == 1,
            "Unsupported record schema version.")
    candidate = record["candidate"]
    fields(candidate, ("product", "version", "target", "source_revision", "working_tree",
                       "source_snapshot_sha256"), "Candidate")
    for name in ("product", "version", "target"):
        text(candidate[name], "Candidate " + name, 1000)
    text(candidate["source_revision"], "Source revision", 256, nullable=True)
    require(candidate["working_tree"] in ("clean", "modified", "unknown"), "Unsupported working state.")
    digest(candidate["source_snapshot_sha256"], nullable=True)
    artifacts = record["artifacts"]
    require(isinstance(artifacts, list) and 0 < len(artifacts) <= 64, "Invalid artifact list.")
    artifact_ids = set()
    artifact_paths = set()
    for artifact in artifacts:
        fields(artifact, ("id", "path", "sha256"), "Artifact")
        identifier(artifact["id"])
        relative_path(artifact["path"])
        digest(artifact["sha256"])
        require(artifact["id"] not in artifact_ids and artifact["path"].casefold() not in artifact_paths,
                "Duplicate artifact identity or path.")
        artifact_ids.add(artifact["id"])
        artifact_paths.add(artifact["path"].casefold())
    checks = record["checks"]
    require(isinstance(checks, list) and 0 < len(checks) <= 128, "Invalid check list.")
    check_ids = set()
    for check in checks:
        fields(check, ("id", "tier", "required", "status", "target", "source_revision", "source_snapshot_sha256",
                       "subjects", "evidence", "details"), "Check")
        identifier(check["id"])
        require(check["id"] not in check_ids, "Duplicate check identity.")
        check_ids.add(check["id"])
        require(check["tier"] in TIERS and check["status"] in STATUSES and type(check["required"]) is bool,
                "Unsupported check tier, status or required flag.")
        text(check["source_revision"], "Check source revision", 256, nullable=True)
        text(check["target"], "Check target", 1000, nullable=True)
        digest(check["source_snapshot_sha256"], nullable=True)
        text(check["details"], "Check details")
        require(isinstance(check["subjects"], list) and len(check["subjects"]) <= 64,
                "Invalid check subjects.")
        subjects = set()
        for subject in check["subjects"]:
            fields(subject, ("artifact_id", "sha256"), "Subject")
            identifier(subject["artifact_id"])
            digest(subject["sha256"])
            require(subject["artifact_id"] in artifact_ids and subject["artifact_id"] not in subjects,
                    "Unknown or duplicate check subject.")
            subjects.add(subject["artifact_id"])
        require(isinstance(check["evidence"], list) and len(check["evidence"]) <= MAX_SELECTED,
                "Invalid evidence list.")
        evidence_paths = set()
        for evidence in check["evidence"]:
            fields(evidence, ("path", "sha256"), "Evidence")
            relative_path(evidence["path"])
            digest(evidence["sha256"])
            require(evidence["path"].casefold() not in evidence_paths, "Duplicate check evidence.")
            evidence_paths.add(evidence["path"].casefold())


def review(record, root):
    validate_record(record)
    root = root.absolute()
    reject_links(root)
    require(root.is_dir(), "Evidence root must be a regular directory.")
    gaps, observed = [], {}
    path_cases = {}
    total = 0

    def verify(entry, label):
        nonlocal total
        name = entry["path"]
        folded = name.casefold()
        require(folded not in path_cases or path_cases[folded] == name,
                "Selected paths have a case collision.")
        path_cases[folded] = name
        if name not in observed:
            require(len(observed) < MAX_SELECTED, "Too many selected files.")
            path = root / name
            reject_links(path)
            if not path.exists():
                observed[name] = None
            else:
                require(stat.S_ISREG(path.stat().st_mode), "Selected evidence must be a regular file.")
                require(path.stat().st_size <= MAX_FILE, "Selected file exceeds the size limit.")
                hasher, count = hashlib.sha256(), 0
                with path.open("rb") as stream:
                    for chunk in iter(lambda: stream.read(1024 * 1024), b""):
                        count += len(chunk)
                        total += len(chunk)
                        require(count <= MAX_FILE and total <= MAX_TOTAL, "Hashing exceeds the size limit.")
                        hasher.update(chunk)
                observed[name] = hasher.hexdigest()
        if observed[name] is None:
            gaps.append(label + ": selected file is missing")
        elif observed[name] != entry["sha256"].lower():
            gaps.append(label + ": selected file digest mismatch")

    candidate = record["candidate"]
    if candidate["source_revision"] is None:
        gaps.append("candidate: source revision is unresolved")
    if candidate["working_tree"] != "clean" and candidate["source_snapshot_sha256"] is None:
        gaps.append("candidate: source snapshot binding is missing")
    artifacts = {item["id"]: item for item in record["artifacts"]}
    for artifact in artifacts.values():
        verify(artifact, "artifact " + artifact["id"])
    required_count = sum(check["required"] for check in record["checks"])
    if not required_count:
        gaps.append("record: no required checks declared")
    for check in record["checks"]:
        label = "check " + check["id"]
        for evidence in check["evidence"]:
            verify(evidence, label)
        if check["required"] and check["status"] != "passed":
            gaps.append(label + ": required status is " + check["status"])
        if check["status"] == "passed":
            target_bound = check["tier"] in ("vendor", "installed", "live", "physical", "multiplayer", "soak")
            if (target_bound or check["target"] is not None) and check["target"] != candidate["target"]:
                gaps.append(label + ": target binding missing or mismatched")
            if check["source_revision"] != candidate["source_revision"]:
                gaps.append(label + ": source revision binding mismatch")
            normalize = lambda value: value.lower() if value is not None else None
            if normalize(check["source_snapshot_sha256"]) != normalize(candidate["source_snapshot_sha256"]):
                gaps.append(label + ": source snapshot binding mismatch")
            if not check["evidence"]:
                gaps.append(label + ": pass has no evidence file")
            if check["tier"] != "source" and not check["subjects"]:
                gaps.append(label + ": pass has no artifact subject")
            for subject in check["subjects"]:
                if subject["sha256"].lower() != artifacts[subject["artifact_id"]]["sha256"].lower():
                    gaps.append(label + ": artifact subject digest mismatch")
    return {
        "schema_version": 1,
        "record_review": "incomplete" if gaps else "consistent",
        "candidate": candidate,
        "required_check_count": required_count,
        "gaps": gaps,
        "observed_sha256": observed,
        "checks": [{key: check[key] for key in ("id", "tier", "required", "status", "details")}
                   for check in record["checks"]],
        "limits": {"check_results": "caller_reported", "source_checkout": "not_verified",
                   "target_environment": "caller_reported", "criteria": "caller_selected",
                   "report_authenticity": "not_verified", "gate_coverage": "not_assessed",
                   "behavior": "not_exercised", "release_authorization": "not_assessed"},
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--record", required=True, type=Path)
    parser.add_argument("--root", required=True, type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)
    try:
        result = review(load_record(args.record), args.root)
        payload = json.dumps(result, indent=2) + "\n"
        if args.output is not None:
            output = args.output.absolute()
            reject_links(output)
            require(not output.exists(), "Review output already exists; choose a new path.")
            output.parent.mkdir(parents=True, exist_ok=True)
            with output.open("x", encoding="utf-8", newline="\n") as stream:
                stream.write(payload)
        print(payload, end="")
        return 0 if result["record_review"] == "consistent" else 1
    except (InputError, OSError, UnicodeError) as exc:
        print("Record review failed: " + str(exc), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
