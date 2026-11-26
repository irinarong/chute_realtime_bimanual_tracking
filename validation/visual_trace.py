"""Capture the simulator-side observation/action boundary for author diagnosis.

The task, policy and scorer remain unchanged. Logging wraps SimClient.call, outside
the solver timing interval, and never queries privileged simulator state.
"""
import gzip
import json
from pathlib import Path
import runpy
import sys

sys.path.insert(0, '/task/tests')
from sim_client import SimClient

out = Path('/results/trace')
out.mkdir(exist_ok=False)
call = SimClient.call
camera_packets = 0
requests = 0
actions = (out / 'actions.jsonl').open('w', buffering=1)


def traced_call(self, *args, **kwargs):
    global camera_packets, requests
    result = call(self, *args, **kwargs)
    obs = result.get('obs')
    if obs is not None:
        requests += 1
        if obs.get('cameras'):
            camera_packets += 1
            if camera_packets <= 8 or camera_packets % 20 == 0:
                name = f'{camera_packets:04}-{int(obs["t"]):05}.json.gz'
                with gzip.open(out/name, 'wt') as f:
                    json.dump(obs, f)
        actions.write(json.dumps(dict(op=kwargs.get('op'), t=obs['t'],
                                      action=kwargs.get('action'),
                                      cameras=kwargs.get('cameras'),
                                      received=list(obs.get('cameras', {})),
                                      proprio=obs['proprio']))+'\n')
    return result


SimClient.call = traced_call
try:
    runpy.run_path('/audit/visual_replay.py', run_name='__main__')
finally:
    actions.close()
    (out/'scope.json').write_text(json.dumps(dict(
        purpose='Diagnose zero-contact clean-camera replay', requests=requests,
        camera_packets=camera_packets, private_truth_requested=False,
        policy_modified=False, task_modified=False, official_ale_validate=False), indent=2)+'\n')
