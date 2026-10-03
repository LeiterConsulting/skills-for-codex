Created the requested native Simple XML app at `output/bench_delta` and packaged `output/bench_delta-0.2.1.tar.gz`. All offline source and release checks passed. Inputs are synthetic fixtures; these results do not establish Splunk compatibility, installation or live behavior. No deployment target was selected.

| Supplied input | Preserved value | Origin |
| --- | --- | --- |
| App ID | `bench_delta` | `input/native.json` |
| App label | `Delta & Readiness` | `input/native.json` |
| Author | `Synthetic evaluation team` | `input/native.json` |
| Version | `0.2.1` | `input/native.json` |
| Description | `Offline benchmark fixture` | `input/native.json` |
| Install state | `disabled` | `input/native.json` |
| Read roles | `bench_reader` | `input/native.json` |
| Write roles | `bench_editor` | `input/native.json` |
| Panel title | `Delta <Health> Å` | JSON-decoded `input/native.json`; equal to parsed XML |
| Earliest / latest | `-12h` / `now` | `input/native.json` |

The exact preserved, JSON-decoded query is:

```spl
| makeresults | eval status="A&B<ready>" | table status
```

The panel title ends with `Å` (U+00C5). Query delimiters are ordinary double quotes (U+0022). The parsed title and query contain no literal backslashes. XML escaping of ampersands and angle brackets preserves their decoded values; UTF-8 text equality checks passed for the label, title, query and both time bounds. Code points and parsed strings are retained in `verification.json`.

Paths, operation and native app shape come from `TASK.md`. The release selection is the supplied helper's four-file manifest, reviewed for this minimal app. Implementation uses the local `candidate/scripts/splunk_app.py`; no external starter or dependencies were downloaded. `authoring-inputs.json` records the chosen inputs, field origins, helper/input hashes and acceptance status.

The release contains exactly these four files under the `bench_delta` root:

- `default/app.conf`
- `default/data/ui/nav/default.xml`
- `default/data/ui/views/home.xml`
- `metadata/default.meta`

`release-files.json` is retained with the source app for selection and is excluded from the archive. Receipts, reports and authoring records are also outside the archive. Selected content was inspected; the archive contains only the app configuration, navigation, single table dashboard and app metadata. Metadata records the supplied read/write roles and `export = none`; enforcement remains a runtime check.

| Acceptance level | Result | Evidence and scope |
| --- | --- | --- |
| Source | Passed | Generated files inspected; exact app.conf metadata, parsed XML text, navigation and role lists verified against the decoded input. |
| Build | Not applicable | Native configuration/XML only; no frontend or backend compilation. |
| Structure/package | Passed | Supplied helper validate and package exited 0; all 24 additional offline assertions passed. |
| AppInspect | Not run | No vendor tool/report or target environment supplied. |
| Installed | Not run | No target selected; nothing installed or enabled. |
| Live | Not run | No search, browser, permissions or runtime behavior exercised on Splunk. |

Commands executed from `/workspace` with Python 3.13.15; each exited 0:

```sh
python candidate/scripts/splunk_app.py scaffold --config input/native.json --output output/bench_delta
python candidate/scripts/splunk_app.py validate --app output/bench_delta --files output/bench_delta/release-files.json
python candidate/scripts/splunk_app.py package --app output/bench_delta --files output/bench_delta/release-files.json --output output/bench_delta-0.2.1.tar.gz
python output/verify_release.py
```

`command-receipts.json` retains actual exit codes, stdout and stderr. `verify_release.py` is a repeatable read-only verifier; its actual result is in `verification.json`. It checked one app root, exact member selection, regular files without links, normalized modes/ownership/timestamps, each member's bytes against the selected source, and SHA-256 equality with the sidecar. All 12 original workspace files matched their pre-generation hashes in `input-hashes.json`; every new file was confined to `output/`.

Actual archive members:

```text
bench_delta
bench_delta/default/app.conf
bench_delta/default/data/ui/nav/default.xml
bench_delta/default/data/ui/views/home.xml
bench_delta/metadata/default.meta
```

Archive size: 708 bytes. SHA-256:

```text
322b37a1178f420d7b6853881a6f50d1984487f80656dfe8523a73292473d8fd
```

The same digest is in `bench_delta-0.2.1.tar.gz.sha256`. Running `sha256sum -c bench_delta-0.2.1.tar.gz.sha256` from `output/` exited 0 and returned `bench_delta-0.2.1.tar.gz: OK`; `digest-check.json` retains that receipt.

Remaining inputs and evidence limits: the deployment platform and exact Splunk version are unknown, so Simple XML 1.1 and configuration compatibility require qualification on the intended release. Existence and capabilities of `bench_reader` and `bench_editor`, effective object permissions, and search execution/time semantics are unverified. The makeresults query is preserved as inert XML text; no live result or data-access evidence is claimed. AppInspect and any applicable Cloud vetting remain outstanding before deployment. The helper is a bounded structural/package validator; it does not validate all Splunk configuration or ACL semantics, validate SPL, scan all selected content for secrets, or test a running server. No performance improvement is claimed. No target connection, publication, installation, game launch or schedule alteration occurred.
