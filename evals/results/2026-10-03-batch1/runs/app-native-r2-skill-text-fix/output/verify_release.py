#!/usr/bin/env python3
"""Offline verification of this fixture's exact source and selected release."""
import configparser
import hashlib
import json
from pathlib import Path
import re
import shlex
import tarfile
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / 'output'
config = json.loads((ROOT / 'input/native.json').read_text(encoding='utf-8'))
app = OUT / config['app_id']
archive_path = OUT / f"{config['app_id']}-{config['version']}.tar.gz"
checks = []
text_checks = []


def check(name, condition, **evidence):
    if not condition:
        raise AssertionError(name)
    checks.append({'name': name, 'status': 'passed', **evidence})


def dump(path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


receipts = {}
for operation in ('scaffold', 'validate', 'package'):
    receipt = json.loads((OUT / f'{operation}-receipt.json').read_text(encoding='utf-8'))
    check(f'{operation} command succeeded', receipt['exit_code'] == 0, exit_code=receipt['exit_code'])
    receipt['result'] = json.loads(receipt['stdout'])
    receipts[operation] = receipt

manifest = json.loads((app / 'release-files.json').read_text(encoding='utf-8'))
selected = [
    'default/app.conf',
    'default/data/ui/nav/default.xml',
    'default/data/ui/views/home.xml',
    'metadata/default.meta',
]
check('Explicit release selection', manifest == {'schema_version': 1, 'files': selected}, files=selected)
source = {name: (app / name).read_bytes() for name in selected}


def verify_content(content, scope):
    conf = configparser.ConfigParser(interpolation=None)
    conf.read_string(content['default/app.conf'].decode('utf-8'))
    values = {
        ('install', 'state'): config['install_state'],
        ('ui', 'label'): config['app_label'],
        ('ui', 'is_visible'): 'true',
        ('ui', 'default_view'): 'home',
        ('launcher', 'author'): config['author'],
        ('launcher', 'version'): config['version'],
        ('launcher', 'description'): config['description'],
        ('package', 'id'): config['app_id'],
        ('id', 'name'): config['app_id'],
        ('id', 'version'): config['version'],
    }
    check(f'{scope}: identity and app configuration', all(conf.get(*key) == value for key, value in values.items()))
    expected_meta = ('[]\naccess = read : [ ' + ', '.join(config['read_roles']) +
                     ' ], write : [ ' + ', '.join(config['write_roles']) + ' ]\nexport = none\n')
    check(f'{scope}: explicit roles and app-local export', content['metadata/default.meta'].decode('utf-8') == expected_meta,
          read_roles=config['read_roles'], write_roles=config['write_roles'], export='none')
    dashboard = ET.fromstring(content['default/data/ui/views/home.xml'])
    check(f'{scope}: native Simple XML shape', dashboard.tag == 'dashboard' and dashboard.get('version') == '1.1'
          and len(dashboard.findall('./row/panel/table/search')) == 1)
    for path, expected in (
        ('label', config['app_label']),
        ('row/panel/title', config['dashboard']['title']),
        ('row/panel/table/search/query', config['dashboard']['query']),
        ('row/panel/table/search/earliest', config['dashboard']['earliest']),
        ('row/panel/table/search/latest', config['dashboard']['latest']),
    ):
        actual = dashboard.findtext(path)
        check(f'{scope}: decoded XML {path} equals supplied value', actual == expected)
        text_checks.append({'scope': scope, 'xml_path': path, 'expected': expected, 'actual': actual,
                           'equal': True, 'expected_code_points': [f'U+{ord(c):04X}' for c in expected],
                           'actual_code_points': [f'U+{ord(c):04X}' for c in actual]})
    nav = ET.fromstring(content['default/data/ui/nav/default.xml'])
    views = nav.findall('view')
    check(f'{scope}: default navigation resolves to released home view', nav.tag == 'nav'
          and nav.get('search_view') == 'search' and len(views) == 1
          and views[0].attrib == {'name': 'home', 'default': 'true'}
          and conf.get('ui', 'default_view') == views[0].get('name'))


verify_content(source, 'Source')
with tarfile.open(archive_path, 'r:gz') as archive:
    members = archive.getmembers()
    names = [member.name for member in members]
    root = config['app_id']
    expected_names = [root] + [f'{root}/{name}' for name in sorted(selected)]
    check('Archive contains exactly one app root and selected release files', names == expected_names, members=names)
    check('Archive uses regular files with expected permissions', members[0].isdir()
          and members[0].mode == 0o755 and all(m.isfile() and m.mode == 0o644 for m in members[1:]))
    check('Archive ownership and timestamps are normalized', all(m.uid == 0 and m.gid == 0 and m.mtime == 0 for m in members))
    packaged = {name: archive.extractfile(f'{root}/{name}').read() for name in selected}
    check('Archive file bytes match inspected release sources', packaged == source)
    inventory = [{'name': m.name, 'type': 'directory' if m.isdir() else 'regular_file',
                  'size': m.size, 'mode': oct(m.mode), 'mtime': m.mtime} for m in members]
verify_content(packaged, 'Archive')

payload = archive_path.read_bytes()
digest = hashlib.sha256(payload).hexdigest()
package_result = receipts['package']['result']
check('Independent archive digest and size match helper receipt', digest == package_result['sha256']
      and len(payload) == package_result['archive_bytes'], sha256=digest, archive_bytes=len(payload))
check('Helper receipt identity and selected files match supplied release', package_result['app_id'] == config['app_id']
      and package_result['version'] == config['version'] and package_result['selected_files'] == sorted(selected))

schema = json.loads((ROOT / 'candidate/assets/native-app.schema.json').read_text(encoding='utf-8'))
check('Supplied version matches bundled schema regex', re.fullmatch(schema['properties']['version']['pattern'], config['version']) is not None)
check('Fixture title contains U+00C5', ord(config['dashboard']['title'][-1]) == 0x00C5)
check('Fixture query contains quotes without literal backslashes', config['dashboard']['query'].count(chr(34)) == 2
      and chr(92) not in config['dashboard']['query'])

before = json.loads((OUT / 'source-hashes.json').read_text(encoding='utf-8'))
after = {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
         for p in sorted(ROOT.rglob('*')) if p.is_file() and OUT not in p.parents}
check('All original workspace files preserved', before == after, file_count=len(before))

(OUT / f'{archive_path.name}.sha256').write_text(f'{digest}  {archive_path.name}\n', encoding='utf-8')
verification = {'command': 'python3 output/verify_release.py', 'status': 'passed',
                'check_count': len(checks), 'checks': checks, 'text_comparisons': text_checks,
                'archive': {'path': str(archive_path.relative_to(ROOT)), 'sha256': digest,
                            'bytes': len(payload), 'members': inventory},
                'release_file_hashes': {name: hashlib.sha256(data).hexdigest() for name, data in source.items()}}
dump(OUT / 'verification.json', verification)

record = {
    'workspace': '/workspace', 'app_root': 'output/bench_delta', 'operation': 'create',
    'app_id': config['app_id'], 'app_label': config['app_label'], 'author': config['author'], 'version': config['version'],
    'deployment': None, 'splunk_version': None, 'app_shape': 'native Classic Simple XML',
    'data_contract': {'fixture_type': 'synthetic offline', **config['dashboard'],
                      'indexes': None, 'fields': ['status'], 'execution': 'not_run'},
    'read_roles': config['read_roles'], 'write_roles': config['write_roles'],
    'template_source': 'candidate/scripts/splunk_app.py',
    'template_revision': {'sha256': before['candidate/scripts/splunk_app.py']},
    'template_reuse_terms': 'Supplied workspace helper authorized for this task; no external starter used.',
    'output_path': str(archive_path.relative_to(ROOT)), 'native_config': config,
    'acceptance': {'source': 'passed', 'build': 'not_applicable_native_app', 'structure_package': 'passed',
                   'appinspect': 'not_run', 'installed': 'not_run', 'live': 'not_run'},
    'input_origins': {**{key: 'input/native.json' for key in config},
                     'workspace': 'Provided workspace MCP shell',
                     'app_root': 'TASK.md', 'operation': 'TASK.md', 'app_shape': 'TASK.md',
                     'deployment': 'TASK.md: no selected deployment target',
                     'splunk_version': 'Not supplied; unknown', 'output_path': 'TASK.md',
                     'template_source': 'Supplied candidate skill/helper',
                     'release_selection': 'Agent selected the four generated runtime files; manifest retained outside archive',
                     'dashboard_layout': 'Supplied helper: one table, home default view, panel title, dashboard label from app_label'},
}
dump(OUT / 'authoring-inputs.json', record)

commands = '\n'.join(f"- `{shlex.join(receipts[op]['command'])}` - exit {receipts[op]['exit_code']}."
                     for op in ('scaffold', 'validate', 'package'))
file_list = '\n'.join(f'- `{name}`' for name in sorted(selected))
report = f'''# Offline native app qualification

Created `output/{config['app_id']}` and `output/{archive_path.name}` from the supplied synthetic fixture. The release passes the helper's structural checks and {len(checks)} offline assertions recorded in `output/verification.json`. Original workspace files are unchanged ({len(before)} file hashes compared).

## Supplied values and origins

Identity, roles, disabled state and dashboard values come from JSON-decoded `input/native.json`. Paths, operation and native Simple XML requirement come from `TASK.md`. `output/authoring-inputs.json` records all values and their origins; the supplied helper's SHA-256 records its local revision.

- App ID: `{config['app_id']}`; version: `{config['version']}`.
- App label: `{config['app_label']}`.
- Author: `{config['author']}`; description: `{config['description']}`.
- Install state: `{config['install_state']}`.
- Read roles: `{', '.join(config['read_roles'])}`; write roles: `{', '.join(config['write_roles'])}`; metadata export: `none`.
- Panel title: `{config['dashboard']['title']}`. Its final character is U+00C5 (`{config['dashboard']['title'][-1]}`).
- Inline search: `{config['dashboard']['query']}`. The two quotation marks are U+0022; the decoded query has no literal backslashes.
- Earliest: `{config['dashboard']['earliest']}`; latest: `{config['dashboard']['latest']}`.

The helper creates a Classic Simple XML 1.1 dashboard with one table, uses the app label as the dashboard label, uses the supplied dashboard title as the panel title, and sets the default view/navigation to `home`. These are recorded helper layout choices. XML text is escaped during serialization; parsed source and archive XML match every supplied text value exactly as Unicode strings. Code points and equality results are retained in the verification receipt.

## Selected release and archive

{file_list}

The inspected archive has one `{config['app_id']}/` root and exactly these four regular files. Every member's bytes match its inspected source. Root mode is 0755, file modes are 0644, and ownership/timestamps are normalized. `release-files.json` is retained in the app source as the selection record and excluded from the archive. Reports, receipts, verifier and other workspace files are excluded. Selected contents were inspected; no runtime local configuration or credentials were selected. This is not a comprehensive secret scan.

- Archive bytes: {len(payload)}.
- SHA-256: `{digest}`.
- Digest file: `output/{archive_path.name}.sha256`.

## Commands and completed checks

{commands}
- `python3 output/verify_release.py` - passed; assertions and actual archive inventory retained in `output/verification.json`.

Helper configuration validation, selected structure/XML parsing, identity/version consistency, default navigation and release selection passed. Independent assertions checked metadata role text, all supplied configuration, parsed XML text and time range, archive membership/type/permissions, source/archive byte equality, digest/size agreement and original-file preservation. The bundled schema's version regex matches the supplied version; no full external JSON Schema validator was run. Command exit codes, stdout and stderr are retained in the three operation receipt JSON files.

## Evidence limits and unresolved inputs

All evidence is offline and synthetic. No search was executed. There is no selected deployment target, and the Splunk product, version, operating environment and actual target roles are unknown. The fixture search uses `makeresults`; no real index, data ingestion or production field contract is established.

Native configuration requires no frontend/backend compilation. AppInspect/vetting, installation and live checks were not run. The helper is a bounded structural/package validator, not a complete Splunk config, ACL, SPL or compatibility validator. Target compatibility with Simple XML 1.1, role availability and effective permissions, search/time behavior, navigation and rendering require the actual authorized target and its applicable checks. No performance result is claimed.

No targets were contacted; nothing was published, installed, launched or scheduled. Completion covers the requested offline source/package deliverables. Deployment acceptance remains unestablished.
'''
(OUT / 'report.md').write_text(report, encoding='utf-8')
print(json.dumps({'status': 'passed', 'checks': len(checks), 'archive': str(archive_path.relative_to(ROOT)),
                  'sha256': digest, 'bytes': len(payload), 'report': 'output/report.md'}, ensure_ascii=False))
