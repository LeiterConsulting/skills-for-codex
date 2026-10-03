# Delta app release report

Created `output/bench_delta` and `output/bench_delta-0.2.1.tar.gz` from `input/native.json` using the unmodified supplied helper. This is offline work with synthetic fixtures; it provides source and structure/package evidence only.

## Supplied values preserved

| Field | Exact decoded value |
| --- | --- |
| App ID | `bench_delta` |
| App label | `Delta & Readiness` |
| Author | `Synthetic evaluation team` |
| Version | `0.2.1` |
| Description | `Offline benchmark fixture` |
| Install state | `disabled` |
| Read roles | `bench_reader` |
| Write roles | `bench_editor` |
| Panel title | `Delta <Health> Å` |
| Earliest | `-12h` |
| Latest | `now` |

The inline search is exactly:

```spl
| makeresults | eval status="A&B<ready>" | table status
```

JSON-decoded strings were compared directly with parsed XML text. The title contains `Å` (U+00C5). The query contains ordinary double quotes (U+0022). Neither string contains a literal backslash (U+005C). XML entities preserve the supplied ampersands and angle brackets as text; the parsed label, title, query and both time bounds equal the input. Code point receipts record the actual characters.

## Release selection and completed checks

The selected release comprises:

- `default/app.conf`
- `default/data/ui/nav/default.xml`
- `default/data/ui/views/home.xml`
- `metadata/default.meta`

`release-files.json` remains in the app scaffold as the explicit release selection. It is excluded from the archive, as are this report, digest, verification script and receipts. The archive has one `bench_delta/` root directory and exactly four regular files.

- Passed the supplied helper's config contract during scaffold creation. No separate JSON Schema validation is claimed.
- Passed the helper's selected-file/path checks, app identity/version checks, XML parsing and navigation/default-view checks; all three helper commands exited 0.
- Passed independent comparisons for all supplied app metadata, disabled installation state, exact role ACLs (`export = none`), Simple XML layout and home navigation.
- Passed direct Unicode equality assertions for all dashboard text and time bounds, including code point checks for the title and search quotes.
- Reviewed all four selected UTF-8 files: they contain only app metadata, navigation, the fixture dashboard and ACLs. No local configuration, credentials, dependencies or unrelated workspace content is selected.
- Passed archive membership, file type, normalized owner/mode/time checks and byte-for-byte comparisons of every packaged file with its selected source.
- Passed digest/size comparisons against the package receipt and digest sidecar. Confirmed input and helper hashes are unchanged from the creation record.

`output/build-receipt.json` retains the helper commands, exit codes and results. `output/verification-receipt.json` retains 28 passed assertions, parsed values, code points, file hashes and archive membership. Re-run the independent checks with `python3 output/verify_release.py` from the workspace.

Archive size: **708 bytes**. SHA-256:

```text
322b37a1178f420d7b6853881a6f50d1984487f80656dfe8523a73292473d8fd  bench_delta-0.2.1.tar.gz
```

Digest sidecar: `output/bench_delta-0.2.1.tar.gz.sha256`.

Input SHA-256: `35313a2b28a98d43365c1e654fa6e9d590fcf08523da696be485974e5b888249`. Helper SHA-256: `b747f2a60829b268aafd2cbd4d14a560525cbdb9bf07b97ba045ed28fb74dbda`. The helper has no separate source revision supplied; its hash identifies the resource used.

## Remaining compatibility and evidence limits

No deployment target is selected. Splunk product, exact version, target platform and applicable AppInspect/vetting requirements remain unresolved. Compatibility of Simple XML 1.1 and the configuration with a particular Splunk release is unverified. The supplied role names are preserved, but their existence and effective access on any target are unverified.

AppInspect was not run. The package was not installed, and no live search, navigation, browser or permission checks ran. The inline SPL and relative time bounds were preserved as inert text, not executed or semantically validated against Splunk. Structural validation does not establish full Splunk configuration or ACL semantics, successful search results, installation acceptance or live behavior. These synthetic fixtures are not live evidence.

No authoring input needed for this offline deliverable remains unresolved. Target-specific compatibility and runtime evidence require a later authorized workflow; no connection, publication, installation, game launch or schedule change was performed.
