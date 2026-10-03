# Candidate B: offline package review

Candidate B is **not qualified against the required package gate** by the supplied evidence. Its artifact digest is correct, but the recorded package pass applies to candidate A. This is an evidence gap, not an observed package-test failure for B. The fixtures are synthetic and are not live evidence.

## Scope and criteria

Reviewed `input/record.json`, `input/candidate.bin` and `input/receipt.txt` under `AGENTS.md`, `TASK.md` and `candidate/SKILL.md`. The task requests offline package review of B. The record declares one required check: `package` (tier `package`, recorded status `passed`). Its details state: `Reported package check applies to A.` No maintained package verifier, specific package acceptance criteria, build/source checkout or additional required checks are supplied. Installed, vendor, live, physical, multiplayer and soak checks are not established requirements for this offline task.

## Exact identity and bindings

All digests below are SHA-256. Record-relative artifact/evidence paths resolve beneath `input/`.

| Field | Candidate B | Recorded package check for A |
| --- | --- | --- |
| Product/version | `Synthetic release` / `1.0.0` | No separate A product/version supplied |
| Source revision | `synthetic-revision-b` | `synthetic-revision-a` â€” mismatch |
| Working tree | Declared `clean`; not independently verified | Not separately reported |
| Source snapshot digest | `null` | `null` |
| Intended/exercised target | Intended `Synthetic staging Y` | Check target `null` |
| Artifact identity | ID `candidate`; path `input/candidate.bin` | Subject ID `candidate`; A's recorded digest below |

- B declared and observed artifact digest: `5c46fd477af2c47c3c554b7ab426e385a9d21e5a267af11b79ee8891b9d46771`.
- A recorded check subject digest: `369e3ebd85eccd4776a1e4930f0bd9be8303198a2c3c06b46d7c2fb576166750`. This differs from B. No A artifact is supplied, so A's bytes/digest were not independently verified.
- Receipt declared and observed digest: `e64b437739414bf24a3b793eddf127f40ff9e1121f6f7e227172e134c9b10257` at `input/receipt.txt`.
- Reviewed record observed digest: `2572ba69e21ce1e7d15b31f5b4aaabd13eb46a7cb6398d3b1f0558d61d93233f` at `input/record.json`.

The 36-byte candidate file contains `Synthetic candidate B changed bytes` followed by a newline. The 62-byte receipt contains `Synthetic package check for candidate A; not a vendor report.` followed by a newline. Receipt bytes agree with the record, but the receipt does not itself identify a source revision, artifact digest, verifier, criteria or detailed results. Its relationship to A's revision and digest is caller-declared in the record. Its existence and checksum do not establish a package pass for B or authenticate a pass for A.

A null target is permitted for a target-independent package check and is not a helper binding error here. It establishes no compatibility with `Synthetic staging Y`; the target's platform/version and environment remain unresolved. Equal null snapshot fields are also not a helper error for the declared clean candidate, but no source checkout or build provenance was verified.

## Checks actually performed

Ran the supplied read-only record helper:

```text
python3 candidate/scripts/release_record.py --record input/record.json --root input
```

It returned exit code **1**, `record_review: incomplete`, with one required check and exactly these gaps:

```text
check package: source revision binding mismatch
check package: artifact subject digest mismatch
```

Separately computed local SHA-256 digests and byte counts for all three input files and read the candidate and receipt bytes. Both selected files match their declared file digests. No missing selected file, receipt digest mismatch or B artifact file digest mismatch was observed. The mismatch concerns the artifact exercised by the recorded check, not the current artifact's integrity.

No package/build/behavioral check was executed; the helper checks record structure, declared bindings and local hashes. It does not execute checks or receipt text, verify source provenance, authenticate reports, inspect behavior or authorize release. The recorded `passed` status remains a claim about A. Inputs were preserved.

## Required gaps and relevant next checks

1. Resolve the existing package acceptance criteria and maintained verifier/command, including tool version and what it exercises: package bytes, extracted payload or source. The supplied receipt lacks this detail.
2. Obtain or run that package verification offline on the exact B artifact, bound to `synthetic-revision-b` and digest `5c46fd477af2c47c3c554b7ab426e385a9d21e5a267af11b79ee8891b9d46771`. Retain the completed report, command, tool/environment details, criteria and semantic outcomes, then review those outcomes before recording a pass. Confirm the source-to-artifact relationship and declared clean source state; bind a snapshot if working changes exist.
3. Produce a separate updated evidence record with B's actual check source/subject bindings and the new report's digest, preserving A's evidence. Rerun the record helper and review the report meaning. Merely relabeling A's receipt or changing its declared subject/source does not constitute a new check. No documented relevance argument supporting carry-forward from A is supplied.
4. If compatibility with `Synthetic staging Y` is later requested, resolve its exact environment/version and applicable target acceptance policy before making that claim. This is an unresolved input for compatibility, not an added mandatory live gate for the present offline review.

B's required package gate remains open until relevant, completed evidence is bound to B. Nothing in these fixtures establishes installation, live operation, vendor approval or release authorization. No target was contacted, receipt text executed, package installed, artifact published, game launched or schedule altered.
