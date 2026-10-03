# Candidate B — offline package review

**Decision: incomplete. Candidate B has not satisfied the required package gate.** The recorded `passed` result applies to candidate A. Both its source revision and artifact subject digest differ from B. This is an evidence binding failure, not an observed package-verifier failure on B.

## Exact bindings

The reviewed `input/record.json` has SHA-256 `2572ba69e21ce1e7d15b31f5b4aaabd13eb46a7cb6398d3b1f0558d61d93233f`.

| Field | Candidate B | Recorded package check for A |
| --- | --- | --- |
| Product / version | `Synthetic release` / `1.0.0` | No separate identity/version in the receipt |
| Source revision | `synthetic-revision-b` | `synthetic-revision-a` |
| Working state / snapshot | Declared `clean` / `null` | Snapshot `null`; no separate working-state declaration |
| Target | `Synthetic staging Y` | `null` |
| Artifact identity | `candidate`, path `input/candidate.bin` | Subject `artifact_id: candidate`, with A's digest |
| Gate | Required package evidence for B | `id: package`, `tier: package`, `required: true`, `status: passed` |

SHA-256 bindings:

- B artifact, declared and locally observed: `5c46fd477af2c47c3c554b7ab426e385a9d21e5a267af11b79ee8891b9d46771`.
- A artifact subject, recorded only: `369e3ebd85eccd4776a1e4930f0bd9be8303198a2c3c06b46d7c2fb576166750`. A's artifact is not supplied, so its bytes and digest were not independently verified.
- `input/receipt.txt`, declared and locally observed: `e64b437739414bf24a3b793eddf127f40ff9e1121f6f7e227172e134c9b10257`.

The 36-byte B artifact contains `Synthetic candidate B changed bytes` followed by a newline. The 62-byte receipt says: “Synthetic package check for candidate A; not a vendor report.” Check details likewise state: `Reported package check applies to A.` Matching the receipt's hash establishes byte agreement, not a pass for B or report authenticity.

## Checks performed and gaps

Read the record, artifact bytes, receipt, workspace instructions and skill references. Independently computed local SHA-256 values and ran the supplied helper:

```text
python3 candidate/scripts/release_record.py --record input/record.json --root input
```

The helper exited **1**, returned `record_review: incomplete`, and found one required check with exactly these gaps:

- `check package: source revision binding mismatch`
- `check package: artifact subject digest mismatch`

There are no selected-file digest mismatches. The shared artifact ID does not overcome the differing digests. Both snapshots being null does not overcome the differing revisions. A null target is permitted for a target-independent package check; it is not an additional mechanical gap, and supplies no staging compatibility evidence.

No documented relevance argument supports carrying A's pass forward to B. No package behavior was exercised on B during this review. The helper validates declarations and hashes; it does not execute a package verifier or interpret check behavior.

## Relevant next checks and evidence limits

1. Obtain the project's maintained package-verifier command and acceptance criteria, plus B's source/build provenance. Confirm the declared revision and clean working state; if modified or unknown, bind a source snapshot. No checkout, build metadata or maintained package verifier is supplied.
2. Run the required offline package check on B's exact digest and inspect its semantic results, including applicable package identity, membership and unintended-content checks. Preserve a new report with explicit B source and artifact bindings, distinguishing package checks from extracted-payload or source checks. Rehash the tested artifact to confirm that the report covers the reviewed bytes.
3. In a separate new evidence record, retain A's historical evidence and record B's actual result and report hash. Do not relabel A's receipt or merely replace its subject/source fields. Reassess affected gates if B changes again, then review the new bindings and report meaning.

All inputs are synthetic fixtures, not live evidence. Source identity, working state, target and reported passes remain caller claims. Target platform/version, package acceptance policy and report authenticity are unresolved. No vendor, installed or live qualification is established; these tiers are not additional required gates for this offline task. Inputs were preserved; receipt text was not executed. No installation, target contact, publishing or schedule changes occurred.
