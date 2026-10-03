#!/usr/bin/env python3
"""Offline, read-only verification of this fixture's selected native release."""
import configparser
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import sys
import tarfile
import xml.etree.ElementTree as ET

sys.dont_write_bytecode = True
root = Path(__file__).resolve().parent.parent
out = root / 'output'
source = root / 'input/native.json'
helper_path = root / 'candidate/scripts/splunk_app.py'
app = out / 'bench_delta'
archive = out / 'bench_delta-0.2.1.tar.gz'
checks = []


def check(condition, name):
    if not condition:
        raise AssertionError(name)
    checks.append({'check': name, 'status': 'passed'})


def sha(data):
    return hashlib.sha256(data).hexdigest()


check(sha(source.read_bytes()) == '35313a2b28a98d43365c1e654fa6e9d590fcf08523da696be485974e5b888249',
      'Input fixture unchanged from its initial recorded SHA-256')
check(sha(helper_path.read_bytes()) == 'b747f2a60829b268aafd2cbd4d14a560525cbdb9bf07b97ba045ed28fb74dbda',
      'Supplied helper unchanged from its initial recorded SHA-256')
spec = importlib.util.spec_from_file_location('fixture_splunk_helper', helper_path)
helper = importlib.util.module_from_spec(spec)
spec.loader.exec_module(helper)
config = helper.validate_config(helper.read_json(source))
checks.append({'check': 'Decoded input passes the supplied helper config contract', 'status': 'passed'})
manifest = helper.read_json(app / 'release-files.json')
expected_files = {
    'default/app.conf', 'default/data/ui/nav/default.xml',
    'default/data/ui/views/home.xml', 'metadata/default.meta',
}
check(manifest['schema_version'] == 1 and len(manifest['files']) == 4
      and set(manifest['files']) == expected_files,
      'Explicit release selection contains exactly the four intended runtime files')
_, selected = helper.selected_files(app, app / 'release-files.json')
checks.append({'check': 'Selected files pass helper path, regular-file, link and size checks', 'status': 'passed'})

conf = configparser.ConfigParser(interpolation=None)
conf.read_string(selected['default/app.conf'].decode('utf-8'))
expected_conf = {
    'install': {'state': config['install_state']},
    'ui': {'is_visible': 'true', 'label': config['app_label'], 'default_view': 'home'},
    'launcher': {'author': config['author'], 'version': config['version'],
                 'description': config['description']},
    'package': {'id': config['app_id']},
    'id': {'name': config['app_id'], 'version': config['version']},
}
check(app.name == config['app_id'] and not conf.defaults()
      and {section: dict(conf[section]) for section in conf.sections()} == expected_conf,
      'App identity, label, author, version, description and disabled state match decoded input')
meta_lines = selected['metadata/default.meta'].decode('utf-8').splitlines()
check(len(meta_lines) == 3 and meta_lines[0] == '[]', 'ACL uses one app-wide metadata stanza')
meta = dict(line.split('=', 1) for line in meta_lines[1:])
meta = {key.strip(): value.strip() for key, value in meta.items()}
acl = re.fullmatch(r'read\s*:\s*\[\s*(.*?)\s*\],\s*write\s*:\s*\[\s*(.*?)\s*\]', meta.get('access', ''))
check(acl is not None
      and [value.strip() for value in acl.group(1).split(',')] == config['read_roles']
      and [value.strip() for value in acl.group(2).split(',')] == config['write_roles']
      and meta.get('export') == 'none',
      'ACL read/write roles equal the supplied role arrays; export is none')

nav = helper.parse_xml(selected['default/data/ui/nav/default.xml'])
check(nav.tag == 'nav' and nav.get('search_view') == 'search'
      and len(nav) == 1 and nav[0].tag == 'view'
      and nav[0].attrib == {'name': 'home', 'default': 'true'}
      and 'default/data/ui/views/home.xml' in selected,
      'Default navigation and app default_view resolve to the selected home dashboard')
view = helper.parse_xml(selected['default/data/ui/views/home.xml'])
searches = view.findall('./row/panel/table/search')
check(view.tag == 'dashboard' and view.attrib == {'version': '1.1', 'theme': 'light'}
      and len(view.findall('.//row')) == len(view.findall('.//panel')) == 1
      and len(view.findall('.//table')) == len(view.findall('.//search')) == len(searches) == 1
      and searches[0].attrib == {}
      and [node.tag for node in searches[0]] == ['query', 'earliest', 'latest'],
      'Native Simple XML has one table and one explicitly scoped inline search')
parsed = {
    'app_label': view.findtext('label'),
    'title': view.findtext('./row/panel/title'),
    'query': searches[0].findtext('query'),
    'earliest': searches[0].findtext('earliest'),
    'latest': searches[0].findtext('latest'),
}
expected_text = {'app_label': config['app_label'], **config['dashboard']}
check(parsed == expected_text
      and all(len(node) == 0 for node in searches[0])
      and len(view.find('label')) == len(view.find('./row/panel/title')) == 0,
      'Parsed XML text equals decoded JSON as exact Unicode strings, including query and time range')
text_evidence = {
    key: {'decoded_input': expected_text[key], 'parsed_xml': value, 'equal': value == expected_text[key],
          'code_points': ['U+%04X' % ord(character) for character in value]}
    for key, value in parsed.items()
}

package_result = json.loads((out / 'package-receipt.json').read_text(encoding='utf-8'))
check(package_result['structure'] == 'passed' and package_result['package'] == 'created'
      and package_result['app_id'] == config['app_id']
      and package_result['version'] == config['version']
      and package_result['selected_file_count'] == len(selected)
      and set(package_result['selected_files']) == set(selected),
      'Actual helper packaging receipt records successful structure validation and selected identity')
payload = archive.read_bytes()
digest = sha(payload)
check(digest == package_result['sha256'] and len(payload) == package_result['archive_bytes'],
      'Independent archive SHA-256 and byte size match the packaging receipt')
with tarfile.open(archive, 'r:gz') as tar:
    members = tar.getmembers()
    check(len(members) == len(selected) + 1 and members[0].isdir()
          and members[0].name.rstrip('/') == config['app_id']
          and {member.name for member in members[1:]} == {
              config['app_id'] + '/' + name for name in selected}
          and all(member.isfile() for member in members[1:]),
          'Archive has one app root and exactly the selected regular files, with no links or extra content')
    for member in members[1:]:
        relative = member.name[len(config['app_id']) + 1:]
        check(tar.extractfile(member).read() == selected[relative],
              'Archive payload equals selected source bytes: ' + relative)
    check(all(member.mtime == 0 and member.uid == member.gid == 0
              and member.uname == member.gname == '' for member in members)
          and members[0].mode == 0o755 and all(member.mode == 0o644 for member in members[1:])
          and int.from_bytes(payload[4:8], 'little') == 0,
          'Archive timestamps, owners and modes use the deterministic helper settings')
    archive_members = [{'name': member.name, 'type': 'directory' if member.isdir() else 'file',
                        'size': member.size, 'mode': oct(member.mode), 'mtime': member.mtime}
                       for member in members]

print(json.dumps({
    'schema_version': 1, 'fixture_only': True,
    'source': {'config': 'input/native.json', 'config_sha256': sha(source.read_bytes()),
               'helper': 'candidate/scripts/splunk_app.py', 'helper_sha256': sha(helper_path.read_bytes())},
    'app_id': config['app_id'], 'version': config['version'],
    'checks': checks, 'text_round_trip': text_evidence,
    'selected_files': [{'path': name, 'bytes': len(content), 'sha256': sha(content)}
                       for name, content in selected.items()],
    'archive': {'path': 'output/' + archive.name, 'sha256': digest, 'bytes': len(payload),
                'members': archive_members},
    'content_review': 'Four selected UTF-8 text files inspected; only app configuration, navigation, dashboard and ACL metadata are included.',
    'deployment_target': None, 'splunk_version': None, 'deployment_type': None,
    'appinspect': 'not_run', 'installed': False, 'runtime': 'not_run',
}, ensure_ascii=False, indent=2))
