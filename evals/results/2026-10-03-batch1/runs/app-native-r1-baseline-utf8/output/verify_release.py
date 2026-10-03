#!/usr/bin/env python3
"""Offline fixture-to-release checks; writes receipts, SHA-256 and report only."""
import configparser
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import stat
import tarfile
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / 'output'
APP = OUT / 'bench_delta'
ARCHIVE = OUT / 'bench_delta-0.2.1.tar.gz'
cfg = json.loads((ROOT / 'input/native.json').read_text(encoding='utf-8'))
build = json.loads((OUT / 'build-receipts.json').read_text(encoding='utf-8'))
checks = []


def check(name, condition, detail):
    if not condition:
        raise AssertionError(name + ': ' + detail)
    checks.append({'name': name, 'status': 'passed', 'detail': detail})


def sha(data):
    return hashlib.sha256(data).hexdigest()


check('helper_commands', all(c['exit_code'] == 0 and not c['stderr'] for c in build['commands'])
      and len(build['commands']) == 3, 'Scaffold, selected-file validation and package commands exited 0 without stderr.')
manifest = json.loads((APP / 'release-files.json').read_text(encoding='utf-8'))
expected_files = ['default/app.conf', 'default/data/ui/nav/default.xml',
                  'default/data/ui/views/home.xml', 'metadata/default.meta']
check('release_selection', manifest == {'schema_version': 1, 'files': expected_files},
      'Explicit release manifest selects only the four native app files; manifest and evidence are excluded from the archive.')
actual_files = sorted(p.relative_to(APP).as_posix() for p in APP.rglob('*') if p.is_file())
check('app_file_set', actual_files == sorted(expected_files + ['release-files.json']),
      'App source contains exactly the selected files and the release manifest.')
check('regular_files', all(stat.S_ISREG((APP / p).lstat().st_mode) and
      not any(parent.is_symlink() for parent in (APP / p, *(APP / p).parents)) for p in expected_files),
      'Selected files are regular files with no linked path components.')
selected = {p: (APP / p).read_bytes() for p in expected_files}
check('utf8', all(data.decode('utf-8').encode('utf-8') == data for data in selected.values()),
      'All selected files round-trip as UTF-8.')
conf = configparser.ConfigParser(interpolation=None)
conf.read_string(selected['default/app.conf'].decode('utf-8'))
expected_conf = {
    'install': {'state': cfg['install_state']},
    'ui': {'is_visible': 'true', 'label': cfg['app_label'], 'default_view': 'home'},
    'launcher': {'author': cfg['author'], 'version': cfg['version'], 'description': cfg['description']},
    'package': {'id': cfg['app_id']},
    'id': {'name': cfg['app_id'], 'version': cfg['version']},
}
check('app_conf_identity', {s: dict(conf[s]) for s in conf.sections()} == expected_conf
      and APP.name == cfg['app_id'],
      'All app.conf sections and values exactly match fixture metadata and the native home-view scaffold, including disabled state and both version stanzas.')
nav = ET.fromstring(selected['default/data/ui/nav/default.xml'])
check('navigation', nav.tag == 'nav' and nav.attrib == {'search_view': 'search'}
      and len(nav) == 1 and nav[0].tag == 'view'
      and nav[0].attrib == {'name': 'home', 'default': 'true'}
      and 'default/data/ui/views/home.xml' in selected,
      'Navigation selects the packaged home view; search_view refers to the platform search view.')
xml_bytes = selected['default/data/ui/views/home.xml']
view = ET.fromstring(xml_bytes)
check('simple_xml_shape', view.tag == 'dashboard' and view.attrib == {'version': '1.1', 'theme': 'light'}
      and [e.tag for e in view.iter()] == ['dashboard', 'label', 'row', 'panel', 'title',
                                          'table', 'search', 'query', 'earliest', 'latest'],
      'One Simple XML 1.1 dashboard with one row, one panel, one table and one inline search; no extra tokens or searches.')
observed = {'app_label': view.findtext('label'),
            'title': view.findtext('row/panel/title'),
            'query': view.findtext('row/panel/table/search/query'),
            'earliest': view.findtext('row/panel/table/search/earliest'),
            'latest': view.findtext('row/panel/table/search/latest')}
expected_text = {'app_label': cfg['app_label'], **cfg['dashboard']}
check('xml_value_equality', observed == expected_text,
      'Parsed XML label, title, query, earliest and latest equal JSON-decoded fixture strings, character for character.')
check('xml_escaping', b'Delta &amp; Readiness' in xml_bytes and b'&lt;Health&gt;' in xml_bytes
      and b'A&amp;B&lt;ready&gt;' in xml_bytes
      and '\u00c5'.encode('utf-8') in xml_bytes
      and all(b'<!DOCTYPE' not in b.upper() and b'<!ENTITY' not in b.upper()
              for p, b in selected.items() if p.endswith('.xml')),
      'Ampersands and angle brackets are escaped as XML text; U+00C5 is UTF-8; no DTD/entity declarations.')
metadata = selected['metadata/default.meta'].decode('utf-8')
acl = re.fullmatch(r'\[\]\naccess = read : \[ (.*?) \], write : \[ (.*?) \]\nexport = none\n', metadata)
check('metadata_roles', acl is not None and acl.group(1).split(', ') == cfg['read_roles']
      and acl.group(2).split(', ') == cfg['write_roles'],
      'Global metadata ACL exactly preserves bench_reader read and bench_editor write roles, with export = none and no wildcard or additional grants.')
archive_hash = sha(ARCHIVE.read_bytes())
check('package_receipt_digest', archive_hash == build['commands'][-1]['result']['sha256']
      and ARCHIVE.stat().st_size == build['commands'][-1]['result']['archive_bytes'],
      'Independently recomputed package SHA-256 and byte length match the packaging receipt.')
with tarfile.open(ARCHIVE, 'r:gz') as tf:
    members = tf.getmembers()
    expected_names = [cfg['app_id']] + [cfg['app_id'] + '/' + p for p in sorted(expected_files)]
    check('archive_membership', [m.name.rstrip('/') for m in members] == expected_names
          and members[0].isdir() and all(m.isfile() for m in members[1:]),
          'Archive contains one bench_delta root and exactly four regular selected files; no links, duplicate names or extra content.')
    check('archive_path_safety', all(not PurePosixPath(m.name).is_absolute()
          and '..' not in PurePosixPath(m.name).parts for m in members),
          'All archive member names are relative and free of path traversal.')
    check('archive_bytes', all(tf.extractfile(m).read() == selected[m.name.split('/', 1)[1]] for m in members[1:]),
          'Every archive file is byte-identical to its selected source file; archive inspected without extracting.')
    check('normalized_archive_metadata', all(m.mtime == 0 and m.uid == 0 and m.gid == 0
          and m.uname == '' and m.gname == '' for m in members)
          and members[0].mode == 0o755 and all(m.mode == 0o644 for m in members[1:])
          and ARCHIVE.read_bytes()[4:8] == bytes(4) and not ARCHIVE.read_bytes()[3] & 8,
          'Tar timestamps/ownership are normalized; root mode 0755 and file modes 0644; gzip timestamp is zero with no stored filename.')
check('source_preservation', all((ROOT / p).is_file() and sha((ROOT / p).read_bytes()) == h
      for p, h in build['source_sha256'].items()),
      'AGENTS.md, TASK.md and all supplied input/candidate files retain their pre-build SHA-256 values.')

# Sidecar uses standard sha256sum syntax, relative to output/.
sidecar = OUT / (ARCHIVE.name + '.sha256')
sidecar.write_text(f'{archive_hash}  {ARCHIVE.name}\n', encoding='utf-8')
check('digest_sidecar', sidecar.read_text(encoding='utf-8') == f'{archive_hash}  {ARCHIVE.name}\n',
      'SHA-256 sidecar names the exact package and contains its recomputed digest.')
receipt = {
    'schema_version': 1,
    'scope': 'Offline synthetic fixtures; no target selected and no runtime evidence.',
    'checks': checks,
    'fixture_values': cfg,
    'parsed_xml_values': observed,
    'xml_text_code_points': {k: [f'U+{ord(ch):04X}' for ch in v] for k, v in observed.items()},
    'selected_files': [{'path': p, 'bytes': len(selected[p]), 'sha256': sha(selected[p])} for p in expected_files],
    'artifact': {'path': 'output/' + ARCHIVE.name, 'bytes': ARCHIVE.stat().st_size, 'sha256': archive_hash},
    'input_sha256': build['source_sha256']['input/native.json'],
    'helper_sha256': build['source_sha256']['candidate/scripts/splunk_app.py'],
    'source_files_preserved': True,
    'external_checks': {'appinspect': 'not_run', 'installed': 'not_run', 'runtime': 'not_run'},
    'unresolved_inputs': ['Deployment target and platform (Enterprise/Cloud)', 'Exact Splunk version',
                          'Target role existence and effective permissions'],
}
(OUT / 'verification.json').write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

lines = [
    '# bench_delta 0.2.1 offline release report', '',
    'Created the native Simple XML app at `output/bench_delta` and packaged the four explicitly selected release files as `output/' + ARCHIVE.name + '`. All ' + str(len(checks)) + ' offline verification checks passed. The supplied fixtures are synthetic and are not live evidence. No deployment target is selected.', '',
    '## Supplied values and provenance', '',
    'Identity, metadata, roles, search and time range came exclusively from JSON-decoded `input/native.json`; no example defaults replaced them. The supplied helper `candidate/scripts/splunk_app.py` generated the app and performed selected-file validation and packaging.', '',
    '- App ID: `' + cfg['app_id'] + '`; version: `' + cfg['version'] + '`.',
    '- App label: `' + cfg['app_label'] + '`; author: `' + cfg['author'] + '`.',
    '- Description: `' + cfg['description'] + '`; install state: `' + cfg['install_state'] + '`.',
    '- Read roles: `' + ', '.join(cfg['read_roles']) + '`; write roles: `' + ', '.join(cfg['write_roles']) + '`; metadata export: `none`.',
    '- Dashboard panel title: `' + cfg['dashboard']['title'] + '`.',
    '- Earliest: `' + cfg['dashboard']['earliest'] + '`; latest: `' + cfg['dashboard']['latest'] + '`.', '',
    'Exact decoded search, preserved as parsed XML text:', '', '```spl', cfg['dashboard']['query'], '```', '',
    'The title ends with the character U+00C5 (Å). The query quotes are U+0022. Neither string contains a literal backslash (U+005C). XML serializes ampersands and angle brackets as entities, then parses back to the identical supplied characters. `verification.json` records parsed values and their code points.', '',
    'Input SHA-256: `' + receipt['input_sha256'] + '`.', '',
    'Supplied helper SHA-256: `' + receipt['helper_sha256'] + '`; no independent helper version was supplied.', '',
    '## Release selection', '',
    '`bench_delta/release-files.json` selects the following files. The manifest, verifier, receipts and report remain outside the archive.', '',
    '| Relative app path | Bytes | SHA-256 |', '| --- | ---: | --- |',
]
for entry in receipt['selected_files']:
    lines.append('| `' + entry['path'] + '` | ' + str(entry['bytes']) + ' | `' + entry['sha256'] + '` |')
lines += ['',
    'The selected contents were inspected: app identity and disabled state, native navigation, a single table with the supplied inline search, and the requested ACL. They contain no credentials, external endpoints, backend code or scheduling configuration. No local configuration, dependencies, caches or unrelated workspace files were selected.', '',
    '## Completed checks', '',
    'All three helper commands exited 0. Their exact arguments, stdout, stderr and results are retained in `build-receipts.json`. Helper validation checks its documented portable config contract, app identity, selected XML and navigation; it is not comprehensive Splunk configuration or formal JSON Schema validation.', '',
    '| Check | Result | Evidence |', '| --- | --- | --- |',
]
for entry in checks:
    lines.append('| `' + entry['name'] + '` | passed | ' + entry['detail'] + ' |')
lines += ['',
    'Full assertion receipts are in `verification.json`; the repeatable verifier is `verify_release.py`. No compilation applies to these configuration/XML files.', '',
    '## Package digest', '',
    '- Artifact: `' + ARCHIVE.name + '` (' + str(ARCHIVE.stat().st_size) + ' bytes).',
    '- SHA-256: `' + archive_hash + '`.',
    '- Digest sidecar: `' + sidecar.name + '`.', '',
    'Run from `output/`: `sha256sum -c ' + sidecar.name + '`. Archive inspection confirmed a single `bench_delta/` root and byte equality for all four selected files. The helper writes normalized archive metadata, which was checked; an independent rebuild comparison was not run.', '',
    '## Remaining compatibility and evidence limits', '',
    '- Deployment platform, exact Splunk version and target are unresolved. Compatibility of Simple XML 1.1 and these configuration keys has not been qualified against a selected release or Enterprise/Cloud environment.',
    '- Target roles `bench_reader` and `bench_editor` were not observed. Role existence, inherited ACL behavior, effective capabilities and permission enforcement require target evidence. The ACL strings were verified locally only.',
    '- AppInspect/vetting was not run; no vendor report was supplied. Cloud private-app eligibility and the applicable install workflow remain unverified.',
    '- No package was installed, no target was contacted, and no live browser/navigation, search or access test ran. SPL syntax and execution, displayed status and time-range behavior are not proven by XML equality. The supplied search uses synthetic `makeresults`, with no supplied real-data index/field contract.',
    '- The helper does not validate every Splunk configuration or ACL semantic. Structural and archive checks establish offline source/package acceptance only. Runtime acceptance requires the exact package on an authorized compatible target.',
    '- All supplied inputs were preserved. No publishing, installation, game launch or schedule changes occurred.', '',
]
(OUT / 'report.md').write_text('\n'.join(lines), encoding='utf-8')
print(json.dumps({'checks_passed': len(checks), 'archive_sha256': archive_hash,
                  'report': 'output/report.md', 'verification': 'output/verification.json'}, indent=2))
