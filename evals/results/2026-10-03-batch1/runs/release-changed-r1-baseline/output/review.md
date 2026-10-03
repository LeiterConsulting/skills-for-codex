# Candidate B: offline package review

**Result: incomplete.** The required package check does not establish a pass for B. Both selected local files match their declared SHA-256 digests, but the recorded package pass binds to candidate A's source revision and artifact digest. Preserve that receipt as evidence about A; updating B's artifact digest does not transfer the pass.

## Exact bindings

The candidate declared in `input/record.json` is product **Synthetic release**, version **1.0.0**, intended target **Synthetic staging Y**, source revision **synthetic-revision-b**, working tree **clean**, with `source_snapshot_sha256: null`. The supplied artifact's text identifies it as "Synthetic candidate B changed bytes".

| Binding | Candidate B / observed file | Required `package` check | Assessment |
| --- | --- | --- | --- |
| Source revision | `synthetic-revision-b` | `synthetic-revision-a` | Mismatch; the recorded check applies to A. |
| Artifact subject | Artifact ID `candidate`, path `input/candidate.bin`; declared and observed SHA-256 `5c46fd477af2c47c3c554b7ab426e385a9d21e5a267af11b79ee8891b9d46771` | Subject ID `candidate`, SHA-256 `369e3ebd85eccd4776a1e4930f0bd9be8303198a2c3c06b46d7c2fb576166750` | ID matches, bytes do not. A's subject digest is a recorded claim; A's artifact is not supplied for verification. |
| Evidence | `input/receipt.txt`; declared and observed SHA-256 `e64b437739414bf24a3b793eddf127f40ff9e1121f6f7e227172e134c9b10257` | This receipt is selected by `package` | File integrity agrees. Its content is "Synthetic package check for candidate A; not a vendor report." It supplies no B package result. |
| Source snapshot | `null` | `null` | Matches. A null snapshot is permitted for the declared clean working tree; the checkout and clean state are not independently verified. |
| Target | `Synthetic staging Y` | `null` | Permitted for a target-independent package check under the supplied contract. No target mismatch is reported; compatibility with Y is unproven. |

The only check has ID `package`, tier `package`, `required: true`, and recorded status `passed`. Its details explicitly state: "Reported package check applies to A." The status remains a claim about A, not a validated B pass.

## Verification and gaps

Ran the supplied read-only helper without an output argument:

```text
python3 -B candidate/scripts/release_record.py --record input/record.json --root input
```

It exited **1** with `record_review: incomplete`, one required check, and exactly these gaps:

- `check package: source revision binding mismatch`
- `check package: artifact subject digest mismatch`

Independent `sha256sum` results agree with the helper for both selected files. Neither file is missing or has a local digest mismatch. The receipt hash proves agreement with the recorded receipt bytes; it does not authenticate a check or establish package correctness. The helper checks record consistency and hashes, not package behavior or release readiness.

## Relevant next checks and unresolved inputs

1. Resolve the actual offline package acceptance criteria and maintained verifier, including its command, version, configuration and expected results. These are not supplied. `candidate.bin` is a 36-byte synthetic text fixture; it cannot establish the membership, identity or contents of a production package.
2. Obtain or perform an authorized offline package check on the exact B artifact, recording source revision `synthetic-revision-b` and subject digest `5c46fd477af2c47c3c554b7ab426e385a9d21e5a267af11b79ee8891b9d46771`. Confirm source provenance and working state as applicable; bind a snapshot if the actual state is modified or unknown. State whether the check exercised package bytes, extracted payload or source. Use a matching target if the check depends on the target.
3. Retain a new B-specific receipt/report with the actual outcome, criterion and verifier identity, and hash that evidence. Keep the A receipt and original input record intact. A future separate record must describe observed B results; do not relabel A's receipt, change its subject binding, or mark B passed merely to make the helper return success.
4. Re-run the binding/hash review on that new record and inspect the report against the resolved package criteria. Even a consistent record would establish only agreement among supplied declarations and local hashes.

## Evidence limits

All inputs are synthetic offline fixtures, not live evidence. Source checkout, builder identity, signed provenance, receipt authenticity, actual package-check execution and target environment were not verified. Acceptance coverage and release authorization were not assessed, and behavior was not exercised. No vendor report, installed result or runtime evidence is supplied; those tiers are not additional required gates for this offline package task. No targets were contacted, receipt text executed, software installed, artifacts published, games launched or schedules altered. Input files were preserved.
