# bench_delta 0.2.1 offline release report

Created the native Simple XML app at `output/bench_delta`, the release archive at `output/bench_delta-0.2.1.tar.gz`, and its SHA-256 sidecar at `output/bench_delta-0.2.1.tar.gz.sha256`. Detailed check results and per-file hashes are in `output/validation.json`.

## Supplied values and provenance

All app values come from `input/native.json`; no identity, role, search, or time value was substituted. The app label is `Delta & Readiness`, author is `Synthetic evaluation team`, description is `Offline benchmark fixture`, and install state remains `disabled`. The dashboard label uses the app label and its single table panel title is `Delta <Health> Å`. Read access is restricted to `bench_reader`, write access to `bench_editor`, with `export = none`.

The inline search is preserved exactly as decoded from JSON:

```spl
| makeresults | eval status="A&B<ready>" | table status
```

Time bounds are `-12h` to `now`. The search was written as inert XML text and was never executed.

Input SHA-256: `35313a2b28a98d43365c1e654fa6e9d590fcf08523da696be485974e5b888249`. It matches the hash recorded before generation. Input and candidate files were preserved. The unmodified supplied helper was used; its SHA-256 is `b747f2a60829b268aafd2cbd4d14a560525cbdb9bf07b97ba045ed28fb74dbda`. The release manifest was selected locally as the four native runtime files created by that helper.

## Completed checks

| Check | Result and evidence |
| --- | --- |
| Native input contract | Passed the helper's explicit config validation during scaffold creation. |
| Selected release structure | Passed the helper's `validate` command and revalidation during packaging; four selected files. |
| Identity and configuration | Independently parsed all five `app.conf` stanzas; exact fixture identity, versions, label, author, description, disabled state, and home view. |
| ACL | Exact metadata text matches the supplied reader/editor roles and app-scoped `export = none`; no extra grants. Effective target ACL semantics remain untested. |
| Simple XML and navigation | Both XML files parse. One home view, one table, one inline search; nav and default view agree. Simple XML uses version 1.1 and light theme. |
| XML text fidelity | Parsed app label, panel title, SPL, earliest and latest equal the decoded JSON values. Ampersands and angle brackets are escaped; U+00C5 is retained in UTF-8. |
| Release selection and content review | Exactly the four files below; regular files with no links. All selected contents inspected. No local configuration, keys, dependencies, input files or report material included. This is a bounded content review, not a comprehensive security assessment. |
| Archive inspection | Exactly one app root and four regular files. Archived file bytes equal source bytes; no traversal paths or links. Root mode 0755, files 0644; zero timestamps and ownership, empty owner names; gzip timestamp zero and no embedded filename. |
| Digest and preservation | Archive SHA-256 independently recomputed; input fixture digest unchanged. |
| Build | Not applicable: native configuration/XML only, without frontend or backend code. |

The release manifest remains in the source app for selection and is deliberately absent from the archive. Archive members are:

```text
bench_delta/
bench_delta/default/app.conf
bench_delta/default/data/ui/nav/default.xml
bench_delta/default/data/ui/views/home.xml
bench_delta/metadata/default.meta
```

Commands completed successfully from `/workspace`:

```sh
python3 candidate/scripts/splunk_app.py scaffold --config input/native.json --output output/bench_delta
python3 candidate/scripts/splunk_app.py validate --app output/bench_delta --files output/bench_delta/release-files.json
python3 candidate/scripts/splunk_app.py package --app output/bench_delta --files output/bench_delta/release-files.json --output output/bench_delta-0.2.1.tar.gz
```

Independent standard-library checks parsed configuration/XML, compared the supplied values, examined archive members and metadata, and compared every archived file byte-for-byte with the selected source. Their final results are recorded in `output/validation.json`.

Archive size: **708 bytes**. SHA-256:

```text
322b37a1178f420d7b6853881a6f50d1984487f80656dfe8523a73292473d8fd  bench_delta-0.2.1.tar.gz
```

Verify from the output directory with `sha256sum -c bench_delta-0.2.1.tar.gz.sha256`.

## Remaining compatibility and evidence limits

These are supplied synthetic fixtures, not live evidence. Completion establishes source and selected-file structure/package acceptance only. The helper checks a conservative subset; it does not establish full Splunk configuration/ACL semantics, validate SPL execution, or establish target compatibility.

No deployment target, deployment type (Enterprise or Cloud), or Splunk version is selected. Compatibility of Simple XML 1.1, app.conf keys and metadata behavior therefore remains unqualified. Target role existence and effective app/search permissions are unresolved. No target was contacted, installed into, or changed.

AppInspect and any applicable Cloud private-app vetting were **not run**; no vendor acceptance is claimed. Installation and live acceptance were **not run**. Navigation, browser rendering, the synthetic search result, search time behavior and role enforcement require validation against the exact authorized target. The archive retains the supplied disabled install state.

The supplied inline synthetic search defines the entire current search contract; no production indexes or fields were provided or inferred. The remaining inputs for target qualification are the intended deployment and exact Splunk version, actual reader/editor role definitions and capabilities, and the applicable AppInspect/vetting and runtime acceptance requirements.
