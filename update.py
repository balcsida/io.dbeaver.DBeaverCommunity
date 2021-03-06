#!/usr/bin/env python3

import os
import sys
import subprocess
import yaml
import json
import urllib.request
import shutil
import iso8601
from lxml import etree

MANIFEST = 'io.dbeaver.DBeaverCommunity.yml'
APPDATA = 'io.dbeaver.DBeaverCommunity.appdata.xml'

with urllib.request.urlopen('https://api.github.com/repos/dbeaver/dbeaver/releases/latest') as url:
    RELEASEDATA = json.loads(url.read().decode())
    VERSION = RELEASEDATA['tag_name']

with open(MANIFEST, 'r') as yaml_file:
    data = yaml.load(yaml_file)

if VERSION in data['modules'][-1]['sources'][-1]['url']:
    print('No update needed. Current version: ' + VERSION)
    sys.exit()

source_entry = data['modules'][-1]['sources'][-1]
source_entry['url'] = 'https://github.com/dbeaver/dbeaver/releases/download/' + VERSION + '/dbeaver-ce-' + VERSION + '-linux.gtk.x86_64.tar.gz'
FILENAME = 'dbeaver-ce-' + VERSION + '-linux.gtk.x86_64.tar.gz'

# This is currently broken, something about YML is not quite right
# print('Downloading ' + FILENAME)
# with urllib.request.urlopen(source_entry['url']) as response, open(FILENAME, 'wb') as out_file:
#     shutil.copyfileobj(response, out_file)
# print('Download complete')

# source_entry['sha256'] = subprocess.check_output(['sha256sum', FILENAME]).decode("utf-8").split(None, 1)[0]
# source_entry['size'] = os.path.getsize(FILENAME)

# with open(MANIFEST, 'w') as yaml_file:
#     yaml.dump(data, yaml_file)

release = etree.Element('release', {
    'version': VERSION,
    'date': iso8601.parse_date(RELEASEDATA['published_at']).strftime('%Y-%m-%d')
})

# TODO: add missing elements (ul/li)
description = etree.SubElement(release,'description')
description.text = RELEASEDATA['body']

parser = etree.XMLParser(remove_comments=False)
tree = etree.parse(APPDATA, parser=parser)
releases = tree.find('releases')
old_releases = list(releases)[:3]
for child in list(releases):
    releases.remove(child)
release.tail = '\n  '
releases.append(release)
for o_r in old_releases:
    releases.append(o_r)
tree.write(APPDATA, encoding="utf-8", xml_declaration=True)

# os.remove(FILENAME)

print("Update done. New version: " + VERSION)
