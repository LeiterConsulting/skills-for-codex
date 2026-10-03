---
name: release-qualification
description: Assess a software release candidate by binding source, artifact digests and check results to the intended target and acceptance criteria. Use for release readiness reviews or release qualification work, not routine edits or source-only reviews without a release question.
---

# Release qualification

Determine what this exact candidate is qualified to do, which requested gates remain open, and what evidence supports that conclusion. Preserve the user's release scope and existing project checks.

## Establish the candidate and criteria

Inspect relevant project instructions, maintained build/package/verifier commands and the requested release purpose. Resolve identity/version, source revision and working changes, artifact paths, target/version, check criteria and input origins from the project or user. Read [record.md](references/record.md) when recording or mechanically reviewing this evidence.

An agent may propose criteria proportionate to the change and release purpose; distinguish proposals from established requirements. Do not require every acceptance tier for every release. Unknown target details allow offline qualification but limit compatibility claims. A source revision alone does not bind uncommitted changes; record a snapshot digest when relevant.

## Gather and interpret evidence

Use maintained project verifiers and the checks relevant to the change. Read [contexts.md](references/contexts.md) only for applicable package, installed, physical/multiplayer or soak concerns. Keep credentials in the target's approved secret mechanism.

Record source/build, package, vendor, installed, live, physical, multiplayer and soak evidence separately when applicable. Identify the exact artifacts and environment each check exercised. A running check, interrupted run, unavailable check or completed run awaiting review remains incomplete. Inspect semantic results; process exit or file presence alone may not establish the requested behavior.

After a change, identify which evidence is affected and recheck those gates. Evidence from a different digest or source snapshot does not automatically qualify the new candidate; carry it forward only with a documented relevance argument. Fix routine in-scope defects when implementation/testing is authorized. In a review-only task, report them and preserve the target.

The optional [release_record.py](scripts/release_record.py) verifies declared file hashes and recorded check bindings. It does not execute checks, inspect log meaning, authenticate reports, verify the source checkout or authorize a release. It treats caller-reported passes as claims, and reports missing or conflicting evidence. Use it in a quiescent evidence workspace; it is not a protection against concurrent hostile file changes.

## Deliver the decision

State the candidate/version/source, target, artifact digests, checks actually performed, observed failures, required gaps and the conclusion within that scope. Provide the local evidence record or reviewed report and any relevant rollback/settings result. Keep optional findings visible.

Qualification does not itself authorize publishing, installing, restarting, replaying data or contacting a customer target. Continue actions already authorized by the user; resolve an actual authorization gap immediately before the affected action. Preserve existing settings and recoverable prior artifacts when an authorized update needs them.
