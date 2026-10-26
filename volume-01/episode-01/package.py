"""Package the six original comic pages as a standard CBZ. No image processing."""
import json
import struct
import zipfile
from pathlib import Path
from xml.etree.ElementTree import Element, SubElement, tostring

root = Path(__file__).resolve().parent
episode = json.loads((root / 'episode.json').read_text())
info = Element('ComicInfo')
for key, value in {
    'Title': episode['episode'],
    'Series': episode['series'],
    'Number': '1',
    'Volume': '1',
    'PageCount': str(len(episode['pages'])),
    'LanguageISO': 'zh',
    'Summary': episode['adaptation'],
}.items():
    SubElement(info, key).text = value

files = []
for page in episode['pages']:
    path = root / page['file']
    with path.open('rb') as stream:
        header = stream.read(24)
    if header[:8] != b'\x89PNG\r\n\x1a\n':
        raise ValueError(f'Not a PNG: {path}')
    width, height = struct.unpack('>II', header[16:24])
    if width < 1000 or height < 1500:
        raise ValueError(f'Insufficient page resolution: {path}')
    files.append(path)
    print(f'{path.name}: {width} x {height}')

archive_path = root / '葬龙谷的风-第一集.cbz'
with zipfile.ZipFile(archive_path, 'w', compression=zipfile.ZIP_STORED) as archive:
    for path in files:
        archive.write(path, path.name)
    archive.writestr('ComicInfo.xml', tostring(info, encoding='utf-8', xml_declaration=True))
with zipfile.ZipFile(archive_path) as archive:
    bad_file = archive.testzip()
    if bad_file is not None:
        raise ValueError(f'Archive validation failed: {bad_file}')
    print(f'CBZ verified: {len(files)} pages, {archive_path.stat().st_size:,} bytes')
