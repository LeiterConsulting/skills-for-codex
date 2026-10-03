# First matched benchmark wave

The [wave-one pack](../evals/benchmark-wave1.json) fixes ten original synthetic tasks: two for each of the five skill pilots. They are concrete offline instances of the broader [agent cases](EVALUATION.md), with fixtures and review rubrics. All agent results remain **not run**.

| Skill | Case IDs | Decision exercised |
| --- | --- | --- |
| Splunk app authoring | `app-native`, `app-conflict` | Package semantics and existing-content preservation |
| Release qualification | `release-changed`, `release-soak` | Candidate bindings and incomplete acceptance evidence |
| Zeepkist API research | `api-parser-null`, `api-stale-catalog` | Mock member contracts, parser limits and catalog currency |
| Source claim audit | `claim-edition`, `claim-budget` | Scoped entitlement claims and bounded review coverage |
| Splunk estate assessment | `estate-denied`, `estate-delta` | Denied/truncated coverage and incomparable snapshots |

The mock API declarations, invented product excerpts, reserved `.invalid` URLs and synthetic exports are original test material. They do not verify real game symbols, vendor facts, live connectors or customer estates. Native app archives and release file hashes permit artifact checks; semantic decisions still require review of the actual output and trace.

## Prepare a comparison

From the repository root, choose a fresh output directory:

```text
python scripts/prepare_benchmark.py --case app-native --output work/benchmarks/app-native
```

An optional `--source-revision` records the caller's checkout label. The helper separately hashes the exact pack, copied resources, skill entrypoint and common files. A caller-reported revision alone does not establish a clean checkout.

The result contains `baseline/`, `skill/` and evaluator-only `review/` directories. Each workspace has identical `AGENTS.md`, `TASK.md`, input bytes, and supporting scripts/assets/references under `candidate/`. The skill workspace additionally has `candidate/SKILL.md`; UI discovery metadata is omitted in both. `PROMPT.txt` supplies the matching condition's entry instruction. Result templates and the rubric stay in `review/`.

The helper creates files only. It does not launch an agent, provision a sandbox, enforce isolation, grade outputs, contact targets or execute receipt text. It refuses existing outputs and linked/reparse paths. Keep generated workspaces/results outside the published assets; the example `work/` directory is ignored by Git.

## Run and review

1. Start fresh agent sessions with the same model, reasoning setting, tools and budgets. Restrict each to its workspace, with no sibling/evaluator access. Disable automatic access to this candidate skill in the baseline; verify no inherited skill instructions or earlier run answers. If the host cannot do this, mark the comparison contaminated and exclude it from performance conclusions. Workspace instructions alone do not enforce isolation.
2. Supply only that workspace's `PROMPT.txt`. Keep ordinary project instructions and supporting resources available in both conditions. This comparison measures the entrypoint's explicit instruction effect. It does not measure implicit trigger accuracy or the incremental benefit of adding helpers/templates.
3. Preserve complete traces, final output, artifacts and relevant hashes for both successful and failed runs. Record the actual model/reasoning/tools/loaded skills, receipt hash, run order and repetition in the result record. Missing token/tool metrics stay `null`; they are not zero. Store trace and artifact references relative to the retained experiment bundle, with hashes where available.
4. Review outputs against every criterion using artifact semantics and trace evidence. Prefer reviewers blind to condition labels where feasible. Record a pass/fail and concrete evidence per criterion, plus unsupported claims and unintended changes. Neither string matches nor a helper's `consistent` response substitute for this review.
5. Mark a run accepted only when every criterion passes and no critical correctness or scope regression appears. A critical failure is a hard rejection; otherwise partial scores may diagnose defects without becoming accepted completion. Leave acceptance unknown until review is complete. Preserve unsuccessful attempts and human corrections.

A first pass of one run per condition is a **20-run smoke wave**, useful for finding defects. It provides little evidence about variability. Follow with repeated matched runs and balanced/randomized condition order; choose the repetition count and decision thresholds before inspecting comparative results. Do not change fixtures or skills halfway through a comparison. After fixing a defect, prepare a new revision and run both conditions again for the affected case.

Compare accepted completions using the attempted-run denominator, critical failures, unsupported claims, unintended changes and human corrections. Summarize elapsed time, token use and tool calls for all attempted runs; also show accepted-run subsets without hiding failed effort. Report paired differences and spread across repetitions rather than one favorable example. Unavailable measurements and excluded/contaminated runs need explicit denominators and reasons.

## Limits and next batches

These tasks exercise offline evidence and artifacts. Real AppInspect, installation, physical input, multiplayer, soak completion, source retrieval, live tool fallback and authorized estate queries need separate consumer-defined contexts. The broader cases include implicit triggers and unrelated requests; run those separately using the same candidate catalog and actual host discovery behavior. Do not infer trigger accuracy from this explicit-entrypoint wave.

No numerical gain or promotion is established by preparing this pack or passing its unit tests. [Evaluation status](EVALUATION.md) records that distinction. The method follows [OpenAI's skill evaluation guidance](https://developers.openai.com/blog/eval-skills).
