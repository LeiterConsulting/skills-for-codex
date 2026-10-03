#!/usr/bin/env python3
"""Offline fixture-to-source and source-to-archive checks; never runs Splunk."""
import configparser
import hashlib
import json
from pathlib import Path
import tarfile
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / 'output'
APP = OUT / 'bench_delta'
ARCHIVE = OUT / 'bench_delta-0.2.1.tar.gz'
checks = []


def load(path):
    return json.loads(path.read_text(encoding='utf-8'))


def check(name, condition, details=None):
    entry = {'name': name, 'status': 'passed' if condition else 'failed'}
    if details is not None:
        entry['details'] = details
    checks.append(entry)
    if not condition:
        (OUT / 'verification-results.json').write_text(
            json.dumps({'checks': checks}, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        raise AssertionError(name)


cfg = load(ROOT / 'input/native.json')
receipts = load(OUT / 'command-results.json')
check('Scaffold, validate and package commands succeeded',
      len(receipts['commands']) == 3 and
      all(r['exit_code'] == 0 and r['stderr'] == '' for r in receipts['commands']))

expected_files = [
    'default/app.conf',
    'default/data/ui/nav/default.xml',
    'default/data/ui/views/home.xml',
    'metadata/default.meta',
]
manifest = load(APP / 'release-files.json')
check('Release manifest selects exactly four intended runtime files',
      manifest == {'schema_version': 1, 'files': expected_files})
actual_files = sorted(p.relative_to(APP).as_posix() for p in APP.rglob('*') if p.is_file())
check('App directory contains only generated source and release manifest',
      actual_files == sorted(expected_files + ['release-files.json']) and
      not any(p.is_symlink() for p in APP.rglob('*')))

conf = configparser.ConfigParser(interpolation=None)
conf.read_string((APP / 'default/app.conf').read_text(encoding='utf-8'))
expected_conf = {
    'install': {'state': cfg['install_state']},
    'ui': {'is_visible': 'true', 'label': cfg['app_label'], 'default_view': 'home'},
    'launcher': {'author': cfg['author'], 'version': cfg['version'], 'description': cfg['description']},
    'package': {'id': cfg['app_id']},
    'id': {'name': cfg['app_id'], 'version': cfg['version']},
}
check('Every app.conf value and app root match the supplied identity/state',
      {section: dict(conf[section]) for section in conf.sections()} == expected_conf and
      APP.name == cfg['app_id'] and not conf.defaults(), expected_conf)

expected_meta = ('[]\naccess = read : [ ' + ', '.join(cfg['read_roles']) +
                 ' ], write : [ ' + ', '.join(cfg['write_roles']) + ' ]\nexport = none\n')
check('Metadata exactly preserves supplied read/write roles and app-scoped export',
      (APP / 'metadata/default.meta').read_text(encoding='utf-8') == expected_meta,
      {'read_roles': cfg['read_roles'], 'write_roles': cfg['write_roles'], 'export': 'none'})

view = ET.parse(APP / 'default/data/ui/views/home.xml').getroot()
check('Native Simple XML has one table and one inline search',
      view.tag == 'dashboard' and view.attrib == {'version': '1.1', 'theme': 'light'} and
      len(view.findall('./row/panel/table')) == 1 and len(view.findall('.//search')) == 1 and
      len(view.findall('.//query')) == 1)
observed = {
    'app_label': view.findtext('label'),
    'title': view.findtext('./row/panel/title'),
    'query': view.findtext('./row/panel/table/search/query'),
    'earliest': view.findtext('./row/panel/table/search/earliest'),
    'latest': view.findtext('./row/panel/table/search/latest'),
}
expected = {'app_label': cfg['app_label'], **cfg['dashboard']}
check('Parsed UTF-8 XML text exactly equals JSON-decoded input', observed == expected,
      {'parsed_values': observed,
       'code_points': {name: [f'U+{ord(c):04X}' for c in value] for name, value in observed.items()}})

nav = ET.parse(APP / 'default/data/ui/nav/default.xml').getroot()
entries = nav.findall('view')
check('Navigation and app.conf route to the released home view',
      nav.tag == 'nav' and nav.attrib == {'search_view': 'search'} and
      len(entries) == 1 and entries[0].attrib == {'name': 'home', 'default': 'true'} and
      conf['ui']['default_view'] == 'home')

expected_members = [cfg['app_id'] + '/'] + [cfg['app_id'] + '/' + p for p in sorted(expected_files)]
with tarfile.open(ARCHIVE, 'r:gz') as archive:
    members = archive.getmembers()
    names = [m.name + ('/' if m.isdir() and not m.name.endswith('/') else '') for m in members]
    check('Real archive contains one app root and exactly the selected files', names == expected_members, names)
    check('Archive uses regular files, deterministic timestamps and expected permissions',
          members[0].isdir() and members[0].mode == 0o755 and
          all(m.isfile() and m.mode == 0o644 for m in members[1:]) and
          all(m.mtime == 0 and m.uid == 0 and m.gid == 0 and not m.linkname for m in members))
    matches = {}
    for member in members[1:]:
        relative = member.name.split('/', 1)[1]
        content = archive.extractfile(member).read()
        matches[relative] = content == (APP / relative).read_bytes()
    check('Every archive file is byte-identical to its selected source', all(matches.values()), matches)

payload = ARCHIVE.read_bytes()
digest = hashlib.sha256(payload).hexdigest()
package_receipt = receipts['commands'][2]['result']
digest_text = (OUT / 'bench_delta-0.2.1.tar.gz.sha256').read_text(encoding='utf-8')
check('Independent SHA-256 and archive size match package receipt and digest file',
      digest == package_receipt['sha256'] and len(payload) == package_receipt['archive_bytes'] and
      digest_text == f'{digest}  {ARCHIVE.name}\n', {'sha256': digest, 'archive_bytes': len(payload)})

baseline = load(OUT / 'source-hashes.json')
current = {p.relative_to(ROOT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
           for p in sorted(ROOT.rglob('*')) if p.is_file() and OUT not in p.parents}
check('All original workspace files remain byte-identical; all additions are in output/',
      current == baseline, {'preserved_original_file_count': len(baseline)})

result = {'status': 'passed', 'check_count': len(checks), 'sha256': digest,
          'archive_bytes': len(payload), 'checks': checks,
          'scope': 'Synthetic offline fixtures only; no AppInspect, SPL execution or installed/live validation.'}
(OUT / 'verification-results.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(json.dumps({'status': result['status'], 'check_count': len(checks), 'sha256': digest,
                  'archive_bytes': len(payload)}, indent=2))
