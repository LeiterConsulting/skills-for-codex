# Consumer-defined research inputs

Use [research-inputs.template.json](../assets/research-inputs.template.json) as a local record shape; resolve nulls from the user, installed metadata or a stated agent choice. Examples and another workstation are not defaults.

| Input | Why it matters |
| --- | --- |
| game_install, research_workspace, output_path | Consumer paths; keep generated research outside unrelated work |
| installed_version, assemblies | Installed source of truth; each assembly records path and SHA-256 |
| loader_version, sdk_versions | Integration contract; repository copies may differ from installed dependencies |
| tool_provider, tool_schema_revision | Consumer-selected tools and actual available methods |
| requested_symbols, research_question | Bound discovery to the decision the user needs |
| source_snapshot | Assembly digests/version, generation time and searchable source location |
| asset_catalog | Separate capture identity/context for asset claims |
| live_scope | Whether runtime evidence is requested and which session/actions are authorized |
| input_origins | Observed metadata, user input or stated agent choice |

Accessible assemblies or an identified searchable snapshot are required for source research. Consumers can use a maintained MCP server or their own authorized decompiler/search tooling. Neither this collection nor a skill creates access to a running game. Keep credentials outside the record.
