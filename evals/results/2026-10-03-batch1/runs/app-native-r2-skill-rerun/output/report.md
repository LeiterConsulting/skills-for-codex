# bench_delta 0.2.1 offline delivery

Created the new native Classic Simple XML app at `output/bench_delta`, plus `output/bench_delta-0.2.1.tar.gz` and `output/bench_delta-0.2.1.tar.gz.sha256`. The selected release structure and all 21 independent verification checks passed. All supplied instructions, input fixtures and candidate resources remain unchanged. These synthetic fixtures are not live evidence.

## Inputs and origins

`TASK.md` specifies a new native app, the output paths and offline qualification. All app values below come directly from `input/native.json`; none were inferred from example assets.

| Input | Exact selected value |
| --- | --- |
| Config schema version | `1` |
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

Exact search, preserved as inert XML text:

```spl
| makeresults | eval status="A&B<ready>" | table status
```

The data contract is a synthetic `makeresults` search with one `status` field; no real indexes or event fixtures are supplied. The parsed title ends in the Unicode character Å, and the search contains ordinary double quotes. XML entity encoding of `&`, `<` and `>` changes serialization only; the parsed title and search match the JSON strings exactly.

The execution workspace is `/workspace`, as required by the workspace shell. Deployment is unselected per `TASK.md`; Splunk edition, version and target role definitions are unresolved. They are qualification gaps, not substituted defaults.

The implementation uses the bundled `candidate/scripts/splunk_app.py` helper under `candidate/SKILL.md`, with no external starter or dependencies. Recorded agent selections from that scaffold are a Simple XML 1.1 light dashboard, one table, the `home` default view, visible UI, and app-local metadata with `export = none`. The supplied disabled install state and role lists are retained exactly. External template source, revision and reuse terms are not applicable; no external starter was fetched.

## Selected release and actual archive

The reviewed explicit manifest is `output/bench_delta/release-files.json`. It selects only:

- `default/app.conf` - supplied identity, version, author, description, disabled state and default view.
- `default/data/ui/nav/default.xml` - default navigation to `home`.
- `default/data/ui/views/home.xml` - native table, supplied label/title/search/time range.
- `metadata/default.meta` - exact supplied read/write roles and `export = none`.

The real archive was opened and its member bytes compared to these source files. Actual members are:

```text
bench_delta/
bench_delta/default/app.conf
bench_delta/default/data/ui/nav/default.xml
bench_delta/default/data/ui/views/home.xml
bench_delta/metadata/default.meta
```

There are no links, special members, extra app roots, `local/`, credentials, dependencies, caches, release manifest or report files in the archive. Selected contents were inspected and contain only the supplied synthetic configuration; this review is not a general secret-scanner result. Archive directories use mode 0755, files use 0644, and owner IDs and timestamps are zero. Gzip also has a zero timestamp.

Archive size: **708 bytes**.

SHA-256:

```text
322b37a1178f420d7b6853881a6f50d1984487f80656dfe8523a73292473d8fd
```

The digest was independently recomputed from the archive bytes and matched the helper result. The `.sha256` sidecar uses the archive basename and standard `sha256sum` format.

## Commands and results

Commands were run from `/workspace` using only the supplied workspace shell and offline standard-library tools. All commands below completed successfully:

```sh
python3 candidate/scripts/splunk_app.py scaffold --config input/native.json --output output/bench_delta
python3 candidate/scripts/splunk_app.py validate --app output/bench_delta --files output/bench_delta/release-files.json
python3 candidate/scripts/splunk_app.py package --app output/bench_delta --files output/bench_delta/release-files.json --output output/bench_delta-0.2.1.tar.gz
python3 output/verify_release.py
(cd output && sha256sum -c bench_delta-0.2.1.tar.gz.sha256)
```

Scaffold and package creation deliberately refuse existing destinations; do not rerun those commands over this delivery. Validation, verification and digest checking can be repeated.

| Evidence level | Result and scope |
| --- | --- |
| Source/config | Passed helper config contract at scaffold creation; inspected all four runtime files; independent checks compare exact app identity, state, metadata roles, title, search and time bounds against `input/native.json`. |
| Build | Not applicable to this configuration/XML app; no compiled frontend or backend. Python helper execution succeeded. |
| Structure | Passed helper checks for release selection, regular paths, app ID/version consistency, XML parsing, default view presence and navigation references. |
| Package | Passed: real archive membership, member types, permissions/timestamps, source-byte equality, size and SHA-256 inspected independently. |
| Preservation | Passed SHA-256 comparison for all input and candidate files plus `AGENTS.md` and `TASK.md`; no added files in input/candidate trees. All new deliverables are under `output/`. |
| AppInspect | Not run; no supplied vendor report or offline AppInspect tooling/evidence. |
| Installed | Not run; no deployment target selected and installation is outside the task. |
| Live | Not run; no Splunk search, browser, navigation or role/permission testing. |

Evidence is retained in `scaffold-result.json`, `validate-result.json`, `package-result.json`, `verification-result.json` and `source-hashes.json` beside this report. `verify_release.py` is the repeatable offline verification script. Provenance hashes:

- `input/native.json`: `35313a2b28a98d43365c1e654fa6e9d590fcf08523da696be485974e5b888249`
- `candidate/scripts/splunk_app.py`: `b747f2a60829b268aafd2cbd4d14a560525cbdb9bf07b97ba045ed28fb74dbda`

## Remaining compatibility and evidence limits

- Target edition/version and deployment remain unknown. Simple XML 1.1, app.conf behavior and target-specific Enterprise or Cloud requirements need qualification against the chosen release before installation.
- The helper and independent assertions cover selected file structure and exact fixture preservation. They do not implement the full Splunk config/XML validator, AppInspect, Cloud vetting or live runtime acceptance.
- The search was preserved, not executed or validated by a Splunk SPL parser. Actual search results, search privileges and behavior of the time bounds have no live evidence.
- `bench_reader` and `bench_editor` are supplied synthetic role names. Their existence, inherited capabilities and effective access on a target are unresolved; ACL behavior was not exercised.
- No installation, enablement, network connection, publication or schedule change was performed. The app remains configured as disabled. No performance or operational-readiness claim is supported by these fixtures.
