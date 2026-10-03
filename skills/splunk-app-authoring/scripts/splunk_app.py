#!/usr/bin/env python3
"""Portable native Splunk scaffold and explicit-file packaging helper."""
from __future__ import annotations

import argparse
import configparser
import gzip
import hashlib
import io
import json
import os
from pathlib import Path, PurePosixPath
import re
import stat
import sys
import tarfile
import xml.etree.ElementTree as ET

APP_ID = re.compile(r"[a-z][a-z0-9_]{2,62}\Z")
VERSION = re.compile(r"[0-9]+\.[0-9]+\.[0-9]+(?:[+-][A-Za-z0-9]+)?\Z")
ROLE = re.compile(r"(?:\*|[A-Za-z][A-Za-z0-9_-]{0,63})\Z")
RESERVED = re.compile(r"(?:con|prn|aux|nul|com[1-9]|lpt[1-9])(?:\..*)?\Z", re.I)
NATIVE_FILES = (
    "default/app.conf",
    "default/data/ui/nav/default.xml",
    "default/data/ui/views/home.xml",
    "metadata/default.meta",
)
MAX_JSON = 64 * 1024
MAX_FILE = 32 * 1024 * 1024
MAX_TOTAL = 128 * 1024 * 1024
MAX_FILES = 10000


class InputError(ValueError):
    pass


def require(condition, message):
    if not condition:
        raise InputError(message)


def reject_links(path):
    """Check each existing component, including Windows junctions."""
    for component in (path, *path.parents):
        if component.exists() or component.is_symlink():
            info = component.lstat()
            linked = stat.S_ISLNK(info.st_mode)
            reparse = getattr(info, "st_file_attributes", 0) & 0x400
            require(not linked and not reparse, "Linked/reparse paths are unsupported.")


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, "Duplicate JSON fields are unsupported.")
        result[key] = value
    return result


def read_json(path):
    reject_links(path.absolute())
    require(path.is_file(), "JSON input must be a regular file.")
    require(path.stat().st_size <= MAX_JSON, "JSON input exceeds the size limit.")
    try:
        return json.loads(path.read_text(encoding="utf-8-sig"), object_pairs_hook=unique_object)
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise InputError("Invalid UTF-8 JSON input.") from exc


def fields(value, expected, label):
    require(isinstance(value, dict) and set(value) == set(expected),
            f"{label} must contain exactly the documented fields.")


def text(value, maximum, label, *, multiline=False):
    require(isinstance(value, str) and value.strip() and len(value) <= maximum,
            f"{label} must be nonempty text within its size limit.")
    require(all(ord(c) >= 32 or (multiline and c in "\n\t") for c in value),
            f"{label} contains unsupported control characters.")
    require(not any(0xD800 <= ord(c) <= 0xDFFF for c in value),
            f"{label} contains an unsupported Unicode surrogate.")
    if not multiline:
        require(value == value.strip() and not value.endswith("\\"),
                f"{label} must be trimmed and cannot end in a continuation slash.")
    return value


def roles(value, label):
    require(isinstance(value, list) and 0 < len(value) <= 32,
            f"{label} must be a nonempty role array.")
    require(all(isinstance(item, str) and ROLE.fullmatch(item) for item in value),
            f"{label} contains an unsupported role name.")
    require(len(set(value)) == len(value), f"{label} contains duplicate roles.")
    return value


def validate_config(config):
    fields(config, ("schema_version", "app_id", "app_label", "author", "version",
                    "description", "install_state", "read_roles", "write_roles",
                    "dashboard"), "Native config")
    require(type(config["schema_version"]) is int and config["schema_version"] == 1,
            "Unsupported config schema version.")
    require(isinstance(config["app_id"], str) and APP_ID.fullmatch(config["app_id"])
            and not RESERVED.fullmatch(config["app_id"]), "Unsupported app_id.")
    require(isinstance(config["version"], str) and VERSION.fullmatch(config["version"]),
            "Unsupported version.")
    text(config["app_label"], 80, "app_label")
    text(config["author"], 100, "author")
    text(config["description"], 200, "description")
    require(config["install_state"] in ("enabled", "disabled"), "Unsupported install_state.")
    roles(config["read_roles"], "read_roles")
    roles(config["write_roles"], "write_roles")
    dashboard = config["dashboard"]
    fields(dashboard, ("title", "query", "earliest", "latest"), "Dashboard")
    text(dashboard["title"], 120, "dashboard.title")
    text(dashboard["query"], 16384, "dashboard.query", multiline=True)
    text(dashboard["earliest"], 100, "dashboard.earliest")
    text(dashboard["latest"], 100, "dashboard.latest")
    return config


def xml_bytes(element):
    ET.indent(element, space="  ")
    return ET.tostring(element, encoding="utf-8", xml_declaration=True) + b"\n"


def scaffold(config_path, output):
    config = validate_config(read_json(config_path))
    output = output.absolute()
    reject_links(output)
    require(not output.exists(), "Scaffold destination already exists; use the update workflow.")
    require(output.name == config["app_id"], "Destination directory must match app_id.")
    dashboard = ET.Element("dashboard", {"version": "1.1", "theme": "light"})
    ET.SubElement(dashboard, "label").text = config["app_label"]
    panel = ET.SubElement(ET.SubElement(dashboard, "row"), "panel")
    ET.SubElement(panel, "title").text = config["dashboard"]["title"]
    search = ET.SubElement(ET.SubElement(panel, "table"), "search")
    for key, tag in (("query", "query"), ("earliest", "earliest"), ("latest", "latest")):
        ET.SubElement(search, tag).text = config["dashboard"][key]
    nav = ET.Element("nav", {"search_view": "search"})
    ET.SubElement(nav, "view", {"name": "home", "default": "true"})
    app_conf = (
        "[install]\nstate = {install_state}\n\n"
        "[ui]\nis_visible = true\nlabel = {app_label}\ndefault_view = home\n\n"
        "[launcher]\nauthor = {author}\nversion = {version}\ndescription = {description}\n\n"
        "[package]\nid = {app_id}\n\n"
        "[id]\nname = {app_id}\nversion = {version}\n"
    ).format(**config)
    metadata = "[]\naccess = read : [ " + ", ".join(config["read_roles"]) + \
        " ], write : [ " + ", ".join(config["write_roles"]) + " ]\nexport = none\n"
    contents = {
        NATIVE_FILES[0]: app_conf.encode("utf-8"),
        NATIVE_FILES[1]: xml_bytes(nav),
        NATIVE_FILES[2]: xml_bytes(dashboard),
        NATIVE_FILES[3]: metadata.encode("utf-8"),
        "release-files.json": (json.dumps({"schema_version": 1, "files": list(NATIVE_FILES)},
                                          indent=2) + "\n").encode("utf-8"),
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.mkdir()  # Exclusive claim; never overwrite an existing destination.
    try:
        for relative, data in contents.items():
            target = output / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            with target.open("xb") as stream:
                stream.write(data)
    except OSError as exc:
        raise InputError("Scaffold incomplete; inspect the retained destination before recovery.") from exc
    return {"app_id": config["app_id"], "created_files": len(contents),
            "release_file_count": len(NATIVE_FILES), "installed": False}


def release_path(value):
    require(isinstance(value, str) and 0 < len(value) <= 240, "Invalid release file path.")
    path = PurePosixPath(value)
    require(not path.is_absolute() and value == path.as_posix(), "Use canonical relative POSIX paths.")
    require(all(part not in ("", ".", "..") for part in path.parts), "Release path traversal is unsupported.")
    for part in path.parts:
        require(not any(c in part for c in '<>:"\\|?*') and not part.endswith((" ", ".")),
                "Release filenames must be portable.")
        require(all(ord(c) >= 32 and not 0xD800 <= ord(c) <= 0xDFFF for c in part),
                "Release filenames contain unsupported characters.")
        require(not RESERVED.fullmatch(part), "Reserved device filenames are unsupported.")
        lower = part.lower()
        require(not lower.startswith(".") and lower not in
                ("local", "node_modules", "__pycache__", "credentials", "passwords.conf"),
                "Private/local/dependency paths are excluded.")
        require(not lower.endswith((".pem", ".key", ".p12", ".pfx", ".pyc", ".pyo")),
                "Key and cache files are excluded.")
    return value


def selected_files(app, manifest):
    app = app.absolute()
    reject_links(app)
    require(app.is_dir() and APP_ID.fullmatch(app.name) and not RESERVED.fullmatch(app.name),
            "App root must be a regular directory with a supported app_id.")
    data = read_json(manifest)
    fields(data, ("schema_version", "files"), "Release manifest")
    require(type(data["schema_version"]) is int and data["schema_version"] == 1,
            "Unsupported manifest schema version.")
    names = data["files"]
    require(isinstance(names, list) and 0 < len(names) <= MAX_FILES, "Invalid release file list.")
    names = [release_path(name) for name in names]
    require(len(set(name.casefold() for name in names)) == len(names), "Duplicate release filenames.")
    require("default/app.conf" in names, "Release must include default/app.conf.")
    selected = {}
    total = 0
    for name in sorted(names):
        path = app / name
        reject_links(path)
        require(path.is_file(), "A selected release file is missing or not regular.")
        size = path.stat().st_size
        require(size <= MAX_FILE, "Selected file exceeds the size limit.")
        content = path.read_bytes()
        total += len(content)
        require(len(content) <= MAX_FILE and total <= MAX_TOTAL, "Release exceeds the size limit.")
        selected[name] = content
    return app, selected


def parse_xml(content):
    upper = content.upper()
    require(b"<!DOCTYPE" not in upper and b"<!ENTITY" not in upper, "XML entity declarations are unsupported.")
    return ET.fromstring(content)


def validate(app, manifest):
    app, selected = selected_files(app, manifest)
    conf = configparser.ConfigParser(interpolation=None)
    conf.read_string(selected["default/app.conf"].decode("utf-8-sig"))
    identity = conf.get("package", "id", fallback=None)
    require(identity == app.name, "App root and package ID must agree.")
    version = conf.get("launcher", "version", fallback="")
    require(VERSION.fullmatch(version), "Launcher version is missing or unsupported.")
    text(conf.get("launcher", "author", fallback=""), 100, "launcher.author")
    text(conf.get("ui", "label", fallback=""), 80, "ui.label")
    for name, content in selected.items():
        if name.lower().endswith(".xml"):
            parse_xml(content)
    if conf.has_option("id", "name"):
        require(conf.get("id", "name") == identity, "ID stanza and package ID must agree.")
    if conf.has_option("id", "version"):
        require(conf.get("id", "version") == version, "Version stanzas must agree.")
    view = conf.get("ui", "default_view", fallback=None)
    if view:
        require(re.fullmatch(r"[A-Za-z][A-Za-z0-9_-]{0,100}", view), "Unsupported default_view identifier.")
        require(f"default/data/ui/views/{view}.xml" in selected, "Default view is absent from release.")
    nav_name = "default/data/ui/nav/default.xml"
    if nav_name in selected:
        nav = parse_xml(selected[nav_name])
        require(nav.tag == "nav", "Default navigation must have a nav root.")
        for entry in nav.iter("view"):
            name = entry.get("name", "")
            if name not in ("search", "reports", "alerts", "dashboards"):
                require(f"default/data/ui/views/{name}.xml" in selected,
                        "Navigation references a view absent from the release.")
    return {"app_id": identity, "version": version, "selected_file_count": len(selected),
            "structure": "passed", "appinspect": "not_run", "runtime": "not_run"}, selected


def package(app, manifest, output):
    result, selected = validate(app, manifest)
    output = output.absolute()
    reject_links(output)
    require(not output.exists(), "Package output already exists; choose a new path.")
    require(output.name.endswith((".tar.gz", ".tgz")), "Use a .tar.gz or .tgz output filename.")
    require(not output.resolve().is_relative_to(app.resolve()),
            "Package output must be outside the app root.")
    tar_buffer = io.BytesIO()
    with tarfile.open(fileobj=tar_buffer, mode="w", format=tarfile.PAX_FORMAT) as archive:
        root = tarfile.TarInfo(result["app_id"] + "/")
        root.type, root.mode, root.mtime = tarfile.DIRTYPE, 0o755, 0
        archive.addfile(root)
        for name, content in selected.items():
            member = tarfile.TarInfo(result["app_id"] + "/" + name)
            member.size, member.mtime = len(content), 0
            member.mode = 0o755 if name.startswith("bin/") and name.endswith((".py", ".sh")) else 0o644
            archive.addfile(member, io.BytesIO(content))
    compressed = io.BytesIO()
    with gzip.GzipFile(fileobj=compressed, mode="wb", filename="", mtime=0) as stream:
        stream.write(tar_buffer.getvalue())
    payload = compressed.getvalue()
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("xb") as stream:
        stream.write(payload)
    return {**result, "archive_bytes": len(payload), "sha256": hashlib.sha256(payload).hexdigest(),
            "package": "created", "selected_files": list(selected)}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    create = commands.add_parser("scaffold", help="Create a new native dashboard app.")
    create.add_argument("--config", required=True, type=Path)
    create.add_argument("--output", required=True, type=Path)
    for name in ("validate", "package"):
        command = commands.add_parser(name)
        command.add_argument("--app", required=True, type=Path)
        command.add_argument("--files", required=True, type=Path)
        if name == "package":
            command.add_argument("--output", required=True, type=Path)
    args = parser.parse_args(argv)
    try:
        if args.command == "scaffold":
            result = scaffold(args.config, args.output)
        elif args.command == "validate":
            result, _ = validate(args.app, args.files)
        else:
            result = package(args.app, args.files, args.output)
        print(json.dumps(result, indent=2))
        return 0
    except (InputError, OSError, UnicodeError, configparser.Error, ET.ParseError) as exc:
        print(f"{args.command} failed: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
