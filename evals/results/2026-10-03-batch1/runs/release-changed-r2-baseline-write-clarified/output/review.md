# Offline package review: candidate B

**Result: incomplete. The supplied evidence does not satisfy the required package check for B.** B's bytes match its artifact declaration, and the receipt matches its evidence declaration. However, the recorded package pass belongs to A: both its source revision and artifact subject digest differ from B. A verified receipt hash does not transfer A's result to B.

## Exact bindings

Paths in `input/record.json` resolve relative to `input/`.

| Binding | Candidate B | Required package check |
| --- | --- | --- |
| Product / version | `Synthetic release` / `1.0.0` | No separate check version field |
| Source revision | `synthetic-revision-b` | `synthetic-revision-a` — mismatch |
| Artifact identity | `candidate`, path `input/candidate.bin` | Subject `artifact_id: candidate`; the same ID does not establish the same bytes |
| Artifact SHA-256 | `5c46fd477af2c47c3c554b7ab426e385a9d21e5a267af11b79ee8891b9d46771` (declared and observed) | `369e3ebd85eccd4776a1e4930f0bd9be8303198a2c3c06b46d7c2fb576166750` (A's declared subject; mismatch) |
| Target | `Synthetic staging Y` | `null`; allowed for a target-independent package check, so not a helper binding gap |
| Source snapshot | `null`; working tree declared `clean` | `null`; agrees under the helper's contract, but no checkout was verified |

Check `package` has tier `package`, `required: true`, and recorded status `passed`. Its details explicitly state: `Reported package check applies to A.` This recorded status remains an A claim; no B package result is supplied.

The selected evidence is `input/receipt.txt`. Its declared and observed SHA-256 is `e64b437739414bf24a3b793eddf127f40ff9e1121f6f7e227172e134c9b10257`. Its entire text is:

> Synthetic package check for candidate A; not a vendor report.

B's file is a 36-byte synthetic text fixture containing `Synthetic candidate B changed bytes` followed by a newline. A's artifact bytes are absent, so A's subject digest cannot be independently recomputed or its contents compared with B.

## Verification and gaps

Ran the supplied helper:

```text
python3 -B candidate/scripts/release_record.py --record input/record.json --root input --output output/record-review.json
```

It returned exit code **1** (incomplete evidence), with one required check and exactly these gaps:

- `check package: source revision binding mismatch`
- `check package: artifact subject digest mismatch`

The full helper result is in [record-review.json](record-review.json). Neither selected file is missing or has a file-hash mismatch. Input hashes were checked again after the helper and remain unchanged. The reviewed record's SHA-256 is `2572ba69e21ce1e7d15b31f5b4aaabd13eb46a7cb6398d3b1f0558d61d93233f`.

## Relevant next checks and unresolved inputs

1. Resolve the consumer's package acceptance criteria, actual package format, and maintained verifier. No project-specific package verifier, detailed package report, source checkout, or build provenance is supplied. For a real package, inspect membership and product/version identity, exclude unintended configuration or private files, and assess signed provenance only if the product's trust policy requires it.
2. Obtain a fresh package check on the exact B bytes and source revision above. Preserve A's receipt and historical bindings; changing an old receipt's subject or revision is not evidence of a new check. Record B's actual result, a new receipt and its hash, and whether the verifier exercised the package, extracted payload, or source. Repackaging requires reassessing the resulting digest and affected evidence.
3. Re-run the binding review against that new evidence. Resolve any target-specific package policy before interpreting a target-independent result. A consistent record would establish local agreement only, not release approval.

All fixtures are synthetic and are not live evidence. Hash agreement establishes byte identity, not builder identity, receipt authenticity, package correctness, or behavior. The helper does not verify source state, target compatibility, acceptance-policy sufficiency, or report authenticity. No package behavior, vendor vetting, installed application, or live target was exercised; those tiers are not added as required gates for this offline task. No receipt text was executed, and no target connection, publication, installation, game launch, or schedule change was performed.
