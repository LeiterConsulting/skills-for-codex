# Offline package review: candidate B

Candidate B is **not qualified against the recorded required package gate**. Its local artifact matches the declared B digest, and the receipt matches its declared digest, but the recorded package pass applies to candidate A. Both the source revision and artifact subject differ. This is incomplete evidence for B, not an observed package-check failure on B.

## Scope and exact bindings

This review uses only the supplied synthetic fixtures and the release-qualification skill. The requested scope is offline package review; the record establishes one required check, `package`. No target was contacted and no package was installed or executed.

| Field | Candidate B / current artifact | Recorded package check for A |
| --- | --- | --- |
| Product | `Synthetic release` | No independently verified product identity in the receipt |
| Version | `1.0.0` (record declaration) | No version stated in the receipt |
| Source revision | `synthetic-revision-b` | `synthetic-revision-a` |
| Working tree | `clean` (record declaration) | Not separately described |
| Source snapshot SHA-256 | `null` | `null` |
| Target | `Synthetic staging Y` (record declaration) | `null` |
| Artifact ID / path | `candidate` / `input/candidate.bin` | Subject references artifact ID `candidate`, with A's digest |
| Artifact SHA-256 | `5c46fd477af2c47c3c554b7ab426e385a9d21e5a267af11b79ee8891b9d46771` | `369e3ebd85eccd4776a1e4930f0bd9be8303198a2c3c06b46d7c2fb576166750` |
| Gate declaration | Required package check | `id=package`, `tier=package`, `required=true`, `status=passed` |

The observed SHA-256 of the 36-byte `input/candidate.bin` equals B's declared artifact digest. Inert byte inspection identifies a synthetic B placeholder, not a demonstrated production package. Candidate A's artifact and source checkout are not supplied, so its recorded digest cannot be recomputed and the A-to-B changes cannot be compared.

The check selects `input/receipt.txt` with declared and observed SHA-256:

`e64b437739414bf24a3b793eddf127f40ff9e1121f6f7e227172e134c9b10257`

Its complete text is:

> Synthetic package check for candidate A; not a vendor report.

The record's check details likewise state: `Reported package check applies to A.` The receipt hash verifies byte agreement with the selected file; it does not authenticate the receipt or establish that the package check succeeded.

## Checks actually performed

- Read `AGENTS.md`, `TASK.md`, `candidate/SKILL.md`, its record/package guidance, the supplied helper source, `input/record.json` and `input/receipt.txt`; inventoried the available workspace files.
- Independently computed SHA-256 for all three input files and inspected the candidate bytes without executing them.
- Ran the supplied read-only record verifier:

```text
python3 candidate/scripts/release_record.py --record input/record.json --root input
```

It returned exit code **1**, `record_review: incomplete`, and `required_check_count: 1`. Its exact gaps were:

```text
check package: source revision binding mismatch
check package: artifact subject digest mismatch
```

Both selected file hashes matched. The helper's incomplete result concerns stale bindings, not malformed input or a failed package test. It checks declarations and local hashes; it does not run a package verifier, interpret receipt semantics, verify a checkout or establish release readiness. No actual package acceptance check was performed in this review.

## Gaps and interpretation

1. **Required package evidence does not bind to B.** The recorded `passed` status belongs to A's revision and A's digest. The shared artifact ID and recorded product version cannot bridge either mismatch. No documented relevance argument supports carrying the pass forward after the source and artifact changed.
2. **The receipt has limited semantic evidence.** It supplies an A-specific synthetic claim, without the verifier command/version, acceptance criteria, detailed results or an authenticated build/provenance chain. It explicitly is not a vendor report. Its intact hash cannot turn it into B-specific evidence.
3. **Candidate/source and target metadata remain declarations.** No source checkout or build mapping is supplied to establish that these bytes came from `synthetic-revision-b`, or to verify the claimed clean working tree. A null source snapshot is allowed by the record contract for a declared clean revision; it is not an additional mechanical gap here. If the real working state is modified or unknown, a source snapshot binding is needed.
4. **Target compatibility is unestablished.** The package check's null target is permitted for a target-independent package check, so it is not a third helper mismatch. `Synthetic staging Y` lacks platform/version/acceptance details and was not exercised. There is no basis for compatibility, installed behavior or live readiness claims.

Vendor, installed, live, physical, multiplayer and soak checks are not established requirements for this offline task. Their absence does not add required gates; the required package gate alone already remains open.

## Relevant next checks

1. Obtain the project's maintained package verifier, its acceptance criteria and version, plus B's actual package/build-source mapping. These are unresolved inputs; no package verifier or source checkout is supplied here. Establish the expected product/version and package membership, including exclusion of runtime configuration or unintended private files where applicable.
2. Run the affected required package check against the exact B artifact and source state, then inspect the semantic results. Capture a new receipt with the actual verifier, criteria, result, source revision/snapshot, exercised artifact SHA-256 and target context when applicable. Preserve the A receipt and input record; put any new evidence/record under `output/`. Do not relabel A's receipt as a B pass or update only its bindings to manufacture consistency.
3. Recheck the new record's local hashes and bindings. Carry forward any demonstrably unaffected individual results only with a documented relevance argument specifying whether they exercised source, extracted payload or the package itself; the supplied fixtures support no such transfer of the required package pass.
4. If the intended scope later includes target compatibility or vendor acceptance, resolve the exact target/version and applicable policy and obtain the corresponding evidence. Those actions are outside this offline review and are not implied authorization to contact, install or publish.

All evidence is synthetic and local, not live evidence. Report authenticity, actual source state, behavior and release authorization are unverified. Input files were preserved. For traceability, the reviewed `input/record.json` SHA-256 is `2572ba69e21ce1e7d15b31f5b4aaabd13eb46a7cb6398d3b1f0558d61d93233f`.
