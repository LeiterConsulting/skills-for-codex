# Portability contract

A public skill must work with a reader's project and machine. Resolve variable values from task context, inspected project metadata or explicit user input. If an agent proposes a value, identify it as a choice; do not present it as discovered fact.

## Input ownership

| Value category | How to resolve it | Where it belongs |
| --- | --- | --- |
| Workspace, application root, output paths | User choice or current target workspace | Command arguments or a local input record |
| App ID, label, author, version | Existing app metadata; for new apps, agent/user-defined identity | App config and local input record |
| Deployment, exact product version, OS and release purpose | Current target evidence or user context | Local task record; unknown stays unknown |
| Data indexes, fields, searches and time ranges | Authorized schema/requirements or explicit synthetic fixture | App assets after review |
| ACL role names and sharing | Target's supported roles plus agent/user-selected policy | App metadata; never an inherited maintainer default |
| Endpoint, account, organization or repository | Explicit target or reliable current project metadata | Local task record or host configuration |
| Credentials and tokens | Target's approved credential/secret mechanism | Secret store; not examples, source files or ordinary JSON |
| External starter/template | Agent/user-selected source, revision and reuse rights | Local input record with provenance |
| Branding, locale and license | User requirement or stated agent proposal | Project assets/metadata |

Examples may contain clearly fictional, self-contained values. They must not activate automatically as a user's configuration. Runtime inputs use a schema or documented contract; missing values are not substituted with a maintainer's machine or company.

## Discovery and choices

Read relevant target instructions and manifests first. Reuse an existing app identity when updating it. For a new app, an agent may propose a conservative ID, label, version and author based on the request, stating its choices. Ask only when the missing decision changes correctness or access. Unknown deployment details need not block offline authoring, but they prevent unsupported compatibility claims.

Keep source/version provenance in a local record. Do not put a private inventory, workstation path, personal contact, target host or customer fixture into a public release. Original reusable logic and sanitized synthetic fixtures belong in this collection; copied third-party code requires compatible reuse terms.

## Dependencies and validation

Skills describe workflows. A script performs deterministic mechanics. A template is input or output material. A connector supplies runtime access. Declare those dependencies separately.

Every executable helper should accept explicit paths, preserve unrelated content, report bounded failures and produce verifiable artifacts. Test meaningful behavior across different identities and locations. Record structural/package checks, vendor validation and actual runtime acceptance separately.
