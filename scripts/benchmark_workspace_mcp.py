#!/usr/bin/env python3
"""Expose only a caller-provisioned, isolated Docker workspace shell over stdio MCP.

The caller must verify container mounts/network/capabilities before starting an agent.
This bridge never provisions containers or exposes a host shell.
"""
import argparse
import json
from pathlib import Path
import re
import subprocess
import sys
import time

TOOL = {"name": "shell", "description": "Run a POSIX shell command in your isolated Linux workspace at /workspace. Python 3.13 and standard Unix tools are available. No external network or other workspace is mounted. Use this tool to read files, write output artifacts and execute supplied helpers.",
        "inputSchema": {"type": "object", "properties": {"command": {"type": "string"}}, "required": ["command"], "additionalProperties": False},
        "annotations": {"readOnlyHint": False, "openWorldHint": False, "destructiveHint": True}}


def execute(container, command, docker="docker"):
    if not re.fullmatch(r"[a-f0-9]{64}", container):
        raise ValueError("Use an exact inspected container ID")
    if not isinstance(command, str) or not command or len(command) > 32768:
        raise ValueError("Expected a command of 1-32768 characters")
    start = time.monotonic()
    try:
        completed = subprocess.run([docker, "exec", "--workdir", "/workspace", container, "sh", "-lc", command],
                                   capture_output=True, timeout=60)
        result = {"exit_code": completed.returncode,
                  "stdout": completed.stdout.decode("utf-8", errors="replace")[:65536],
                  "stderr": completed.stderr.decode("utf-8", errors="replace")[:65536],
                  "truncated": len(completed.stdout) > 65536 or len(completed.stderr) > 65536}
    except subprocess.TimeoutExpired:
        # An exec timeout does not guarantee the child stopped inside the container.
        # Stop this exact container and fail closed; the evaluator retains/reviews it.
        subprocess.run([docker, "stop", "--time", "1", container], capture_output=True, timeout=15)
        result = {"exit_code": None, "stdout": "", "stderr": "Command exceeded 60 seconds; assigned container stopped", "truncated": False}
    result["elapsed_seconds"] = round(time.monotonic() - start, 6)
    return result


def handle(message, container, audit=None):
    method = message.get("method")
    if method == "initialize":
        return {"protocolVersion": message.get("params", {}).get("protocolVersion", "2024-11-05"),
                "capabilities": {"tools": {}}, "serverInfo": {"name": "isolated-workspace", "version": "0.1.1"}}
    if method == "ping":
        return {}
    if method == "tools/list":
        return {"tools": [TOOL]}
    if method == "tools/call":
        params = message.get("params", {})
        arguments = params.get("arguments", {})
        if params.get("name") != "shell" or set(arguments) != {"command"}:
            raise ValueError("Unknown tool or arguments")
        result = execute(container, arguments["command"])
        if audit:
            with Path(audit).open("a", encoding="utf-8") as stream:
                stream.write(json.dumps({"command": arguments["command"], "result": result}, ensure_ascii=True) + "\n")
        return {"content": [{"type": "text", "text": json.dumps(result)}], "isError": result["exit_code"] is None}
    raise ValueError("Unsupported method")


def main():
    # MCP stdio is UTF-8, independent of the Windows host's legacy encoding.
    # Otherwise non-ASCII JSON command text changes before container execution.
    sys.stdin.reconfigure(encoding="utf-8", errors="strict")
    sys.stdout.reconfigure(encoding="utf-8", errors="strict")
    sys.stderr.reconfigure(encoding="utf-8", errors="strict")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--container", required=True)
    parser.add_argument("--audit", help="Evaluator-selected local JSONL output, outside agent mounts")
    args = parser.parse_args()
    if not re.fullmatch(r"[a-f0-9]{64}", args.container):
        parser.error("Use an exact inspected container ID")
    for line in sys.stdin:
        if len(line) > 1024 * 1024:
            raise ValueError("Oversized MCP message")
        message = json.loads(line)
        if "id" not in message:
            continue
        response = {"jsonrpc": "2.0", "id": message["id"]}
        try:
            response["result"] = handle(message, args.container, args.audit)
        except (OSError, ValueError, subprocess.SubprocessError) as error:
            response["error"] = {"code": -32602, "message": str(error)}
        print(json.dumps(response), flush=True)


if __name__ == "__main__":
    main()
