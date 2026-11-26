"""Resolve a host NVIDIA ICD against Apptainer's injected driver library mount.

Author runtime adapter only. Never edits the host ICD or the Docker image.
"""
import argparse
import hashlib
import json
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument('source', type=Path)
parser.add_argument('output', type=Path)
args = parser.parse_args()
raw = args.source.read_bytes()
config = json.loads(raw)
original = config['ICD']['library_path']
soname = Path(original).name
if not soname.startswith(('libGLX_nvidia.so', 'libnvidia-vulkan.so')):
    raise ValueError(f'Unexpected NVIDIA ICD library: {original}')
resolved = '/.singularity.d/libs/' + soname
config['ICD']['library_path'] = resolved
args.output.write_text(json.dumps(config, indent=2) + '\n')
record = dict(source=str(args.source), source_sha256=hashlib.sha256(raw).hexdigest(),
              host_library_path=original, container_library_path=resolved,
              scope='Apptainer driver path adaptation; host ICD unchanged')
args.output.with_suffix('.provenance.json').write_text(json.dumps(record, indent=2) + '\n')
print(json.dumps(record), flush=True)
