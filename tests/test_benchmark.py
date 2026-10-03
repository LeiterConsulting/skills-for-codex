"""Check matched fixture preparation and preservation; not agent performance."""
import copy
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/prepare_benchmark.py"
SPEC = importlib.util.spec_from_file_location("prepare_benchmark", SCRIPT)
PREP = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(PREP)


def read_tree(path):
    return {item.relative_to(path).as_posix(): item.read_bytes()
            for item in path.rglob("*") if item.is_file()}


class BenchmarkTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="benchmark fixture ")
        self.addCleanup(self.temp.cleanup)
        self.output = Path(self.temp.name) / "comparison"
        self.pack, self.pack_hash = PREP.load_pack()

    def modified_pack(self, mutate):
        value = copy.deepcopy(self.pack)
        mutate(value)
        path = Path(self.temp.name) / "modified.json"
        path.write_text(json.dumps(value), encoding="utf-8")
        return path

    def test_every_case_prepares_matched_inputs_resources_and_only_entrypoint_treatment(self):
        self.assertEqual(len(self.pack["cases"]), 10)
        for case in self.pack["cases"]:
            with self.subTest(case=case["id"]):
                output = Path(self.temp.name) / case["id"]
                PREP.prepare(case["id"], output, "caller-revision")
                baseline = read_tree(output / "baseline")
                skill = read_tree(output / "skill")
                self.assertNotIn("candidate/SKILL.md", baseline)
                self.assertIn("candidate/SKILL.md", skill)
                self.assertFalse(any(name.startswith("candidate/agents/") for name in skill))
                expected = {**baseline, "candidate/SKILL.md": skill["candidate/SKILL.md"], "PROMPT.txt": skill["PROMPT.txt"]}
                self.assertEqual(expected, skill)
                for name, value in case["fixtures"].items():
                    self.assertEqual(baseline["input/" + name], value.encode("utf-8"))
                self.assertFalse(any("rubric" in name or "result.json" in name for name in baseline))
                self.assertEqual(read_tree(output / "skill")["candidate/SKILL.md"],
                                 (ROOT / "skills" / case["skill"] / "SKILL.md").read_bytes())

    def test_receipt_hashes_match_copied_bytes_and_record_is_not_a_run(self):
        result = PREP.prepare("app-native", self.output)
        path = self.output / "review/prepared.json"
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        self.assertEqual(result["receipt_sha256"], digest)
        receipt = json.loads(path.read_bytes())
        for section, prefix in (("common_files", ""), ("resource_files", "candidate/"), ("candidate_files", "candidate/")):
            for name, expected in receipt[section].items():
                data = (self.output / "skill" / (prefix + name)).read_bytes()
                self.assertEqual(hashlib.sha256(data).hexdigest(), expected)
        for condition in ("baseline", "skill"):
            record = json.loads((self.output / "review" / (condition + ".result.json")).read_bytes())
            self.assertEqual(record["prepared_receipt_sha256"], digest)
            self.assertEqual(record["run_status"], "not_run")
            self.assertIsNone(record["review"]["accepted"])
            self.assertTrue(all(value is None for value in record["metrics"].values()))
            self.assertTrue(all(item["passed"] is None for item in record["review"]["criteria"]))

    def test_repeated_preparation_has_same_receipt_without_destination_coupling(self):
        first = PREP.prepare("release-changed", self.output, "revision-one")
        second = PREP.prepare("release-changed", Path(self.temp.name) / "other", "revision-one")
        self.assertEqual(first["receipt_sha256"], second["receipt_sha256"])

    def test_existing_output_preserved(self):
        self.output.mkdir()
        marker = self.output / "keep.txt"
        marker.write_bytes(b"user bytes")
        with self.assertRaisesRegex(ValueError, "already exists"):
            PREP.prepare("app-native", self.output)
        self.assertEqual(read_tree(self.output), {"keep.txt": b"user bytes"})

    def test_case_selection_failure_leaves_no_output(self):
        with self.assertRaisesRegex(ValueError, "Unknown"):
            PREP.prepare("not-a-case", self.output)
        self.assertFalse(self.output.exists())

    def test_fixture_traversal_and_reserved_paths_rejected_before_creation(self):
        for bad in (".", "../escape", "/escape", "folder/../../escape", "folder\\escape", "NUL.txt", "folder/name."):
            with self.subTest(path=bad):
                pack = self.modified_pack(lambda value: value["cases"][0].update(fixtures={bad: "bad"}))
                with self.assertRaises(ValueError):
                    PREP.prepare("app-native", self.output, pack_path=pack)
                self.assertFalse(self.output.exists())

    def test_case_and_prefix_filename_collisions_rejected_before_creation(self):
        for fixtures in ({"one": "a", "ONE": "b"}, {"one": "a", "one/nested": "b"}):
            pack = self.modified_pack(lambda value: value["cases"][0].update(fixtures=fixtures))
            with self.assertRaises(ValueError):
                PREP.prepare("app-native", self.output, pack_path=pack)
            self.assertFalse(self.output.exists())

    def test_changed_fixture_changes_receipt_and_unicode_bytes_survive(self):
        first = PREP.prepare("app-native", self.output)
        content = "consumer variant Å <value>\r\n"
        pack = self.modified_pack(lambda value: value["cases"][0]["fixtures"].update({"variant.txt": content}))
        other = Path(self.temp.name) / "variant"
        second = PREP.prepare("app-native", other, pack_path=pack)
        self.assertNotEqual(first["receipt_sha256"], second["receipt_sha256"])
        self.assertEqual((other / "baseline/input/variant.txt").read_bytes(), content.encode("utf-8"))

    def test_duplicate_json_and_duplicate_case_ids_rejected(self):
        path = Path(self.temp.name) / "bad.json"
        path.write_text('{"schema_version":1,"schema_version":1}', encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "Duplicate JSON"):
            PREP.load_pack(path)
        pack = self.modified_pack(lambda value: value["cases"].append(value["cases"][0]))
        with self.assertRaisesRegex(ValueError, "Duplicate case"):
            PREP.load_pack(pack)

    def test_linked_output_parent_rejected(self):
        target = Path(self.temp.name) / "target"
        target.mkdir()
        link = Path(self.temp.name) / "linked"
        try:
            link.symlink_to(target, target_is_directory=True)
        except OSError as error:
            self.skipTest("Host cannot create directory symlink: " + str(error))
        with self.assertRaisesRegex(ValueError, "Linked/reparse"):
            PREP.prepare("app-native", link / "new")
        self.assertEqual(list(target.iterdir()), [])

    @unittest.skipUnless(os.name == "nt", "Windows junction behavior")
    def test_junction_output_parent_rejected(self):
        target = Path(self.temp.name) / "target"
        target.mkdir()
        junction = Path(self.temp.name) / "junction"
        junction.relative_to(Path(self.temp.name))
        target.relative_to(Path(self.temp.name))
        made = subprocess.run(["cmd", "/c", "mklink", "/J", str(junction), str(target)], capture_output=True, text=True)
        if made.returncode:
            self.skipTest("Host cannot create junction: " + made.stderr)
        try:
            with self.assertRaisesRegex(ValueError, "Linked/reparse"):
                PREP.prepare("app-native", junction / "new")
            self.assertEqual(list(target.iterdir()), [])
        finally:
            # Remove the known junction itself with a native filesystem call.
            os.rmdir(junction)

    def test_cli_preparation_reports_not_run_and_unknown_case_fails(self):
        result = subprocess.run([sys.executable, str(SCRIPT), "--case", "app-native", "--output", str(self.output)],
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)["agent_runs"], "not_run")
        result = subprocess.run([sys.executable, str(SCRIPT), "--case", "not-a-case", "--output", str(self.output / "new")],
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 2)
        self.assertFalse((self.output / "new").exists())

    def test_native_fixture_can_build_and_package_with_actual_bundled_helper(self):
        PREP.prepare("app-native", self.output)
        workspace = self.output / "skill"
        helper = workspace / "candidate/scripts/splunk_app.py"
        app = workspace / "output/bench_delta"
        artifact = workspace / "output/bench_delta-0.2.1.tar.gz"
        for args in (("scaffold", "--config", str(workspace / "input/native.json"), "--output", str(app)),
                     ("validate", "--app", str(app), "--files", str(app / "release-files.json")),
                     ("package", "--app", str(app), "--files", str(app / "release-files.json"), "--output", str(artifact))):
            result = subprocess.run([sys.executable, str(helper), *args], capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue(artifact.is_file())
        # No agent ran: the prepared record must still say not_run.
        record = json.loads((self.output / "review/skill.result.json").read_bytes())
        self.assertEqual(record["run_status"], "not_run")

    def test_release_fixtures_preserve_intended_candidate_and_soak_gaps(self):
        for case, expected in (("release-changed", ("artifact subject digest mismatch", "source revision binding mismatch")),
                               ("release-soak", ("running",))):
            output = Path(self.temp.name) / case
            PREP.prepare(case, output)
            workspace = output / "skill"
            result = subprocess.run([sys.executable, str(workspace / "candidate/scripts/release_record.py"),
                                     "--record", str(workspace / "input/record.json"), "--root", str(workspace / "input")],
                                    capture_output=True, text=True)
            self.assertEqual(result.returncode, 1, result.stderr)
            review = json.loads(result.stdout)
            self.assertEqual(review["record_review"], "incomplete")
            for gap in expected:
                self.assertTrue(any(gap in item for item in review["gaps"]), review["gaps"])


if __name__ == "__main__":
    unittest.main()
