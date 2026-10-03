#!/usr/bin/env python3
"""Offline fixture/selected-release/archive checks; no Splunk calls."""
from pathlib import Path
import configparser
import hashlib
import json
import re
import subprocess
import tarfile
import xml.etree.ElementTree as ET

root = Path(__file__).resolve().parent.parent
out = root / 'output'
app = out / 'bench_delta'
archive = out / 'bench_delta-0.2.1.tar.gz'
config = json.loads((root / 'input/native.json').read_text(encoding='utf-8'))
checks = []

def require(condition, name):
    if not condition:
        raise AssertionError(name)
    checks.append(name)

expected_hashes = {
    'AGENTS.md': 'b93d3ef3fac06196eeb40945b9094c5ec33c94ee75082406ed1f8277bbad2eee',
    'TASK.md': '1eabcf0cee707988c0454021346bad7550e4b0e8b889d6cbb315b9f3e4546724',
    'input/native.json': '35313a2b28a98d43365c1e654fa6e9d590fcf08523da696be485974e5b888249',
    'candidate/SKILL.md': 'b86d9e011f7c109f7e051e6324e96b2d765cfa4f88c430a2896125fbc1086ad2',
    'candidate/assets/authoring-inputs.example.json': '9f9b6de510676f2533d151cd4f358ae8a61a588c2ccd40415fb1352413826bcb',
    'candidate/assets/native-app.example.json': '246782ca52ced45b87591f0b8699067c28027cdee78bf7cf7c0320cea8f35180',
    'candidate/assets/native-app.schema.json': 'a2f00804896a9e5b1dfa1a8f9cdf92a54744277646159d932c7be4edc949660b',
    'candidate/references/architecture.md': 'f3bb7e59af17f1b86d0c4df4e56d6774b8f8ff08ba0ac49f66d8ab546ee5f21e',
    'candidate/references/inputs.md': '8d7a7acf007744b5a8c8e6c9ae41983a48d0d945b578a166777f845a3c411db3',
    'candidate/references/validation.md': '45e2eb5df3b5e8580b89e950c6c385d27471430c503ce2d0a9140e1605042182',
    'candidate/scripts/splunk_app.py': 'b747f2a60829b268aafd2cbd4d14a560525cbdb9bf07b97ba045ed28fb74dbda',
}
for name, digest in expected_hashes.items():
    require(hashlib.sha256((root / name).read_bytes()).hexdigest() == digest,
            'Preserved original bytes: ' + name)

command = ['python3', 'candidate/scripts/splunk_app.py', 'validate', '--app', 'output/bench_delta', '--files', 'output/bench_delta/release-files.json']
run = subprocess.run(command, cwd=root, text=True, capture_output=True, check=True)
validation = json.loads(run.stdout)
require(validation['structure'] == 'passed', 'Helper structural validation passed')

manifest = json.loads((app / 'release-files.json').read_text(encoding='utf-8'))
selected = manifest['files']
expected_files = ['default/app.conf', 'default/data/ui/nav/default.xml', 'default/data/ui/views/home.xml', 'metadata/default.meta']
require(manifest['schema_version'] == 1 and selected == expected_files,
        'Explicit release manifest selects exactly four intended runtime files')
conf = configparser.ConfigParser(interpolation=None)
conf.read_string((app / 'default/app.conf').read_text(encoding='utf-8'))
for section, key, source in [
    ('package', 'id', 'app_id'), ('id', 'name', 'app_id'),
    ('id', 'version', 'version'), ('launcher', 'version', 'version'),
    ('launcher', 'author', 'author'), ('launcher', 'description', 'description'),
    ('ui', 'label', 'app_label'), ('install', 'state', 'install_state'),
]:
    require(conf.get(section, key) == config[source],
            'Exact supplied configuration: ' + section + '.' + key)
require(app.name == config['app_id'] == 'bench_delta', 'App directory and identity agree')
require(conf.get('ui', 'default_view') == 'home' and conf.getboolean('ui', 'is_visible'),
        'Visible app uses home as its default view')

view_bytes = (app / 'default/data/ui/views/home.xml').read_bytes()
view = ET.fromstring(view_bytes)
require(view.tag == 'dashboard' and view.attrib == {'version': '1.1', 'theme': 'light'},
        'Native Simple XML 1.1 dashboard with a single table')
require(len(view.findall('./row/panel/table')) == 1 and len(view.findall('.//search')) == 1,
        'Exactly one inline table search; no extra searches')
require(view.findtext('./label') == config['app_label'], 'XML label matches the supplied app label')
require(view.findtext('./row/panel/title') == config['dashboard']['title'],
        'XML title round-trips exactly to the decoded fixture title')
for key in ('query', 'earliest', 'latest'):
    require(view.findtext('./row/panel/table/search/' + key) == config['dashboard'][key],
            'Exact fixture search text/time: ' + key)
require(b'&amp;' in view_bytes and b'&lt;' in view_bytes and b'&gt;' in view_bytes,
        'XML safely escapes ampersand and angle brackets')
require(b'<!DOCTYPE' not in view_bytes.upper() and b'<!ENTITY' not in view_bytes.upper(),
        'Dashboard has no DTD or entity declarations')
nav = ET.fromstring((app / 'default/data/ui/nav/default.xml').read_bytes())
require(nav.tag == 'nav' and nav.attrib == {'search_view': 'search'} and
        len(nav.findall('view')) == 1 and nav.find('view').attrib == {'name': 'home', 'default': 'true'},
        'Default navigation resolves to the packaged home view')
expected_meta = '[]\naccess = read : [ ' + ', '.join(config['read_roles']) + ' ], write : [ ' + ', '.join(config['write_roles']) + ' ]\nexport = none\n'
require((app / 'metadata/default.meta').read_text(encoding='utf-8') == expected_meta,
        'Exact supplied read/write role lists; app-local export = none')

payload = archive.read_bytes()
digest = hashlib.sha256(payload).hexdigest()
package_result = json.loads((out / 'package-result.json').read_text(encoding='utf-8'))
require(package_result['exit_code'] == 0 and package_result['stdout']['sha256'] == digest,
        'Independently computed SHA-256 agrees with package result')
require(package_result['stdout']['archive_bytes'] == len(payload), 'Archive size agrees with package result')
require(payload[:3] == b'\x1f\x8b\x08' and payload[4:8] == b'\x00\x00\x00\x00',
        'Gzip header has a deterministic zero timestamp')
archive_members = []
with tarfile.open(archive, mode='r:gz') as tar:
    members = tar.getmembers()
    expected_names = [config['app_id']] + [config['app_id'] + '/' + name for name in sorted(selected)]
    require([m.name.rstrip('/') for m in members] == expected_names,
            'Real archive has one app root and exactly the four selected files')
    require(members[0].isdir() and members[0].mode == 0o755, 'Archive root is a directory with mode 0755')
    for m in members:
        require(m.uid == m.gid == 0 and m.mtime == 0,
                'Normalized archive owner/time: ' + m.name)
        archive_members.append({'name': m.name, 'size': m.size, 'mode': oct(m.mode), 'type': 'directory' if m.isdir() else 'file'})
    for m in members[1:]:
        require(m.isfile() and m.mode == 0o644, 'Regular archive member with mode 0644: ' + m.name)
        relative = m.name[len(config['app_id']) + 1:]
        require(tar.extractfile(m).read() == (app / relative).read_bytes(),
                'Archived bytes equal reviewed source bytes: ' + relative)

schema = json.loads((root / 'candidate/assets/native-app.schema.json').read_text(encoding='utf-8'))
schema_probe = {
    'version_pattern': schema['properties']['version']['pattern'],
    'supplied_version_matches': re.fullmatch(schema['properties']['version']['pattern'], config['version']) is not None,
    'role_pattern': schema['$defs']['roles']['items']['pattern'],
    'wildcard_matches': re.fullmatch(schema['$defs']['roles']['items']['pattern'], '*') is not None,
    'full_json_schema_validation': 'not_run',
}
result = {
    'status': 'passed',
    'passed_check_count': len(checks),
    'checks': checks,
    'fixture': config,
    'origins': {'fixture_values': 'input/native.json', 'operation_and_output_paths': 'TASK.md', 'native_implementation': 'candidate/scripts/splunk_app.py', 'release_selection': 'Four generated native runtime files reviewed; release-files.json excluded from package'},
    'input_sha256': expected_hashes,
    'helper_validation': {'command': command, 'exit_code': run.returncode, 'stdout': validation, 'stderr': run.stderr},
    'schema_regex_probe': schema_probe,
    'archive': {'path': 'output/' + archive.name, 'bytes': len(payload), 'sha256': digest, 'members': archive_members},
    'evidence_limits': {'build': 'No frontend/backend compilation applicable to native configuration/XML', 'appinspect': 'not_run', 'installed': 'not_run', 'live': 'not_run', 'deployment_target': None, 'splunk_version': None, 'edition_or_cloud_environment': None, 'target_role_existence_and_capabilities': 'unverified', 'spl_execution_and_results': 'unverified', 'browser_navigation_and_acl_enforcement': 'unverified', 'performance': 'not_measured'},
}
(out / (archive.name + '.sha256')).write_text(digest + '  ' + archive.name + '\n', encoding='utf-8')
(out / 'checks.json').write_text(json.dumps(result, indent=2, ensure_ascii=True) + '\n', encoding='utf-8')
print(json.dumps({'status': result['status'], 'passed_check_count': result['passed_check_count'], 'archive': result['archive'], 'schema_regex_probe': schema_probe}, indent=2))
