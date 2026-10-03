# Claim/source register contract

Use [claim-register.template.json](../assets/claim-register.template.json) and [claim-register.schema.json](../assets/claim-register.schema.json) to record consumer-defined scope/evidence. Nulls are unresolved values. The schema describes a record; it does not browse sources or establish factual correctness.

The top level contains schema_version, audit_scope, sources, claims and backlog. Scope records purpose, product, versions, environments, review mode, budget and input origins. The agent/user chooses them from the task. Keep credentials and private source material outside public examples.

Each source has an ID, URL, section locator, publication/retrieval timestamps, optional captured-content digest and availability. A section may be a heading/anchor or stable file/line reference; retain a snapshot/reference when content is mutable. Avoid copying whole licensed pages.

Each claim has an ID, statement, product/version/environment/qualification scope, assertion/inference kind, supporting source IDs, outcome, review timestamp and rationale. Outcomes: unreviewed, supported, contradicted, conflicting or unavailable. Completed outcomes need a real review timestamp and rationale; supported/contradicted/conflicting claims also need referenced sources. URL availability never establishes support.

Validate relationships as well as syntax: source IDs must exist; claims must retain supporting section mappings; backlog IDs must resolve; timestamps must reflect actual work. JSON Schema cannot establish those relationships or the truth of an assertion/inference. Preserve conflicting source IDs and statements in the rationale.

The schema uses [JSON Schema Draft 2020-12](https://json-schema.org/draft/2020-12). It permits unresolved templates and requires additional fields for completed outcomes. Enable format assertions and verify that the consumer-selected validator supports URI/date/date-time checks. Some validators silently skip formats whose optional dependencies are absent; see [jsonschema format validation](https://python-jsonschema.readthedocs.io/en/stable/validate/#validating-formats). Structure validation is not a completed audit.

Prioritize consequences proportionately: compatibility, upgrade paths, authorization, security and entitlement often deserve attention before low-consequence display text. Backlog priority/reason are explicit; no universal interval or fixed budget is supplied.

Deliver counts with denominators and scope: sources checked for change, claims actually reviewed, changed claims, unresolved claims and remaining backlog. Preserve prior verification history where available. Partial audits advance only genuinely reviewed records.
