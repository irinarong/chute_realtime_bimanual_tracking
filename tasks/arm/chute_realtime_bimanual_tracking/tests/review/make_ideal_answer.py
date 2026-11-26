"""Author-time fixture generator. Never shipped into the agent's environment.

This constructs independent ideal terminal snapshots, not robot trajectories.
Run again after changing the hidden set; then remeasure the anchor.
"""
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE))
from cell_env import LOW_END, TOTE_AT
from ideal_answer import FORMAT
from outcomes import layout_offsets


def main():
    hidden = json.loads((HERE / "hidden/shifts.json").read_text())
    config = json.loads((HERE / "grader_config.json").read_text())
    answer = {"format": FORMAT, "shifts": []}
    for seed in hidden["seeds"][:config["shifts"]]:
        _, _, _, tote = layout_offsets(seed, hidden.get("salt", 0), LOW_END, TOTE_AT)
        answer["shifts"].append({
            "seed": seed,
            "events": [{
                "index": i,
                "position_world_m": (tote + [0, 0, 0.05]).tolist(),
                "velocity_m_s": [0, 0, 0],
                "finger_contacts": [False] * 4,
            } for i in range(config["events_per_shift"])],
            "bystander_max_displacements_m": [0, 0],
        })
    out = HERE.parent / "solution/privileged/ideal_answer.json"
    out.write_text(json.dumps(answer, indent=2) + "\n")
    print(out)


if __name__ == "__main__":
    main()
