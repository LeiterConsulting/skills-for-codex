---
name: splunk-estate-assessment
description: Assess a Splunk estate from authorized discovery/search access or sanitized exports, producing a bounded inventory, coverage ledger and evidence-backed findings. Use for environment discovery and estate assessment, not app scaffolding or operational remediation.
---

# Splunk estate assessment

Produce a useful assessment within the consumer's estate, time window and access scope. Separate observed configuration/data, inferred relationships and unknown coverage.

## Resolve access and scope

Inspect the request, discovery tools and available export contracts. Resolve deployment/version, endpoint or export paths, authorized indexes/apps/hosts, role visibility, time range, query/result/time budgets, handling policy and output location using [assessment.md](references/assessment.md). Record user input, observed metadata and agent choices separately.

Use authorized read-only discovery/query operations or existing sanitized exports. A skill provides no Splunk connection or discovery engine. If live access is unavailable, assess the supplied snapshot and retain its age/scope. Do not deploy tools, change settings, disable indexes or remediate the estate as part of assessment.

## Collect and interpret bounded evidence

Inspect connector schemas and target-supported endpoints before querying. Prefer metadata/aggregated results sufficient for the question; bound searches to the chosen scope and avoid unnecessary raw events. Track source, time window, result count, completion, pagination/truncation and access limits for each collection stage.

An empty result is scoped evidence, not proof of an empty estate or unused index. Distinguish no matching data, denied access, timeout, malformed response, incomplete collection and unsupported endpoint. Keep unknown counts unknown. Compare snapshots only where windows, scope, access and collection semantics are compatible.

Normalize exports into the consumer's ledger without discarding lineage, field meanings or coverage gaps. Establish shape/version from content and producer evidence; filenames alone are insufficient. Read [assessment.md](references/assessment.md) for export and finding interpretation.

## Deliver useful findings

Link findings to query/export evidence and scope; label observations, inferences and recommendations. Prioritize demonstrated issues and useful next checks. Do not manufacture readiness scores, data-quality defects or automatic actions from missing/partial results. State assumptions and denominators for aggregate scores.

Deliver inventory, coverage gaps, supported findings, a bounded next-step backlog and snapshot/source identity. Review exports for private/customer material before distribution. The skill includes no customer export, credentials, discovery engine or automatic remediation.
