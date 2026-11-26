"""Run inside the exact image, as root, with task sources under /opt/ale/source.

This is a CPU integration smoke test, not an official GPU ALE validation.
"""
import json
import os
from pathlib import Path
import subprocess
import sys

TASK = Path("/opt/ale/source")
OUT = Path("/tmp/chute-smoke")
OUT.mkdir(exist_ok=True)
env = dict(os.environ, ALE_STAGE_DIR=str(TASK / "tests"), ALE_HOME="/home/user",
           CELL_SIM_PYTHON="/simulator-must-not-start", PYTHONDONTWRITEBYTECODE="1")
env.pop("ALE_VERIFY_PYTHON", None)
subprocess.run(["bash", "setup.sh"], cwd=TASK / "environment/setup", env=env, check=True)
subprocess.run(["runuser", "-u", "user", "--", "bash", "-c",
                'test ! -r /opt/ale/source/tests/anchor.json && test ! -r /opt/ale/source/solution/privileged/oracle_token && test -r /home/user/lab/outcomes.py'],
               check=True)
subprocess.run(["runuser", "-u", "user", "--", "/opt/venv/bin/python", "-c",
                "import numpy,PIL,cv2,torch; from pxr import Usd; print('AGENT_PYTHON_IMPORTS_OK')"], check=True)
subprocess.run(["runuser", "-u", "user", "--", "/opt/sim/bin/python", "-c",
                "import isaacsim,numpy,PIL; print('AGENT_SIM_IMPORTS_OK')"], check=True)
items = json.loads(Path("/opt/cell_items/items.json").read_text())
sys.path.insert(0, str(TASK / "tests"))
from shift import CATALOG
assert len(CATALOG) == 20 and set(CATALOG).issubset(items)
for value in items.values():
    assert Path(value["usd"]).is_file(), value
assert Path(os.environ["CELL_ROOM"]).is_file()
assert Path("/opt/og_data/omnigibson-robot-assets/models/r1pro").is_dir()


def verify(name, expected):
    path = OUT / (name + ".json")
    env["ROBOTICS_GRADER_VERDICT_PATH"] = str(path)
    subprocess.run([sys.executable, str(TASK / "tests/verify.py")], env=env, check=True)
    verdict = json.loads(path.read_text())
    assert verdict["rewards"]["reward"] == expected, verdict
    print(name, verdict["rewards"], verdict["metrics"], flush=True)


verify("untouched", 0)
subprocess.run(["bash", str(TASK / "solution/solve.sh")], env=env, check=True)
subprocess.run(["chown", "-R", "user:user", "/home/user/submission"], check=True)
verify("oracle-1", 1)
verify("oracle-2", 1)
token = Path("/home/user/submission/.oracle_token")
saved = token.read_bytes()
token.write_text("invalid")
verify("unauthorized", 0)
token.write_bytes(saved)
answer = Path("/home/user/submission/ideal_answer.json")
data = json.loads(answer.read_text())
for shift in data["shifts"]:
    for event in shift["events"]:
        event["position_world_m"] = [10, 10, 10]
answer.write_text(json.dumps(data))
verify("wrong-answer", 0)

# Exercise real root -> user process isolation through the canonical solver wire.
answer.unlink()
subprocess.run(["cp", "/home/user/example_controller/run.sh", "/home/user/submission/run.sh"], check=True)
subprocess.run(["cp", "/home/user/example_controller/controller.py", "/home/user/submission/controller.py"], check=True)
subprocess.run(["chown", "-R", "user:user", "/home/user/submission"], check=True)
sys.path.insert(0, str(TASK / "tests"))
os.environ.update(ALE_HOME="/home/user", ALE_STAGE_DIR=str(TASK / "tests"))
from robotics_grader import Solver
solver = Solver(step_timeout=10)
try:
    solver.reset()
    action = solver.act(0, {"t": 0, "proprio": [0.0] * 61, "odometry": [0, 0, 0], "cameras": {}})
    assert len(action) == 26
finally:
    solver.close()
(OUT / "summary.json").write_text(json.dumps({
    "cpu_smoke_passed": True, "root_to_user_solver": True, "asset_count": len(items),
    "synthetic_oracle_reward": 1, "physical_rollout_tested": False,
    "official_ale_validate": False,
}, indent=2) + "\n")
print("DOCKER_CPU_SMOKE_PASSED", flush=True)
