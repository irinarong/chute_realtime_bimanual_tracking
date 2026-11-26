"""Privileged terminal-state fixture evaluator. No robot or physics is executed.

Only the reference token authorizes this alternate input path. Ordinary submissions
are always evaluated by the simulator. A fixture is a list of independent per-event
terminal snapshots, NOT a physically feasible joint arrangement of all objects.
"""
import hashlib
import hmac
import json
import math
import os
from pathlib import Path
import stat

import numpy as np

from cell_env import BYSTANDER_MOVE, LOW_END, REST_SPEED, TOTE_AT
from outcomes import inside_tote, layout_offsets, released_and_resting, summarize_credits
from props import TOTE
from robotics_grader import ratio_rewards, zero_verdict

ARTIFACT = "ideal_answer.json"
FORMAT = "chute.ideal-terminal-snapshots.v1"


def read_regular(path, limit):
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
    with os.fdopen(fd, "rb") as f:
        if not stat.S_ISREG(os.fstat(f.fileno()).st_mode):
            raise ValueError("artifact must be a regular file")
        data = f.read(limit + 1)
    if len(data) > limit:
        raise ValueError("artifact is too large")
    return data


def exact_keys(value, keys):
    if not isinstance(value, dict) or set(value) != set(keys):
        raise ValueError("unexpected or missing fields")


def finite_number(value):
    if type(value) not in (int, float) or not math.isfinite(value):
        raise ValueError("expected a finite number")
    return float(value)


def vector(value):
    if not isinstance(value, list) or len(value) != 3:
        raise ValueError("expected a three-dimensional vector")
    return np.array([finite_number(v) for v in value])


def evaluate(payload, seeds, salt, parts):
    exact_keys(payload, ("format", "shifts"))
    if payload["format"] != FORMAT or not isinstance(payload["shifts"], list) or len(payload["shifts"]) != len(seeds):
        raise ValueError("wrong fixture format or shift coverage")
    details = []
    for shift, seed in zip(payload["shifts"], seeds):
        exact_keys(shift, ("seed", "events", "bystander_max_displacements_m"))
        if type(shift["seed"]) is not int or shift["seed"] != seed:
            raise ValueError("wrong shift order or identity")
        events = shift["events"]
        if not isinstance(events, list) or len(events) != parts:
            raise ValueError("every part needs one terminal snapshot")
        _, _, _, tote = layout_offsets(seed, salt, LOW_END, TOTE_AT)
        credits = []
        for index, event in enumerate(events):
            exact_keys(event, ("index", "position_world_m", "velocity_m_s", "finger_contacts"))
            if type(event["index"]) is not int or event["index"] != index:
                raise ValueError("wrong event order or identity")
            pos, vel = vector(event["position_world_m"]), vector(event["velocity_m_s"])
            contacts = event["finger_contacts"]
            if not isinstance(contacts, list) or len(contacts) != 4 or any(type(v) is not bool for v in contacts):
                raise ValueError("expected four finger contact booleans")
            placed = released_and_resting(
                inside_tote(pos, tote, np.eye(3), TOTE["inner"]), any(contacts),
                math.hypot(*vel), REST_SPEED,
            )
            credits.append(1.0 if placed else 0.0)
        # A 20-part shift uses all catalogue items and has two bystanders.
        # Refuse other configurations until their fixture schema is defined.
        displacements = shift["bystander_max_displacements_m"]
        if parts != 20 or not isinstance(displacements, list) or len(displacements) != 2:
            raise ValueError("fixture supports the task's 20-part/two-bystander shifts only")
        distances = [finite_number(v) for v in displacements]
        if any(v < 0 for v in distances):
            raise ValueError("displacement cannot be negative")
        details.append(summarize_credits(credits, sum(v > BYSTANDER_MOVE for v in distances)))
    if not details:
        raise ValueError("empty hidden set")
    return sum(d["score"] for d in details) / len(details), details


def maybe_verdict(submission, stage, config, anchor, meta):
    """None means ordinary controller evaluation. Invalid fixture attempts score zero."""
    submission, stage = Path(submission), Path(stage)
    answer = submission / ARTIFACT
    if not os.path.lexists(answer):
        return None
    extra = {"synthetic_reference": 1.0, "physical_rollout": 0.0}
    try:
        token = read_regular(submission / ".oracle_token", 1024).decode().strip()
        expected = (stage / "oracle_token.sha256").read_text().strip()
        if not token or not hmac.compare_digest(hashlib.sha256(token.encode()).hexdigest(), expected):
            raise ValueError("ideal-answer reference is not authorized")
        hidden = json.loads((stage / "hidden/shifts.json").read_text())
        seeds = hidden["seeds"][:int(config.get("shifts", 6))]
        payload = json.loads(read_regular(answer, 1_000_000))
        measured, details = evaluate(payload, seeds, int(hidden.get("salt", 0)), int(config.get("events_per_shift", 20)))
    except (OSError, ValueError, TypeError, OverflowError, RecursionError) as exc:
        return zero_verdict(reason="invalid ideal-answer fixture: " + str(exc), anchored=anchor is not None, extra=extra)
    verdict = ratio_rewards(measured, anchor, cap=config.get("scoring_cap", 1.5),
                            metric_name=meta.get("metric", "part_pickup_score"),
                            full_at=meta.get("full_at", 1.0), extra=extra)
    verdict["diagnostic"] = json.dumps({
        "mode": "privileged_synthetic_terminal_snapshots",
        "limitations": "No simulator, grasp, camera, timing or match-lock validation. Not controller success.",
        "shifts": details,
    })
    return verdict
