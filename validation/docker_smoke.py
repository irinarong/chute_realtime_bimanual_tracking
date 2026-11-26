"""Run inside the exact image, as root, with task sources under /opt/ale/source.

This is a CPU integration smoke test, not an official GPU ALE validation.
"""
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

TASK = Path("/opt/ale/source")
OUT = Path("/tmp/chute-smoke")
OUT.mkdir(exist_ok=True)
env = dict(os.environ, ALE_STAGE_DIR=str(TASK / "tests"), ALE_HOME="/home/user",
           CELL_SIM_PYTHON="/simulator-must-not-start", PYTHONDONTWRITEBYTECODE="1",
           ALE_VERIFY_PYTHON=sys.executable, PYTHONPATH="/opt/ale/engine")
env.pop("ROBOTICS_GRADER_VERDICT_PATH", None)
verifier_output = Path("/logs/verifier")
verifier_output.mkdir(parents=True, exist_ok=True)
verifier_output.chmod(0o700)
sys.path.insert(0, "/opt/ale/engine")
from ale_verify import read_result
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

# Exercise reply-budget accounting under the actual agent UID on Linux.
cpu_checks = Path("/tmp/chute-cpu-meter-tests")
cpu_checks.mkdir(mode=0o755)
for source in (TASK / "tests/cpu_meter.py", TASK / "tests/review/test_cpu_meter.py"):
    destination = cpu_checks / source.name
    shutil.copyfile(source, destination)
    destination.chmod(0o644)
subprocess.run(["runuser", "-u", "user", "--", sys.executable,
                str(cpu_checks / "test_cpu_meter.py")], env=env, check=True)


def verify(name, expected):
    path = OUT / (name + ".json")
    for filename in ("reward.json", "verification.json"):
        (verifier_output / filename).unlink(missing_ok=True)
    subprocess.run([sys.executable, str(TASK / "tests/verify.py")], env=env, check=True)
    verdict = read_result((verifier_output / "reward.json").read_bytes(),
                          (verifier_output / "verification.json").read_bytes())
    assert verdict["reward"] == expected, verdict
    shutil.copyfile(verifier_output / "verification.json", path)
    shutil.copyfile(verifier_output / "reward.json", OUT / (name + "-reward.json"))
    print(name, verdict["reward"], verdict["metrics"], flush=True)


verify("untouched", 0)
# Emulate oracle-only source staging and run the actual solve entry point as user.
oracle_stage = Path("/tmp/chute-oracle-stage")
shutil.copytree(TASK / "solution", oracle_stage)
subprocess.run(["chown", "-R", "user:user", str(oracle_stage)], check=True)
subprocess.run(["runuser", "-u", "user", "--", "bash", str(oracle_stage / "solve.sh")],
               env=env, check=True)
shutil.rmtree(oracle_stage)
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
    "pinned_ale_result_sdk": True, "oracle_entrypoint_runs_as_user": True,
    "agent_uid_cpu_accounting_tests_passed": 3,
    "official_ale_validate": False,
}, indent=2) + "\n")
print("DOCKER_CPU_SMOKE_PASSED", flush=True)
