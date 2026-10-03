"""Behavioral checks for evidence bindings, hashes and bounded read-only review."""
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
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "skills/release-qualification/scripts/release_record.py"
SPEC = importlib.util.spec_from_file_location("release_record", SCRIPT)
HELPER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(HELPER)


def sha(data):
    return hashlib.sha256(data).hexdigest()


class ReleaseRecordTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="release evidence ")
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.artifact = self.root / "candidate.bin"
        self.artifact.write_bytes(b"synthetic candidate one")
        self.evidence = self.root / "package report.txt"
        self.evidence.write_bytes(b"synthetic verifier receipt; not a real release")
        self.record = {
            "schema_version": 1,
            "candidate": {"product": "Example product", "version": "1.2.3", "target": "Chosen staging fixture",
                "source_revision": "revision-one", "working_tree": "clean", "source_snapshot_sha256": None},
            "artifacts": [{"id": "candidate", "path": "candidate.bin", "sha256": sha(self.artifact.read_bytes())}],
            "checks": [{"id": "package", "tier": "package", "required": True, "status": "passed",
                "target": None,
                "source_revision": "revision-one", "source_snapshot_sha256": None,
                "subjects": [{"artifact_id": "candidate", "sha256": sha(self.artifact.read_bytes())}],
                "evidence": [{"path": self.evidence.name, "sha256": sha(self.evidence.read_bytes())}],
                "details": "Synthetic exact-file package receipt"}],
        }

    def review(self, record=None):
        return HELPER.review(self.record if record is None else record, self.root)

    def write_record(self, record=None):
        path = self.root / "record.json"
        path.write_text(json.dumps(self.record if record is None else record), encoding="utf-8")
        return path

    def cli(self, *extra):
        return subprocess.run([sys.executable, str(SCRIPT), "--record", str(self.write_record()),
                               "--root", str(self.root), *extra], capture_output=True, text=True)

    def test_consistent_record_preserves_files_and_limits_claim(self):
        before = {p.name: p.read_bytes() for p in self.root.iterdir()}
        result = self.review()
        self.assertEqual(result["record_review"], "consistent")
        self.assertEqual(result["gaps"], [])
        self.assertEqual(result["observed_sha256"]["candidate.bin"], sha(self.artifact.read_bytes()))
        self.assertEqual(result["limits"]["check_results"], "caller_reported")
        self.assertEqual(result["limits"]["release_authorization"], "not_assessed")
        self.assertEqual(before, {p.name: p.read_bytes() for p in self.root.iterdir()})

    def test_changed_artifact_cannot_reuse_old_pass_after_manifest_update(self):
        self.artifact.write_bytes(b"synthetic candidate two")
        self.assertEqual(self.review()["record_review"], "incomplete")
        self.record["artifacts"][0]["sha256"] = sha(self.artifact.read_bytes())
        result = self.review()
        self.assertIn("check package: artifact subject digest mismatch", result["gaps"])
        self.record["checks"][0]["subjects"][0]["sha256"] = sha(self.artifact.read_bytes())
        self.assertEqual(self.review()["record_review"], "consistent")

    def test_evidence_tampering_and_missing_file_are_gaps(self):
        self.evidence.write_bytes(b"changed receipt")
        self.assertEqual(self.review()["record_review"], "incomplete")
        self.evidence.unlink()
        self.assertIn("check package: selected file is missing", self.review()["gaps"])

    def test_incomplete_statuses_never_become_passes(self):
        for status in ("failed", "not_run", "running", "needs_review", "not_applicable"):
            with self.subTest(status=status):
                self.record["checks"][0]["tier"] = "soak"
                self.record["checks"][0]["status"] = status
                self.assertEqual(self.review()["record_review"], "incomplete")

    def test_optional_unavailable_physical_check_remains_visible(self):
        check = copy.deepcopy(self.record["checks"][0])
        check.update(id="controller", tier="physical", required=False, status="not_run", subjects=[], evidence=[],
                     details="Human input is outside this package-only qualification scope")
        self.record["checks"].append(check)
        result = self.review()
        self.assertEqual(result["record_review"], "consistent")
        self.assertEqual(result["checks"][1]["status"], "not_run")
        self.assertFalse(result["checks"][1]["required"])

    def test_no_required_set_and_unknown_source_are_gaps(self):
        self.record["checks"][0]["required"] = False
        self.assertEqual(self.review()["record_review"], "incomplete")
        self.record["checks"][0]["required"] = True
        self.record["candidate"]["source_revision"] = None
        self.record["checks"][0]["source_revision"] = None
        self.assertIn("candidate: source revision is unresolved", self.review()["gaps"])

    def test_source_revision_and_modified_snapshot_must_match(self):
        self.record["candidate"]["source_revision"] = "revision-two"
        self.assertEqual(self.review()["record_review"], "incomplete")
        self.record["checks"][0]["source_revision"] = "revision-two"
        self.record["candidate"]["working_tree"] = "modified"
        self.assertEqual(self.review()["record_review"], "incomplete")
        snapshot = sha(b"synthetic source snapshot")
        self.record["candidate"]["source_snapshot_sha256"] = snapshot
        self.assertEqual(self.review()["record_review"], "incomplete")
        self.record["checks"][0]["source_snapshot_sha256"] = snapshot
        self.assertEqual(self.review()["record_review"], "consistent")

    def test_runtime_pass_binds_the_exercised_target(self):
        check = self.record["checks"][0]
        for tier in ("vendor", "installed", "live", "physical", "multiplayer", "soak"):
            with self.subTest(tier=tier):
                check.update(tier=tier, target=None)
                self.assertEqual(self.review()["record_review"], "incomplete")
                check["target"] = "Different environment"
                self.assertEqual(self.review()["record_review"], "incomplete")
                check["target"] = self.record["candidate"]["target"]
                self.assertEqual(self.review()["record_review"], "consistent")

    def test_pass_needs_evidence_and_non_source_artifact_subject(self):
        check = self.record["checks"][0]
        check["evidence"] = []
        self.assertEqual(self.review()["record_review"], "incomplete")
        check["evidence"] = [{"path": self.evidence.name, "sha256": sha(self.evidence.read_bytes())}]
        check["subjects"] = []
        self.assertEqual(self.review()["record_review"], "incomplete")
        check["tier"] = "source"
        self.assertEqual(self.review()["record_review"], "consistent")

    def test_different_identities_unicode_targets_and_relative_paths(self):
        self.artifact.rename(self.root / "renamed package.bin")
        record = self.record
        record["candidate"].update(product="Autre produit", target="日本語の選択したテスト環境")
        record["artifacts"][0].update(id="other_payload", path="renamed package.bin")
        record["checks"][0]["subjects"][0]["artifact_id"] = "other_payload"
        result = self.cli()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)["candidate"]["target"], record["candidate"]["target"])

    def test_portable_paths_reject_escape_and_control_characters(self):
        for name in ("../outside", "/absolute", "default/../file", "a//file", "C:/drive", "bad\\file",
                     "bad\nfile", "con.txt", "trailing."):
            with self.subTest(name=repr(name)):
                self.record["artifacts"][0]["path"] = name
                with self.assertRaises(HELPER.InputError):
                    self.review()

    def test_duplicate_fields_ids_and_unknown_secret_fields_rejected(self):
        path = self.root / "duplicate.json"
        path.write_text('{"schema_version":1,"schema_version":1}')
        with self.assertRaises(HELPER.InputError):
            HELPER.load_record(path)
        self.record["checks"].append(copy.deepcopy(self.record["checks"][0]))
        with self.assertRaises(HELPER.InputError):
            self.review()
        self.record["checks"].pop()
        self.record["api_key"] = "synthetic-do-not-echo"
        result = self.cli()
        self.assertEqual(result.returncode, 2)
        self.assertNotIn("synthetic-do-not-echo", result.stderr)

    def test_unknown_subject_and_case_collisions_rejected(self):
        self.record["checks"][0]["subjects"][0]["artifact_id"] = "missing"
        with self.assertRaises(HELPER.InputError):
            self.review()
        self.record["checks"][0]["subjects"][0]["artifact_id"] = "candidate"
        self.record["checks"][0]["evidence"][0]["path"] = "CANDIDATE.BIN"
        with self.assertRaises(HELPER.InputError):
            self.review()

    def test_hash_limits_stop_large_selection(self):
        with patch.object(HELPER, "MAX_FILE", 1):
            with self.assertRaises(HELPER.InputError):
                self.review()
        with patch.object(HELPER, "MAX_TOTAL", 1):
            with self.assertRaises(HELPER.InputError):
                self.review()

    def test_cli_exit_status_output_preservation_and_details_are_inert(self):
        output = self.root / "chosen results" / "review.json"
        marker = self.root / "must-not-exist"
        self.record["checks"][0]["details"] = "touch " + str(marker)
        result = self.cli("--output", str(output))
        self.assertEqual(result.returncode, 0, result.stderr)
        accepted = output.read_bytes()
        self.assertFalse(marker.exists())
        self.assertEqual(json.loads(result.stdout), json.loads(accepted))
        result = self.cli("--output", str(output))
        self.assertEqual(result.returncode, 2)
        self.assertEqual(output.read_bytes(), accepted)
        self.record["checks"][0]["status"] = "running"
        self.assertEqual(self.cli().returncode, 1)

    def test_symlink_selected_file_rejected(self):
        target = self.root / "outside.bin"
        self.artifact.rename(target)
        try:
            self.artifact.symlink_to(target)
        except OSError:
            self.skipTest("OS does not permit test symlink creation")
        with self.assertRaises(HELPER.InputError):
            self.review()

    @unittest.skipUnless(os.name == "nt", "Windows junction boundary")
    def test_windows_junction_root_rejected(self):
        linked = self.root / "linked evidence"
        target = self.root / "target evidence"
        target.mkdir()
        linked.relative_to(self.root)
        target.relative_to(self.root)
        result = subprocess.run(["cmd", "/c", "mklink", "/J", str(linked), str(target)],
                                capture_output=True, text=True)
        if result.returncode:
            self.skipTest("OS does not permit test junction creation")
        try:
            with self.assertRaises(HELPER.InputError):
                HELPER.review(self.record, linked)
        finally:
            os.rmdir(linked)  # Remove only the junction, preserving its target.


if __name__ == "__main__":
    unittest.main()
