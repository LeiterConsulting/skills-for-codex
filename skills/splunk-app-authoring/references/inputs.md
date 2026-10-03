# Inputs and local choices

Use [authoring-inputs.example.json](../assets/authoring-inputs.example.json) as a local record shape. Nulls intentionally require resolution. Do not run it as a scaffold config.

| Input | Required when | Resolution |
| --- | --- | --- |
| workspace and app_root | All app work | User-selected/current target; inspect existing content |
| operation | All app work | create or update from the actual request |
| app_id, app_label, author, version | App output | Preserve existing metadata or define/propose for a new app |
| deployment and splunk_version | Compatibility/live claims | Confirm from target evidence; unknown for offline work is allowed |
| app_shape | All app work | Native, search-driven, React or REST/CRUD based on requirement |
| data_contract | Real data behavior | Define indexes, fields, access, query and time range |
| read_roles and write_roles | Published app objects | Resolve actual target roles and chosen sharing |
| template_source and template_revision | External starter use | Define source, version and reuse terms |
| output_path | Packaging | Choose a new path; preserve earlier artifacts |
| acceptance | Completion | State structural, package, AppInspect and runtime criteria |

A local record can annotate each resolved field with an origin: user, observed project metadata, or stated agent choice. Conflicts are surfaced rather than silently resolved by the example config.

## Bundled native helper

The helper has a deliberately smaller config contract. Every value is supplied in JSON:

- schema_version: 1
- app_id: lowercase letter followed by lowercase letters, digits or underscores; 3–63 characters
- app_label, author and description: bounded single-line text
- version: Major.Minor.Revision, optionally followed by a single alphanumeric suffix using + or -
- install_state: enabled or disabled
- read_roles, write_roles: nonempty arrays of explicitly chosen role names, or the wildcard *
- dashboard: title, query, earliest and latest; all explicitly supplied

The helper implements a conservative portable subset, not every valid Splunk app ID/version or every dashboard form. The query is written as inert XML text. It is not executed or judged for data access or SPL safety.

[The native example](../assets/native-app.example.json) is a synthetic demonstration. Copy and adapt it only when that scaffold meets the request. Paths are supplied with --config, --app, --files and --output, never stored as maintainer defaults.

The release manifest contains schema_version and a list of relative POSIX file paths. An agent or user selects the release content. The helper rejects traversal, linked files and private configuration/key filenames. These checks do not guarantee the absence of secrets in selected file contents; review those contents before external distribution.
