#!/usr/bin/env python3
"""Offline release verification; run from the workspace root. Writes output/ only."""
import configparser
import hashlib
import json
from pathlib import Path
import tarfile
import xml.etree.ElementTree as ET


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def check(name, condition, evidence):
    if not condition:
        raise AssertionError(name)
    checks.append({'name': name, 'status': 'passed', 'evidence': evidence})


checks = []
config = json.loads(Path('input/native.json').read_text(encoding='utf-8'))
app = Path('output/bench_delta')
archive_path = Path('output/bench_delta-0.2.1.tar.gz')
receipt = json.loads(Path('output/command-results.json').read_text(encoding='utf-8'))
manifest = json.loads((app / 'release-files.json').read_text(encoding='utf-8'))
expected_files = [
    'default/app.conf',
    'default/data/ui/nav/default.xml',
    'default/data/ui/views/home.xml',
    'metadata/default.meta',
]
check('explicit release selection', manifest == {'schema_version': 1, 'files': expected_files}, expected_files)

conf = configparser.ConfigParser(interpolation=None)
conf.read_string((app / 'default/app.conf').read_text(encoding='utf-8'))
expected_conf = {
    'install': {'state': config['install_state']},
    'ui': {'is_visible': 'true', 'label': config['app_label'], 'default_view': 'home'},
    'launcher': {key: config[key] for key in ('author', 'version', 'description')},
    'package': {'id': config['app_id']},
    'id': {'name': config['app_id'], 'version': config['version']},
}
actual_conf = {section: dict(conf[section]) for section in conf.sections()}
check('app identity, metadata and install state', app.name == config['app_id'] and actual_conf == expected_conf, actual_conf)

nav = ET.parse(app / 'default/data/ui/nav/default.xml').getroot()
check('navigation to packaged home view', nav.tag == 'nav' and nav.attrib == {'search_view': 'search'} and len(nav) == 1 and nav[0].tag == 'view' and nav[0].attrib == {'name': 'home', 'default': 'true'}, {'default_view': 'home', 'search_view': 'search'})
view = ET.parse(app / 'default/data/ui/views/home.xml').getroot()
expected_tags = ['dashboard', 'label', 'row', 'panel', 'title', 'table', 'search', 'query', 'earliest', 'latest']
check('native Simple XML table structure', [element.tag for element in view.iter()] == expected_tags and view.attrib == {'version': '1.1', 'theme': 'light'}, {'tags': expected_tags, 'attributes': view.attrib})
actual_dashboard = {'title': view.findtext('row/panel/title')}
for key in ('query', 'earliest', 'latest'):
    actual_dashboard[key] = view.findtext('row/panel/table/search/' + key)
check('exact decoded dashboard and label values', actual_dashboard == config['dashboard'] and view.findtext('label') == config['app_label'], {'app_label': view.findtext('label'), 'dashboard': actual_dashboard})
code_points = {key: {'input': [f'U+{ord(char):04X}' for char in config['dashboard'][key]], 'xml': [f'U+{ord(char):04X}' for char in actual_dashboard[key]]} for key in ('title', 'query')}
check('Unicode and quote round trip', all(item['input'] == item['xml'] for item in code_points.values()), code_points)
expected_meta = [
    '[]',
    'access = read : [ ' + ', '.join(config['read_roles']) + ' ], write : [ ' + ', '.join(config['write_roles']) + ' ]',
    'export = none',
]
check('exact read/write roles and app-local export', (app / 'metadata/default.meta').read_text(encoding='utf-8').splitlines() == expected_meta, {'read_roles': config['read_roles'], 'write_roles': config['write_roles'], 'export': 'none'})

expected_members = [config['app_id'] + '/'] + [config['app_id'] + '/' + name for name in sorted(expected_files)]
with tarfile.open(archive_path, 'r:gz') as archive:
    members = archive.getmembers()
    check('actual archive membership', [member.name.rstrip('/') for member in members] == [name.rstrip('/') for name in expected_members], [member.name for member in members])
    check('archive types and normalized permissions', members[0].isdir() and members[0].mode == 0o755 and all(member.isfile() and member.mode == 0o644 for member in members[1:]) and all(member.uid == member.gid == member.mtime == 0 for member in members), [{'name': member.name, 'type': 'directory' if member.isdir() else 'regular_file', 'mode': oct(member.mode), 'uid': member.uid, 'gid': member.gid, 'mtime': member.mtime} for member in members])
    file_hashes = {}
    for member, relative in zip(members[1:], sorted(expected_files), strict=True):
        packaged = archive.extractfile(member).read()
        source = (app / relative).read_bytes()
        check('archive byte equality: ' + relative, packaged == source, {'bytes': len(packaged), 'sha256': hashlib.sha256(packaged).hexdigest()})
        file_hashes[relative] = hashlib.sha256(packaged).hexdigest()
check('gzip timestamp normalized', archive_path.read_bytes()[4:8] == bytes(4), {'mtime': 0})
package_receipt = next(command['result'] for command in receipt['commands'] if 'package' in command['argv'])
sha256 = digest(archive_path)
check('independent package digest', sha256 == package_receipt['sha256'] and archive_path.stat().st_size == package_receipt['archive_bytes'], {'sha256': sha256, 'bytes': archive_path.stat().st_size})
source_before = receipt['source_sha256_before']
source_after = {path.as_posix(): digest(path) for path in sorted(Path('.').rglob('*')) if path.is_file() and 'output' not in path.parts}
check('all supplied source files preserved', source_after == source_before, source_after)

result = {'status': 'passed', 'check_count': len(checks), 'checks': checks, 'selected_file_sha256': file_hashes, 'archive': archive_path.as_posix(), 'sha256': sha256, 'appinspect': 'not_run', 'installed': 'not_run', 'live': 'not_run'}
Path('output/verification.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
Path('output/bench_delta-0.2.1.tar.gz.sha256').write_text(f'{sha256}  {archive_path.name}\n', encoding='utf-8')
print(json.dumps({'status': result['status'], 'check_count': result['check_count'], 'sha256': sha256}, indent=2))
