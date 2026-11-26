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
built = json.loads(Path(args.image_inspect).read_text())[0]
expected = built['Id']

with tarfile.open(args.archive, 'r:') as archive:
    def read(name):
        member = archive.getmember(name)
        if not member.isfile() or member.size > 4_000_000:
            raise ValueError(f'Not a small image metadata file: {name}')
        return archive.extractfile(member).read()

    names = set(archive.getnames())
    manifest = json.loads(read('manifest.json'))
    matching = []
    for entry in manifest:
        config = json.loads(read(entry['Config']))
        if (config.get('config') == built['Config']
                and config.get('rootfs', {}).get('diff_ids') == built['RootFS']['Layers']
                and config.get('architecture') == built['Architecture']
                and config.get('os') == built['Os']):
            matching.append(entry)
    if len(matching) != 1:
        raise ValueError('Saved image config does not match the built Docker image')
    config_digest = 'sha256:' + hashlib.sha256(read(matching[0]['Config'])).hexdigest()
    record = dict(image_id=expected, config=matching[0]['Config'], config_digest=config_digest,
                  layers=len(matching[0]['Layers']), transport='docker-archive')
    if {'oci-layout', 'index.json'} <= names:
        layout = json.loads(read('oci-layout'))
        if layout.get('imageLayoutVersion') != '1.0.0':
            raise ValueError(f'Unexpected OCI layout: {layout}')
        leaves = []

        def walk(node, depth=0, digest=None):
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
                    walk(json.loads(raw), depth + 1, descriptor['digest'])
            else:
                leaves.append((digest, node))

        walk(json.loads(read('index.json')))
        # Docker's containerd image store reports a manifest ID in Descriptor/Id;
        # older graph-driver stores report a config ID. Verify the appropriate
        # immutable descriptor, rather than equating these different hashes.
        descriptor = built.get('Descriptor')
        if descriptor:
            if descriptor['digest'] != expected:
                raise ValueError('Docker image ID and descriptor disagree')
            selected = [(digest, node) for digest, node in leaves if digest == expected]
        else:
            selected = [(digest, node) for digest, node in leaves
                        if node.get('config', {}).get('digest') == expected]
        if len(selected) != 1:
            raise ValueError('OCI layout does not uniquely describe the expected image')
        digest, node = selected[0]
        if node['config']['digest'] != config_digest:
            raise ValueError('OCI and Docker compatibility manifests disagree on config')
        record.update(transport='oci-archive', manifest_digest=digest, layer_media_types=sorted({
            layer['mediaType'] for layer in node['layers']}))
    elif config_digest != expected:
        raise ValueError('Legacy Docker archive config ID differs from built image')
    Path(args.output).write_text(json.dumps(record, indent=2) + '\n')
    print(record['transport'])
