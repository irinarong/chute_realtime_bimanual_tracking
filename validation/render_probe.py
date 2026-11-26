"""Author-only static RGB diagnostic; never used by task grading or setup."""
import ctypes
import json
from pathlib import Path
import sys
import time

import numpy as np
from PIL import Image

sys.path.insert(0, '/task/tests')
out = Path('/results')
started = time.monotonic()
report = dict(scope='Static rendering diagnostic, no agent or scored rollout',
              official_ale_validate=False, image_overlay='Kit and Warp1.16')
try:
    ngx = ctypes.CDLL('libnvidia-ngx.so.1')
    report['ngx_loadable'] = True
except OSError as exc:
    report.update(ngx_loadable=False, ngx_error=str(exc))
(out / 'render-probe.json').write_text(json.dumps(report, indent=2) + '\n')

from cell_env import Cell
hidden = json.loads(Path('/task/tests/hidden/shifts.json').read_text())
cell = Cell('track', hidden['seeds'][0], n_parts=20, salt=hidden.get('salt', 0), assisted=False)
try:
    import carb
    settings = carb.settings.get_settings()
    keys = ['/rtx/rendermode', '/rtx/rtx/modes/rt/enabled', '/rtx/rtx/modes/rt2/enabled',
            '/rtx/post/dlss/execMode', '/rtx/post/aa/op']
    report['settings'] = {k: settings.get(k) for k in keys}
    report['captures'] = []
    initial_time = float(cell.og.sim.current_time)
    initial_joints = cell.robot.get_joint_positions().detach().cpu().numpy().copy()
    initial_poses = [np.concatenate([v.detach().cpu().numpy() for v in p.get_position_orientation()]) for p in cell.parts]
    rendered = 0
    for target in (4, 32, 128):
        for _ in range(target-rendered):
            cell.og.sim.render()
        rendered = target
        obs = cell._capture(('head',))['head']
        rgb = obs['rgb']
        Image.fromarray(rgb).save(out / f'head-render-{target:03}.png')
        np.save(out / f'depth-render-{target:03}.npy', obs['depth'])
        joints = cell.robot.get_joint_positions().detach().cpu().numpy()
        poses = [np.concatenate([v.detach().cpu().numpy() for v in p.get_position_orientation()]) for p in cell.parts]
        row = dict(render_calls=target, task_step=cell.step_id,
                   physics_time_delta=float(cell.og.sim.current_time)-initial_time,
                   max_joint_delta=float(np.max(np.abs(joints-initial_joints))),
                   max_part_pose_delta=float(np.max(np.abs(np.array(poses)-initial_poses))),
                   rgb_mean=float(rgb.mean()), rgb_std=float(rgb.std()),
                   # Diagnostic statistic only: not an image-quality pass criterion.
                   adjacent_pixel_difference=float(np.abs(np.diff(rgb.astype(float), axis=1)).mean()),
                   elapsed_s=time.monotonic()-started)
        report['captures'].append(row)
        (out / 'render-probe.json').write_text(json.dumps(report, indent=2) + '\n')
        print(json.dumps(row), flush=True)
        assert row['task_step'] == 0 and row['physics_time_delta'] == 0
        assert row['max_joint_delta'] < 1e-6 and row['max_part_pose_delta'] < 1e-6
    report['loaded_ngx_maps'] = [line for line in Path('/proc/self/maps').read_text().splitlines() if 'ngx' in line.lower()]
    report['completed'] = True
    (out / 'render-probe.json').write_text(json.dumps(report, indent=2) + '\n')
finally:
    cell.og.shutdown()
