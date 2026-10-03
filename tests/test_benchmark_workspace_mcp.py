"""The bridge has one container-only tool; unit checks do not prove container isolation."""
import importlib.util
import io
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("bridge", ROOT / "scripts/benchmark_workspace_mcp.py")
BRIDGE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(BRIDGE)
CID = "a" * 64


class WorkspaceBridgeTests(unittest.TestCase):
    def test_utf8_wire_command_survives_a_legacy_encoded_windows_stream(self):
        command = "python -c 'print(\"Å — α\")'"
        request = {"jsonrpc": "2.0", "id": 7, "method": "tools/call", "params": {"name": "shell", "arguments": {"command": command}}}
        wire_input = io.BytesIO((json.dumps(request, ensure_ascii=False) + "\n").encode("utf-8"))
        wire_output = io.BytesIO()
        wire_error = io.BytesIO()
        stdin = io.TextIOWrapper(wire_input, encoding="cp1252")
        stdout = io.TextIOWrapper(wire_output, encoding="cp1252")
        stderr = io.TextIOWrapper(wire_error, encoding="cp1252")
        result = {"exit_code": 0, "stdout": "Å — α\n", "stderr": "", "truncated": False, "elapsed_seconds": 0.1}
        with patch.object(BRIDGE.sys, "stdin", stdin), patch.object(BRIDGE.sys, "stdout", stdout), patch.object(BRIDGE.sys, "stderr", stderr), patch.object(BRIDGE.sys, "argv", ["bridge", "--container", CID]), patch.object(BRIDGE, "execute", return_value=result) as execute:
            BRIDGE.main()
        execute.assert_called_once_with(CID, command)
        response = json.loads(wire_output.getvalue().decode("utf-8"))
        self.assertEqual(response["id"], 7)
        self.assertEqual(json.loads(response["result"]["content"][0]["text"])["stdout"], "Å — α\n")
        self.assertEqual(stdin.encoding, "utf-8")

    def test_single_tool_and_protocol_handshake(self):
        result = BRIDGE.handle({"method": "initialize", "params": {"protocolVersion": "2025-06-18"}}, CID)
        self.assertEqual(result["protocolVersion"], "2025-06-18")
        self.assertEqual(BRIDGE.handle({"method": "tools/list"}, CID), {"tools": [BRIDGE.TOOL]})
        self.assertEqual(BRIDGE.TOOL["annotations"]["openWorldHint"], False)

    def test_container_identifier_and_bad_commands_never_start_a_process(self):
        for container, command in (("other-container", "cat TASK.md"), (CID, ""), (CID, "x" * 32769), (CID, None)):
            with patch.object(BRIDGE.subprocess, "run") as run:
                with self.assertRaises(ValueError):
                    BRIDGE.execute(container, command)
                run.assert_not_called()

    def test_shell_metacharacters_are_an_argument_to_container_exec_not_host_shell(self):
        command = "cat TASK.md; python -c 'print(1)'"
        completed = subprocess.CompletedProcess([], 0, b"result\n", b"")
        with patch.object(BRIDGE.subprocess, "run", return_value=completed) as run:
            result = BRIDGE.execute(CID, command)
        args, kwargs = run.call_args
        self.assertEqual(args[0], ["docker", "exec", "--workdir", "/workspace", CID, "sh", "-lc", command])
        self.assertNotIn("shell", kwargs)
        self.assertEqual(result["stdout"], "result\n")

    def test_nonzero_checker_exit_is_reported_without_fabricating_tool_transport_failure(self):
        completed = subprocess.CompletedProcess([], 1, b'{"record_review":"incomplete"}', b"")
        with patch.object(BRIDGE.subprocess, "run", return_value=completed):
            result = BRIDGE.handle({"method": "tools/call", "params": {"name": "shell", "arguments": {"command": "python helper.py"}}}, CID)
        self.assertFalse(result["isError"])
        self.assertEqual(json.loads(result["content"][0]["text"])["exit_code"], 1)

    def test_unknown_tool_or_extra_arguments_cannot_execute(self):
        for params in ({"name": "host", "arguments": {"command": "x"}},
                       {"name": "shell", "arguments": {"command": "x", "container": "other"}}):
            with patch.object(BRIDGE, "execute") as execute:
                with self.assertRaises(ValueError):
                    BRIDGE.handle({"method": "tools/call", "params": params}, CID)
                execute.assert_not_called()

    def test_timeout_stops_exact_container_and_reports_unknown_execution_result(self):
        with patch.object(BRIDGE.subprocess, "run", side_effect=[subprocess.TimeoutExpired([], 60), subprocess.CompletedProcess([], 0, b"", b"")]) as run:
            result = BRIDGE.execute(CID, "sleep 90")
        self.assertIsNone(result["exit_code"])
        self.assertEqual(run.call_args_list[1].args[0], ["docker", "stop", "--time", "1", CID])

    def test_oversized_output_is_visibly_truncated(self):
        completed = subprocess.CompletedProcess([], 0, b"x" * 70000, b"")
        with patch.object(BRIDGE.subprocess, "run", return_value=completed):
            result = BRIDGE.execute(CID, "large output")
        self.assertTrue(result["truncated"])
        self.assertEqual(len(result["stdout"]), 65536)

    def test_audit_retains_command_result_separately_from_model_response(self):
        with tempfile.TemporaryDirectory() as directory:
            audit = Path(directory) / "calls.jsonl"
            result = {"exit_code": 0, "stdout": "artifact", "stderr": "", "truncated": False, "elapsed_seconds": 0.1}
            with patch.object(BRIDGE, "execute", return_value=result):
                BRIDGE.handle({"method": "tools/call", "params": {"name": "shell", "arguments": {"command": "cat artifact"}}}, CID, audit)
            self.assertEqual(json.loads(audit.read_text()), {"command": "cat artifact", "result": result})


if __name__ == "__main__":
    unittest.main()
