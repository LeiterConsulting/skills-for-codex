#!/usr/bin/env python3
"""Check collection metadata, linked resources and public portability."""
from pathlib import Path
import json
import re
import sys

ROOT = Path(__file__).resolve().parents[1]


def check():
    errors = []
    catalog = json.loads((ROOT / "catalog.json").read_text(encoding="utf-8"))
    names = []
    for skill in catalog["skills"]:
        names.append(skill["name"])
        directory = ROOT / skill["path"]
        source = (directory / "SKILL.md").read_text(encoding="utf-8")
        front = re.match(r"\A---\n(.*?)\n---\n", source, re.S)
        if not front:
            errors.append("Missing skill frontmatter: " + skill["name"])
            continue
        if not re.search(r"^name: " + re.escape(skill["name"]) + r"$", front[1], re.M):
            errors.append("Skill name/catalog mismatch: " + skill["name"])
        if not re.search(r"^description: .+", front[1], re.M):
            errors.append("Missing skill description: " + skill["name"])
        for match in re.finditer(r"\]\(([^)]+)\)", source):
            target = match[1]
            if not target.startswith(("https://", "#")) and not (directory / target.split("#")[0]).is_file():
                errors.append("Missing skill resource: " + target)
        for field in ("inputs", "acceptance"):
            if not (ROOT / skill[field]).is_file():
                errors.append("Missing catalog resource: " + skill[field])
    if len(set(names)) != len(names):
        errors.append("Duplicate skill names.")
    for path in ROOT.rglob("*"):
        if any(part in (".git", "__pycache__", ".venv", "work", "dist", ".artifacts")
               for part in path.relative_to(ROOT).parts):
            continue
        if path.is_symlink():
            errors.append("Public collection contains a symlink.")
        if path.is_file() and path.suffix in (".md", ".json", ".yaml", ".yml"):
            content = path.read_text(encoding="utf-8")
            if re.search(r"(?<![A-Za-z0-9])[A-Za-z]:[\\/]", content) or re.search(r"/(?:Users|home)/[^/\s]+/", content):
                errors.append("Host-specific absolute path in " + path.relative_to(ROOT).as_posix())
            if path.suffix == ".json":
                json.loads(content)
    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1
    print(json.dumps({"skills": len(names), "catalog": "passed", "resource_links": "passed",
                      "host_path_guard": "passed", "scope": "structure; not behavioral or secret validation"}))
    return 0


if __name__ == "__main__":
    raise SystemExit(check())
