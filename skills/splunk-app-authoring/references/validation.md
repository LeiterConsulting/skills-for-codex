# Package and runtime evidence

Use existing project checks where available. The bundled helper reads an explicit release manifest, verifies app identity and selected XML/navigation, and writes a deterministic tar.gz with one app root. Its validation is intentionally bounded: it does not parse every Splunk config, enforce all ACL semantics, compile backend/UI code, validate SPL, run AppInspect or test a running Splunk deployment.

The helper refuses an existing scaffold destination or package output. It never deletes old archives, changes an installed app, logs into Splunk or restarts a service. Release selection rejects traversal, symlinks/reparse points and private configuration/key filenames.

Inspect archive members and selected file contents before distribution. Avoid copying local/, credentials, virtual environments, dependencies, caches or arbitrary workspace files. Include runtime assets and seed data only when intended and reviewed. Do not replace a project's release workflow with this helper if it has stronger checks.

## Text values and verification records

Compare JSON-decoded inputs with parsed XML text as Unicode strings. Raw JSON escapes, a string representation and escaped tool output are representations of a value; they do not establish literal backslashes in that value. Read and write text as UTF-8. If display encoding is ambiguous, inspect the parsed string's code points before reporting a defect or an unresolved user choice.

Populate quoted report values and check descriptions from those same parsed values. A passed equality assertion does not support a different prose interpretation of the characters. Record a check as passed only after its assertion or maintained verifier ran; keep the actual result with the receipt.

## Acceptance levels

| Level | Evidence |
| --- | --- |
| Source | Relevant implementation and configuration inspected |
| Build | Applicable frontend/backend compilation or checks passed |
| Structure/package | Selected structure valid, archive membership/identity inspected, digest recorded |
| AppInspect | Actual vendor report for the relevant target and package |
| Installed | Exact package installed on the intended authorized target |
| Live | Searches, navigation, permissions, writes and browser behavior exercised as applicable |

A structural check cannot establish installation or live acceptance. For [Splunk Cloud private apps](https://help.splunk.com/en/splunk-cloud-platform/administer/admin-manual/10.6/manage-apps-and-add-ons-in-splunk-cloud-platform/manage-private-apps-on-your-splunk-cloud-platform-deployment), use the applicable AppInspect/vetting/install workflow. Requirements depend on the target release and environment.

Retain input provenance, artifact digest, relevant source version and the status of each required check in a local acceptance record. Unknown target/version information remains a qualification gap.
