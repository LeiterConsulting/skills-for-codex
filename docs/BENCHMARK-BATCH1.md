# First matched batch: app-native and release-changed

The primary matched batch completed **eight fresh trials using corrected UTF-8 transport; seven were accepted**. One release skill agent omitted the required report file. A common runtime instruction was clarified, a fresh write/Unicode preflight passed, and a separate fresh baseline/skill repair pair both delivered accepted reports. The original failure stays in the denominator. The 14 earlier attempts are retained as diagnostics and excluded from performance conclusions. **No general performance gain or skill promotion is established.**

The [results ledger](../evals/results/2026-10-03-batch1/summary.json) includes individual metrics, grades, artifacts, transport checks and hashes. The corrected cohort used source commit `5b609d4c518255009795f3eb3af185f321dfcac3`, app skill 0.1.1 and release skill 0.1.0. The frozen task pack remains 0.1.0. Exact task/candidate bytes are archived; source labels alone do not prove working-byte identity or identical line endings.

## Design and verified scope

Each comparison used independent Codex CLI 0.160.0 processes with fresh runtime homes, `gpt-6.1-sol`, reasoning `xhigh`, identical tools/time limits, Python 3.13.15 and the same immutable container image. Each pair ran concurrently; repetition two reversed submission order. Actual scheduler interleaving was not measured.

Both conditions received identical tasks, ordinary instructions, fixtures, helpers, templates and references. Only the skill condition received and explicitly loaded `candidate/SKILL.md`. This measures the explicit entrypoint instruction effect with supporting resources already available to the baseline. Implicit triggers and added-helper value require separate comparisons.

Each container mounted only its assigned workspace. Network was disabled, root filesystem read-only, capabilities dropped and new privileges disabled. Exact mount sources, initial file inventories, fresh context and preserved input/resource hashes were checked. Preflight found evaluator/host paths absent and TCP unreachable. The final preflight transmitted literal `Å — α` unchanged and verified its code points. Every corrected trial's requested command and returned result matches the received bridge audit exactly, without truncation or MCP transport errors.

Core utilities remained visible. These checks verify the actual fresh context, mounted files and executed workspace MCP route; they do not certify containment against a hostile agent. See the [reusable runtime recipe](ISOLATED-BENCHMARK-RUNTIME.md), whose paths, image, credentials, model and settings are resolved by the agent/user.

An independent reviewer received neutral entry labels, fixtures, actual deliverables and final responses, without condition assignments, candidate resources or traces. Content can reveal guidance use, so blinding was partial. The [reviewer receipt](../evals/results/2026-10-03-batch1/reviewer-receipt.json) retains parsed artifact observations and semantic verdicts; private paths are replaced with public relative paths and the condition mapping was added after review. Trace/isolation/preservation auditing was performed separately by the coordinator.

## Corrected matched observations

App-native has two attempted and accepted trials per condition. Release-changed baseline completion is **2/2**, while skill completion is **1/2** because the second trial omitted `output/review.md`. Its correct final response did not deliver the requested file. Acceptance applies to the offline benchmark task, not vendor compatibility or release approval.

The table compares the accepted primary app-native trials. Positive changes mean a higher skill mean. Release attempt metrics remain in the ledger; their means include an early missing-deliverable failure and are not a time-to-accepted-output comparison. The separate post-clarification release pair is retained without pooling or replacing primary results.

| Case / metric | Baseline mean | Skill mean | Skill mean change |
| --- | ---: | ---: | ---: |
| app-native elapsed seconds | 278.23 | 307.66 | +10.58% |
| app-native input tokens | 262,319.00 | 223,433.00 | -14.82% |
| app-native output tokens | 7,952.00 | 9,011.50 | +13.32% |
| app-native workspace shell calls | 12.50 | 10.50 | -16.00% |

`app-native` skill-minus-baseline elapsed differences were +58.93, -0.07 seconds.

Elapsed time covers CLI launch through completion, including model/tool startup and excluding container provisioning. CLI token counts accumulate across the turn and include cached input. Cached input means were app-native: 207,552 baseline / 187,328 skill. Tool counts mean recorded workspace MCP calls, not every code-mode wrapper operation. Remote latency, cache variation, concurrent scheduling and output detail limit interpretation. Two repetitions cannot establish a reliable speed/cost difference, and no monetary cost is estimated.

## Actual artifacts and decisions

All four corrected app-native packages match the supplied identity, version, author, disabled state, roles, decoded Unicode/XML-sensitive title, search and time range. Each archive contains one app-root directory and exactly the four selected regular files, with archived bytes matching source files. All are 708 bytes with SHA-256:

```text
322b37a1178f420d7b6853881a6f50d1984487f80656dfe8523a73292473d8fd
```

Reports and verification records were checked against actual parsed values and package bytes. All corrected app reports passed fidelity review. AppInspect, target compatibility, installation and live behavior remain unrun.

All three delivered primary release reports independently identify current artifact B's digest and the mismatched A subject/source revision. The fourth trial's final response states these facts correctly, but its required file is absent. Its artifact criterion fails while the final-only source-gap and next-check semantic criteria pass. Delivered reports leave B's package gate incomplete and request a maintained check with new exact-B bindings; they do not relabel A's old pass. The helper's expected incomplete verdict returns exit code 1. Nonzero shell results, including recovered missing-tool attempts and expected incomplete verdicts, remain visible per run and differ from MCP transport failures.

## Retained defects and reruns

The first bridge decoded UTF-8 stdin using Windows CP1252. Exact CLI/audit cross-checking found ten changed commands across nine of the 14 earlier attempts. All 14 are excluded from performance conclusions, including those without an observed changed command. Their original artifacts, requested/received commands, metrics and artifact grades remain available for diagnosis. Their timings are not used in the table above.

One original app report's `Å` became `Ã…` through this transport defect while its XML/package remained correct. The [original report](../evals/results/2026-10-03-batch1/runs/app-native-r2-skill/output/report.md) remains beside an explicitly [evaluator-corrected copy](../evals/results/2026-10-03-batch1/runs/app-native-r2-skill/output/report.corrected.md); original scored output and metrics were preserved. An unchanged diagnostic pair then exposed [material false report/check descriptions](../evals/results/2026-10-03-batch1/runs/app-native-r2-baseline-rerun/output/report.md) about literal backslashes absent from the decoded title/query. Correct package bytes did not make those claims true: completion was rejected under the predeclared no-critical-correctness-regression rule. That legacy artifact rejection does not supply a valid performance comparison.

A narrow shared validation-reference correction at `d6caf1e55b759b5051576cc2350d8f63a14dd878` added parsed-value/UTF-8 reporting guidance available to both conditions. Four fresh app attempts passed artifact review, but still used the defective transport and remain excluded. Fixtures, native helper and skill entrypoint were unchanged. After identifying the bridge defect, strict UTF-8 stdio and a legacy-stream regression test were added, and the entire eight-trial batch was rerun with fresh independent agents.

The evaluator also corrected panel-title and tar-root inspection assumptions, repeated affected artifact checks and confirmed nested JSON escaping without changing fixtures. One corrected-cohort evaluator receipt initially had a mistyped source label; the original label and correction are retained privately. Only that unmounted receipt and its bound review-record hashes changed; agent inputs did not.

The second primary release skill worker interpreted the host's read-only filesystem setting as also prohibiting writes through the separately writable MCP container. It attempted no output write and returned response-only prose. This [missing-deliverable failure](../evals/results/2026-10-03-batch1/runs/release-changed-r2-skill-utf8/result.json) remains in the primary denominator. Both conditions then received the same explicit clarification distinguishing the host filesystem from the authorized `/workspace/output` destination. Task, fixtures, skill/resources, model/reasoning, tools, CLI sandbox and mounts were unchanged. A fresh write/Unicode/isolation probe passed, followed by a separate fresh repetition-two pair; both reports passed artifact review. This resolves the observed harness ambiguity without erasing the original failure or establishing a treatment effect.

Across 24 task attempts, 22 artifact completions were accepted and two rejected: one legacy material reporting failure and one primary missing report. Fourteen legacy trials are excluded from performance conclusions. The eight primary corrected attempts and two separate repair attempts have verified UTF-8 transport; they are not pooled. There were no in-trial human corrections. One separate post-trial report copy was corrected. Six infrastructure preflights remain outside the task denominator: three readiness failures, an ASCII-only pass that missed the encoding defect, a Unicode/isolation pass, and a subsequent Unicode/write/isolation pass. Failures and fixes are recorded in the ledger and runtime recipe.

## Publication and decision

Full original CLI traces, stderr, contexts, container inspections and failure records stay private. Public evidence includes original synthetic inputs/outputs, unredacted requested/received workspace commands/results, final responses, copied-byte receipts, independent artifact review, reviewed records, exact source-byte snapshots and an [evidence hash manifest](../evals/results/2026-10-03-batch1/evidence-manifest.json). Git attributes preserve evidence line endings; staged/remote byte checks bind the manifest to published files. Full CLI trace hashes are retained, but their contents are excluded because runtime warnings contain workstation paths.

Temporary experiment authentication copies were removed after workers exited, and exact experiment containers are stopped. Private portfolio records, customer material, workstation paths, environment values, authentication and account-linked context are excluded from GitHub. Synthetic names are fixture values, not consumer defaults.

Keep both skills as pilots. Both conditions can deliver accepted offline artifacts and evidence decisions, but the primary release skill condition also has a retained delivery failure. These small samples do not establish a reliable correctness or efficiency benefit or trigger quality. Next run `app-conflict` and `release-soak` under the corrected transport and clarified write boundary, followed by the three instruction-only pilots. Set a larger sample and decision thresholds before promotion; qualify real vendor/runtime or consumer acceptance separately.
