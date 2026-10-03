# Evaluation status

Collection version 0.2.0 contains two initial skill pilots. Original helpers and resources are prepared for reuse; no agent performance improvement has been established.

## Splunk app authoring 0.1.0

| Check | Current result |
| --- | --- |
| Native helper tests on the maintainer's Windows Python 3.13 host | 23 discovered; 22 passed; symlink creation test skipped because the host lacks that privilege |
| Structure and portability validation | Passed: catalog, skill resource links and host path guard |
| Bundled skill frontmatter validation | Passed |
| Windows CI, Python 3.10 and 3.13 | Both jobs passed; 23 of 23 tests passed, including symlink and junction checks |
| Linux CI, Python 3.10 and 3.13 | Both jobs passed; 22 tests passed and the Windows-only junction check was skipped |
| Agent prompt behavior and trigger accuracy | Cases prepared; not yet measured |
| Matched baseline versus skill performance | Not run |
| Splunk AppInspect | Not run |
| Installed or live Splunk behavior | Not run |

Helper cases verify different app identities, authors, role choices and directories; Unicode/XML semantics; missing inputs and config injection; existing content preservation; exact archive membership; deterministic packaging; digest accuracy; portable filenames; and rejection of invalid release selection, Windows junctions and package destinations hidden by parent segments. A skipped OS-specific check is not a pass.

The [initial CI run](https://github.com/LeiterConsulting/skills-for-codex/actions/runs/37133306517) passed all four jobs for implementation commit `abefc51decca0306fd7304b8e2f943b26a101dfd` on October 3, 2026. Each job also passed collection validation. The Windows CI hosts could exercise the symlink check that was unavailable on the local host.

## Release qualification 0.1.0

| Check | Current result |
| --- | --- |
| Record helper tests on the local Windows Python 3.13 host | 17 discovered; 16 passed; symlink creation skipped because the host lacks that privilege |
| Full collection tests on the local host | 40 discovered; 38 passed; both symlink checks skipped |
| Structure/resource/portability and skill frontmatter checks | Passed |
| Windows/Linux CI, Python 3.10 and 3.13 | All four jobs passed: Windows 40/40 tests; Linux 38 passed with two Windows-only junction checks skipped |
| Agent behavior and matched performance evaluations | Cases prepared; not run |
| Consumer release readiness or deployment | Not established by this collection's helper tests |

Record helper cases exercise stale artifact subjects after a candidate change, mismatched source snapshots and targets, evidence digest/missing-file gaps, incomplete soak statuses, optional physical checks, Unicode identities/paths, output preservation, inert details, bounded hashing, case collisions and linked/reparse paths. A `consistent` record means declared bindings and file hashes agree; pass results remain caller-reported. No verifier, installer, customer connection or release action is executed by the helper.

The [second pilot CI run](https://github.com/LeiterConsulting/skills-for-codex/actions/runs/37141382266) passed for implementation commit `167d29b32edab2a6e8f10c480693f4e891dfefe8` on October 3, 2026. It exercised both helpers and collection validation on all four platform/Python combinations. Symlink checks passed in both Windows and Linux CI.

## Agent evaluation cases

[Splunk cases](../evals/splunk-app-authoring.cases.json) include explicit/implicit invocation, existing app updates, React/CRUD requirements, unrelated requests, unknown targets and conflicting destinations. [Release qualification cases](../evals/release-qualification.cases.json) cover changed candidates, partial soaks, package-only scope, dirty sources, target differences, authorized repairs, source-only requests and ambiguous delivery. These are test requests with observable acceptance criteria, not evidence that an agent has passed them.

Run future evaluations in fresh isolated workspaces with matched model/reasoning, tools, source snapshot, input brief and fixture. Preserve ordinary project instructions in both baseline and skill conditions. Distinguish instruction gains from new helper/template gains.

Record task completion and its denominator, time to accepted output, token use, tool/failed calls, human corrections, trigger misses/false activations, unsupported acceptance claims and unintended changes. Keep failed runs and qualitative findings.

Promote based on a demonstrated bottleneck improvement with no critical correctness or scope regression. Set numerical targets after measuring baseline variability. Follow [OpenAI's evaluation guidance](https://developers.openai.com/blog/eval-skills) for trace/artifact-based checks.
