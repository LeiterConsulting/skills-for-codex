# Isolated benchmark execution

The [workspace MCP bridge](../scripts/benchmark_workspace_mcp.py) gives an agent a shell inside one caller-provisioned Docker container. It does not provision or inspect that container. Its host-side subprocess passes the command as an argument to `docker exec`; it never runs the command through a host shell. The evaluator selects the exact 64-character container ID and an audit file outside the mounted workspace.

Use this with [matched workspace preparation](BENCHMARKS.md). Define these values for your own evaluation:

| Input | Who resolves it |
| --- | --- |
| Case, fresh output bundle and source snapshot | Agent/user; retain the pack and copied-byte receipts |
| Model, reasoning, time limits and enabled tools | Evaluator; use the same settings in both conditions |
| Docker executable and immutable image digest | Agent/user; inspect the image and available runtime before use |
| Each assigned workspace, container ID and private audit destination | Evaluator; never mount the pair root or evaluator directory |
| Codex executable and clean runtime home | Agent/user; record the exact version and effective configuration |
| Authentication | Host-approved secret mechanism; outside fixtures, mounts and public records |
| Publication destination and redaction rules | Agent/user; publish only reviewed, reusable evidence |

## Provision and verify

Create a separate container for each trial with only its assigned workspace bound at `/workspace`. Use network mode `none`, a read-only root filesystem, all capabilities dropped, `no-new-privileges`, bounded process/memory/CPU limits and a bounded temporary filesystem. Do not mount authentication, a Docker socket, the pair root, another workspace or evaluator files. The benchmark workspace is writable because agents must create deliverables.

Inspect the exact container ID and retain its image, mounts and isolation settings. Check the complete initial mounted file inventory against the prepared receipt, including the skill entrypoint's presence only in the skill condition. Probe evaluator, host and sibling paths and an outbound connection. Send a command containing literal non-ASCII characters through the actual CLI/MCP route, verify the output code points, and compare every requested command/result with the bridge audit. An ASCII-only marker cannot detect encoding corruption. A container name, prompt instruction or CLI exit code is insufficient evidence of isolation.

Start the bridge using caller-resolved paths:

```text
python scripts/benchmark_workspace_mcp.py --container EXACT_INSPECTED_CONTAINER_ID --audit PRIVATE_AUDIT_JSONL
```

Bridge 0.1.1 explicitly configures stdin, stdout and stderr as strict UTF-8, as required by MCP. The initial bridge used Windows legacy stdin decoding and corrupted non-ASCII command text; its 14 earlier trials are retained as diagnostics and excluded from performance conclusions. A regression test reproduces a legacy-encoded stream and proves exact UTF-8 command preservation.

Configure it as a stdio MCP server named `workspace`, with only `shell` enabled. The tool has a 60-second command timeout and visibly bounded output. A command timeout stops the exact assigned container because terminating the host `docker exec` process alone does not establish that its container child stopped. Retain that failure and restart only in a fresh trial.

## Fresh agent context

The first batch used Codex CLI 0.160.0. A new runtime home was seeded only with authentication, with no user configuration, skills, instructions, plugins, history or memories. The child process removed inherited `CODEX_*` and `OPENAI_*` environment entries before setting its own runtime home. Desktop pipe/session entries otherwise exposed account tools despite a fresh home; keep their values out of published records.

The matched CLI settings were `exec --json --ephemeral --skip-git-repo-check --ignore-user-config --ignore-rules --sandbox read-only`, explicit model/reasoning, `approval_policy="never"`, `web_search="disabled"`, and these feature controls:

```text
--disable shell_tool --disable unified_exec --disable view_image
--disable memories --disable plugins --disable apps --disable skill_search
--disable multi_agent --disable browser_use --disable in_app_browser
--disable computer_use --enable skip_host_skill_discovery
```

`skip_host_skill_discovery` is an under-development feature in this CLI; its warning is retained in the original traces. Keep the code-mode tool host enabled: disabling it also disabled the assigned MCP interface in preflight. Configure `mcp_servers.workspace.enabled_tools=["shell"]`, a server timeout exceeding 60 seconds, and `mcp_servers.workspace.tools.shell.approval_mode="approve"` for this already inspected offline container. Without that explicit per-tool setting, the approval-never policy blocked the intended MCP calls. Do not apply that setting to uninspected containers or unrelated tools.

Give both agents the same instruction to use the workspace MCP shell for every file read, write and command, with the shell rooted at `/workspace`. Supply only the assigned `PROMPT.txt`. Common core utilities remain visible; the batch therefore verifies fresh context, mounted-file isolation, absent account tools and the **actual executed tool route**. It is not a general containment certification against a hostile agent or tool vulnerability.

Explicitly distinguish the read-only host filesystem from the separately authorized writable container destination in that common instruction. One primary release trial omitted its required report because it applied the host restriction to the MCP container without attempting a write. Retain that failed completion. The affected comparison was rerun with fresh agents after this common clarification and a write/readback probe:

```text
The host filesystem remains read-only. The separately provisioned workspace MCP
container has an explicitly authorized writable /workspace mount. Create the
task's required output files through that MCP tool within /workspace/output;
do not apply the host filesystem restriction to this separately authorized
container destination.
```

This clarification changes neither host permissions nor the container mount. Use it only for a provisioned and inspected writable container. Probe creation/readback of an authorized output before task scoring; a read-only marker probe does not verify output delivery capability. Keep repair-cohort results separate from the original denominator.

Current host behavior can change. Recheck the effective tool inventory and probes before scoring another runtime version. See the [official configuration reference](https://learn.chatgpt.com/docs/config-file/config-reference) and [MCP stdio transport](https://modelcontextprotocol.io/specification/2025-06-18/basic/transports).

## Retain and review

Keep original JSONL agent traces, bridge command/results, stderr, context, isolation inspections, copied-byte receipts, runtime exit status and output artifacts outside the public checkout. Review every executed tool call and all input/resource hashes. Assert exact equality of requested CLI command text, received bridge command text and returned result payloads; preserve both versions when diagnosing a mismatch. A bridge command returning nonzero differs from a tool transport failure; an intentionally incomplete release-record verdict may correctly return nonzero.

Keep preflight failures outside the task-attempt denominator while reporting them explicitly. Preserve unsuccessful task attempts inside that denominator. Stop only the evaluator's exact containers when runs finish and remove temporary authentication copies from their exact private homes after every worker has exited. Do not sweep unrelated Docker containers or change the user's normal Codex home.

Publish sanitized commands/results and original synthetic artifacts with their hashes when useful. Retain the untouched originals privately; name every redaction and distinguish published hashes from original trace hashes. Do not publish authentication, environment values, workstation paths, private portfolio records or account-linked tool context.
