"""Semantic tests for portable app generation and explicit release selection."""
import copy
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tarfile
import tempfile
import unittest
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "skills/splunk-app-authoring/scripts/splunk_app.py"
SPEC = importlib.util.spec_from_file_location("splunk_app", SCRIPT)
HELPER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(HELPER)
EXAMPLE = json.loads((ROOT / "skills/splunk-app-authoring/assets/native-app.example.json").read_text())


class NativeAppTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="portable app ")
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)

    def config(self, **changes):
        config = copy.deepcopy(EXAMPLE)
        config.update(changes)
        return config

    def write_config(self, config, name="input.json"):
        path = self.root / name
        path.write_text(json.dumps(config, ensure_ascii=False), encoding="utf-8")
        return path

    def create(self, config=None, workspace="workspace"):
        config = config or self.config()
        app = self.root / workspace / config["app_id"]
        HELPER.scaffold(self.write_config(config), app)
        return app

    def manifest(self, app, files):
        path = app / "release-files.json"
        path.write_text(json.dumps({"schema_version": 1, "files": files}), encoding="utf-8")
        return path

    def test_two_independent_identities_authors_roles_and_locations(self):
        for index, identity in enumerate(("alpha_health", "beta_audit")):
            config = self.config(app_id=identity, app_label=f"Label {index}",
                                 author=f"Author {index}", version=f"1.{index}.2",
                                 read_roles=[f"reader_{index}"], write_roles=[f"writer_{index}"])
            app = self.create(config, workspace=f"chosen path {index}")
            result, selected = HELPER.validate(app, app / "release-files.json")
            self.assertEqual(result["app_id"], identity)
            self.assertIn(f"author = Author {index}".encode(), selected["default/app.conf"])
            self.assertIn(f"reader_{index}".encode(), selected["metadata/default.meta"])
            self.assertNotIn(b"Example contributors", selected["default/app.conf"])

    def test_unicode_and_xml_characters_keep_original_semantics(self):
        config = self.config(app_label="Santé & <Ops>", author="Equipe",
                             description="Unicode native app", install_state="disabled")
        config["dashboard"].update(title="<Errors & latency>", query='| makeresults\n| eval x="<&>"',
                                   earliest="-7d", latest="@d")
        app = self.create(config)
        view = ET.parse(app / "default/data/ui/views/home.xml").getroot()
        self.assertEqual(view.findtext("label"), config["app_label"])
        self.assertEqual(view.findtext("row/panel/title"), config["dashboard"]["title"])
        self.assertEqual(view.findtext("row/panel/table/search/query"), config["dashboard"]["query"])
        self.assertEqual(view.findtext("row/panel/table/search/earliest"), "-7d")
        self.assertIn("state = disabled", (app / "default/app.conf").read_text())

    def test_missing_identity_rejected_before_any_write(self):
        config = self.config()
        del config["author"]
        output = self.root / "unused" / "example_health"
        with self.assertRaises(HELPER.InputError):
            HELPER.scaffold(self.write_config(config), output)
        self.assertFalse(output.parent.exists())

    def test_extra_secret_field_rejected_without_echoing_value(self):
        config = self.config(api_key="synthetic_private_value")
        process = subprocess.run([sys.executable, str(SCRIPT), "scaffold",
                                  "--config", str(self.write_config(config)),
                                  "--output", str(self.root / "example_health")],
                                 capture_output=True, text=True)
        self.assertEqual(process.returncode, 2)
        self.assertNotIn("synthetic_private_value", process.stderr)
        self.assertFalse((self.root / "example_health").exists())

    def test_newline_conf_injection_rejected_before_write(self):
        config = self.config(author="Author\n[install]\nstate=disabled")
        with self.assertRaises(HELPER.InputError):
            self.create(config)
        self.assertFalse((self.root / "workspace").exists())

    def test_invalid_ids_roles_and_schema_types_rejected(self):
        bad_cases = [{"app_id": "../../escape"}, {"app_id": "CON"}, {"read_roles": []},
                     {"write_roles": ["admin]\n[ui]"]}, {"schema_version": True}]
        for changes in bad_cases:
            with self.subTest(changes=changes):
                with self.assertRaises(HELPER.InputError):
                    HELPER.validate_config(self.config(**changes))

    def test_existing_destination_preserved(self):
        app = self.root / "example_health"
        app.mkdir()
        sentinel = app / "existing.txt"
        sentinel.write_text("existing user content")
        with self.assertRaises(HELPER.InputError):
            HELPER.scaffold(self.write_config(self.config()), app)
        self.assertEqual(sentinel.read_text(), "existing user content")
        self.assertEqual(list(app.iterdir()), [sentinel])

    def test_output_name_must_match_user_defined_identity(self):
        with self.assertRaises(HELPER.InputError):
            HELPER.scaffold(self.write_config(self.config()), self.root / "wrong_identity")
        self.assertFalse((self.root / "wrong_identity").exists())

    def test_duplicate_json_fields_rejected(self):
        path = self.root / "duplicate.json"
        path.write_text('{"schema_version":1,"schema_version":1}')
        with self.assertRaises(HELPER.InputError):
            HELPER.read_json(path)

    def test_selected_archive_has_one_root_and_exact_content(self):
        app = self.create()
        package = self.root / "release.tar.gz"
        result = HELPER.package(app, app / "release-files.json", package)
        with tarfile.open(package) as archive:
            members = archive.getmembers()
            files = [member for member in members if member.isfile()]
            self.assertEqual({m.name for m in files},
                             {app.name + "/" + name for name in HELPER.NATIVE_FILES})
            for member in files:
                relative = member.name.split("/", 1)[1]
                self.assertEqual(archive.extractfile(member).read(), (app / relative).read_bytes())
                self.assertEqual(member.uid, 0)
                self.assertEqual(member.mtime, 0)
        self.assertEqual(result["sha256"], hashlib.sha256(package.read_bytes()).hexdigest())
        self.assertEqual(result["appinspect"], "not_run")
        self.assertEqual(result["runtime"], "not_run")

    def test_unlisted_credentials_and_config_never_enter_package(self):
        app = self.create()
        (app / "local").mkdir()
        (app / "local/private.conf").write_text("synthetic runtime configuration")
        (app / ".env").write_text("SYNTHETIC_SECRET=do-not-package")
        (app / "scratch.txt").write_text("not selected")
        output = self.root / "selected.tar.gz"
        HELPER.package(app, app / "release-files.json", output)
        with tarfile.open(output) as archive:
            names = archive.getnames()
        self.assertFalse(any("local/" in name or ".env" in name or "scratch" in name for name in names))

    def test_packaging_deterministic_across_output_names(self):
        app = self.create()
        one, two = self.root / "one.tar.gz", self.root / "two.tar.gz"
        HELPER.package(app, app / "release-files.json", one)
        HELPER.package(app, app / "release-files.json", two)
        self.assertEqual(one.read_bytes(), two.read_bytes())

    def test_existing_archive_preserved(self):
        app = self.create()
        output = self.root / "old.tar.gz"
        output.write_bytes(b"prior accepted artifact")
        with self.assertRaises(HELPER.InputError):
            HELPER.package(app, app / "release-files.json", output)
        self.assertEqual(output.read_bytes(), b"prior accepted artifact")

    def test_package_inside_app_rejected(self):
        app = self.create()
        with self.assertRaises(HELPER.InputError):
            HELPER.package(app, app / "release-files.json", app / "release.tar.gz")
        self.assertFalse((app / "release.tar.gz").exists())

    def test_parent_segment_cannot_hide_package_inside_app(self):
        app = self.create()
        alias = self.root / "alias"
        alias.mkdir()
        output = alias / ".." / "workspace" / app.name / "release.tar.gz"
        with self.assertRaises(HELPER.InputError):
            HELPER.package(app, app / "release-files.json", output)
        self.assertFalse((app / "release.tar.gz").exists())

    def test_release_filename_characters_are_portable(self):
        for name in ("views/bad\nname.xml", "views/bad\x00name.xml", "views/bad\ud800name.xml"):
            with self.subTest(name=repr(name)):
                with self.assertRaises(HELPER.InputError):
                    HELPER.release_path(name)

    def test_private_traversal_absolute_and_case_collision_rejected(self):
        app = self.create()
        cases = [["default/app.conf", "../outside"],
                 ["default/app.conf", "/absolute"],
                 ["default/app.conf", "local/private.conf"],
                 ["default/app.conf", ".env"],
                 ["default/app.conf", "identity.pem"],
                 ["default/app.conf", "default/APP.CONF"]]
        for names in cases:
            with self.subTest(names=names):
                with self.assertRaises(HELPER.InputError):
                    HELPER.validate(app, self.manifest(app, names))

    def test_symlink_release_file_rejected(self):
        app = self.create()
        original = app / "default/app.conf"
        outside = self.root / "outside.conf"
        outside.write_bytes(original.read_bytes())
        original.unlink()
        try:
            original.symlink_to(outside)
        except OSError as exc:
            self.skipTest("OS does not permit test symlink creation: " + str(exc))
        with self.assertRaises(HELPER.InputError):
            HELPER.validate(app, app / "release-files.json")

    def test_missing_and_mismatched_identity_rejected(self):
        app = self.create()
        path = app / "default/app.conf"
        content = path.read_text()
        path.write_text(content.replace("id = example_health", "id = different_health"))
        with self.assertRaises(HELPER.InputError):
            HELPER.validate(app, app / "release-files.json")

    @unittest.skipUnless(os.name == "nt", "Windows junction boundary")
    def test_windows_junction_release_directory_rejected(self):
        app = self.create()
        linked = app / "default"
        target = self.root / "relocated default"
        target.relative_to(self.root)
        linked.relative_to(self.root)
        linked.rename(target)
        result = subprocess.run(["cmd", "/c", "mklink", "/J", str(linked), str(target)],
                                capture_output=True, text=True)
        if result.returncode:
            target.rename(linked)
            self.skipTest("OS does not permit the test junction")
        try:
            with self.assertRaises(HELPER.InputError):
                HELPER.validate(app, app / "release-files.json")
        finally:
            os.rmdir(linked)  # Remove only the junction, preserving its target.
            target.rename(linked)

    def test_missing_default_view_rejected(self):
        app = self.create()
        names = [name for name in HELPER.NATIVE_FILES if not name.endswith("views/home.xml")]
        with self.assertRaises(HELPER.InputError):
            HELPER.validate(app, self.manifest(app, names))

    def test_broken_xml_and_entity_declarations_rejected(self):
        app = self.create()
        view = app / "default/data/ui/views/home.xml"
        for content in ("<dashboard>", '<!DOCTYPE dashboard [<!ENTITY a "x">]><dashboard/>'):
            with self.subTest(content=content):
                view.write_text(content)
                with self.assertRaises((HELPER.InputError, ET.ParseError)):
                    HELPER.validate(app, app / "release-files.json")

    def test_cli_workflow_uses_explicit_paths(self):
        config = self.write_config(self.config(app_id="cli_health"))
        app = self.root / "cli path" / "cli_health"
        archive = self.root / "cli release" / "app.tar.gz"
        for args in (["scaffold", "--config", str(config), "--output", str(app)],
                     ["validate", "--app", str(app), "--files", str(app / "release-files.json")],
                     ["package", "--app", str(app), "--files", str(app / "release-files.json"),
                      "--output", str(archive)]):
            result = subprocess.run([sys.executable, str(SCRIPT), *args],
                                    text=True, capture_output=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(json.loads(result.stdout)["app_id"], "cli_health")
        self.assertTrue(archive.is_file())


if __name__ == "__main__":
    unittest.main()
