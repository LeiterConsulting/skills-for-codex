# bench_delta 0.2.1 - offline acceptance report

Created the requested native Simple XML app at `output/bench_delta`, its release archive at `output/bench_delta-0.2.1.tar.gz`, and the SHA-256 sidecar `output/bench_delta-0.2.1.tar.gz.sha256`. Source and package checks passed. These are synthetic fixture results, not live evidence. No deployment target was selected or contacted; no installation, publishing, external connection, or schedule change occurred.

## Inputs and provenance

`TASK.md` specifies a new native Simple XML app, output paths, versioned package, digest, and this report. `AGENTS.md` requires offline work, preservation of inputs, and deliverables under `output/`. All app identity, access-role, install-state, dashboard/search, and time values below originate solely in `input/native.json`; example assets provided no defaults. JSON values are shown with JSON escaping. The dashboard round-trip checks compare parsed XML text directly with decoded fixture strings, with no additional unescaping, rewriting, or normalization.

```json
{
  "schema_version": 1,
  "app_id": "bench_delta",
  "app_label": "Delta & Readiness",
  "author": "Synthetic evaluation team",
  "version": "0.2.1",
  "description": "Offline benchmark fixture",
  "install_state": "disabled",
  "read_roles": [
    "bench_reader"
  ],
  "write_roles": [
    "bench_editor"
  ],
  "dashboard": {
    "title": "Delta <Health> \u00c5",
    "query": "| makeresults | eval status=\"A&B<ready>\" | table status",
    "earliest": "-12h",
    "latest": "now"
  }
}
```

Implementation uses the supplied local `candidate/scripts/splunk_app.py`, as directed by `candidate/SKILL.md` and its input, architecture, and validation references. No external starter or dependencies were fetched. The agent selected and reviewed the helper's four generated runtime files for release; the generated release manifest remains in the source app but is excluded from the archive. The helper creates Simple XML version `1.1`, light theme, one table and inline search, a `home` default view, visible app navigation, and app-local `export = none` metadata. The supplied install state remains `disabled`. Role names are referenced in metadata; roles are not created.

Input SHA-256: `35313a2b28a98d43365c1e654fa6e9d590fcf08523da696be485974e5b888249`.

Helper SHA-256: `b747f2a60829b268aafd2cbd4d14a560525cbdb9bf07b97ba045ed28fb74dbda`.

Original input, instruction, and candidate-file hashes were checked against the pre-generation snapshot and passed. Full provenance, exact values, commands, and results are in `checks.json` and `package-result.json`.

## Selected release and actual archive

| Selected source file | Purpose |
| --- | --- |
| `default/app.conf` | Supplied app identity, label, author, version, description, disabled state, and home default view |
| `default/data/ui/nav/default.xml` | Default navigation to home |
| `default/data/ui/views/home.xml` | Native table dashboard with the exact fixture title, query, earliest, and latest |
| `metadata/default.meta` | Exact read/write roles and app-local export |

The real tar archive was opened and inspected, without extraction. It contains the `bench_delta/` directory plus exactly those four regular files under that root. Each archived file matches the corresponding reviewed source byte for byte. No links, traversal, `local/`, credentials, cache/dependency files, release manifest, verifier, or report are included. Selected content was reviewed; this is not a comprehensive secret scan.

Archive size: **708 bytes**. Root mode is `0755`, files are `0644`, owner IDs and timestamps are zero, and gzip timestamp is zero. Deterministic header settings were inspected; no claim of a repeated independent build is made.

SHA-256:

```text
322b37a1178f420d7b6853881a6f50d1984487f80656dfe8523a73292473d8fd  bench_delta-0.2.1.tar.gz
```

## Commands and completed checks

Commands ran from `/workspace`; every listed command returned exit code `0`.

```sh
python3 candidate/scripts/splunk_app.py scaffold --config input/native.json --output output/bench_delta
python3 candidate/scripts/splunk_app.py validate --app output/bench_delta --files output/bench_delta/release-files.json
python3 candidate/scripts/splunk_app.py package --app output/bench_delta --files output/bench_delta/release-files.json --output output/bench_delta-0.2.1.tar.gz
python3 output/verify_release.py
(cd output && sha256sum -c bench_delta-0.2.1.tar.gz.sha256)
```

Scaffold reported five created source files, four release files, and `installed: false`. Validate and package reported app `bench_delta`, version `0.2.1`, four selected files, and `structure: passed`; both explicitly report `appinspect: not_run` and `runtime: not_run`. The verifier also invokes the helper's validation command and reports **52 passing assertions**. Its coverage includes input preservation, exact metadata and disabled state, XML parsing/escaping and exact fixture text/time round-trips, a single table/search, valid home navigation, exact ACL text, archive membership, source/archive byte equality, normalized archive metadata, archive size, and independently computed digest.

The archive digest was independently compared with the helper package result, and the checksum sidecar verification returned `bench_delta-0.2.1.tar.gz: OK`. The helper's complete-config checks and local version/wildcard regex probes passed. Full JSON Schema validation and complete Splunk validation were not performed.

## Evidence limits and unresolved inputs

| Acceptance level | Result and limit |
| --- | --- |
| Source | Reviewed generated config, XML, ACL text, and explicit release list; exact fixture values preserved |
| Build | No frontend/backend compilation applies to this configuration/XML app; no Splunk build or execution performed |
| Structure/package | Passed supplied helper and independent fixture/archive checks; manifest excludes non-runtime deliverables |
| AppInspect | Not run; no vendor report or target-specific Cloud vetting evidence supplied |
| Installed | Not run; no authorized deployment target selected and app remains configured disabled |
| Live | Not run; search execution/results, browser rendering/navigation, runtime permissions, and performance remain unverified |

Deployment environment, Splunk version, Enterprise/Cloud edition, and any Cloud vetting/install requirements remain unknown. Simple XML `1.1`, config settings, and metadata behavior must be qualified against the exact target release before claiming compatibility. Existence of `bench_reader` and `bench_editor`, their capabilities, inherited ACL behavior, and actual permission enforcement are unresolved target inputs. No broadening of the supplied roles occurred.

The helper parses selected XML and limited app identity/navigation structure; it does not enforce every Splunk configuration or ACL rule, validate SPL syntax/data access, run AppInspect, or simulate a running Splunk server. The exact synthetic `makeresults` query and `-12h` to `now` range were preserved but never executed. No real data contract, search result, end-user browser behavior, installed acceptance, Cloud approval, or performance improvement is claimed. No live evidence can be inferred from these fixtures.

## Supporting deliverables

- `bench_delta/`: source app and explicit release manifest.
- `bench_delta-0.2.1.tar.gz` and `.sha256`: release archive and standard checksum sidecar.
- `checks.json`: fixture/provenance, assertions, helper validation, archive inventory/digest, and unresolved evidence.
- `package-result.json`: exact package command, exit code, helper result, and stderr.
- `verify_release.py`: repeatable offline checks of the existing release (does not rebuild, install, or contact a target).
