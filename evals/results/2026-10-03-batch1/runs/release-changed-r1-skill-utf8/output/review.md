# Offline package review: candidate B

Candidate B is **not qualified by the supplied evidence** for the required package gate. Its local artifact hash agrees with the record, but the sole recorded package pass applies to candidate A. The evidence record is incomplete; this is a binding failure, not an observed failure from executing B's package verifier.

## Scope and exact bindings

This review uses only the synthetic fixtures in `input/`. It assesses offline package evidence and does not establish target compatibility or authorize release actions.

| Field | Candidate B declaration | Required `package` check declaration |
| --- | --- | --- |
| Product/version | `Synthetic release` / `1.0.0` | No separate product/version fields; receipt names A |
| Source revision | `synthetic-revision-b` | `synthetic-revision-a` — mismatch |
| Working state | `clean` (caller-reported) | No working-state field |
| Source snapshot SHA-256 | `null` | `null` — agrees; permitted for a declared clean source revision |
| Target | `Synthetic staging Y` (caller-reported) | `null` — permitted for a target-independent package check; no evidence of exercising Y |
| Artifact identity/path | ID `candidate`, record-relative `candidate.bin`, resolved as `input/candidate.bin` | Subject ID `candidate`; identical logical ID does not establish identical bytes |
| Artifact SHA-256 | `5c46fd477af2c47c3c554b7ab426e385a9d21e5a267af11b79ee8891b9d46771` | `369e3ebd85eccd4776a1e4930f0bd9be8303198a2c3c06b46d7c2fb576166750` — mismatch |
| Gate/status | One required gate | ID `package`, tier `package`, `required: true`, `status: passed` (reported for A) |

The check details say `Reported package check applies to A.` Its selected evidence is record-relative `receipt.txt`, resolved as `input/receipt.txt`, with declared SHA-256 `e64b437739414bf24a3b793eddf127f40ff9e1121f6f7e227172e134c9b10257`. The entire receipt reads:

> Synthetic package check for candidate A; not a vendor report.

## Checks actually performed

Read `AGENTS.md`, `TASK.md`, `candidate/SKILL.md`, the skill's evidence-record contract and relevant package guidance, the supplied helper, and the input record and receipt. Inspected the synthetic candidate bytes and computed SHA-256 directly from the local files:

| File | Bytes | Observed SHA-256 | Comparison |
| --- | ---: | --- | --- |
| `input/candidate.bin` | 36 | `5c46fd477af2c47c3c554b7ab426e385a9d21e5a267af11b79ee8891b9d46771` | Matches B's declared artifact hash |
| `input/receipt.txt` | 62 | `e64b437739414bf24a3b793eddf127f40ff9e1121f6f7e227172e134c9b10257` | Matches declared evidence hash; content concerns A |
| `input/record.json` | 1066 | `2572ba69e21ce1e7d15b31f5b4aaabd13eb46a7cb6398d3b1f0558d61d93233f` | Review input fingerprint; no expected record hash supplied |

Ran the supplied read-only consistency helper:

```text
python -B candidate/scripts/release_record.py --record input/record.json --root input
```

It returned exit code **1**, `record_review: incomplete`, and `required_check_count: 1`, with exactly these gaps:

```text
check package: source revision binding mismatch
check package: artifact subject digest mismatch
```

No package verifier, build, source checkout verification, vendor validation or behavioral test was performed. The helper verifies declared bindings and selected local hashes; it does not execute checks or authenticate their reports. Receipt text was read as evidence and was not executed. Input files were preserved.

## Required gap and evidence limits

B needs applicable package evidence bound to its exact artifact and source state. Updating the artifact's declared digest did not update what the old check exercised. Both the source revision and artifact bytes differ from A; no documented relevance argument supports carrying A's result forward. The old `passed` status remains an A claim and cannot close B's required gate. A's artifact and source checkout are absent, so a payload/source comparison or narrowed carry-forward justification cannot be evaluated here.

The matching receipt hash establishes byte agreement with the declared receipt, not the receipt's authenticity, check criteria, verifier behavior or applicability to B. The receipt contains no substantive results, command or acceptance thresholds. The `clean` working state, revision, product/version and target identity are declarations; no checkout, build provenance, actual target/version or package metadata is independently verified. A null snapshot is allowed under this record contract for the declared clean state, but does not prove that state.

These are synthetic fixtures, not live evidence. There is no basis to claim vendor acceptance, installation, live behavior or compatibility with `Synthetic staging Y`. Only the package gate is declared required; other tiers are not added as requirements for this offline task. No target connection, installation, publishing, game launch, receipt execution or schedule change occurred.

## Relevant next checks

1. Obtain the maintained package-verifier command and established package acceptance criteria, plus the source/build information needed to establish that B's bytes came from `synthetic-revision-b`. Verify the declared clean state; if the source is modified or unknown, bind an appropriate source snapshot. These inputs are not supplied here.
2. Run the relevant package check on the exact B package with SHA-256 `5c46fd477af2c47c3c554b7ab426e385a9d21e5a267af11b79ee8891b9d46771`. Identify whether the check exercises the package, extracted payload or source, inspect its semantic results against the criteria, and review applicable package identity/content and provenance using maintained project tooling. Do not infer a pass from a process exit or receipt presence alone.
3. Preserve A's receipt and the original record. Produce a new B-specific receipt and evidence record with B's source binding, artifact subject digest, check command/criteria/results and receipt hash. Keep a null check target only for a justified target-independent package check; any target-specific claim must name and establish the exercised environment. Re-run the consistency helper and review the new report's meaning before closing B's package gate. Relabeling A's receipt or changing only its subject/source fields would not supply a new check.

Until applicable B evidence is available and reviewed, the required offline package gate remains open. No broader release decision can be established from these fixtures.
