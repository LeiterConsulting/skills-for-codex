# bench_delta 0.2.1 offline release report

Created the new native Simple XML app at `output/bench_delta` and the archive at `output/bench_delta-0.2.1.tar.gz` using the supplied synthetic fixture. Source inspection and selected-file structure/package checks passed. No deployment target is selected. Input files were preserved.

## Supplied values and provenance

All app identity, role, search and time values came from JSON-decoding `input/native.json`; the example config was not substituted. The supplied helper created the app. The agent selected its four native runtime files for release; reports, receipts, the verifier and `release-files.json` are outside the archive.

| Field | Value |
| --- | --- |
| App ID | `bench_delta` |
| App label | `Delta & Readiness` |
| Author | `Synthetic evaluation team` |
| Version | `0.2.1` |
| Description | `Offline benchmark fixture` |
| Install state | `disabled` |
| Read roles | `bench_reader` |
| Write roles | `bench_editor` |
| Object export | `none` |
| Default view | `home` |
| Dashboard panel title | `Delta <Health> Å` |
| Earliest | `-12h` |
| Latest | `now` |

The exact parsed inline search is:

```spl
| makeresults | eval status="A&B<ready>" | table status
```

The dashboard label, panel title, query, earliest and latest were compared as decoded Unicode strings against parsed XML text. Every equality assertion passed. XML escaping preserves ampersands and angle brackets as text. The title ends with U+00C5 (`Å`); the query contains 2 U+0022 double quotes and 0 U+005C backslashes. These counts come from the same parsed values, not their JSON/tool display representations. Full code-point evidence is in [verification-receipt.json](verification-receipt.json).

Input SHA-256: `35313a2b28a98d43365c1e654fa6e9d590fcf08523da696be485974e5b888249`.

Supplied helper source SHA-256: `b747f2a60829b268aafd2cbd4d14a560525cbdb9bf07b97ba045ed28fb74dbda`. Both hashes matched the initial recorded values. This hash identifies the source used; no external template or starter was fetched.

## Selected release and archive

[release-files.json](bench_delta/release-files.json) explicitly selects these files:

| Relative app path | Bytes |
| --- | ---: |
| `default/app.conf` | 269 |
| `default/data/ui/nav/default.xml` | 111 |
| `default/data/ui/views/home.xml` | 440 |
| `metadata/default.meta` | 76 |

The archive has one `bench_delta` directory root and exactly those four regular files. Each archived payload matched its selected source bytes. No symlinks, hard links, private configuration, keys, dependencies, caches, receipts or other workspace content are included. The four selected UTF-8 text files were inspected and contain the app configuration, navigation, synthetic dashboard and ACL metadata.

Archive size: 708 bytes.

SHA-256: `322b37a1178f420d7b6853881a6f50d1984487f80656dfe8523a73292473d8fd`.

Digest file: [bench_delta-0.2.1.tar.gz.sha256](bench_delta-0.2.1.tar.gz.sha256). Independent Python hashing matched the actual helper packaging receipt, and `sha256sum -c` passed; its output is retained in [sha256-check.txt](sha256-check.txt). Archive ownership, modes and zero timestamps match the supplied helper's deterministic settings.

## Completed checks

The supplied `validate` command passed before packaging. The supplied `package` command also validated the selected release and recorded its actual result in [package-receipt.json](package-receipt.json). The additional verifier executed 19 assertions successfully; its actual results are retained in [verification-receipt.json](verification-receipt.json).

| Check | Result |
| --- | --- |
| Input fixture unchanged from its initial recorded SHA-256 | Passed |
| Supplied helper unchanged from its initial recorded SHA-256 | Passed |
| Decoded input passes the supplied helper config contract | Passed |
| Explicit release selection contains exactly the four intended runtime files | Passed |
| Selected files pass helper path, regular-file, link and size checks | Passed |
| App identity, label, author, version, description and disabled state match decoded input | Passed |
| ACL uses one app-wide metadata stanza | Passed |
| ACL read/write roles equal the supplied role arrays; export is none | Passed |
| Default navigation and app default_view resolve to the selected home dashboard | Passed |
| Native Simple XML has one table and one explicitly scoped inline search | Passed |
| Parsed XML text equals decoded JSON as exact Unicode strings, including query and time range | Passed |
| Actual helper packaging receipt records successful structure validation and selected identity | Passed |
| Independent archive SHA-256 and byte size match the packaging receipt | Passed |
| Archive has one app root and exactly the selected regular files, with no links or extra content | Passed |
| Archive payload equals selected source bytes: default/app.conf | Passed |
| Archive payload equals selected source bytes: default/data/ui/nav/default.xml | Passed |
| Archive payload equals selected source bytes: default/data/ui/views/home.xml | Passed |
| Archive payload equals selected source bytes: metadata/default.meta | Passed |
| Archive timestamps, owners and modes use the deterministic helper settings | Passed |
| Conventional SHA-256 digest file verification | Passed |

The read-only verifier can be rerun from the workspace with `python3 -B output/verify_release.py`. The helper validation command is `python3 -B candidate/scripts/splunk_app.py validate --app output/bench_delta --files output/bench_delta/release-files.json`. Verify the digest with `cd output` followed by `sha256sum -c bench_delta-0.2.1.tar.gz.sha256`.

## Remaining compatibility and evidence limits

| Acceptance level | Evidence/status |
| --- | --- |
| Source | Supplied helper and four selected release files inspected; fixture metadata preserved |
| Build | Not applicable: this release has native configuration/XML and no custom frontend/backend compilation |
| Structure/package | Passed, with exact Unicode/ACL comparisons, archive payload inspection and digest verification |
| AppInspect | Not run; no vendor report supplied |
| Installed | Not installed; no deployment target selected |
| Live | Not run; no Splunk search, permissions, navigation or browser session exercised |

The Splunk release, deployment type (Enterprise or Cloud), deployment target and target role definitions/user mappings are unresolved. Compatibility of the generated Simple XML version 1.1 dashboard, navigation, app configuration and ACL behavior must be qualified against the eventual target. Structural validation is not a target compatibility or AppInspect result.

The input is synthetic offline evidence. The inline SPL and `-12h`/`now` range were preserved and checked as text, but SPL execution, returned results, time behavior and effective access were not tested. The role names remain exactly as supplied; their existence and authorization effects on a target are unknown. No live data contract or operational readiness is established by this fixture.

Any future authorized deployment would require target-specific compatibility checks, the applicable AppInspect/vetting workflow and installed/runtime acceptance evidence. This task performed no connections, installation, publication or deployment, and the supplied disabled state remains in the package. There are no unresolved app-authoring values; the remaining gaps concern target qualification and live evidence.
