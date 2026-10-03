Created the native Simple XML app at [bench_delta/](bench_delta/) and the release archive [bench_delta-0.2.1.tar.gz](bench_delta-0.2.1.tar.gz). Offline source and selected-file structure/package checks passed. These supplied synthetic fixtures are not live evidence. No deployment target was selected; nothing was installed, published, connected to a target, or scheduled.

Inputs and origins:

| Input | Exact value | Origin |
| --- | --- | --- |
| App ID / version | `bench_delta` / `0.2.1` | `input/native.json` |
| App label | `Delta & Readiness` | `input/native.json` |
| Author | `Synthetic evaluation team` | `input/native.json` |
| Description | `Offline benchmark fixture` | `input/native.json` |
| Install state | `disabled` | `input/native.json` |
| Read roles | `bench_reader` | `input/native.json` |
| Write roles | `bench_editor` | `input/native.json` |
| Panel title | `Delta <Health> Å` | `input/native.json`; supplied helper places this title on the table panel |
| Time range | `-12h` to `now` | `input/native.json` |
| App shape and output paths | Native Simple XML; `output/bench_delta`, versioned archive | `TASK.md` |
| Deployment / Splunk version | No target selected / unknown | `TASK.md` / not supplied |

The inline search is exactly the parsed JSON value:

```spl
| makeresults | eval status="A&B<ready>" | table status
```

The app uses Simple XML 1.1 with one table panel, app label as the dashboard label, and navigation/default view set to `home`. XML escapes reserved characters and preserves the parsed title, label, query and times exactly. The title contains Unicode Å; the query contains ordinary double quotes. App metadata uses the supplied read/write roles and `export = none`. No roles are provisioned by this app. No indexes, credentials, custom code, saved schedules or external dependencies were added.

The selected release manifest, [bench_delta/release-files.json](bench_delta/release-files.json), contains only:

```text
bench_delta/default/app.conf
bench_delta/default/data/ui/nav/default.xml
bench_delta/default/data/ui/views/home.xml
bench_delta/metadata/default.meta
```

This is the actual archive membership beneath its single `bench_delta` directory root. The release manifest and report/acceptance records remain outside the archive. All four selected file contents were reviewed.

Commands and results:

```sh
python3 candidate/scripts/splunk_app.py scaffold --config input/native.json --output output/bench_delta
python3 candidate/scripts/splunk_app.py validate --app output/bench_delta --files output/bench_delta/release-files.json
python3 candidate/scripts/splunk_app.py package --app output/bench_delta --files output/bench_delta/release-files.json --output output/bench_delta-0.2.1.tar.gz
(cd output && sha256sum -c bench_delta-0.2.1.tar.gz.sha256)
```

All commands exited 0. Scaffold created five files, including the explicit four-file release manifest. Validation returned app ID `bench_delta`, version `0.2.1`, selected file count 4, and `structure: passed`. Packaging returned `package: created`, 708 bytes, and the digest below. The independent digest-sidecar check returned `bench_delta-0.2.1.tar.gz: OK`.

Additional inline Python checks used `configparser`, `xml.etree.ElementTree`, `tarfile` and `hashlib`. They compared every supplied identity/configuration value, ACL roles, decoded XML text, search and time range with `input/native.json`; checked navigation/default view and manifest membership; inspected the real archive; compared every archived file byte-for-byte with its selected source; and confirmed archived identity/version, regular members, modes (0755 root, 0644 files), zero timestamps and owner IDs. The supplied schema's version regex also matched `0.2.1`; this isolated regex check is not full JSON Schema validation. SHA-256 checks confirmed all 12 original workspace files were unchanged and no files were added outside `output/`.

| Acceptance level | Result and scope |
| --- | --- |
| Source | Passed helper input validation, selected content review and exact-value comparisons. |
| Build | Not applicable: native configuration/XML only; no frontend/backend compilation. |
| Structure/package | Passed bounded helper validation, actual archive checks and independent digest verification. |
| AppInspect | Not run; no vendor report or target-specific vetting evidence. |
| Installed | Not run; no target selected and deployment is outside this task. |
| Live | Not run; searches, browser rendering, navigation and effective permissions were not exercised. |

SHA-256:

```text
322b37a1178f420d7b6853881a6f50d1984487f80656dfe8523a73292473d8fd  bench_delta-0.2.1.tar.gz
```

The digest sidecar is [bench_delta-0.2.1.tar.gz.sha256](bench_delta-0.2.1.tar.gz.sha256). [authoring-inputs.json](authoring-inputs.json) records the chosen inputs and their origins, [checks.json](checks.json) records check results and actual archive members, and [input-hashes.json](input-hashes.json) records the supplied-file baseline. The scaffold/package source is the supplied `candidate/scripts/splunk_app.py`, SHA-256 `b747f2a60829b268aafd2cbd4d14a560525cbdb9bf07b97ba045ed28fb74dbda`; no source release/Git revision was supplied and no external starter was used.

Remaining compatibility and evidence limits: Splunk edition, version and deployment details are unresolved. Compatibility of Simple XML 1.1, app.conf and ACL behavior must be checked against the eventual target. Existence and capabilities of `bench_reader` and `bench_editor`, effective inherited permissions and the user's ability to run the supplied SPL are unverified. The synthetic search was preserved but never executed or validated by Splunk, so no result, performance or real-data behavior is claimed. The helper is not a complete Splunk validator, SPL checker, ACL validator, secret scanner or AppInspect replacement. Official online references were not consulted during this offline task. A later authorized deployment would still require the applicable AppInspect/vetting checks and target installation/browser/search/permission verification; none of that evidence is available here.
