"""Development rollout of the physical reference from the built image under Apptainer.

This tests image CUDA/Isaac/camera operation; it is NOT ALE lifecycle validation.
"""
import base64
import io
import json
import os
from pathlib import Path
import sys
import time

import numpy as np
from PIL import Image

TASK = Path("/task")
OUT = Path("/results")
sys.path[:0] = [str(TASK / "tests"), str(TASK / "solution/privileged")]
from sim_client import SimClient, SimError
from oracle import Oracle

hidden = json.loads((TASK / "tests/hidden/shifts.json").read_text())
token = (TASK / "solution/privileged/oracle_token").read_text().strip()
env = dict(os.environ, CELL_TOKEN_SHA256=(TASK / "tests/oracle_token.sha256").read_text().strip())
started = time.monotonic()
sim = SimClient(str(TASK / "tests/cell_server.py"), env=env, log_path=str(OUT / "isaac.log"))
try:
    obs = sim.reset("track", hidden["seeds"][0], 20, cameras=("head",), salt=hidden.get("salt", 0), token=token)
    head = obs["cameras"]["head"]
    rgb = np.asarray(Image.open(io.BytesIO(base64.b64decode(head["rgb_png"]))))
    depth = np.frombuffer(base64.b64decode(head["depth_mm_u16"]), dtype="<u2")
    assert rgb.ndim == 3 and rgb.shape[2] == 3 and rgb.std() > 0
    assert (depth > 0).any()
    Image.fromarray(rgb).save(OUT / "head-initial.png")
    try:
        sim.truth("wrong")
    except SimError:
        pass
    else:
        raise AssertionError("truth gate allowed a wrong token")
    oracle = Oracle(**json.loads((TASK / "solution/privileged/reference_params.json").read_text()))
    for step in range(30000):
        if obs["done"]:
            break
        truth = sim.truth(token)
        row = oracle.act({"proprio": np.asarray(truth["proprio"], float)}, truth)
        obs = sim.step(row, cameras=("head",) if step == 0 else ())
        if step % 1000 == 0:
            print(json.dumps({"step": step, "t": obs["t"], "elapsed_s": time.monotonic()-started}), flush=True)
    result = sim.summary()
    result.update(
        scope="Built Docker image converted to Apptainer; one physical privileged-reference shift",
        official_ale_validate=False, uid_isolation_tested=False, match_lock_tested=False,
        elapsed_s=time.monotonic()-started, rgb_std=float(rgb.std()),
        depth_nonzero_fraction=float(np.mean(depth > 0)),
    )
    (OUT / "physical-smoke.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({k:v for k,v in result.items() if k not in {"records", "constants"}}), flush=True)
finally:
    sim.close()
