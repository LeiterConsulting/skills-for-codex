# Choose a Splunk app architecture

Use native configuration and dashboards for requirements they can meet. Choose Classic Simple XML or Dashboard Studio based on the target version and requested interactions. The bundled helper creates only one Simple XML table with an inline, explicitly supplied search.

For a search-driven app, define indexes/fields, time scope, saved searches/macros/lookups and the permission model before custom UI. Preserve token and search semantics when editing existing views.

Use custom React when native views cannot support the required interaction. Select a current compatible starter/toolchain from the target context. Prefer supported Splunk UI components, isolate request handling, and honor the app namespace and Splunk Web routing. Preserve existing build and packaging scripts.

For REST/CRUD behavior, define persistence, input validation, authorized read/write operations, response receipts and target-specific session/CSRF handling. Register narrow handlers and expose only the necessary Web routes. A failed or empty write response must not be presented as confirmed success. Keep secrets out of browser code and generated assets.

This skill does not ship a React starter or pretend its native helper implements backend operations. A requested React/CRUD app requires actual project code and relevant runtime validation.

## Official references

Verify details against the exact target release.

- [app.conf reference](https://help.splunk.com/en/data-management/splunk-enterprise-admin-manual/9.4/configuration-file-reference/9.4.1-configuration-file-reference/app.conf)
- [Simple XML reference](https://help.splunk.com/en/splunk-enterprise/create-dashboards-and-reports/simple-xml-dashboards/9.1/simple-xml-reference/simple-xml-reference)
- [Splunk app development resources](https://help.splunk.com/en/splunk-enterprise/get-started/overview/10.2/splunk-enterprise-resources-and-documentation/customize-and-extend-splunk-enterprise)
