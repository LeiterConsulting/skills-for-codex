# Offline native app release

Created `output/bench_delta` and `output/bench_delta-0.2.1.tar.gz` from `input/native.json` using the supplied native helper. All fixtures are synthetic; these checks establish offline source and package evidence only. No deployment target is selected.

## Exact supplied values

| Field | Preserved value |
| --- | --- |
| App ID | `bench_delta` |
| Label | `Delta & Readiness` |
| Author | `Synthetic evaluation team` |
| Version | `0.2.1` |
| Description | `Offline benchmark fixture` |
| Install state | `disabled` |
| Read roles | `bench_reader` |
| Write roles | `bench_editor` |
| Dashboard panel title | `Delta <Health> Å` |
| Earliest | `-12h` |
| Latest | `now` |

Inline search (exact JSON-decoded value):

```spl
| makeresults | eval status="A&B<ready>" | table status
```

The app uses one Simple XML 1.1 dashboard (`home`) containing a table with the supplied inline search and time range. The dashboard label uses the app label; the panel title uses the supplied dashboard title. Navigation selects `home`. Default metadata uses the supplied role lists with `export = none`.

Quoted values above come from JSON-decoded input. Parsed XML text was asserted equal to those values as Unicode strings. The title's final code point is `U+00C5`. The title has 0 U+005C backslash characters; the query has 0. Query U+0022 quotation marks occur at zero-based positions [28, 39]. Full expected and actual code points are retained in `verification.json`. XML entities preserve the literal ampersands and angle brackets when parsed.

## Completed checks

- Supplied helper scaffold and `validate` commands completed successfully; input configuration and the four selected release files passed the helper's bounded validation.
- All `app.conf` fields, metadata role lists, dashboard structure, navigation, label, title, search and time bounds were checked against the supplied values.
- Every selected file was read and reviewed. The release contains only the four files below; no private configuration, keys, dependencies, caches, reports or authoring scripts are selected.
- The helper's `package` command completed successfully. Archive membership, file types, byte equality with selected files, fixed metadata, archive size and an independently computed SHA-256 passed.
- All 11 supplied workspace files remained byte-identical to their recorded initial SHA-256 values.

Selected release files:

- `default/app.conf`
- `default/data/ui/nav/default.xml`
- `default/data/ui/views/home.xml`
- `metadata/default.meta`

The archive contains those four files beneath the single `bench_delta/` root. `release-files.json` remains a local release-selection record and is excluded from the archive.

## Digest and receipts

- Archive size: 708 bytes.
- SHA-256: `322b37a1178f420d7b6853881a6f50d1984487f80656dfe8523a73292473d8fd`.
- Digest file: `output/bench_delta-0.2.1.tar.gz.sha256` (verify from `output/` with `sha256sum -c bench_delta-0.2.1.tar.gz.sha256`).
- Input SHA-256: `35313a2b28a98d43365c1e654fa6e9d590fcf08523da696be485974e5b888249`.
- Helper SHA-256: `b747f2a60829b268aafd2cbd4d14a560525cbdb9bf07b97ba045ed28fb74dbda`.
- `verification.json` records actual command arguments, exit codes, stdout/stderr, parsed results, passed assertions, Unicode comparisons, archive members and source/artifact hashes.
- `complete_task.py` preserves the local build/check procedure; it refuses existing release destinations.

## Compatibility and evidence limits

Splunk deployment type, target version and intended environment remain unresolved. Compatibility of Simple XML 1.1, app configuration, default navigation and metadata must be qualified against the chosen target release. The supplied role names are preserved; their existence, capabilities, user membership and effective ACL behavior have not been verified on a target.

No SPL execution, time-range interpretation, data access, displayed search result, browser behavior or effective app visibility/permissions was tested. The helper treats the query as inert XML text and does not validate SPL semantics. Its structural checks do not parse every Splunk setting or enforce every ACL rule.

AppInspect/vetting, installation and live runtime acceptance were not run. The supplied `disabled` install state is preserved. No targets were contacted, apps published or installed, or schedules changed. Future compatibility, AppInspect and runtime checks require an explicitly selected and authorized target; the synthetic fixtures cannot establish live evidence.
