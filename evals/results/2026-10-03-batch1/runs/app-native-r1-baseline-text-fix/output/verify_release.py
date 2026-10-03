#!/usr/bin/env python3
"""Verify the offline release against JSON-decoded fixture values; write receipts."""
import configparser
import hashlib
import json
from pathlib import Path
import tarfile
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / 'output'
CONFIG = ROOT / 'input/native.json'
APP = OUT / 'bench_delta'
ARCHIVE = OUT / 'bench_delta-0.2.1.tar.gz'


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_json(path):
    return json.loads(path.read_text(encoding='utf-8'))


def conf_from(data):
    conf = configparser.ConfigParser(interpolation=None)
    conf.read_string(data.decode('utf-8'))
    return conf


checks = []


def check(name, condition):
    if not condition:
        raise AssertionError(name)
    checks.append({'name': name, 'status': 'passed'})


config = read_json(CONFIG)
build = read_json(OUT / 'build-receipt.json')
check('Input fixture unchanged since scaffold', sha256(CONFIG) == build['provenance']['input']['sha256'])
check('Supplied helper unchanged', sha256(ROOT / build['provenance']['helper']['path']) == build['provenance']['helper']['sha256'])
check('Scaffold, helper validation and package commands succeeded',
      len(build['commands']) == 3 and all(c['exit_code'] == 0 for c in build['commands']))
manifest = read_json(APP / 'release-files.json')
selected = manifest['files']
expected_files = [
    'default/app.conf', 'default/data/ui/nav/default.xml',
    'default/data/ui/views/home.xml', 'metadata/default.meta',
]
check('Release manifest selects exactly the four native files',
      manifest == {'schema_version': 1, 'files': expected_files})
check('App root exactly matches supplied identity', APP.name == config['app_id'])
check('App tree contains only selected files and scaffold manifest',
      sorted(str(p.relative_to(APP)) for p in APP.rglob('*') if p.is_file()) == sorted(selected + ['release-files.json']))
check('App tree has no symbolic links', not any(p.is_symlink() for p in APP.rglob('*')))
contents = {name: (APP / name).read_bytes() for name in selected}
check('All selected contents decode as UTF-8', all(isinstance(data.decode('utf-8'), str) for data in contents.values()))
conf = conf_from(contents['default/app.conf'])
expected_conf = {
    'install': {'state': config['install_state']},
    'ui': {'is_visible': 'true', 'label': config['app_label'], 'default_view': 'home'},
    'launcher': {'author': config['author'], 'version': config['version'], 'description': config['description']},
    'package': {'id': config['app_id']},
    'id': {'name': config['app_id'], 'version': config['version']},
}
check('app.conf identity, metadata and disabled state exactly match supplied values',
      {section: dict(conf[section]) for section in conf.sections()} == expected_conf)
expected_acl = ('[]\naccess = read : [ ' + ', '.join(config['read_roles']) +
                ' ], write : [ ' + ', '.join(config['write_roles']) + ' ]\nexport = none\n')
check('ACL contains exactly supplied read/write roles with export=none',
      contents['metadata/default.meta'].decode('utf-8') == expected_acl)
nav = ET.fromstring(contents['default/data/ui/nav/default.xml'])
check('Navigation selects existing home view', nav.tag == 'nav' and nav.attrib == {'search_view': 'search'}
      and len(nav) == 1 and nav[0].tag == 'view' and nav[0].attrib == {'name': 'home', 'default': 'true'})
dashboard = ET.fromstring(contents['default/data/ui/views/home.xml'])
check('Simple XML 1.1 dashboard contains one row/panel/table/inline search',
      dashboard.tag == 'dashboard' and dashboard.attrib == {'version': '1.1', 'theme': 'light'}
      and len(dashboard.findall('row')) == 1 and len(dashboard.findall('./row/panel')) == 1
      and len(dashboard.findall('.//table')) == 1 and len(dashboard.findall('.//search')) == 1)
nodes = {
    'app_label': dashboard.find('label'),
    'title': dashboard.find('./row/panel/title'),
    'query': dashboard.find('./row/panel/table/search/query'),
    'earliest': dashboard.find('./row/panel/table/search/earliest'),
    'latest': dashboard.find('./row/panel/table/search/latest'),
}
parsed_values = {}
for key, node in nodes.items():
    expected = config['app_label'] if key == 'app_label' else config['dashboard'][key]
    check(f'Parsed XML {key} exactly equals decoded fixture Unicode text',
          node is not None and len(node) == 0 and node.text == expected)
    parsed_values[key] = node.text
check('Title contains U+00C5 and no literal backslash',
      '\u00c5' in parsed_values['title'] and '\\' not in parsed_values['title'])
check('Query contains two U+0022 quotes and no literal backslash',
      parsed_values['query'].count('"') == 2 and '\\' not in parsed_values['query'])

with tarfile.open(ARCHIVE, 'r:gz') as archive:
    members = archive.getmembers()
    archive_names = [member.name for member in members]
    expected_names = [config['app_id']] + [config['app_id'] + '/' + name for name in sorted(selected)]
    check('Archive has exactly one app root and four selected files', archive_names == expected_names)
    check('Archive contains only one directory and regular files; no links',
          members[0].isdir() and all(member.isfile() for member in members[1:]))
    check('Archive has normalized owners, modes and timestamps',
          all(member.uid == 0 and member.gid == 0 and member.uname == '' and member.gname == ''
              and member.mtime == 0 and member.mode == (0o755 if member.isdir() else 0o644)
              for member in members))
    for name in selected:
        check(f'Archive bytes equal selected source: {name}',
              archive.extractfile(config['app_id'] + '/' + name).read() == contents[name])
archive_sha = sha256(ARCHIVE)
check('Archive size and SHA-256 match package receipt',
      ARCHIVE.stat().st_size == build['commands'][-1]['result']['archive_bytes']
      and archive_sha == build['commands'][-1]['result']['sha256'])
check('SHA-256 sidecar matches archive',
      (OUT / (ARCHIVE.name + '.sha256')).read_text(encoding='utf-8') == archive_sha + '  ' + ARCHIVE.name + '\n')

receipt = {
    'schema_version': 1, 'status': 'passed', 'evidence_kind': 'offline synthetic fixtures',
    'checks': checks, 'parsed_xml_values': parsed_values,
    'codepoints': {key: [f'U+{ord(char):04X}' for char in parsed_values[key]] for key in ('title', 'query')},
    'selected_files': {name: {'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest()} for name, data in contents.items()},
    'archive': {'path': str(ARCHIVE.relative_to(ROOT)), 'bytes': ARCHIVE.stat().st_size,
                'sha256': archive_sha, 'members': archive_names},
    'verifier': {'path': 'output/verify_release.py', 'sha256': sha256(Path(__file__))},
    'compatibility': {'deployment': None, 'splunk_version': None, 'appinspect': 'not_run', 'installed': False, 'runtime': 'not_run'},
}
(OUT / 'verification-receipt.json').write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

report = f'''# Delta app release report

Created `output/bench_delta` and `output/{ARCHIVE.name}` from `input/native.json` using the unmodified supplied helper. This is offline work with synthetic fixtures; it provides source and structure/package evidence only.

## Supplied values preserved

| Field | Exact decoded value |
| --- | --- |
| App ID | `{config['app_id']}` |
| App label | `{parsed_values['app_label']}` |
| Author | `{config['author']}` |
| Version | `{config['version']}` |
| Description | `{config['description']}` |
| Install state | `{config['install_state']}` |
| Read roles | `{', '.join(config['read_roles'])}` |
| Write roles | `{', '.join(config['write_roles'])}` |
| Panel title | `{parsed_values['title']}` |
| Earliest | `{parsed_values['earliest']}` |
| Latest | `{parsed_values['latest']}` |

The inline search is exactly:

```spl
{parsed_values['query']}
```

JSON-decoded strings were compared directly with parsed XML text. The title contains `{parsed_values['title'][-1]}` (U+00C5). The query contains ordinary double quotes (U+0022). Neither string contains a literal backslash (U+005C). XML entities preserve the supplied ampersands and angle brackets as text; the parsed label, title, query and both time bounds equal the input. Code point receipts record the actual characters.

## Release selection and completed checks

The selected release comprises:

{chr(10).join('- `' + name + '`' for name in selected)}

`release-files.json` remains in the app scaffold as the explicit release selection. It is excluded from the archive, as are this report, digest, verification script and receipts. The archive has one `bench_delta/` root directory and exactly four regular files.

- Passed the supplied helper's config contract during scaffold creation. No separate JSON Schema validation is claimed.
- Passed the helper's selected-file/path checks, app identity/version checks, XML parsing and navigation/default-view checks; all three helper commands exited 0.
- Passed independent comparisons for all supplied app metadata, disabled installation state, exact role ACLs (`export = none`), Simple XML layout and home navigation.
- Passed direct Unicode equality assertions for all dashboard text and time bounds, including code point checks for the title and search quotes.
- Reviewed all four selected UTF-8 files: they contain only app metadata, navigation, the fixture dashboard and ACLs. No local configuration, credentials, dependencies or unrelated workspace content is selected.
- Passed archive membership, file type, normalized owner/mode/time checks and byte-for-byte comparisons of every packaged file with its selected source.
- Passed digest/size comparisons against the package receipt and digest sidecar. Confirmed input and helper hashes are unchanged from the creation record.

`output/build-receipt.json` retains the helper commands, exit codes and results. `output/verification-receipt.json` retains {len(checks)} passed assertions, parsed values, code points, file hashes and archive membership. Re-run the independent checks with `python3 output/verify_release.py` from the workspace.

Archive size: **{ARCHIVE.stat().st_size} bytes**. SHA-256:

```text
{archive_sha}  {ARCHIVE.name}
```

Digest sidecar: `output/{ARCHIVE.name}.sha256`.

Input SHA-256: `{build['provenance']['input']['sha256']}`. Helper SHA-256: `{build['provenance']['helper']['sha256']}`. The helper has no separate source revision supplied; its hash identifies the resource used.

## Remaining compatibility and evidence limits

No deployment target is selected. Splunk product, exact version, target platform and applicable AppInspect/vetting requirements remain unresolved. Compatibility of Simple XML 1.1 and the configuration with a particular Splunk release is unverified. The supplied role names are preserved, but their existence and effective access on any target are unverified.

AppInspect was not run. The package was not installed, and no live search, navigation, browser or permission checks ran. The inline SPL and relative time bounds were preserved as inert text, not executed or semantically validated against Splunk. Structural validation does not establish full Splunk configuration or ACL semantics, successful search results, installation acceptance or live behavior. These synthetic fixtures are not live evidence.

No authoring input needed for this offline deliverable remains unresolved. Target-specific compatibility and runtime evidence require a later authorized workflow; no connection, publication, installation, game launch or schedule change was performed.
'''
(OUT / 'report.md').write_text(report, encoding='utf-8')
print(json.dumps({'status': 'passed', 'checks': len(checks), 'sha256': archive_sha, 'report': 'output/report.md'}, indent=2))
