"""Development rollout of the physical reference from the built image under Apptainer.

This tests image CUDA/Isaac/camera operation; it is NOT ALE lifecycle validation.
"""
import argparse
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

parser = argparse.ArgumentParser()
parser.add_argument("--grasping", choices=("physical", "assisted"), default="physical")
parser.add_argument("--server", default=str(TASK / "tests/cell_server.py"))
args = parser.parse_args()
assisted = args.grasping == "assisted"
hidden = json.loads((TASK / "tests/hidden/shifts.json").read_text())
token = (TASK / "solution/privileged/oracle_token").read_text().strip()
env = dict(os.environ, CELL_TOKEN_SHA256=(TASK / "tests/oracle_token.sha256").read_text().strip())
started = time.monotonic()
sim = SimClient(args.server, env=env, log_path=str(OUT / "isaac.log"))
try:
    # Truth authorization is checked separately by sim.truth(). Omitting the reset
    # token keeps ordinary friction-only grasping while allowing author diagnosis.
    obs = sim.reset("track", hidden["seeds"][0], 20, cameras=("head",), salt=hidden.get("salt", 0), token=token if assisted else "")
    assert sim.truth(token)["assisted"] is assisted
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
    print(json.dumps({"camera_check_passed": True, "truth_gate_passed": True,
                      "assisted_grasping": assisted,
                      "startup_elapsed_s": time.monotonic()-started}), flush=True)
    oracle = Oracle(**json.loads((TASK / "solution/privileged/reference_params.json").read_text()))
    for step in range(30000):
        if obs["done"]:
            break
        truth = sim.truth(token)
        row = oracle.act({"proprio": np.asarray(truth["proprio"], float)}, truth)
        obs = sim.step(row, cameras=("head",) if step == 0 else ())
        if step % 1000 == 0:
            progress = sim.summary()
            progress.update(completed_shift=False, official_ale_validate=False,
                            privileged_state=True, assisted_grasping=assisted,
                            elapsed_s=time.monotonic()-started)
            (OUT / "physical-progress.json").write_text(json.dumps(progress, indent=2) + "\n")
            print(json.dumps({k: progress[k] for k in
                              ("steps", "events_done", "parts", "placed", "elapsed_s")}), flush=True)
    result = sim.summary()
    result.update(
        scope="Built Docker image converted to Apptainer; one truth-driven controller shift",
        image_overlay=os.environ.get("CHUTE_IMAGE_OVERLAY", ""),
        privileged_state=True, assisted_grasping=assisted,
        official_ale_validate=False, uid_isolation_tested=False, match_lock_tested=False,
        elapsed_s=time.monotonic()-started, rgb_std=float(rgb.std()),
        depth_nonzero_fraction=float(np.mean(depth > 0)),
        completed_shift=bool(obs["done"]) and result["events_done"] == result["parts"],
    )
    (OUT / "physical-smoke.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({k:v for k,v in result.items() if k not in {"records", "constants"}}), flush=True)
    if not result["completed_shift"]:
        raise RuntimeError("GPU smoke did not finish its complete shift; partial result was preserved")
finally:
    sim.close()
