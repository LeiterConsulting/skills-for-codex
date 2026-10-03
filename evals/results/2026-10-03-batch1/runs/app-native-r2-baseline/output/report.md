# Native Splunk app release report

Created [bench_delta](bench_delta/) from the supplied synthetic fixture `input/native.json`, using the unmodified bundled `candidate/scripts/splunk_app.py` helper. The release is [bench_delta-0.2.1.tar.gz](bench_delta-0.2.1.tar.gz), 708 bytes. All evidence is offline; no deployment target is selected.

## Preserved configuration

| Field | Supplied and verified value |
| --- | --- |
| App ID / package ID / ID stanza | `bench_delta` |
| App label / dashboard label | `Delta & Readiness` |
| Author | `Synthetic evaluation team` |
| Version (launcher and ID stanza) | `0.2.1` |
| Description | `Offline benchmark fixture` |
| Install state | `disabled` |
| Read roles | `bench_reader` |
| Write roles | `bench_editor` |
| Dashboard panel title | `Delta <Health> Å` |
| Earliest / latest | `-12h` / `now` |

The Simple XML dashboard uses version `1.1`, a light theme, one table and one inline search. The default view is `home`; navigation points to the included `home.xml`. The app-level `metadata/default.meta` stanza is `[]`, with exactly the supplied read/write roles and `export = none`.

The search text after JSON decoding and XML parsing is exactly:

```text
| makeresults | eval status="A&B<ready>" | table status
```

The JSON Unicode escape decodes to U+00C5 (LATIN CAPITAL LETTER A WITH RING ABOVE), and the JSON escaped quotation marks decode to plain double quotes in the search. These decoded fixture values are preserved exactly. XML escaping of `&`, `<` and `>` round-trips to the supplied text. The search has not been parsed or executed by Splunk.

## Release selection

[release-files.json](bench_delta/release-files.json) explicitly selects only these four runtime files:

- `default/app.conf`
- `default/data/ui/nav/default.xml`
- `default/data/ui/views/home.xml`
- `metadata/default.meta`

The manifest stays in the source app and is excluded from the archive. The package contains one `bench_delta/` directory entry and those four regular files. The report, digest, validation record, source fixture and helper are excluded. Selected contents were inspected and contain only app configuration, navigation, the synthetic dashboard/search and ACL metadata; no executable backend, credentials, dependency tree or `local/` configuration is included.

## Completed checks

| Check | Result and scope |
| --- | --- |
| Input contract | Passed the helper's Python config validator against `input/native.json`; no external JSON Schema validator was used. |
| Exact fixture fidelity | Parsed app.conf, XML and ACL text match all supplied metadata, disabled state, role lists, dashboard title, search and time bounds. |
| Selected release validation | Helper `validate` passed for four files: canonical paths, regular unlinked files, file/total size limits, package/root and version agreement, XML parsing, default-view and navigation references. |
| Content inspection | All four selected files reviewed before packaging. |
| Package validation | Helper `package` passed its release validation and produced the requested archive. |
| Archive inspection | Exact member list verified; archived bytes match selected source files; no links, traversal or unselected members. Directory mode `0755`, file modes `0644`, uid/gid and timestamps zero. |
| Reproducibility | In-memory reconstruction under the same Python runtime produced identical tar.gz bytes; gzip timestamp is zero and no source filename is embedded. |
| Digest | Independently calculated SHA-256; recorded below and in the checksum sidecar. |
| Preservation | Fixture and helper hashes match the values read before scaffolding. Supplied files were not edited; deliverables are in `output/`. |

The machine-readable results and per-file hashes are in [validation.json](validation.json).

Reproduce the structural check from the workspace root:

```sh
python3 -B candidate/scripts/splunk_app.py validate --app output/bench_delta --files output/bench_delta/release-files.json
cd output
sha256sum -c bench_delta-0.2.1.tar.gz.sha256
```

SHA-256 of `bench_delta-0.2.1.tar.gz`:

```text
322b37a1178f420d7b6853881a6f50d1984487f80656dfe8523a73292473d8fd
```

Checksum sidecar: [bench_delta-0.2.1.tar.gz.sha256](bench_delta-0.2.1.tar.gz.sha256).

Provenance hashes:

- `input/native.json`: `35313a2b28a98d43365c1e654fa6e9d590fcf08523da696be485974e5b888249`
- `candidate/scripts/splunk_app.py`: `b747f2a60829b268aafd2cbd4d14a560525cbdb9bf07b97ba045ed28fb74dbda`

## Compatibility and evidence limits

Source inspection and offline structure/package acceptance are complete. There is no frontend/backend compilation step for these native configuration files. No AppInspect report, Splunk installation, browser test, live navigation, search execution or effective-permission test was performed. No target was contacted, package published, software installed or schedule altered.

The target deployment type and exact Splunk release are unknown. Simple XML `1.1` support, target-specific app.conf/metadata behavior, disabled-app behavior and Enterprise/Cloud vetting requirements remain unverified. The supplied reference documents are offline guidance, not current target evidence. The helper checks a bounded portable subset and does not validate all Splunk configuration or ACL semantics, SPL syntax/results, time-expression behavior, or runtime access.

The existence and capabilities of `bench_reader` and `bench_editor`, and their effective access on a target remain unresolved. These synthetic fixtures establish no behavior against live data. Installation, AppInspect and live acceptance require a subsequently selected, authorized target and its exact compatibility requirements.
