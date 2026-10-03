# Evidence record and inputs

Resolve these values from user requirements, observed project metadata or stated agent choices. Keep their origins in the local task record. Paths, product identity, target, thresholds, tool commands and acceptance policy belong to the consumer, not this collection's maintainer.

The optional helper checks a JSON record and selected local files using Python 3.10+ standard library. It performs no network access, command execution, installation, signing or archive extraction. Invoke it with explicit paths:

```text
python skills/release-qualification/scripts/release_record.py --record work/release-record.json --root work/evidence --output work/review.json
```

`--root` contains the artifact and evidence files selected in the record. `--output` is optional: results always go to stdout; a chosen output must be new. Records/reports may contain private target context; review them before public distribution. The helper does not publish or copy the selected file contents.

## Contract

Every object accepts exactly the listed fields. Identifiers use letters, digits, underscores or hyphens, beginning with a letter; paths are portable, canonical relative POSIX paths. Digests are 64 hexadecimal characters. Repeated JSON keys, duplicate IDs, ambiguous paths, links and Windows reparse points are rejected.

| Object | Fields |
| --- | --- |
| Top level | `schema_version` (1), `candidate`, `artifacts`, `checks` |
| candidate | `product`, `version`, `target` (nonempty text), `source_revision` (text or null), `working_tree` (`clean`, `modified`, `unknown`), `source_snapshot_sha256` (digest or null) |
| artifacts[] | `id`, `path`, `sha256` |
| checks[] | `id`, `tier`, `required` (boolean), `status`, `target` (exercised environment text or null), `source_revision` (text or null), `source_snapshot_sha256` (digest or null), `subjects`, `evidence`, `details` (nonempty text) |
| subjects[] | `artifact_id`, `sha256` of the artifact that was actually exercised |
| evidence[] | `path`, `sha256` of a selected report/receipt/log |

Tiers: `source`, `build`, `package`, `vendor`, `installed`, `live`, `physical`, `multiplayer`, `soak`. Statuses: `passed`, `failed`, `not_run`, `running`, `needs_review`, `not_applicable`. Artifact and check lists must be nonempty. Limits: 1 MiB record, 64 artifacts, 128 checks, 256 distinct selected files, 2 GiB per selected file and 4 GiB total hashed bytes.

Use [release-record.template.json](../assets/release-record.template.json) as a shape, replacing nulls and example values. It is deliberately unresolved and cannot establish qualification. Add only the gates appropriate to the requested release purpose. Record external reports locally only when permitted; retain their original reference in `details`. Credentials belong outside these records.

## Meaning of a review

For a required pass, the helper requires a matching source revision/snapshot, at least one evidence file and matching artifact subjects for tiers other than `source`. A clean source revision may have a null snapshot; modified/unknown working state needs a snapshot digest to bind the reported source state. The snapshot binding is declared, not recomputed from a checkout. A source-tier check can have no artifact subjects.

Recorded passes for vendor/installed/live/physical/multiplayer/soak checks need an exercised `target` matching the candidate. Source/build/package checks may use null for target-independent checks; if a target is supplied, it must match. Targets are caller-reported identities, not independently discovered environments. Describe exact versions, fixtures and relevant platform details; a matching string alone cannot establish compatibility.

Selected artifact/evidence files must match their declared digests, including optional check evidence. Required checks that are not `passed` remain gaps. A `not_applicable` check belongs outside the required set with the applicability reason in `details`; the agent/user must justify that choice. An empty required set is a gap. Check summaries include optional statuses and details so failures remain visible.

Changing an artifact and updating only its declared digest leaves older check subjects mismatched. For recorded passes, source/check bindings must agree. This prevents accidental reuse of a stale recorded pass; it cannot prevent a caller from supplying a false claim or changing the criteria.

The output `record_review` is `consistent` or `incomplete`. It means only that the supplied record, bindings and local hashes agree under these rules. `consistent` is not a readiness certificate, source attestation, behavioral pass or approval. Inspect the actual checks and target policy before a release decision.

Exit codes: 0 for a consistent record, 1 for incomplete evidence, 2 for malformed input, unsupported paths or I/O errors. A missing selected file is an evidence gap. An output path is never overwritten. No check command embedded in `details` is executed.
