---
name: source-claim-audit
description: Audit technical or product guidance against authoritative sources with exact version, environment and qualification scope; maintain source-to-claim mappings and unresolved conflicts. Use for factual guidance audits and affected-claim reviews, not ordinary rewriting or merely checking whether links load.
---

# Source claim audit

Determine which maintained claims are supported, contradicted or unresolved within the request. Keep source review, claim verification and product behavior validation distinct.

## Set the audit scope

Inspect the claim inventory, source register and relevant project instructions. Resolve product/version/edition/environment scope, source policy, priority/budget, output location and publication authority from the user or project. Read [register.md](references/register.md) for the record contract and [the register schema](assets/claim-register.schema.json) when producing structured records.

For change monitoring, identify changed sources, then verify affected claims and selected high-consequence claims. Keep a finite backlog for remaining work. Change detection does not revalidate every historical statement. For OpenAI-specific guidance, use the host's available OpenAI documentation workflow and its source policy.

## Verify the claims

Use authoritative sources for the exact release/environment, with supporting section and qualifications. Verify the assertion, not just URL availability. Distinguish customer-managed from provider-managed behavior, edition/entitlement from version availability, and controlled/beta availability from general availability.

Record source section, reviewed scope, outcome, rationale and actual review date. Distinguish publication date, retrieval time and completed claim review. Label inferences. Preserve conflicting/unavailable evidence and the decision it prevents; do not invent a reconciliation or review date.

## Deliver or update within scope

Correct supported factual errors when edits are authorized, preserving unrelated interface and operational rules. Report affected claims, evidence, unresolved items and the finite backlog. Maintain source-to-claim relationships when either register changes; derived summaries must retain the mapping.

A documentation audit does not prove browser behavior, exports, live publication or deployment synchronization. Use relevant target checks for those claims and report them separately. Scheduling/publication rules stay in the consumer's project or automation; this skill creates no schedule or publication authority.
