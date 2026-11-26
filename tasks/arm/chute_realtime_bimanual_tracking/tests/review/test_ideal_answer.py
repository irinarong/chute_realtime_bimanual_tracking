import copy
import json
import os
from pathlib import Path
import subprocess
import sys

import numpy as np
import pytest

HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE))
from cell_env import LOW_END, TOTE_AT
from ideal_answer import ARTIFACT, evaluate, maybe_verdict
from outcomes import inside_tote, layout_offsets, released_and_resting, summarize_credits
from props import TOTE

HIDDEN = json.loads((HERE / "hidden/shifts.json").read_text())
CONFIG = json.loads((HERE / "grader_config.json").read_text())
SEEDS, SALT = HIDDEN["seeds"], HIDDEN.get("salt", 0)
ANSWER = json.loads((HERE.parent / "solution/privileged" / ARTIFACT).read_text())


def score(answer):
    return evaluate(answer, SEEDS, SALT, 20)


def test_perfect_and_wrong_states():
    value, details = score(ANSWER)
    assert value == 1 and [d["placed"] for d in details] == [20] * 6
    for field, value in [
        ("position_world_m", [20, 20, 20]),
        ("velocity_m_s", [0.05, 0, 0]),
        ("finger_contacts", [True, False, False, False]),
    ]:
        answer = copy.deepcopy(ANSWER)
        for shift in answer["shifts"]:
            for event in shift["events"]:
                event[field] = value
        assert score(answer)[0] == 0
    answer = copy.deepcopy(ANSWER)
    answer["shifts"][0]["events"][0]["position_world_m"] = [20, 20, 20]
    assert score(answer)[0] == pytest.approx(119 / 120)
    answer = copy.deepcopy(ANSWER)
    for shift in answer["shifts"]:
        shift["bystander_max_displacements_m"] = [0.051, 0]
    assert score(answer)[0] == pytest.approx(0.975)


@pytest.mark.parametrize("mutation", ["missing_shift", "missing_event", "duplicate_event", "nan", "string", "reward", "wrong_seed", "negative_displacement"])
def test_malformed(mutation):
    answer = copy.deepcopy(ANSWER)
    event = answer["shifts"][0]["events"][0]
    if mutation == "missing_shift": answer["shifts"].pop()
    if mutation == "missing_event": answer["shifts"][0]["events"].pop()
    if mutation == "duplicate_event": answer["shifts"][0]["events"][1] = event
    if mutation == "nan": event["position_world_m"][0] = float("nan")
    if mutation == "string": event["position_world_m"][0] = "0.1"
    if mutation == "reward": answer["reward"] = 1
    if mutation == "wrong_seed": answer["shifts"][0]["seed"] += 1
    if mutation == "negative_displacement": answer["shifts"][0]["bystander_max_displacements_m"][0] = -1
    with pytest.raises(ValueError):
        score(answer)


def test_authorization_and_bad_files(tmp_path):
    assert maybe_verdict(tmp_path, HERE, CONFIG, 1, {}) is None
    answer = tmp_path / ARTIFACT
    answer.write_text(json.dumps(ANSWER))
    assert maybe_verdict(tmp_path, HERE, CONFIG, 1, {})["rewards"]["reward"] == 0
    token = tmp_path / ".oracle_token"
    token.write_text("wrong")
    assert maybe_verdict(tmp_path, HERE, CONFIG, 1, {})["rewards"]["reward"] == 0
    token.write_bytes((HERE.parent / "solution/privileged/oracle_token").read_bytes())
    verdict = maybe_verdict(tmp_path, HERE, CONFIG, 1, {})
    assert verdict["rewards"]["reward"] == 1
    assert verdict["metrics"]["synthetic_reference"] == 1
    assert verdict["metrics"]["physical_rollout"] == 0
    answer.write_text('{"bad":')
    assert maybe_verdict(tmp_path, HERE, CONFIG, 1, {})["rewards"]["reward"] == 0
    answer.write_text("x" * 1_000_001)
    assert maybe_verdict(tmp_path, HERE, CONFIG, 1, {})["rewards"]["reward"] == 0
    answer.unlink()
    answer.symlink_to(HERE.parent / "solution/privileged" / ARTIFACT)
    assert maybe_verdict(tmp_path, HERE, CONFIG, 1, {})["rewards"]["reward"] == 0
    answer.unlink()
    os.mkfifo(answer)
    assert maybe_verdict(tmp_path, HERE, CONFIG, 1, {})["rewards"]["reward"] == 0


def test_layout_and_raw_metric_regression():
    for seed in SEEDS:
        g = np.random.default_rng([21, seed, SALT])
        low = LOW_END + [g.uniform(-0.05, 0.05), g.uniform(-0.08, 0.08), g.uniform(-0.03, 0.03)]
        yaw = g.uniform(-0.15, 0.15)
        tote = TOTE_AT + [g.uniform(-0.05, 0.05), g.uniform(-0.05, 0.05), 0]
        new_g, new_low, new_yaw, new_tote = layout_offsets(seed, SALT, LOW_END, TOTE_AT)
        np.testing.assert_array_equal(low, new_low)
        assert yaw == new_yaw
        np.testing.assert_array_equal(tote, new_tote)
        np.testing.assert_array_equal(g.permutation(20), new_g.permutation(20))
    rng = np.random.default_rng(72)
    for _ in range(200):
        c = rng.choice([0, 0.5, 1], 20).tolist()
        moved = int(rng.integers(3))
        got = summarize_credits(c, moved)
        assert got["score"] == max(0, (sum(c) - 0.5 * moved) / 20)
        assert got["score_first_third"] == sum(c[:6]) / 6
        assert got["score_last_third"] == sum(c[-6:]) / 6
        local = rng.uniform(-0.5, 0.5, 3)
        a, b, h = TOTE["inner"]
        expected = abs(local[0]) < a / 2 and abs(local[1]) < b / 2 and -0.01 < local[2] < h + 0.30
        assert inside_tote(local + TOTE_AT, TOTE_AT, np.eye(3), TOTE["inner"]) == expected
    assert not released_and_resting(True, False, 0.05, 0.05)
    assert not released_and_resting(True, True, 0, 0.05)


def test_actual_entrypoints_without_simulator(tmp_path):
    env = dict(os.environ, ALE_HOME=str(tmp_path), ALE_STAGE_DIR=str(HERE),
               ROBOTICS_GRADER_VERDICT_PATH=str(tmp_path / "verdict.json"),
               CELL_SIM_PYTHON="/simulator-must-not-start")
    env.pop("ALE_VERIFY_PYTHON", None)
    subprocess.run([sys.executable, str(HERE / "verify.py")], env=env, check=True)
    assert json.loads((tmp_path / "verdict.json").read_text())["rewards"]["reward"] == 0
    subprocess.run(["bash", str(HERE.parent / "solution/solve.sh")], env=env, check=True)
    subprocess.run([sys.executable, str(HERE / "verify.py")], env=env, check=True)
    v = json.loads((tmp_path / "verdict.json").read_text())
    assert v["rewards"]["reward"] == 1
    assert v["metrics"]["part_pickup_score"] == 1
    assert v["metrics"]["physical_rollout"] == 0


def test_agent_payload_has_no_reference_material():
    payload = HERE.parent / "environment/setup/payload"
    secret = (HERE.parent / "solution/privileged/oracle_token").read_bytes().strip()
    for path in payload.rglob("*"):
        if path.is_file() and "__pycache__" not in path.parts:
            assert secret not in path.read_bytes()
            assert path.name not in {ARTIFACT, ".oracle_token", "anchor.json", "ideal_answer.py"}
    for name in ("cell_env.py", "outcomes.py", "cell_server.py", "sim_client.py", "props.py", "shift.py", "cpu_meter.py"):
        assert (payload / "lab" / name).read_bytes() == (HERE / name).read_bytes()


def test_physical_entrypoint_stages_complete_controller(tmp_path):
    """Selecting the physical variant must not accidentally evaluate a stale fixture."""
    submission = tmp_path / "submission"
    submission.mkdir()
    (submission / ARTIFACT).write_text("stale fixture")
    (submission / "keep.txt").write_text("user output")
    env = dict(os.environ, ALE_HOME=str(tmp_path), REFERENCE_PYTHON=sys.executable,
               PYTHONDONTWRITEBYTECODE="1")
    subprocess.run(["bash", str(HERE.parent / "solution/solve_physical.sh")], env=env, check=True)
    assert not (submission / ARTIFACT).exists()
    assert (submission / "keep.txt").read_text() == "user output"
    for name in ("motion.py", "narrow.py", "wide.py", "dual.py", "assist.py",
                 "packing.py", "robot.urdf", "shapes.json", ".oracle_token"):
        assert (submission / name).is_file(), name
    run = subprocess.run(["bash", str(submission / "run.sh")], env=env,
                         input='{"type":"reset"}\n{"type":"close"}\n', text=True,
                         capture_output=True, timeout=30, check=True)
    assert run.stdout.splitlines() == ["READY", '{"ok": true}', '{"ok": true}']
