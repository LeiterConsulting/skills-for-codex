#!/usr/bin/env python3
"""Offline checks of this fixture's exact release content; does not execute SPL."""
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
CONFIG = json.loads((ROOT / 'input/native.json').read_text(encoding='utf-8'))
FILES = [
    'default/app.conf',
    'default/data/ui/nav/default.xml',
    'default/data/ui/views/home.xml',
    'metadata/default.meta',
]
checks = []


def check(condition, description):
    if not condition:
        raise AssertionError(description)
    checks.append(description)


manifest = json.loads((APP / 'release-files.json').read_text(encoding='utf-8'))
check(manifest == {'schema_version': 1, 'files': FILES}, 'Explicit release manifest selects exactly the four reviewed runtime files')
check(APP.name == CONFIG['app_id'], 'App directory matches supplied app ID')
conf = configparser.ConfigParser(interpolation=None)
conf.read_string((APP / 'default/app.conf').read_text(encoding='utf-8'))
expected_conf = {
    'install': {'state': CONFIG['install_state']},
    'ui': {'is_visible': 'true', 'label': CONFIG['app_label'], 'default_view': 'home'},
    'launcher': {'author': CONFIG['author'], 'version': CONFIG['version'], 'description': CONFIG['description']},
    'package': {'id': CONFIG['app_id']},
    'id': {'name': CONFIG['app_id'], 'version': CONFIG['version']},
}
check({s: dict(conf[s]) for s in conf.sections()} == expected_conf, 'All app.conf identity, state and navigation values match the supplied values and recorded scaffold choices')
expected_meta = '[]\naccess = read : [ ' + ', '.join(CONFIG['read_roles']) + ' ], write : [ ' + ', '.join(CONFIG['write_roles']) + ' ]\nexport = none\n'
check((APP / 'metadata/default.meta').read_text(encoding='utf-8') == expected_meta, 'Read/write role lists are exact and app objects use export = none')
view_bytes = (APP / 'default/data/ui/views/home.xml').read_bytes()
view = ET.fromstring(view_bytes)
check(view.tag == 'dashboard' and view.get('version') == '1.1' and len(view.findall('row/panel/table/search')) == 1, 'Simple XML 1.1 dashboard has exactly one table search')
check(view.findtext('label') == CONFIG['app_label'], 'Dashboard label round-trips to the supplied label')
check(view.findtext('row/panel/title') == CONFIG['dashboard']['title'], 'Panel title round-trips exactly, including Unicode and angle brackets')
search = view.find('row/panel/table/search')
check(search.findtext('query') == CONFIG['dashboard']['query'], 'Search text round-trips exactly, including quotes, ampersand and angle brackets')
check(search.findtext('earliest') == CONFIG['dashboard']['earliest'] and search.findtext('latest') == CONFIG['dashboard']['latest'], 'Time bounds round-trip exactly to -12h and now')
check(b'&amp;' in view_bytes and b'&lt;' in view_bytes and b'&gt;' in view_bytes and CONFIG['dashboard']['title'].encode('utf-8').endswith(bytes([195, 133])), 'XML entities and UTF-8 encoding preserve the fixture text')
nav = ET.fromstring((APP / 'default/data/ui/nav/default.xml').read_bytes())
check(nav.tag == 'nav' and [v.attrib for v in nav.findall('view')] == [{'name': 'home', 'default': 'true'}], 'Navigation resolves to the released default home view')

with tarfile.open(ARCHIVE, 'r:gz') as archive:
    members = archive.getmembers()
    expected_names = [CONFIG['app_id']] + [CONFIG['app_id'] + '/' + f for f in sorted(FILES)]
    check([m.name.rstrip('/') for m in members] == expected_names, 'Actual archive has one bench_delta root and exactly four selected files, with no manifest or evidence files')
    check(members[0].isdir() and all(m.isfile() for m in members[1:]), 'Archive contains only a directory and regular files; no links or special entries')
    check(members[0].mode == 0o755 and all(m.mode == 0o644 for m in members[1:]) and all(m.mtime == 0 and m.uid == 0 and m.gid == 0 for m in members), 'Archive permissions, owner fields and timestamps match deterministic helper settings')
    for relative in FILES:
        check(archive.extractfile(CONFIG['app_id'] + '/' + relative).read() == (APP / relative).read_bytes(), 'Archived bytes match reviewed source: ' + relative)

payload = ARCHIVE.read_bytes()
digest = hashlib.sha256(payload).hexdigest()
package_result = json.loads((OUT / 'package-result.json').read_text(encoding='utf-8'))
check(digest == package_result['sha256'] and len(payload) == package_result['archive_bytes'], 'Independently computed SHA-256 and size match the packaging result')
check(int.from_bytes(payload[4:8], 'little') == 0, 'Gzip header uses a zero timestamp')

baseline = json.loads((OUT / 'source-hashes.json').read_text(encoding='utf-8'))
paths = [ROOT / 'AGENTS.md', ROOT / 'TASK.md', *sorted((ROOT / 'input').rglob('*')), *sorted((ROOT / 'candidate').rglob('*'))]
actual = {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in paths if p.is_file()}
check(actual == baseline, 'Input fixtures, instructions and candidate resources remain byte-for-byte unchanged, with no added files in those trees')

(OUT / (ARCHIVE.name + '.sha256')).write_text(digest + '  ' + ARCHIVE.name + '\n', encoding='utf-8')
result = {'status': 'passed', 'check_count': len(checks), 'checks': checks, 'sha256': digest, 'archive_bytes': len(payload), 'archive_members': expected_names}
(OUT / 'verification-result.json').write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
print(json.dumps(result, indent=2))
