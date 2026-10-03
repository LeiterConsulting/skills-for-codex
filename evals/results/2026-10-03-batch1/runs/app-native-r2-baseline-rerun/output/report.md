Created the native Simple XML app at `output/bench_delta` from `input/native.json`, validated its four selected release files, and produced the requested archive and SHA-256 digest. All evidence comes from the supplied synthetic fixtures and local file checks; it is not live Splunk evidence.

Deliverables (links are relative to this report):

- [App source and release manifest](bench_delta/)
- [Release archive](bench_delta-0.2.1.tar.gz) â€” 708 bytes
- [SHA-256 sidecar](bench_delta-0.2.1.tar.gz.sha256)
- [Structural validation receipt](validation.json)
- [Package receipt](package-result.json)
- [Independent checks, file hashes, archive inventory and source provenance](checks.json)

Archive SHA-256:

```text
322b37a1178f420d7b6853881a6f50d1984487f80656dfe8523a73292473d8fd
```

The identity and behavior preserve the supplied values:

| Setting | Value |
| --- | --- |
| App ID / version | `bench_delta` / `0.2.1` |
| App label | `Delta & Readiness` |
| Author | `Synthetic evaluation team` |
| Description | `Offline benchmark fixture` |
| Install state | `disabled` |
| Read roles | `bench_reader` |
| Write roles | `bench_editor` |
| Metadata export | `none` (app scope) |
| Default view | `home` |
| Native view | Simple XML dashboard, version `1.1`, light theme; one table and inline search |
| Panel title | `Delta <Health> \u00c5` |
| Earliest / latest | `-12h` / `now` |

The inline search is exactly the JSON-decoded fixture value:

```text
| makeresults | eval status=\"A&B<ready>\" | table status
```

The title contains a literal backslash followed by `u00c5`, and the search contains literal backslashes before its quotation marks. They were preserved without a second decoding pass. XML serialization escapes `&`, `<` and `>`; parsing the resulting XML recovers the exact supplied strings. If the intended title was an actual Ã… character, or the intended search omitted the backslashes before quotes, that intent remains unresolved. No correction was inferred.

The explicit release selection is:

```text
bench_delta/default/app.conf
bench_delta/default/data/ui/nav/default.xml
bench_delta/default/data/ui/views/home.xml
bench_delta/metadata/default.meta
```

`release-files.json` remains in the app source as the packaging selection record and is excluded from the archive. The archive contains one app-root directory and these four regular files. The reviewed content contains only app configuration, navigation, the dashboard and role metadata. No local configuration, credentials, keys, dependencies, caches, saved searches or schedules are selected.

| Completed check | Result |
| --- | --- |
| Supplied helper's native configuration contract | Passed during scaffold creation |
| Selected-file paths, regular-file requirements and size limits | Passed helper validation |
| App/package identity and matching version stanzas | Passed |
| XML parsing, default view and navigation references | Passed |
| Exact fixture values in app.conf, metadata and parsed dashboard | Passed independent comparison |
| XML escaping and one-table/one-search structure | Passed |
| Archive membership, file bytes, modes, owners and timestamps | Passed independent inspection |
| Deterministic package reconstruction in memory | Byte-for-byte match |
| Independent SHA-256 and byte count | Match package receipt |
| Original supplied files | All 11 pre/post SHA-256 values unchanged |

The independent verification recorded 19 passed checks in `checks.json`. Source/configuration review and structure/package acceptance are complete. There is no frontend or backend compilation step for this native configuration-only app. The supplied Python helper performs a conservative configuration check; a separate JSON Schema validator was not run.

The helper commands used, from the workspace root, were:

```sh
python3 -B candidate/scripts/splunk_app.py scaffold --config input/native.json --output output/bench_delta
python3 -B candidate/scripts/splunk_app.py validate --app output/bench_delta --files output/bench_delta/release-files.json
python3 -B candidate/scripts/splunk_app.py package --app output/bench_delta --files output/bench_delta/release-files.json --output output/bench_delta-0.2.1.tar.gz
```

The scaffold and package commands refuse existing destinations; they are recorded for provenance rather than as overwrite instructions. The digest can be checked from `output/` with `sha256sum -c bench_delta-0.2.1.tar.gz.sha256`.

Input provenance: `input/native.json` SHA-256 is `35313a2b28a98d43365c1e654fa6e9d590fcf08523da696be485974e5b888249`. The unchanged helper SHA-256 is `b747f2a60829b268aafd2cbd4d14a560525cbdb9bf07b97ba045ed28fb74dbda`. The supplied architecture, input and validation references informed the native structure and evidence boundaries. Full source hashes are retained in `checks.json`.

No deployment target, Splunk release or deployment type was supplied. Compatibility with a particular Splunk Enterprise or Cloud release, Simple XML version/theme support and target-specific packaging/vetting requirements remains unverified. AppInspect was not run, and no vendor report exists in these fixtures. The package was not installed or published, and no target connection, game launch or schedule change was performed.

SPL syntax and execution, returned data, browser rendering/navigation, and effective authorization were not exercised. The existence of `bench_reader` and `bench_editor`, their inheritance and search capabilities, and effective app-object access need target evidence. Metadata text matching does not prove live ACL behavior. Installation, AppInspect and live acceptance remain pending until an authorized target and version are specified; this offline task is complete at the source and structure/package evidence levels.
