# bench_delta 0.2.1 offline release report

Created the native Simple XML app at `output/bench_delta` and packaged the four explicitly selected release files as `output/bench_delta-0.2.1.tar.gz`. All 18 offline verification checks passed. The supplied fixtures are synthetic and are not live evidence. No deployment target is selected.

## Supplied values and provenance

Identity, metadata, roles, search and time range came exclusively from JSON-decoded `input/native.json`; no example defaults replaced them. The supplied helper `candidate/scripts/splunk_app.py` generated the app and performed selected-file validation and packaging.

- App ID: `bench_delta`; version: `0.2.1`.
- App label: `Delta & Readiness`; author: `Synthetic evaluation team`.
- Description: `Offline benchmark fixture`; install state: `disabled`.
- Read roles: `bench_reader`; write roles: `bench_editor`; metadata export: `none`.
- Dashboard panel title: `Delta <Health> Å`.
- Earliest: `-12h`; latest: `now`.

Exact decoded search, preserved as parsed XML text:

```spl
| makeresults | eval status="A&B<ready>" | table status
```

The title ends with the character U+00C5 (Å). The query quotes are U+0022. Neither string contains a literal backslash (U+005C). XML serializes ampersands and angle brackets as entities, then parses back to the identical supplied characters. `verification.json` records parsed values and their code points.

Input SHA-256: `35313a2b28a98d43365c1e654fa6e9d590fcf08523da696be485974e5b888249`.

Supplied helper SHA-256: `b747f2a60829b268aafd2cbd4d14a560525cbdb9bf07b97ba045ed28fb74dbda`; no independent helper version was supplied.

## Release selection

`bench_delta/release-files.json` selects the following files. The manifest, verifier, receipts and report remain outside the archive.

| Relative app path | Bytes | SHA-256 |
| --- | ---: | --- |
| `default/app.conf` | 269 | `00443390c065b47c53767e3572f22720bf29a5f52dd2ba3a7c6579106771b4bf` |
| `default/data/ui/nav/default.xml` | 111 | `ac1b36dccc69734bf4b14590b1364818a1d93e20efea5217e7d8e1c96a70dd05` |
| `default/data/ui/views/home.xml` | 440 | `0ed0aed44b5dff1b87d514d216b6c818625a5211476f8da2d14df25591cdf0f4` |
| `metadata/default.meta` | 76 | `84e42421923038931260b66ac7fc1a8ff28bd28c89535381cd880fb8f0489b89` |

The selected contents were inspected: app identity and disabled state, native navigation, a single table with the supplied inline search, and the requested ACL. They contain no credentials, external endpoints, backend code or scheduling configuration. No local configuration, dependencies, caches or unrelated workspace files were selected.

## Completed checks

All three helper commands exited 0. Their exact arguments, stdout, stderr and results are retained in `build-receipts.json`. Helper validation checks its documented portable config contract, app identity, selected XML and navigation; it is not comprehensive Splunk configuration or formal JSON Schema validation.

| Check | Result | Evidence |
| --- | --- | --- |
| `helper_commands` | passed | Scaffold, selected-file validation and package commands exited 0 without stderr. |
| `release_selection` | passed | Explicit release manifest selects only the four native app files; manifest and evidence are excluded from the archive. |
| `app_file_set` | passed | App source contains exactly the selected files and the release manifest. |
| `regular_files` | passed | Selected files are regular files with no linked path components. |
| `utf8` | passed | All selected files round-trip as UTF-8. |
| `app_conf_identity` | passed | All app.conf sections and values exactly match fixture metadata and the native home-view scaffold, including disabled state and both version stanzas. |
| `navigation` | passed | Navigation selects the packaged home view; search_view refers to the platform search view. |
| `simple_xml_shape` | passed | One Simple XML 1.1 dashboard with one row, one panel, one table and one inline search; no extra tokens or searches. |
| `xml_value_equality` | passed | Parsed XML label, title, query, earliest and latest equal JSON-decoded fixture strings, character for character. |
| `xml_escaping` | passed | Ampersands and angle brackets are escaped as XML text; U+00C5 is UTF-8; no DTD/entity declarations. |
| `metadata_roles` | passed | Global metadata ACL exactly preserves bench_reader read and bench_editor write roles, with export = none and no wildcard or additional grants. |
| `package_receipt_digest` | passed | Independently recomputed package SHA-256 and byte length match the packaging receipt. |
| `archive_membership` | passed | Archive contains one bench_delta root and exactly four regular selected files; no links, duplicate names or extra content. |
| `archive_path_safety` | passed | All archive member names are relative and free of path traversal. |
| `archive_bytes` | passed | Every archive file is byte-identical to its selected source file; archive inspected without extracting. |
| `normalized_archive_metadata` | passed | Tar timestamps/ownership are normalized; root mode 0755 and file modes 0644; gzip timestamp is zero with no stored filename. |
| `source_preservation` | passed | AGENTS.md, TASK.md and all supplied input/candidate files retain their pre-build SHA-256 values. |
| `digest_sidecar` | passed | SHA-256 sidecar names the exact package and contains its recomputed digest. |

Full assertion receipts are in `verification.json`; the repeatable verifier is `verify_release.py`. No compilation applies to these configuration/XML files.

## Package digest

- Artifact: `bench_delta-0.2.1.tar.gz` (708 bytes).
- SHA-256: `322b37a1178f420d7b6853881a6f50d1984487f80656dfe8523a73292473d8fd`.
- Digest sidecar: `bench_delta-0.2.1.tar.gz.sha256`.

Run from `output/`: `sha256sum -c bench_delta-0.2.1.tar.gz.sha256`. Archive inspection confirmed a single `bench_delta/` root and byte equality for all four selected files. The helper writes normalized archive metadata, which was checked; an independent rebuild comparison was not run.

## Remaining compatibility and evidence limits

- Deployment platform, exact Splunk version and target are unresolved. Compatibility of Simple XML 1.1 and these configuration keys has not been qualified against a selected release or Enterprise/Cloud environment.
- Target roles `bench_reader` and `bench_editor` were not observed. Role existence, inherited ACL behavior, effective capabilities and permission enforcement require target evidence. The ACL strings were verified locally only.
- AppInspect/vetting was not run; no vendor report was supplied. Cloud private-app eligibility and the applicable install workflow remain unverified.
- No package was installed, no target was contacted, and no live browser/navigation, search or access test ran. SPL syntax and execution, displayed status and time-range behavior are not proven by XML equality. The supplied search uses synthetic `makeresults`, with no supplied real-data index/field contract.
- The helper does not validate every Splunk configuration or ACL semantic. Structural and archive checks establish offline source/package acceptance only. Runtime acceptance requires the exact package on an authorized compatible target.
- All supplied inputs were preserved. No publishing, installation, game launch or schedule changes occurred.
