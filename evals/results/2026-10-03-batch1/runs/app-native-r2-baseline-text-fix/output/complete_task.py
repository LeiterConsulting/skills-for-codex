#!/usr/bin/env python3
"""Build and verify this offline fixture using only supplied local resources."""
from pathlib import Path
import configparser
import hashlib
import json
import re
import subprocess
import sys
import tarfile
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / 'output'
INPUT = ROOT / 'input/native.json'
HELPER = ROOT / 'candidate/scripts/splunk_app.py'
CONFIG = json.loads(INPUT.read_text(encoding='utf-8'))
APP = OUT / CONFIG['app_id']
MANIFEST = APP / 'release-files.json'
ARCHIVE = OUT / f"{CONFIG['app_id']}-{CONFIG['version']}.tar.gz"
DIGEST = Path(str(ARCHIVE) + '.sha256')
RECEIPT = OUT / 'verification.json'
REPORT = OUT / 'report.md'
assert CONFIG['app_id'] == 'bench_delta' and CONFIG['version'] == '0.2.1'
for destination in (APP, ARCHIVE, DIGEST, RECEIPT, REPORT):
    if destination.exists():
        raise SystemExit(f'Refusing existing destination: {destination.relative_to(ROOT)}')


def sha(data):
    return hashlib.sha256(data).hexdigest()


def relative(path):
    return path.relative_to(ROOT).as_posix()


sources = {relative(p): sha(p.read_bytes()) for p in ROOT.rglob('*')
           if p.is_file() and not p.is_relative_to(OUT)}
receipt = {
    'fixture_only': True,
    'input': {'path': relative(INPUT), 'sha256': sources[relative(INPUT)]},
    'helper': {'path': relative(HELPER), 'sha256': sources[relative(HELPER)]},
    'source_sha256': sources,
    'configuration': CONFIG,
    'commands': [],
    'checks': [],
    'appinspect': 'not_run',
    'installed': False,
    'runtime': 'not_run',
    'deployment_target': None,
    'splunk_version': None,
}


def run_helper(*args):
    command = [sys.executable, relative(HELPER), *args]
    result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True,
                            encoding='utf-8', env=None)
    record = {'argv': command, 'exit_code': result.returncode,
              'stdout': result.stdout, 'stderr': result.stderr}
    receipt['commands'].append(record)
    if result.returncode != 0:
        RECEIPT.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        raise SystemExit(f'Helper failed: {args[0]}: {result.stderr}')
    parsed = json.loads(result.stdout)
    record['result'] = parsed
    return parsed


def check(name, condition, evidence):
    assert condition, name
    receipt['checks'].append({'name': name, 'status': 'passed', 'evidence': evidence})


scaffold = run_helper('scaffold', '--config', relative(INPUT), '--output', relative(APP))
validation = run_helper('validate', '--app', relative(APP), '--files', relative(MANIFEST))
check('Supplied helper scaffold and selected-file validation',
      scaffold['created_files'] == 5 and scaffold['release_file_count'] == 4
      and validation['structure'] == 'passed' and validation['selected_file_count'] == 4,
      {'scaffold': scaffold, 'validate': validation})

conf = configparser.ConfigParser(interpolation=None)
conf.read_string((APP / 'default/app.conf').read_text(encoding='utf-8'))
expected_conf = {
    'install': {'state': CONFIG['install_state']},
    'ui': {'is_visible': 'true', 'label': CONFIG['app_label'], 'default_view': 'home'},
    'launcher': {k: CONFIG[k] for k in ('author', 'version', 'description')},
    'package': {'id': CONFIG['app_id']},
    'id': {'name': CONFIG['app_id'], 'version': CONFIG['version']},
}
actual_conf = {section: dict(conf[section]) for section in conf.sections()}
check('All app.conf values match supplied identity and state', actual_conf == expected_conf, actual_conf)

meta = (APP / 'metadata/default.meta').read_text(encoding='utf-8')
match = re.fullmatch(r'\[\]\naccess = read : \[ (.*?) \], write : \[ (.*?) \]\nexport = none\n', meta)
actual_roles = {} if match is None else {
    'read_roles': match.group(1).split(', '), 'write_roles': match.group(2).split(', ')}
check('ACL role lists and app-local export match',
      actual_roles == {k: CONFIG[k] for k in ('read_roles', 'write_roles')},
      {'roles': actual_roles, 'export': 'none', 'scope': '[]'})

view = ET.parse(APP / 'default/data/ui/views/home.xml').getroot()
nav = ET.parse(APP / 'default/data/ui/nav/default.xml').getroot()
check('One native Simple XML table and home navigation',
      view.tag == 'dashboard' and view.attrib == {'version': '1.1', 'theme': 'light'}
      and len(view.findall('row/panel/table')) == 1
      and len(view.findall('.//search')) == 1
      and nav.tag == 'nav' and nav.attrib == {'search_view': 'search'}
      and len(nav) == 1 and nav[0].tag == 'view'
      and nav[0].attrib == {'name': 'home', 'default': 'true'},
      {'dashboard_attributes': view.attrib, 'nav_attributes': nav.attrib,
       'nav_view': nav[0].attrib})
xml_paths = {'app_label': 'label', 'title': 'row/panel/title',
             'query': 'row/panel/table/search/query',
             'earliest': 'row/panel/table/search/earliest',
             'latest': 'row/panel/table/search/latest'}
text_evidence = {}
for key, xml_path in xml_paths.items():
    expected = CONFIG['app_label'] if key == 'app_label' else CONFIG['dashboard'][key]
    actual = view.findtext(xml_path)
    evidence = {'expected': expected, 'actual': actual, 'xml_path': xml_path,
                'expected_code_points': [f'U+{ord(c):04X}' for c in expected],
                'actual_code_points': [f'U+{ord(c):04X}' for c in actual],
                'backslash_count': actual.count(chr(92)),
                'quote_positions': [i for i, c in enumerate(actual) if c == '"']}
    text_evidence[key] = evidence
    check(f'JSON-decoded {key} equals parsed XML text', actual == expected, evidence)
receipt['text_evidence'] = text_evidence

selected = json.loads(MANIFEST.read_text(encoding='utf-8'))['files']
expected_selected = ['default/app.conf', 'default/data/ui/nav/default.xml',
                     'default/data/ui/views/home.xml', 'metadata/default.meta']
check('Release manifest selects exactly the four reviewed app files',
      selected == expected_selected, {'manifest': relative(MANIFEST), 'files': selected})
package = run_helper('package', '--app', relative(APP), '--files', relative(MANIFEST),
                     '--output', relative(ARCHIVE))
expected_members = [CONFIG['app_id'] + '/'] + [CONFIG['app_id'] + '/' + p for p in sorted(selected)]
with tarfile.open(ARCHIVE, 'r:gz') as archive:
    members = archive.getmembers()
    actual_members = [m.name.rstrip('/') + '/' if m.isdir() else m.name for m in members]
    check('Archive has one app root and only selected regular files',
          actual_members == expected_members and members[0].isdir()
          and all(m.isfile() for m in members[1:]), actual_members)
    file_evidence = []
    for member in members[1:]:
        path = member.name.split('/', 1)[1]
        archived = archive.extractfile(member).read()
        source = (APP / path).read_bytes()
        file_evidence.append({'path': path, 'bytes': len(source), 'sha256': sha(source)})
        assert archived == source, f'Archive differs: {path}'
    check('Archive file bytes equal the selected app files', True, file_evidence)
    check('Archive metadata has fixed times and portable modes',
          members[0].mode == 0o755 and all(m.mode == 0o644 for m in members[1:])
          and all(m.mtime == 0 and m.uid == 0 and m.gid == 0 for m in members),
          [{'name': m.name, 'mode': oct(m.mode), 'mtime': m.mtime,
            'uid': m.uid, 'gid': m.gid} for m in members])
payload = ARCHIVE.read_bytes()
checksum = sha(payload)
check('Independent SHA-256 and archive size match package receipt',
      checksum == package['sha256'] and len(payload) == package['archive_bytes'],
      {'sha256': checksum, 'archive_bytes': len(payload)})
DIGEST.write_text(f'{checksum}  {ARCHIVE.name}\n', encoding='utf-8')
check('All supplied workspace files remain byte-identical',
      all((ROOT / p).is_file() and sha((ROOT / p).read_bytes()) == original
          for p, original in sources.items()), sources)
receipt['artifact'] = {'path': relative(ARCHIVE), 'sha256': checksum,
                       'bytes': len(payload), 'digest_path': relative(DIGEST),
                       'members': actual_members}
receipt['completion'] = 'offline_structure_and_package_passed'
inline = lambda value: '`' + value + '`'
d = CONFIG['dashboard']
report = f'''# Offline native app release

Created `{relative(APP)}` and `{relative(ARCHIVE)}` from `{relative(INPUT)}` using the supplied native helper. All fixtures are synthetic; these checks establish offline source and package evidence only. No deployment target is selected.

## Exact supplied values

| Field | Preserved value |
| --- | --- |
| App ID | {inline(CONFIG['app_id'])} |
| Label | {inline(CONFIG['app_label'])} |
| Author | {inline(CONFIG['author'])} |
| Version | {inline(CONFIG['version'])} |
| Description | {inline(CONFIG['description'])} |
| Install state | {inline(CONFIG['install_state'])} |
| Read roles | {inline(', '.join(CONFIG['read_roles']))} |
| Write roles | {inline(', '.join(CONFIG['write_roles']))} |
| Dashboard panel title | {inline(d['title'])} |
| Earliest | {inline(d['earliest'])} |
| Latest | {inline(d['latest'])} |

Inline search (exact JSON-decoded value):

```spl
{d['query']}
```

The app uses one Simple XML 1.1 dashboard (`home`) containing a table with the supplied inline search and time range. The dashboard label uses the app label; the panel title uses the supplied dashboard title. Navigation selects `home`. Default metadata uses the supplied role lists with `export = none`.

Quoted values above come from JSON-decoded input. Parsed XML text was asserted equal to those values as Unicode strings. The title's final code point is `{text_evidence['title']['actual_code_points'][-1]}`. The title has {text_evidence['title']['backslash_count']} U+005C backslash characters; the query has {text_evidence['query']['backslash_count']}. Query U+0022 quotation marks occur at zero-based positions {text_evidence['query']['quote_positions']}. Full expected and actual code points are retained in `verification.json`. XML entities preserve the literal ampersands and angle brackets when parsed.

## Completed checks

- Supplied helper scaffold and `validate` commands completed successfully; input configuration and the four selected release files passed the helper's bounded validation.
- All `app.conf` fields, metadata role lists, dashboard structure, navigation, label, title, search and time bounds were checked against the supplied values.
- Every selected file was read and reviewed. The release contains only the four files below; no private configuration, keys, dependencies, caches, reports or authoring scripts are selected.
- The helper's `package` command completed successfully. Archive membership, file types, byte equality with selected files, fixed metadata, archive size and an independently computed SHA-256 passed.
- All {len(sources)} supplied workspace files remained byte-identical to their recorded initial SHA-256 values.

Selected release files:

{chr(10).join('- `' + p + '`' for p in selected)}

The archive contains those four files beneath the single `bench_delta/` root. `release-files.json` remains a local release-selection record and is excluded from the archive.

## Digest and receipts

- Archive size: {len(payload)} bytes.
- SHA-256: `{checksum}`.
- Digest file: `{relative(DIGEST)}` (verify from `output/` with `sha256sum -c {DIGEST.name}`).
- Input SHA-256: `{sources[relative(INPUT)]}`.
- Helper SHA-256: `{sources[relative(HELPER)]}`.
- `verification.json` records actual command arguments, exit codes, stdout/stderr, parsed results, passed assertions, Unicode comparisons, archive members and source/artifact hashes.
- `complete_task.py` preserves the local build/check procedure; it refuses existing release destinations.

## Compatibility and evidence limits

Splunk deployment type, target version and intended environment remain unresolved. Compatibility of Simple XML 1.1, app configuration, default navigation and metadata must be qualified against the chosen target release. The supplied role names are preserved; their existence, capabilities, user membership and effective ACL behavior have not been verified on a target.

No SPL execution, time-range interpretation, data access, displayed search result, browser behavior or effective app visibility/permissions was tested. The helper treats the query as inert XML text and does not validate SPL semantics. Its structural checks do not parse every Splunk setting or enforce every ACL rule.

AppInspect/vetting, installation and live runtime acceptance were not run. The supplied `disabled` install state is preserved. No targets were contacted, apps published or installed, or schedules changed. Future compatibility, AppInspect and runtime checks require an explicitly selected and authorized target; the synthetic fixtures cannot establish live evidence.
'''
REPORT.write_text(report, encoding='utf-8')
report_text = REPORT.read_text(encoding='utf-8')
check('Report quoted values match JSON-decoded input',
      all(inline(CONFIG[k]) in report_text for k in ('app_id', 'app_label', 'author', 'version', 'description', 'install_state'))
      and all(inline(d[k]) in report_text for k in ('title', 'earliest', 'latest'))
      and all(inline(', '.join(CONFIG[k])) in report_text for k in ('read_roles', 'write_roles'))
      and '```spl\n' + d['query'] + '\n```' in report_text,
      {'report': relative(REPORT), 'sha256': sha(REPORT.read_bytes()), 'query_format': 'fenced SPL block'})
RECEIPT.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(json.dumps({'app': relative(APP), 'archive': relative(ARCHIVE),
                  'sha256': checksum, 'passed_assertions': len(receipt['checks']),
                  'report': relative(REPORT)}, ensure_ascii=False, indent=2))
