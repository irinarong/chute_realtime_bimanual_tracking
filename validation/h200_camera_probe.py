"""Capture the ordinary agent's initial RGB-D observation on the declared GPU.

Public seed, no truth token, no actions, no hidden evaluation or extra rendering.
Image statistics are descriptive; visual inspection is recorded separately.
"""
import base64
import hashlib
import io
import json
import os
from pathlib import Path
import sys
import time

import numpy as np
from PIL import Image

TASK, OUT = Path('/task'), Path('/results')
sys.path.insert(0, str(TASK / 'tests'))
from sim_client import SimClient

provenance = json.loads((OUT / 'candidate/source-provenance.json').read_text())
for name, expected in provenance['task_files'].items():
    assert hashlib.sha256((TASK / name).read_bytes()).hexdigest() == expected, name
started = time.monotonic()
report = dict(scope='Ordinary initial RGB-D observation; public seed17, no controller',
              task_source=provenance['git_commit'], task_tree=provenance['task_git_tree'],
              privileged_state=False, assisted_grasping=False, hidden_evaluation=False,
              official_ale_validate=False, extra_render_calls=0, actions_sent=0)
sim = SimClient(str(TASK / 'tests/cell_server.py'),
                env=dict(os.environ, CELL_TOKEN_SHA256=''),
                log_path=str(OUT / 'camera-isaac.log'))
try:
    obs = sim.reset('track', 17, parts=20, cameras=('head', 'left_wrist', 'right_wrist'), salt=0, token='')
    report.update(task_step=obs['t'], cameras={})
    assert set(obs['cameras']) == {'head', 'left_wrist', 'right_wrist'}
    for name, data in obs['cameras'].items():
        png = base64.b64decode(data['rgb_png'])
        (OUT / (name + '.png')).write_bytes(png)
        rgb = np.asarray(Image.open(io.BytesIO(png)))
        depth = np.frombuffer(base64.b64decode(data['depth_mm_u16']), dtype='<u2').reshape(data['shape'])
        np.save(OUT / (name + '-depth.npy'), depth)
        assert rgb.shape[:2] == depth.shape
        report['cameras'][name] = dict(shape=list(rgb.shape), t_capture=data['t_capture'],
            rgb_std=float(rgb.std()), rgb_mean=float(rgb.mean()),
            depth_nonzero_fraction=float(np.mean(depth > 0)), png_sha256=hashlib.sha256(png).hexdigest())
    report['completed'] = True
except Exception as exc:
    report.update(completed=False, error=str(exc))
    raise
finally:
    report['elapsed_s'] = time.monotonic() - started
    (OUT / 'camera-probe.json').write_text(json.dumps(report, indent=2) + '\n')
    sim.close()
print(json.dumps(report), flush=True)
