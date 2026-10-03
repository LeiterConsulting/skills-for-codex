---
name: splunk-app-authoring
description: Author or update Splunk Enterprise or Cloud apps, choosing native dashboards or project-specific UI/backend code, then qualify the package. Use for app creation and substantial app changes; a small existing-view edit must preserve the app.
---

# Splunk app authoring

Turn the user's requirement into a maintainable Splunk app using the current target's instructions and explicit project inputs. Keep existing app identity and unrelated work when updating an app.

## Resolve the target

Inspect the workspace, app metadata, data assumptions and available build/package commands. Resolve workspace/output paths, identity, author, version, deployment, data/search scope and access roles using [inputs.md](references/inputs.md). An agent may discover or propose values; record their origins. Example assets contain fictional values, not user defaults. Keep credentials in the host's approved secret mechanism.

Clarify only decisions that affect the requested behavior or access. Unknown version or deployment details do not prevent offline work; retain them as unknown in the acceptance record.

## Choose and implement

Prefer native dashboards/configuration when they meet the requirement. Read [architecture.md](references/architecture.md) for native, search-driven, React and REST/CRUD choices. Use existing project scripts and supported components. If a starter is needed, select its source/revision and reuse terms with the user or from the target context; no private starter is required by this skill.

For a new minimal native dashboard, the optional [helper](scripts/splunk_app.py) accepts a complete config using [native-app.schema.json](assets/native-app.schema.json). It creates a new app only and never installs it. Use a caller-chosen destination whose final directory name matches the chosen app ID. For an existing app, edit its implementation instead of running scaffold.

For custom UI/backend work, implement the requested behavior in the chosen project. Keep routes, handlers, views and permissions aligned. Do not substitute the minimal native scaffold for a requested React or CRUD application.

## Validate and deliver

Run the target's relevant checks. Read [validation.md](references/validation.md) for package and runtime evidence. The helper validates selected structure/XML and packages only an explicit release file list. It is not AppInspect, a complete Splunk validator, a secret scanner, or an installer.

Inspect the real archive contents and app identity. Preserve runtime configuration, credentials and unrelated files outside the release package. Report source/build/package, AppInspect and installed/live results separately, with unavailable checks identified.

Deliver the affected app/assets, chosen inputs and their origins, commands/results, artifact digest, and remaining acceptance gaps. Measure behavior before claiming that this skill improves performance.
