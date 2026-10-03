# Candidate B: offline package review

**Result: incomplete.** The required `package` check is recorded as `passed`, but its source revision and artifact subject identify candidate A. It does not satisfy candidate B's required package check. The supplied B artifact and A receipt both match their respective declared file hashes; that byte agreement does not transfer A's result to B or establish that B fails a package check.

## Exact bindings

The record declares product `Synthetic release`, version `1.0.0`, target `Synthetic staging Y`, source revision `synthetic-revision-b`, working tree `clean`, and source snapshot SHA-256 `null`. These metadata are caller-reported; no source checkout or build provenance was supplied.

| Binding | Candidate B / current artifact | Required package check / A receipt | Assessment |
| --- | --- | --- | --- |
| Source revision | `synthetic-revision-b` | `synthetic-revision-a` | Mismatch; A's source result cannot be credited to B. |
| Artifact identity | `candidate`, path `candidate.bin` under `input/` | Subject `artifact_id: candidate` | ID agrees, but does not establish byte identity. |
| Artifact SHA-256 | `5c46fd477af2c47c3c554b7ab426e385a9d21e5a267af11b79ee8891b9d46771` (declared and observed) | `369e3ebd85eccd4776a1e4930f0bd9be8303198a2c3c06b46d7c2fb576166750` (recorded A subject) | Mismatch; the check exercised a different recorded artifact. A's artifact was not supplied for rehashing. |
| Source snapshot SHA-256 | `null` | `null` | Agrees. The supplied contract permits a null snapshot for a declared clean source revision; this does not verify that claim. |
| Target | `Synthetic staging Y` | `null` | No helper gap: package-tier checks may be target-independent. The receipt establishes no target-specific compatibility. |
| Check policy/status | One required check | `id: package`, `tier: package`, `required: true`, `status: passed` | The recorded status is retained, but its bindings leave B's required gate unsatisfied. |

The selected evidence is `input/receipt.txt`, SHA-256 `e64b437739414bf24a3b793eddf127f40ff9e1121f6f7e227172e134c9b10257` (declared and observed). Its entire textual statement is:

> Synthetic package check for candidate A; not a vendor report.

The record's check details also state `Reported package check applies to A.` The receipt is 62 bytes, including its final newline. It is synthetic evidence about A, with no verifier identity, acceptance criteria, command, or detailed findings. Candidate B's 36-byte fixture reads `Synthetic candidate B changed bytes` followed by a newline; it is not a supplied archive or real package whose membership can be assessed.

## Verification and gaps

Ran the supplied helper without an output option or any receipt execution:

```text
python3 candidate/scripts/release_record.py --record input/record.json --root input
```

It returned exit code **1** (incomplete evidence, not malformed input), `record_review: incomplete`, `required_check_count: 1`, and exactly these gaps:

- `check package: source revision binding mismatch`
- `check package: artifact subject digest mismatch`

Independent SHA-256 hashing agreed with the helper for B and the receipt. The reviewed `input/record.json` has SHA-256 `2572ba69e21ce1e7d15b31f5b4aaabd13eb46a7cb6398d3b1f0558d61d93233f`. All three input files were left unchanged. Updating B's declared digest alone cannot repair the stale check; editing A's subjects or source revision would not create evidence of a check on B.

## Relevant next checks and unresolved inputs

1. Resolve the project's actual offline package acceptance criteria and maintained verifier/command. None is supplied here. Obtain a fresh result on B's exact bytes, identifying whether the verifier exercised the package, extracted payload, or source. If B changes again, reassess which evidence remains applicable.
2. Bind that result to `synthetic-revision-b` and artifact `candidate` with SHA-256 `5c46fd477af2c47c3c554b7ab426e385a9d21e5a267af11b79ee8891b9d46771`. Retain A's receipt as historical evidence. A new review record should reference the actual B receipt and its observed digest; do not relabel A's pass or alter the supplied input record.
3. For an actual package, inspect identity/version, membership, and unintended private or runtime configuration files using the project's verifier. Resolve how the package is linked to the claimed source state and builder; verify signed provenance only if the product's trust policy requires it. The fixture cannot establish those properties.
4. Resolve whether the package criterion is target-independent. If it depends on staging Y, identify the exact relevant platform/version and bind the exercised target accordingly. Broader vendor, installed, live, physical, multiplayer, or soak gates require established release criteria before being added; they are outside this offline package assessment.

## Evidence limits

These are synthetic local fixtures, not live evidence. File hashes establish byte agreement only. The helper checks record consistency and selected hashes; it does not independently verify check execution, report authenticity, the source checkout/clean state, builder provenance, product/version, target environment, acceptance-policy adequacy, behavior, or release authorization. Even a future `consistent` result would not itself be a readiness certificate. No target connection, publication, installation, game launch, or schedule change was performed.
