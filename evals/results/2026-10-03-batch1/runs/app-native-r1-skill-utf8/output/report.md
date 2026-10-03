# bench_delta 0.2.1 offline acceptance report

Created the new native Classic Simple XML app in `output/bench_delta` and the release archive `output/bench_delta-0.2.1.tar.gz`. All checks below use supplied synthetic fixtures. They are not live Splunk evidence.

The app contains one table and a default `home` navigation view. It retains the supplied disabled installation state.

| Supplied input | Preserved value |
| --- | --- |
| `app_id` | `"bench_delta"` |
| `app_label` | `"Delta & Readiness"` |
| `author` | `"Synthetic evaluation team"` |
| `version` | `"0.2.1"` |
| `description` | `"Offline benchmark fixture"` |
| `install_state` | `"disabled"` |
| `read_roles` | `["bench_reader"]` |
| `write_roles` | `["bench_editor"]` |
| `dashboard.title` | `"Delta <Health> Å"` |
| `dashboard.earliest` | `"-12h"` |
| `dashboard.latest` | `"now"` |

Exact search, taken from the JSON-decoded input and compared with parsed XML text:

```spl
| makeresults | eval status="A&B<ready>" | table status
```

The decoded title is `Delta <Health> Å`. Its final character is U+00C5. Input and parsed XML code points match; `verification.json` records both title and search code points. XML escapes for ampersands and angle brackets preserve the supplied text.

Identity, author, version, description, install state, roles, search and time values originate in `input/native.json`; required paths and the native app requirement originate in `TASK.md`. The supplied helper was selected for implementation. Its choices are a `home` view, Simple XML version `1.1`, light theme and `export = none`. `inputs-and-origins.json` records these origins and unknown target inputs.

| Acceptance level | Result and evidence |
| --- | --- |
| Source | Passed: inspected all four selected runtime files; exact parsed configuration, role metadata, label, title, query and time range match the supplied input. |
| Build | Not applicable: native configuration/XML, with no frontend or backend compilation. |
| Structure/package | Passed: helper validation and packaging returned exit 0; independent verifier passed 16 assertions. |
| AppInspect | Not run; no vendor validation report supplied or generated. |
| Installed | Not run; no deployment target selected. |
| Live | Not run; search execution, UI rendering, navigation and effective permissions were not exercised. |

The independent verifier checks navigation and XML structure; decoded Unicode equality; exact read/write roles and app-local export; exact archive membership; regular file types and normalized permissions/timestamps; byte equality of archived and selected source files; independent digest agreement; and unchanged hashes for every supplied source file.

The archive contains one `bench_delta/` root and exactly these four selected release files:

- `bench_delta/default/app.conf`
- `bench_delta/default/data/ui/nav/default.xml`
- `bench_delta/default/data/ui/views/home.xml`
- `bench_delta/metadata/default.meta`

`release-files.json` remains in the source app as the explicit packaging manifest. Reports, receipts, verification code and input provenance are outside the archive. The archive contains no local configuration, credentials, dependencies, linked files or extra workspace files.

Archive size: 708 bytes. SHA-256:

```text
322b37a1178f420d7b6853881a6f50d1984487f80656dfe8523a73292473d8fd
```

The checksum file is `output/bench_delta-0.2.1.tar.gz.sha256` (verify from `output/` with `sha256sum -c bench_delta-0.2.1.tar.gz.sha256`). Selected file hashes are in `verification.json`.

Executed commands and exit codes (full returned results are retained in `command-results.json`):

```text
/usr/local/bin/python3 candidate/scripts/splunk_app.py scaffold --config input/native.json --output output/bench_delta  [exit 0]
/usr/local/bin/python3 candidate/scripts/splunk_app.py validate --app output/bench_delta --files output/bench_delta/release-files.json  [exit 0]
/usr/local/bin/python3 candidate/scripts/splunk_app.py package --app output/bench_delta --files output/bench_delta/release-files.json --output output/bench_delta-0.2.1.tar.gz  [exit 0]
/usr/local/bin/python3 output/verify_release.py  [exit 0]
```

Source provenance:

- `input/native.json` SHA-256: `35313a2b28a98d43365c1e654fa6e9d590fcf08523da696be485974e5b888249`
- `candidate/scripts/splunk_app.py` SHA-256: `b747f2a60829b268aafd2cbd4d14a560525cbdb9bf07b97ba045ed28fb74dbda`

Remaining compatibility and evidence limits: the Splunk edition, release and deployment environment are unknown. Target support for Simple XML version `1.1`, installation policy and any Cloud vetting requirements remain unqualified. The named roles are preserved exactly, but their existence and effective access on a real target are unverified. The inline `makeresults` search has no index dependency; its SPL execution and returned table are unverified. The helper is a bounded structure/XML/package check, not a complete Splunk configuration or ACL validator, SPL validator, secret scanner or AppInspect substitute. No performance claim is made.

No supplied authoring value remains unresolved. The unresolved inputs are the deployment target, Splunk version/edition, target role availability and associated runtime acceptance evidence. No targets were contacted, packages installed, content published, games launched or schedules changed.
