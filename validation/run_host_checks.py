"""Record real solve/verify entrypoint results. Requires NumPy; never runs Isaac."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
TASK = ROOT / "tasks/arm/chute_realtime_bimanual_tracking"
OUT = ROOT / "validation/host-runs"
OUT.mkdir(exist_ok=True)

with tempfile.TemporaryDirectory(prefix="chute-reference-") as temp:
    home = Path(temp)
    env = dict(os.environ, ALE_HOME=str(home), ALE_STAGE_DIR=str(TASK / "tests"),
               CELL_SIM_PYTHON="/simulator-must-not-start", PYTHONDONTWRITEBYTECODE="1")
    env.pop("ALE_VERIFY_PYTHON", None)

    def verify(name, expected):
        path = OUT / (name + ".json")
        env["ROBOTICS_GRADER_VERDICT_PATH"] = str(path)
        subprocess.run([sys.executable, str(TASK / "tests/verify.py")], env=env, check=True)
        data = json.loads(path.read_text())
        assert data["rewards"]["reward"] == expected, data
        print(name, data["rewards"], data["metrics"])

    verify("untouched", 0)
    subprocess.run(["bash", str(TASK / "solution/solve.sh")], env=env, check=True)
    verify("oracle-1", 1)
    verify("oracle-2", 1)
    token = home / "submission/.oracle_token"
    saved = token.read_bytes()
    token.write_text("invalid")
    verify("unauthorized", 0)
    token.write_bytes(saved)
    answer = home / "submission/ideal_answer.json"
    data = json.loads(answer.read_text())
    for shift in data["shifts"]:
        for event in shift["events"]:
            event["position_world_m"] = [10, 10, 10]
    answer.write_text(json.dumps(data))
    verify("wrong-answer", 0)
