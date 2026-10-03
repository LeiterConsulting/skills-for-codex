# Offline package review — candidate B

**Decision: incomplete evidence for B.** The required `package` check is recorded as `passed`, but its source revision and artifact subject belong to A. Neither binding matches candidate B. This does not demonstrate that B failed a package check; no package result for B is supplied. A's recorded pass cannot qualify B.

This review uses only the supplied synthetic fixtures. It establishes local byte agreement and record consistency limits, not live evidence, package correctness or release authorization.

## Exact bindings and observations

Paths in `input/record.json` resolve relative to `input/`.

| Binding | Candidate B / current artifact | Recorded required package check |
| --- | --- | --- |
| Product / version | `Synthetic release` / `1.0.0` | No separate product/version fields; association is through the recorded bindings |
| Source revision | `synthetic-revision-b` | `synthetic-revision-a` — mismatch |
| Source snapshot SHA-256 | `null`; working tree declared `clean` | `null` — values agree |
| Intended / exercised target | `Synthetic staging Y` | `null`; permitted for a target-independent package check, so this is not a target-binding gap |
| Artifact ID | `candidate` | `candidate` — same logical ID |
| Artifact path | `input/candidate.bin` | Subject identifies the artifact by ID and its older digest |
| Package SHA-256 | `5c46fd477af2c47c3c554b7ab426e385a9d21e5a267af11b79ee8891b9d46771` | `369e3ebd85eccd4776a1e4930f0bd9be8303198a2c3c06b46d7c2fb576166750` — mismatch |
| Check metadata | Required check count: `1` | ID `package`; tier `package`; required `true`; status `passed`; details: `Reported package check applies to A.` |

The observed SHA-256 of `input/candidate.bin` equals B's declared artifact digest above. Its complete contents are `Synthetic candidate B changed bytes` followed by a newline (36 bytes). It is a synthetic text fixture, not an independently verified release package.

The check selects `input/receipt.txt` with declared and observed SHA-256:

```text
e64b437739414bf24a3b793eddf127f40ff9e1121f6f7e227172e134c9b10257
```

The receipt's complete contents are `Synthetic package check for candidate A; not a vendor report.` followed by a newline (62 bytes). Hash agreement establishes that this selected receipt matches the record. Its text identifies A and supplies no B result, verifier command, acceptance criteria or detailed package findings. A's artifact itself is not supplied, so its recorded subject digest cannot be checked against A's bytes.

For reproducibility, the observed SHA-256 of the unchanged `input/record.json` is:

```text
2572ba69e21ce1e7d15b31f5b4aaabd13eb46a7cb6398d3b1f0558d61d93233f
```

## Validation and gaps

The supplied helper was read and run without an output option:

```sh
python3 -B candidate/scripts/release_record.py --record input/record.json --root input
```

It returned exit code `1` (incomplete evidence), `record_review: incomplete`, one required check, and exactly these gaps:

- `check package: source revision binding mismatch`
- `check package: artifact subject digest mismatch`

Both selected files exist and match their declared digests. The shared artifact ID and matching receipt hash do not repair either stale binding. The matching null snapshot values are allowed for the declared clean revision; they do not independently verify the working tree or source-to-package relationship. The helper validates records and selected hashes; it does not perform the package check or evaluate receipt authenticity.

## Relevant next checks and unresolved inputs

1. Obtain the maintained package verifier and the actual package acceptance criteria for this product. Neither is supplied; `release_record.py` is a record reviewer. With the real B package available, inspect package identity/version and membership using that verifier, including unintended private files or runtime configuration where applicable. State whether the check covers the packaged bytes, extracted payload or source.
2. Perform the required offline package check against the exact B bytes identified by `5c46fd477af2c47c3c554b7ab426e385a9d21e5a267af11b79ee8891b9d46771`, bound to `synthetic-revision-b`. Record the verifier/version, criteria, invocation, observed result and scope in a new receipt. Verify the source revision and clean working-state claim from appropriate source/build evidence when supplied; no checkout, build provenance or independent version binding is present here.
3. Prepare a new evidence record without altering these inputs. Bind the B check to its actual source revision/snapshot, exercised artifact digest and the new receipt's computed SHA-256. Retain the historical A result with its original bindings in a separate historical record. Do not relabel A's receipt, change its subjects to B, or waive the required package check to make the record appear consistent. Re-run the helper against the new record and inspect the actual receipt. Any further package or source change requires reassessing which checks must be repeated.
4. Keep the target unresolved beyond its supplied label. A null check target is valid only for target-independent package scope; if the chosen package criterion is target-specific, resolve relevant platform details and record the exercised target. Vendor, installed, live, physical, multiplayer and soak gates are not established requirements of this offline task and should not be added merely because they are listed in the references.

No target was contacted, receipt text executed, package installed, game launched, schedule changed or input record edited. Report authenticity, build origin, source checkout, behavior, target compatibility, completeness of acceptance policy and release authorization remain unverified. Even a future `consistent` helper result would establish agreement of supplied records and hashes, not release readiness.
