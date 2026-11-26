"""Identify the saved-image transport and verify its config before SIF conversion."""
import argparse
import hashlib
import json
from pathlib import Path
import tarfile

parser = argparse.ArgumentParser()
parser.add_argument('archive')
parser.add_argument('image_inspect')
parser.add_argument('output')
args = parser.parse_args()
expected = json.loads(Path(args.image_inspect).read_text())[0]['Id']

with tarfile.open(args.archive, 'r:') as archive:
    def read(name):
        member = archive.getmember(name)
        if not member.isfile() or member.size > 4_000_000:
            raise ValueError(f'Not a small image metadata file: {name}')
        return archive.extractfile(member).read()

    names = set(archive.getnames())
    manifest = json.loads(read('manifest.json'))
    matching = [entry for entry in manifest
                if 'sha256:' + hashlib.sha256(read(entry['Config'])).hexdigest() == expected]
    if len(matching) != 1:
        raise ValueError('Saved image config does not match the built Docker image')
    record = dict(image_id=expected, config=matching[0]['Config'],
                  layers=len(matching[0]['Layers']), transport='docker-archive')
    if {'oci-layout', 'index.json'} <= names:
        layout = json.loads(read('oci-layout'))
        if layout.get('imageLayoutVersion') != '1.0.0':
            raise ValueError(f'Unexpected OCI layout: {layout}')
        leaves = []

        def walk(node, depth=0):
            if depth > 4:
                raise ValueError('OCI index nesting limit exceeded')
            if 'manifests' in node:
                for descriptor in node['manifests']:
                    algo, digest = descriptor['digest'].split(':', 1)
                    if algo != 'sha256':
                        raise ValueError('Unsupported digest algorithm')
                    raw = read(f'blobs/sha256/{digest}')
                    if hashlib.sha256(raw).hexdigest() != digest:
                        raise ValueError('OCI manifest digest mismatch')
                    walk(json.loads(raw), depth + 1)
            else:
                leaves.append(node)

        walk(json.loads(read('index.json')))
        selected = [node for node in leaves if node.get('config', {}).get('digest') == expected]
        if len(selected) != 1:
            raise ValueError('OCI layout does not uniquely describe the expected image')
        record.update(transport='oci-archive', layer_media_types=sorted({
            layer['mediaType'] for layer in selected[0]['layers']}))
    Path(args.output).write_text(json.dumps(record, indent=2) + '\n')
    print(record['transport'])
