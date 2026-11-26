"""Stage this host's NGX driver for author Apptainer runs; never ship it in the task.

Apptainer's default nvliblist omits NGX on DCC. Controlled run62728432 showed
severe RGB noise without it and clean DLSS output with it, without physics changes.
Official ALE Docker requests NVIDIA_DRIVER_CAPABILITIES=all instead.
"""
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys

target = Path(sys.argv[1])
target.mkdir(parents=True, exist_ok=False)
listing = subprocess.check_output(['/sbin/ldconfig', '-p'], text=True)
paths = [Path(line.split('=>', 1)[1].strip()).resolve()
         for line in listing.splitlines()
         if line.strip().startswith('libnvidia-ngx.so.1 ') and 'x86-64' in line]
paths = sorted(set(paths))
if len(paths) != 1:
    raise RuntimeError(f'Expected one host64-bit NGX library, found {paths}')
source = paths[0]
dest = target / 'libnvidia-ngx.so.1'
shutil.copyfile(source, dest)
digest = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
assert digest(source) == digest(dest)
report = dict(scope='Host-matched driver injection for author Apptainer only',
              source=str(source), staged=str(dest), sha256=digest(dest))
(target / 'provenance.json').write_text(json.dumps(report, indent=2) + '\n')
print(json.dumps(report))
