# Evaluation status

Version 0.1.0 is an initial skill pilot. Original helpers and resources are prepared for reuse; no performance improvement has been established.

## Checks performed

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

## Agent evaluation cases

[evaluation cases](../evals/splunk-app-authoring.cases.json) include explicit/implicit invocation, existing app updates, React/CRUD requirements, unrelated requests, unknown targets and conflicting destinations. These are test requests with observable acceptance criteria, not evidence that an agent has passed them.

Run future evaluations in fresh isolated workspaces with matched model/reasoning, tools, source snapshot, input brief and fixture. Preserve ordinary project instructions in both baseline and skill conditions. Distinguish instruction gains from new helper/template gains.

Record task completion and its denominator, time to accepted output, token use, tool/failed calls, human corrections, trigger misses/false activations, unsupported acceptance claims and unintended changes. Keep failed runs and qualitative findings.

Promote based on a demonstrated bottleneck improvement with no critical correctness or scope regression. Set numerical targets after measuring baseline variability. Follow [OpenAI's evaluation guidance](https://developers.openai.com/blog/eval-skills) for trace/artifact-based checks.
