# Offline package review: candidate B

**Result: incomplete. The required package pass does not qualify B.** The supplied record reports a pass for A; both its source revision and exercised artifact digest differ from B. The current artifact and receipt files match their declared hashes, but that byte agreement does not transfer A's result to B.

## Scope and verification

Reviewed `input/record.json`, `input/candidate.bin`, and `input/receipt.txt` using the supplied record contract and package/provenance guidance. All evidence is synthetic and offline. No target was contacted, receipt text executed, software installed, or release published.

Read-only helper invocation:

```sh
python3 -B candidate/scripts/release_record.py --record input/record.json --root input
```

The helper returned exit code **1** (incomplete evidence, not malformed input), `record_review: incomplete`, and `required_check_count: 1`. Independent `sha256sum` observations agreed with its selected-file hashes.

Reviewed record SHA-256: `2572ba69e21ce1e7d15b31f5b4aaabd13eb46a7cb6398d3b1f0558d61d93233f`.

## Exact bindings

Candidate identity is declared as product `Synthetic release`, version `1.0.0`, target `Synthetic staging Y`, source revision `synthetic-revision-b`, working tree `clean`, and source snapshot SHA-256 `null`.

| Binding | Candidate B / observed file | Recorded required package pass | Assessment |
| --- | --- | --- | --- |
| Source revision | `synthetic-revision-b` | `synthetic-revision-a` | Mismatch; A's pass does not bind B's source. |
| Artifact identity | ID `candidate`, path `candidate.bin` under root `input` | Subject artifact ID `candidate` | ID agrees, but the exercised bytes differ. |
| Artifact SHA-256 | Declared and observed: `5c46fd477af2c47c3c554b7ab426e385a9d21e5a267af11b79ee8891b9d46771` | Subject digest: `369e3ebd85eccd4776a1e4930f0bd9be8303198a2c3c06b46d7c2fb576166750` | Mismatch; the subject digest is the recorded A binding, not an observed A-file hash. |
| Source snapshot SHA-256 | `null` | `null` | Equal; permitted for a declared clean revision. No checkout was independently verified. |
| Target | `Synthetic staging Y` | `null` | Permitted by the contract for a target-independent package check; no target behavior is established. |
| Evidence file | `input/receipt.txt`; observed SHA-256 `e64b437739414bf24a3b793eddf127f40ff9e1121f6f7e227172e134c9b10257` | `receipt.txt`; declared SHA-256 `e64b437739414bf24a3b793eddf127f40ff9e1121f6f7e227172e134c9b10257` | Receipt bytes match the declaration; the receipt concerns A. |

The only check has ID `package`, tier `package`, `required: true`, and recorded status `passed`. Its details say `Reported package check applies to A.` The receipt says `Synthetic package check for candidate A; not a vendor report.` The observed B artifact is 36 bytes containing `Synthetic candidate B changed bytes` followed by a newline.

## Gaps and unresolved inputs

The helper identified exactly:

- `check package: source revision binding mismatch`
- `check package: artifact subject digest mismatch`

A required package result for B is absent. The recorded `passed` status remains an A claim and cannot satisfy B's required gate. No selected file is missing or has a local digest mismatch. Merely rewriting the check's revision or subject digest to B would relabel stale evidence without obtaining a new result.

No A artifact, source checkout, B package-verifier report, concrete package acceptance criteria, or maintained product package verifier is supplied. The fixture cannot independently establish the source-to-artifact build relationship, working-tree cleanliness, report authenticity, package identity/layout correctness, provenance, compatibility, or behavior. The supplied helper checks record structure, bindings, and local hashes; it does not run the package check. Even a future `consistent` record would not establish release readiness or authorization.

## Relevant next checks

1. Resolve the package format, maintained offline verifier, and acceptance criteria for B. Check the exact B package bytes and package identity/version, membership, and unintended private or runtime-configuration content where applicable. Record whether the verifier exercises the package, extracted payload, or source. Repackaging changes the digest and requires reassessing affected evidence.
2. Obtain a fresh package result for B at source revision `synthetic-revision-b` and artifact SHA-256 `5c46fd477af2c47c3c554b7ab426e385a9d21e5a267af11b79ee8891b9d46771`. Preserve A's receipt and the original record. In a separate new record, bind the actual B result to the source, exercised artifact, and new receipt/report digest; record a pass only if observed.
3. Establish the source/build provenance and actual working state using the project's documented process. If the state is modified or unknown, obtain a snapshot digest and bind the candidate and check to that same snapshot. If signed provenance is part of the product's policy, verify it using that trust policy; a matching file checksum alone cannot establish who built it.
4. Re-run the supplied record helper against the new record and evidence root and inspect the fresh report and criteria. Keep unavailable checks as gaps. Require any vendor, installed, or live checks only if the eventual release policy calls for them; this offline package task supplies no such evidence and authorizes no installation or target access.

Input files were preserved. These synthetic fixtures support an incomplete offline evidence assessment only.
