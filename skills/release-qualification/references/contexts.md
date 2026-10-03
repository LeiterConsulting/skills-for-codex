# Conditional acceptance concerns

Read only the section relevant to the requested release. These are decision prompts, not mandatory gates for every product.

## Packages and provenance

Bind version, source revision/working snapshot and digest to the candidate. Inspect archive membership and identity using the project's maintained verifier; keep runtime configuration and unintended private files out of release content. Repackaging changes the package digest even when payload files appear unchanged: say whether a check exercised the package, extracted payload or source.

A checksum establishes byte agreement with the expected digest. It does not establish who built the artifact or whether its behavior is correct. When the product uses signed provenance, verify it with its documented trust policy. [GitHub artifact attestations](https://docs.github.com/en/actions/concepts/security/artifact-attestations) link builds to provenance; attestations still need verification and policy evaluation.

For a Splunk Cloud app, use the exact target's [private app vetting/install requirements](https://help.splunk.com/en/splunk-cloud-platform/administer/admin-manual/10.6/manage-apps-and-add-ons-in-splunk-cloud-platform/manage-private-apps-on-your-splunk-cloud-platform-deployment). Local XML/package checks do not substitute for the actual AppInspect/vetting report or installed behavior.

## Installed applications, services and native integrations

Separate staging, replacement, installed hash agreement and live operation. If the maintained installer requires an application to be closed, prove that condition immediately before mutation. For a service update, a stopped service entry may not prove its wrapper/children have exited or released the binary; use the product's bounded quiescence/recovery mechanism.

Resolve paths, process identities, service names, settings preservation, rollback destinations and retry limits from the target. Preserve prior payload/settings when the update requires recovery. Do not kill unrelated processes or replace a consumer's maintained installer with a generic recipe. A successful replacement does not prove restart, connectivity or upgrade/recovery behavior.

## Live, physical and multiple-client acceptance

Name the actual installed version, exercised environment and fixture. A unit test or injected/virtual event may support an offline claim without establishing human controller/device input. One client does not establish remote ordering, convergence or multiplayer behavior. Require those tiers only when the requested behavior or established release criteria call for them.

Coordinate user-timed checks, preserve active work and record unavailable/manual checks as gaps. Inspect a running session before considering a new one. A tool being present does not establish live access or successful execution.

## Soaks and external delivery

Define the duration, fixture/faults, success metrics, final review and stop conditions for the task before interpreting a soak. A healthy partial run is partial evidence. Preserve interruptions and failures; do not convert `running` or `needs_review` to a pass. A candidate change requires assessing which results are invalidated.

For delivery correctness, inspect the receiver's evidence and exact request/payload identities when relevant. A timeout does not alone establish rejection or safe retry; an accepted message can lose its response. Use the product's reconciliation/quarantine policy and preserve pending evidence. A helper must not silently replay or discard data as part of qualification.
