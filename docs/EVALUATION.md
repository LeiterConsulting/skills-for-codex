# Evaluation status

Collection version 0.4.0 contains five skill pilots. Splunk app authoring is now 0.1.1 after a shared validation-reference correction; the remaining skills are 0.1.0. Original helpers and resources are prepared for reuse; no agent performance improvement has been established.

## Splunk app authoring

| Check | Current result |
| --- | --- |
| Native helper tests on the maintainer's Windows Python 3.13 host | 23 discovered; 22 passed; symlink creation test skipped because the host lacks that privilege |
| Structure and portability validation | Passed: catalog, skill resource links and host path guard |
| Bundled skill frontmatter validation | Passed |
| Windows CI, Python 3.10 and 3.13 | Both jobs passed; 23 of 23 tests passed, including symlink and junction checks |
| Linux CI, Python 3.10 and 3.13 | Both jobs passed; 22 tests passed and the Windows-only junction check was skipped |
| Agent prompt behavior and trigger accuracy | Explicit app-native behavior reviewed; implicit triggers and broader cases unrun |
| Matched baseline versus skill performance | app-native reviewed; small samples and reporting defects, no general gain established; see [results](BENCHMARK-BATCH1.md) |
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
| Agent behavior and matched performance evaluations | release-changed: two repetitions per condition reviewed; other cases/triggers unrun; see [results](BENCHMARK-BATCH1.md) |
| Consumer release readiness or deployment | Not established by this collection's helper tests |

Record helper cases exercise stale artifact subjects after a candidate change, mismatched source snapshots and targets, evidence digest/missing-file gaps, incomplete soak statuses, optional physical checks, Unicode identities/paths, output preservation, inert details, bounded hashing, case collisions and linked/reparse paths. A `consistent` record means declared bindings and file hashes agree; pass results remain caller-reported. No verifier, installer, customer connection or release action is executed by the helper.

The [second pilot CI run](https://github.com/LeiterConsulting/skills-for-codex/actions/runs/37141382266) passed for implementation commit `167d29b32edab2a6e8f10c480693f4e891dfefe8` on October 3, 2026. It exercised both helpers and collection validation on all four platform/Python combinations. Symlink checks passed in both Windows and Linux CI.

## Research and assessment instruction pilots

The Zeepkist API research, source claim audit and Splunk estate assessment pilots have focused entrypoints, consumer input templates and references. Skill/frontmatter, JSON syntax and collection resource/portability checks passed locally. The claim register's Draft 2020-12 schema definition passed; two valid synthetic fixtures were accepted and six invalid fixtures rejected in a local validator with URI/date/date-time assertions active. These eight schema checks are local checks, outside the standard-library CI suite.

No new executable helper is included in these three pilots. The existing 40 helper tests retain their prior scope. Live game/MCP research, consumer Splunk access/exports, real factual audits, trigger behavior and performance improvement have not been qualified by these structural checks. The collection does not provide missing runtime access.

The [five-skill catalog CI run](https://github.com/LeiterConsulting/skills-for-codex/actions/runs/37142805565) passed all four Windows/Linux and Python 3.10/3.13 jobs for implementation commit `5dea6f3f611031046020002e0bd3ad81438dd0c7` on October 3, 2026. Collection checks passed for all five skills; Windows passed all 40 helper tests and Linux passed 38 with two Windows-only junction skips. This run does not include the local schema format fixtures or agent behavior evaluations.

Each instruction pilot has seven observable agent cases prepared and not yet run:

- [Zeepkist API research cases](../evals/zeepkist-api-research.cases.json)
- [Source claim audit cases](../evals/source-claim-audit.cases.json)
- [Splunk estate assessment cases](../evals/splunk-estate-assessment.cases.json)

## Agent evaluation method

The [first matched benchmark wave](BENCHMARKS.md) now has ten fixed synthetic tasks, two per pilot, drawn from the case families below. Its preparer creates matched workspaces, copied-byte receipts and result records. Preparation and its unit tests exercise the evaluation assets, not agent behavior. The original 37 broad case requests remain unrun as written. Two concrete matched cases now have [reviewed results](BENCHMARK-BATCH1.md); the other eight pack cases remain unrun. This wave tests explicit entrypoint instructions with identical supporting resources; implicit trigger accuracy and helper/template gains need separate comparisons.

The local standard-library suite now discovers 63 tests: 60 passed and three symlink checks were skipped because the Windows host lacks that privilege. The benchmark preparer adds 14 checks, covering equal fixture/resource bytes, entrypoint-only treatment, fresh destination preservation, path/link rejection, reproducible receipts, unavailable metric defaults, a usable native packaging fixture and the deliberately incomplete release fixtures. Its junction check passed. Nine additional MCP bridge tests cover container-only argument execution, protocol, input rejection, visible output truncation, audit retention, exact-container timeout stopping and UTF-8 command preservation through a legacy-encoded Windows stream. Those tests mock Docker; real runtime isolation and transport equality were separately probed in the benchmark. No agent was launched by the unit tests.

The first 14 task attempts used a bridge with legacy stdin decoding. They retain artifact grades and failures as diagnostics, but are excluded from performance conclusions. The [corrected matched batch](BENCHMARK-BATCH1.md) uses eight fresh agents after the UTF-8 repair, with two repetitions per condition per case: seven completions accepted, one release report missing. A common host/container write-boundary clarification and fresh probe preceded a separate two-agent repair pair; both delivered accepted reports. The failure remains in the primary denominator and cohorts are not pooled.

The [matched-batch publication CI run](https://github.com/LeiterConsulting/skills-for-codex/actions/runs/37161419678) passed all four jobs for commit `979c0ab225ff5538185f306826fdb8a6c0de082a` on October 3, 2026. Windows passed 63/63 tests; Linux passed 60 with three Windows-only junction checks skipped. Collection validation passed in every job. This CI covers executable units and collection structure; independent synthetic artifact grading remains separate.

[Splunk cases](../evals/splunk-app-authoring.cases.json) include explicit/implicit invocation, existing app updates, React/CRUD requirements, unrelated requests, unknown targets and conflicting destinations. [Release qualification cases](../evals/release-qualification.cases.json) cover changed candidates, partial soaks, package-only scope, dirty sources, target differences, authorized repairs, source-only requests and ambiguous delivery. These are test requests with observable acceptance criteria, not evidence that an agent has passed them.

Run future evaluations in fresh isolated workspaces with matched model/reasoning, tools, source snapshot, input brief and fixture. Preserve ordinary project instructions in both baseline and skill conditions. Distinguish instruction gains from new helper/template gains.

Record task completion and its denominator, time to accepted output, token use, tool/failed calls, human corrections, trigger misses/false activations, unsupported acceptance claims and unintended changes. Keep failed runs and qualitative findings.

Promote based on a demonstrated bottleneck improvement with no critical correctness or scope regression. Set numerical targets after measuring baseline variability. Follow [OpenAI's evaluation guidance](https://developers.openai.com/blog/eval-skills) for trace/artifact-based checks.
