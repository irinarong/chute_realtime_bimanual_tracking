"""Refresh author smoke inputs while preserving the pinned SDK in the prior archive."""
import gzip
import hashlib
import io
import json
from pathlib import Path
import tarfile
import subprocess

ROOT = Path(__file__).resolve().parents[1]
ARCHIVE = ROOT / 'validation/candidate.tar.gz'
entries = {}
with tarfile.open(ARCHIVE) as old:
    for member in old:
        if member.isfile() and member.name.startswith('engine/'):
            entries[member.name] = (old.extractfile(member).read(), 0o644)
assert len(entries) == 18, 'the pinned ale_verify and fastjsonschema sources are required'
for name in ('docker_smoke.py', 'docker_smoke.sh', 'physical_reference_smoke.py'):
    p = ROOT / 'validation' / name
    entries[name] = (p.read_bytes(), 0o755 if p.suffix == '.sh' else 0o644)
task = ROOT / 'tasks/arm/chute_realtime_bimanual_tracking'
for p in sorted(task.rglob('*')):
    if not p.is_file() or any(part in {'__pycache__', '.DS_Store'} or part.startswith('._')
                              for part in p.relative_to(task).parts):
        continue
    assert not p.is_symlink(), p
    entries[str(p.relative_to(ROOT))] = (p.read_bytes(), 0o755 if p.suffix == '.sh' else 0o644)
prefix = str(task.relative_to(ROOT)) + '/'
tracked = subprocess.check_output(['git', 'ls-files', '--', prefix], cwd=ROOT, text=True).splitlines()
assert set(tracked) == {name for name in entries if name.startswith(prefix)}, 'Untracked or missing task files'
provenance = {
    'git_commit': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
    'task_git_tree': subprocess.check_output(['git', 'rev-parse', 'HEAD:' + prefix.rstrip('/')], cwd=ROOT, text=True).strip(),
    'task_files': {name[len(prefix):]: hashlib.sha256(entries[name][0]).hexdigest() for name in tracked},
}
for name in tracked:
    committed = subprocess.check_output(['git', 'show', 'HEAD:' + name], cwd=ROOT)
    assert committed == entries[name][0], 'Commit task changes before packaging: ' + name
entries['source-provenance.json'] = ((json.dumps(provenance, indent=2) + '\n').encode(), 0o644)
next_archive = ARCHIVE.with_name('candidate.next.tar.gz')
with next_archive.open('wb') as output, gzip.GzipFile(fileobj=output, filename='', mode='wb', mtime=0) as gz, tarfile.open(fileobj=gz, mode='w') as archive:
    for name, (contents, mode) in sorted(entries.items()):
        member = tarfile.TarInfo(name)
        member.size, member.mode, member.mtime = len(contents), mode, 0
        archive.addfile(member, io.BytesIO(contents))
next_archive.replace(ARCHIVE)
manifest = {'scope': 'Author smoke bundle; SDK is not part of the submitted task',
            'sha256': hashlib.sha256(ARCHIVE.read_bytes()).hexdigest(),
            'source_provenance': provenance,
            'files': {name: hashlib.sha256(contents).hexdigest() for name, (contents, _) in sorted(entries.items())}}
ARCHIVE.with_name('candidate-manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
print(json.dumps({'sha256': manifest['sha256'], 'file_count': len(entries)}))
