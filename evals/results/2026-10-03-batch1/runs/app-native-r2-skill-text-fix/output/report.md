# Offline native app qualification

Created `output/bench_delta` and `output/bench_delta-0.2.1.tar.gz` from the supplied synthetic fixture. The release passes the helper's structural checks and 32 offline assertions recorded in `output/verification.json`. Original workspace files are unchanged (12 file hashes compared).

## Supplied values and origins

Identity, roles, disabled state and dashboard values come from JSON-decoded `input/native.json`. Paths, operation and native Simple XML requirement come from `TASK.md`. `output/authoring-inputs.json` records all values and their origins; the supplied helper's SHA-256 records its local revision.

- App ID: `bench_delta`; version: `0.2.1`.
- App label: `Delta & Readiness`.
- Author: `Synthetic evaluation team`; description: `Offline benchmark fixture`.
- Install state: `disabled`.
- Read roles: `bench_reader`; write roles: `bench_editor`; metadata export: `none`.
- Panel title: `Delta <Health> Å`. Its final character is U+00C5 (`Å`).
- Inline search: `| makeresults | eval status="A&B<ready>" | table status`. The two quotation marks are U+0022; the decoded query has no literal backslashes.
- Earliest: `-12h`; latest: `now`.

The helper creates a Classic Simple XML 1.1 dashboard with one table, uses the app label as the dashboard label, uses the supplied dashboard title as the panel title, and sets the default view/navigation to `home`. These are recorded helper layout choices. XML text is escaped during serialization; parsed source and archive XML match every supplied text value exactly as Unicode strings. Code points and equality results are retained in the verification receipt.

## Selected release and archive

- `default/app.conf`
- `default/data/ui/nav/default.xml`
- `default/data/ui/views/home.xml`
- `metadata/default.meta`

The inspected archive has one `bench_delta/` root and exactly these four regular files. Every member's bytes match its inspected source. Root mode is 0755, file modes are 0644, and ownership/timestamps are normalized. `release-files.json` is retained in the app source as the selection record and excluded from the archive. Reports, receipts, verifier and other workspace files are excluded. Selected contents were inspected; no runtime local configuration or credentials were selected. This is not a comprehensive secret scan.

- Archive bytes: 708.
- SHA-256: `322b37a1178f420d7b6853881a6f50d1984487f80656dfe8523a73292473d8fd`.
- Digest file: `output/bench_delta-0.2.1.tar.gz.sha256`.

## Commands and completed checks

- `python3 candidate/scripts/splunk_app.py scaffold --config input/native.json --output output/bench_delta` - exit 0.
- `python3 candidate/scripts/splunk_app.py validate --app output/bench_delta --files output/bench_delta/release-files.json` - exit 0.
- `python3 candidate/scripts/splunk_app.py package --app output/bench_delta --files output/bench_delta/release-files.json --output output/bench_delta-0.2.1.tar.gz` - exit 0.
- `python3 output/verify_release.py` - passed; assertions and actual archive inventory retained in `output/verification.json`.

Helper configuration validation, selected structure/XML parsing, identity/version consistency, default navigation and release selection passed. Independent assertions checked metadata role text, all supplied configuration, parsed XML text and time range, archive membership/type/permissions, source/archive byte equality, digest/size agreement and original-file preservation. The bundled schema's version regex matches the supplied version; no full external JSON Schema validator was run. Command exit codes, stdout and stderr are retained in the three operation receipt JSON files.

## Evidence limits and unresolved inputs

All evidence is offline and synthetic. No search was executed. There is no selected deployment target, and the Splunk product, version, operating environment and actual target roles are unknown. The fixture search uses `makeresults`; no real index, data ingestion or production field contract is established.

Native configuration requires no frontend/backend compilation. AppInspect/vetting, installation and live checks were not run. The helper is a bounded structural/package validator, not a complete Splunk config, ACL, SPL or compatibility validator. Target compatibility with Simple XML 1.1, role availability and effective permissions, search/time behavior, navigation and rendering require the actual authorized target and its applicable checks. No performance result is claimed.

No targets were contacted; nothing was published, installed, launched or scheduled. Completion covers the requested offline source/package deliverables. Deployment acceptance remains unestablished.
