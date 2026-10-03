#!/usr/bin/env python3
"""Offline checks for this fixture; does not connect to or execute Splunk."""
import configparser
import hashlib
import json
from pathlib import Path
import re
import tarfile
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / 'output'
config = json.loads((ROOT / 'input/native.json').read_text(encoding='utf-8'))
app = OUT / config['app_id']
selected = [
    'default/app.conf',
    'default/data/ui/nav/default.xml',
    'default/data/ui/views/home.xml',
    'metadata/default.meta',
]
checks = []

def check(name, condition):
    if not condition:
        raise AssertionError(name)
    checks.append({'name': name, 'status': 'passed'})

def digest(data):
    return hashlib.sha256(data).hexdigest()

manifest = json.loads((app / 'release-files.json').read_text(encoding='utf-8'))
check('Explicit release manifest selects exactly the four reviewed files',
      manifest == {'schema_version': 1, 'files': selected})
check('App root and release identity match the supplied input', app.name == config['app_id'])
conf = configparser.ConfigParser(interpolation=None)
conf.read_string((app / 'default/app.conf').read_text(encoding='utf-8'))
expected_conf = {
    'install': {'state': config['install_state']},
    'ui': {'is_visible': 'true', 'label': config['app_label'], 'default_view': 'home'},
    'launcher': {k: config[k] for k in ('author', 'version', 'description')},
    'package': {'id': config['app_id']},
    'id': {'name': config['app_id'], 'version': config['version']},
}
check('All app.conf values preserve identity, author, version, description and disabled state',
      {section: dict(conf[section]) for section in conf.sections()} == expected_conf)
nav = ET.parse(app / 'default/data/ui/nav/default.xml').getroot()
check('Navigation resolves to the released home view',
      nav.tag == 'nav' and nav.attrib == {'search_view': 'search'} and
      len(nav) == 1 and nav[0].tag == 'view' and
      nav[0].attrib == {'name': 'home', 'default': 'true'})
view = ET.parse(app / 'default/data/ui/views/home.xml').getroot()
check('Native Simple XML contains one table and one inline search',
      view.tag == 'dashboard' and view.get('version') == '1.1' and
      len(view.findall('./row/panel/table')) == 1 and len(list(view.iter('search'))) == 1)
parsed = {
    'app_label': view.findtext('label'),
    'title': view.findtext('./row/panel/title'),
    'query': view.findtext('./row/panel/table/search/query'),
    'earliest': view.findtext('./row/panel/table/search/earliest'),
    'latest': view.findtext('./row/panel/table/search/latest'),
}
check('JSON-decoded label equals parsed XML label', parsed['app_label'] == config['app_label'])
for key in ('title', 'query', 'earliest', 'latest'):
    check(f'JSON-decoded dashboard.{key} equals parsed XML text', parsed[key] == config['dashboard'][key])
metadata = (app / 'metadata/default.meta').read_text(encoding='utf-8').splitlines()
check('App metadata uses the default stanza', metadata[0] == '[]')
meta = dict(line.split('=', 1) for line in metadata[1:] if line.strip())
meta = {k.strip(): v.strip() for k, v in meta.items()}
access = re.fullmatch(r'read\s*:\s*\[\s*(.*?)\s*\]\s*,\s*write\s*:\s*\[\s*(.*?)\s*\]', meta['access'])
check('Metadata ACL has explicit read and write lists', access is not None)
read_roles, write_roles = [[role.strip() for role in group.split(',')] for group in access.groups()]
check('Read and write roles exactly match the input',
      read_roles == config['read_roles'] and write_roles == config['write_roles'])
check('Metadata export scope is none', meta['export'] == 'none' and set(meta) == {'access', 'export'})
archive_path = OUT / f"{config['app_id']}-{config['version']}.tar.gz"
with tarfile.open(archive_path, 'r:gz') as archive:
    members = archive.getmembers()
    expected_members = [config['app_id']] + [config['app_id'] + '/' + name for name in sorted(selected)]
    check('Archive has exactly one app root and the selected release files',
          [member.name for member in members] == expected_members)
    check('Archive contains regular files and the app root directory, with no links',
          members[0].isdir() and all(member.isfile() for member in members[1:]))
    check('Archive ownership, modes and timestamps are normalized',
          all(member.uid == 0 and member.gid == 0 and member.mtime == 0 for member in members) and
          members[0].mode == 0o755 and all(member.mode == 0o644 for member in members[1:]))
    for name in selected:
        check(f'Archived bytes equal the reviewed source: {name}',
              archive.extractfile(config['app_id'] + '/' + name).read() == (app / name).read_bytes())
archive_digest = digest(archive_path.read_bytes())
checksum = (OUT / (archive_path.name + '.sha256')).read_text(encoding='utf-8')
check('SHA-256 sidecar matches the actual archive', checksum == f'{archive_digest}  {archive_path.name}\n')
original_hashes = json.loads((OUT / 'input-hashes.json').read_text(encoding='utf-8'))
check('Every original workspace file is unchanged',
      all((ROOT / path).is_file() and digest((ROOT / path).read_bytes()) == sha
          for path, sha in original_hashes.items()))
current_originals = {p.relative_to(ROOT).as_posix() for p in ROOT.rglob('*')
                     if p.is_file() and not p.is_relative_to(OUT)}
check('Every new deliverable is confined to output/', current_originals == set(original_hashes))
print(json.dumps({
    'status': 'passed',
    'checks': checks,
    'parsed_values': parsed,
    'title_code_points': [f'U+{ord(c):04X}' for c in parsed['title']],
    'query_code_points': [f'U+{ord(c):04X}' for c in parsed['query']],
    'roles': {'read': read_roles, 'write': write_roles},
    'archive': {'path': archive_path.relative_to(ROOT).as_posix(),
                'bytes': archive_path.stat().st_size, 'sha256': archive_digest,
                'members': expected_members},
    'selected_file_sha256': {name: digest((app / name).read_bytes()) for name in selected},
    'original_file_count': len(original_hashes),
}, indent=2, ensure_ascii=False))
