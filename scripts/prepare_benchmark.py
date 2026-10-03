#!/usr/bin/env python3
"""Prepare one synthetic, matched instruction comparison; never launch an agent."""
import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import stat
import sys

ROOT = Path(__file__).resolve().parents[1]
PACK = ROOT / "evals/benchmark-wave1.json"
PROJECT_INSTRUCTIONS = """# Benchmark workspace

Complete TASK.md offline using the supplied synthetic fixtures.
Preserve input files; put new deliverables in output/.
The optional scripts, assets and references in candidate/ are available resources.
Use only this workspace and the identical tools assigned by the evaluator.
Do not read sibling workspaces, evaluator records, rubrics or another skill copy.
Do not connect to targets, publish, install, launch games or alter schedules.
Report evidence limits and unresolved inputs. These fixtures are not live evidence.
"""


def sha(data):
    return hashlib.sha256(data).hexdigest()


def encoded(value):
    return (json.dumps(value, indent=2, ensure_ascii=True, sort_keys=True) + "\n").encode()


def no_duplicates(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("Duplicate JSON field: " + key)
        result[key] = value
    return result


def portable_path(value):
    if not isinstance(value, str) or not value or "\\" in value:
        raise ValueError("Expected a relative POSIX path")
    path = PurePosixPath(value)
    if not path.parts or path.is_absolute() or path.as_posix() != value:
        raise ValueError("Noncanonical fixture path")
    for part in path.parts:
        if part in (".", "..") or part.endswith((".", " ")) or re.search(r'[<>:"|?*\x00-\x1f]', part):
            raise ValueError("Unsafe fixture path")
        if re.fullmatch(r"(?i:con|prn|aux|nul|com[1-9]|lpt[1-9])", part.split(".")[0]):
            raise ValueError("Reserved filename")
    return path


def linked(path):
    if not path.exists() and not path.is_symlink():
        return False
    info = path.lstat()
    return path.is_symlink() or bool(getattr(info, "st_file_attributes", 0) & stat.FILE_ATTRIBUTE_REPARSE_POINT)


def unlinked_ancestors(path):
    for item in (path, *path.parents):
        if linked(item):
            raise ValueError("Linked/reparse paths are not supported")


def load_pack(path=PACK):
    unlinked_ancestors(path.absolute())
    data = path.read_bytes()
    if len(data) > 1024 * 1024:
        raise ValueError("Benchmark pack exceeds 1 MiB")
    pack = json.loads(data, object_pairs_hook=no_duplicates)
    if set(pack) != {"schema_version", "pack_version", "status", "cases"} or pack["schema_version"] != 1:
        raise ValueError("Invalid benchmark pack fields/version")
    if pack["status"] != "not_run" or not isinstance(pack["pack_version"], str):
        raise ValueError("Pack defines unrun tasks, not results")
    if not isinstance(pack["cases"], list) or not 1 <= len(pack["cases"]) <= 64:
        raise ValueError("Expected 1-64 cases")
    ids = set()
    for case in pack["cases"]:
        if set(case) != {"id", "skill", "source_case", "prompt", "fixtures", "criteria"}:
            raise ValueError("Invalid case fields")
        for field in ("id", "skill", "source_case"):
            value = case[field]
            if not isinstance(value, str) or not re.fullmatch(r"[a-z][a-z0-9-]{0,63}", value):
                raise ValueError("Invalid case/skill identifier")
        if case["id"] in ids:
            raise ValueError("Duplicate case id")
        ids.add(case["id"])
        if not isinstance(case["prompt"], str) or not case["prompt"] or len(case["prompt"]) > 16384:
            raise ValueError("Missing/oversized prompt")
        if not isinstance(case["fixtures"], dict) or not 1 <= len(case["fixtures"]) <= 64:
            raise ValueError("Expected 1-64 fixtures")
        names = set()
        for name, content in case["fixtures"].items():
            portable_path(name)
            if name.casefold() in names or not isinstance(content, str) or len(content.encode("utf-8")) > 65536:
                raise ValueError("Colliding or oversized fixture")
            names.add(name.casefold())
        # Prefix collisions would otherwise leave a partially written destination.
        for name in names:
            if any(parent.as_posix() in names for parent in PurePosixPath(name).parents if parent.parts):
                raise ValueError("Fixture file/directory collision")
        if not isinstance(case["criteria"], list) or not 1 <= len(case["criteria"]) <= 16:
            raise ValueError("Expected 1-16 review criteria")
        checks = set()
        for criterion in case["criteria"]:
            if set(criterion) != {"id", "critical", "review", "expected"}:
                raise ValueError("Invalid criterion fields")
            if not isinstance(criterion["id"], str) or not re.fullmatch(r"[a-z][a-z0-9-]{0,63}", criterion["id"]):
                raise ValueError("Invalid criterion id")
            if criterion["id"] in checks or type(criterion["critical"]) is not bool:
                raise ValueError("Duplicate criterion or invalid critical flag")
            checks.add(criterion["id"])
            if criterion["review"] not in ("artifact", "semantic", "trace"):
                raise ValueError("Invalid review method")
            if not isinstance(criterion["expected"], str) or not criterion["expected"]:
                raise ValueError("Missing expected behavior")
    return pack, sha(data)


def skill_files(root, name):
    folder = root / "skills" / name
    unlinked_ancestors(folder.absolute())
    files = {}
    for path in sorted(folder.rglob("*")):
        if linked(path):
            raise ValueError("Candidate resources contain a linked/reparse path")
        relative = path.relative_to(folder).as_posix()
        if "__pycache__" in path.relative_to(folder).parts:
            continue
        if path.is_file():
            portable_path(relative)
            data = path.read_bytes()
            if len(data) > 2 * 1024 * 1024:
                raise ValueError("Candidate file exceeds 2 MiB")
            files[relative] = data
    if "SKILL.md" not in files or len(files) > 128:
        raise ValueError("Missing/oversized candidate skill")
    return files


def inventory(files):
    return {name: sha(data) for name, data in sorted(files.items())}


def write_new(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("xb") as stream:
        stream.write(data)


def prepare(case_id, output, source_revision=None, root=ROOT, pack_path=PACK):
    pack, pack_hash = load_pack(pack_path)
    case = next((item for item in pack["cases"] if item["id"] == case_id), None)
    if case is None:
        raise ValueError("Unknown benchmark case")
    output = Path(output).absolute()
    if ".." in output.parts:
        raise ValueError("Choose an output path without parent segments")
    unlinked_ancestors(output)
    if output.exists():
        raise ValueError("Benchmark output already exists")
    files = skill_files(root, case["skill"])
    resources = {name: data for name, data in files.items() if name != "SKILL.md" and not name.startswith("agents/")}
    candidate = {**resources, "SKILL.md": files["SKILL.md"]}
    fixtures = {"input/" + name: data.encode("utf-8") for name, data in case["fixtures"].items()}
    common = {**fixtures, "TASK.md": (case["prompt"].rstrip() + "\n").encode("utf-8"),
              "AGENTS.md": PROJECT_INSTRUCTIONS.encode("utf-8")}
    receipt = {"schema_version": 1, "pack_version": pack["pack_version"], "case_id": case_id,
               "skill": case["skill"], "source_revision": source_revision, "pack_sha256": pack_hash,
               "common_files": inventory(common), "resource_files": inventory(resources),
               "candidate_files": inventory(candidate), "evaluation": "not_run",
               "comparison": "explicit skill instructions; supporting resources available to both conditions"}
    receipt_hash = sha(encoded(receipt))
    output.mkdir(parents=True, exist_ok=False)
    for condition in ("baseline", "skill"):
        workspace = output / condition
        for name, data in common.items():
            write_new(workspace / name, data)
        selected = candidate if condition == "skill" else resources
        for name, data in selected.items():
            write_new(workspace / "candidate" / name, data)
        lead = ("Read candidate/SKILL.md and use it for this task.\n" if condition == "skill"
                else "Complete the task using the supplied files and resources.\n")
        write_new(workspace / "PROMPT.txt", (lead + "Read AGENTS.md and TASK.md.\n").encode())
        record = {"schema_version": 1, "run_id": None, "case_id": case_id, "condition": condition,
                  "run_status": "not_run", "repetition": 1, "run_order": None,
                  "prepared_receipt_sha256": receipt_hash,
                  "context": {"model": None, "reasoning": None, "tools": None,
                              "loaded_skills": None, "isolation_verified": None},
                  "metrics": {"elapsed_seconds": None, "input_tokens": None, "output_tokens": None,
                              "tool_calls": None, "failed_tool_calls": None, "human_corrections": None},
                  "trace": None, "artifacts": [],
                  "review": {"reviewer": None, "accepted": None, "unsupported_claims": None,
                             "unintended_changes": None,
                             "criteria": [{"id": item["id"], "passed": None, "evidence": None}
                                          for item in case["criteria"]], "notes": None}}
        write_new(output / "review" / (condition + ".result.json"), encoded(record))
    write_new(output / "review/rubric.json", encoded({"case_id": case_id, "criteria": case["criteria"]}))
    write_new(output / "review/prepared.json", encoded(receipt))
    return {"case_id": case_id, "conditions_prepared": 2, "receipt_sha256": receipt_hash,
            "agent_runs": "not_run", "output": str(output)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--case", required=True, help="Case id from evals/benchmark-wave1.json")
    parser.add_argument("--output", required=True, help="Caller-selected new comparison directory")
    parser.add_argument("--source-revision", help="Optional caller-reported checkout revision; bytes are hashed independently")
    args = parser.parse_args()
    try:
        print(json.dumps(prepare(args.case, args.output, args.source_revision)))
        return 0
    except (OSError, ValueError, TypeError, KeyError) as error:
        print("Cannot prepare benchmark: " + str(error), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
