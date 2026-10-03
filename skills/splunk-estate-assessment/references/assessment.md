# Inputs, collection and coverage ledger

Use [assessment.template.json](../assets/assessment.template.json) as a normalized local record shape. It contains unresolved consumer inputs and is not an adapter for every exporter. Preserve original exports and producer/version/digest metadata; map fields explicitly and retain missing/incompatible fields as gaps.

| Input | Agent/user resolution |
| --- | --- |
| Deployment, exact version, estate boundary | Target metadata or supplied context; unknown limits claims |
| Endpoint/connector or export paths | Authorized target or provided sanitized snapshots |
| Index/app/host scope, role visibility | Task/access context; missing permissions limit inventory |
| Time range, query/result/time budgets | Task constraints or stated proportionate agent choices |
| Output path, handling policy | Consumer destination, retention/distribution and redaction |
| Producer/export schema, capture time | Export/source evidence; record unknowns |

Credentials stay in the target's approved secret mechanism, outside templates. Verify target-specific [Cloud REST access constraints](https://help.splunk.com/en/splunk-enterprise/leverage-rest-apis/rest-api-tutorials/9.2/rest-api-tutorials/access-requirements-and-limitations-for-the-splunk-cloud-platform-rest-api) and [search endpoint semantics](https://help.splunk.com/en/splunk-enterprise/leverage-rest-apis/rest-api-reference/10.2/search-endpoints/search-endpoint-descriptions); linked versions are reference entry points, not assumed targets.

## Evidence and coverage

For each relevant inventory domain, record scope, query/endpoint or export reference, capture time, time window, result count and collection outcome. Outcomes: complete, partial, denied, failed, unavailable, not_requested or unknown. One complete domain does not establish full estate visibility.

Check pagination, row limits, preview/final results, scope filters and response envelopes before summarizing. A result list may be empty because extraction failed; inspect response status/shape rather than coercing it to a successful zero. Preserve producer-reported failures and coverage gaps.

No events in a short window does not demonstrate an unused index. Check purpose, retention/window, expected cadence and visible permissions before proposing action. Do not disable internal/configured indexes from an assessment. Similar host/sourcetype names do not prove topology or shared ownership.

Findings need evidence references, observation/inference classification, confidence/limits, consequence and the smallest next check. Separate generated suggestions from observed facts. An upstream readiness score needs provenance, inputs and missing coverage; it is not measured reliability.

## Comparison and handoff

Align entity keys/namespaces, producer/schema versions, time window, access and completion state before snapshot deltas. Missing entities in a partial/lower-visibility snapshot are not proven removed. Report incomparable portions.

Summaries, runbooks and handoffs should cite the same evidence IDs and preserve uncertainty. Keep sensitive fixtures/local paths outside public releases. Proposed recommendations do not authorize remediation or external sharing.
