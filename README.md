# Skills for Codex

Reusable skills and original helper assets for agents and users. Project-specific values are resolved from the target project or supplied explicitly; no skill depends on the maintainer's machine, credentials or private repositories.

## Available skills

| Skill | Capability | Status |
| --- | --- | --- |
| [splunk-app-authoring](skills/splunk-app-authoring/SKILL.md) | Choose a Splunk app approach, resolve inputs, author an app and qualify its package | Initial pilot; bundled native scaffold and packaging helper |
| [release-qualification](skills/release-qualification/SKILL.md) | Assess a candidate against chosen targets/gates and keep evidence bound to the tested source/artifacts | Initial pilot; read-only evidence record helper |
| [zeepkist-api-research](skills/zeepkist-api-research/SKILL.md) | Establish installed symbol contracts while separating code, catalogs and live evidence | Instruction pilot; consumer-provided runtime/tools |
| [source-claim-audit](skills/source-claim-audit/SKILL.md) | Verify scoped claims, source mappings and unresolved conflicts | Instruction pilot; original claim register/schema |
| [splunk-estate-assessment](skills/splunk-estate-assessment/SKILL.md) | Assess authorized estate evidence with explicit inventory coverage | Instruction pilot; consumer connector or sanitized export |

The authoring skill supports existing projects and user-selected starters. The bundled helper creates a minimal native Simple XML dashboard app and packages an explicit file list. React and REST/CRUD implementations require an appropriate target project or starter and task-specific implementation.

Release qualification uses the consumer's maintained checks and acceptance policy. Its helper verifies selected hashes and recorded bindings; it neither executes the checks nor establishes release approval. [The record contract](skills/release-qualification/references/record.md) describes explicit target, artifact and evidence inputs.

The remaining skills provide focused instructions, references and unresolved input templates. They do not bundle game binaries, decompiled code, Splunk discovery engines, customer exports or source inventories. Resolve paths, targets, tool providers, audit scopes and budgets from the consumer's task.

## Use a skill

Clone or download this repository. Ask your agent to use the selected `skills/<name>/SKILL.md`, or copy the entire skill folder into a skill directory supported by your host. For current Codex discovery and installation behavior, see [Build skills](https://learn.chatgpt.com/docs/build-skills).

Example request:

> Use $splunk-app-authoring to create a native service health dashboard in my chosen workspace. Resolve the app identity and target requirements from my brief; list any remaining decisions.

> Use $release-qualification to review this candidate for my specified target and release purpose. Use my project's maintained checks, preserve existing artifacts, and report the required evidence gaps.

Read [the portability contract](docs/PORTABILITY.md) for how values are supplied. Assets containing example values are demonstrations, not defaults for a user's app.

## Helper example

From the repository root, select a new output directory and run:

```text
python skills/splunk-app-authoring/scripts/splunk_app.py scaffold --config skills/splunk-app-authoring/assets/native-app.example.json --output work/example_health
python skills/splunk-app-authoring/scripts/splunk_app.py validate --app work/example_health --files work/example_health/release-files.json
python skills/splunk-app-authoring/scripts/splunk_app.py package --app work/example_health --files work/example_health/release-files.json --output dist/example_health-0.1.0.tar.gz
```

The example identity, author, search, time range and roles are defined in the example config. Replace them with agent/user-defined values for your app. The helper refuses existing scaffold destinations and existing package outputs.

## Validation

```text
python -m unittest discover -s tests -v
python scripts/validate_collection.py
```

CI runs these checks on Windows and Linux with Python 3.10 and 3.13. [Evaluation status and cases](docs/EVALUATION.md) distinguish helper tests from agent behavior, vendor validation and live acceptance. Passing a local helper is not an AppInspect approval, a runtime test or release authorization.

The [first benchmark wave](docs/BENCHMARKS.md) supplies ten synthetic tasks, matched baseline/skill workspace preparation, hash receipts, review rubrics and unrun result templates. Supporting resources are identical in both conditions. The preparer does not launch agents or establish performance gains.

## Contributing and license

Contributions should satisfy the portability contract, include observable acceptance cases and retain accurate evidence limits. Add only task-specific guidance that changes agent decisions.

New original instructions, schemas and helpers are available under the [MIT license](LICENSE). Splunk and other external platforms retain their own licenses and terms. This collection is independent of Splunk and OpenAI; no vendor approval is implied.
