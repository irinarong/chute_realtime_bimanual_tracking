"""Replay the archived visual policy through the current run_shift for diagnosis.

Same-UID Apptainer infrastructure: NOT ALE isolation or a new frontier-agent run.
Task code, current timing/ProbeLock and the archived controller remain unchanged.
"""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time

TASK = Path('/task')
OUT = Path('/results')
AUDIT = Path('/audit')
if os.geteuid() == 0:
    raise RuntimeError('This diagnostic adapter must never execute controller code as root')
sys.path.insert(0, str(TASK / 'tests'))
from verify import oracle_token, run_shift
from robotics_grader import ProbeLock, Solver, SolverAborted, seed_rng
from sim_client import SimClient

manifest = json.loads((AUDIT / 'source-manifest.json').read_text())
for name, expected in manifest['controller_files'].items():
    if hashlib.sha256((AUDIT / 'controller' / name).read_bytes()).hexdigest() != expected:
        raise RuntimeError(f'Archived controller hash mismatch: {name}')
if oracle_token():
    raise RuntimeError('Visual replay must not have a reference token in its submission')

stderr = (OUT / 'controller-stderr.log').open('w')


class DiagnosticSolver(Solver):
    """Keep the canonical wire/priority/restart machinery; only replace its UID launcher."""
    def _spawn(self):
        return subprocess.Popen(
            ['bash', self.entry], cwd=self.submission,
            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=stderr,
            text=True, bufsize=1, start_new_session=True,
            env=dict(os.environ, PYTHONDONTWRITEBYTECODE='1'),
        )


config = json.loads((TASK / 'tests/grader_config.json').read_text())
hidden = json.loads((TASK / 'tests/hidden/shifts.json').read_text())
lock = ProbeLock(seed_rng(), rate=config.get('probe_rate', 0.01),
                 pass_fraction=config.get('probe_pass_fraction', 0.1), dims=61)
started = time.monotonic()
solver = sim = None
result = dict(scope='Archived visual policy, one current-task shift through unchanged run_shift',
              autonomous_agent_run=False, official_ale_validate=False, uid_isolation_tested=False,
              privileged_state=False, assisted_grasping=False,
              current_timing_used=True, match_lock_tested=True,
              controller_manifest=manifest)
try:
    # Never clear a host user's account from this same-UID diagnostic environment.
    solver = DiagnosticSolver(step_timeout=config.get('step_timeout_s', 30),
                              submission=str(AUDIT / 'controller'), clear_account=False)
    # No truth authorization is configured, even in the parent simulator process.
    sim = SimClient(str(TASK / 'tests/cell_server.py'),
                    env=dict(os.environ, CELL_TOKEN_SHA256=''),
                    log_path=str(OUT / 'visual-isaac.log'))
    try:
        summary = run_shift(sim, solver, lock, config, hidden['seeds'][0], hidden.get('salt', 0))
        result.update(summary=summary, canonical_episode_score=summary['score'])
    except SolverAborted as exc:
        # The task charges an aborted episode zero; retain physical progress separately.
        result.update(solver_aborted=str(exc), canonical_episode_score=0.0, summary=sim.summary())
    result.update(lock=lock.rewards(), elapsed_s=time.monotonic()-started,
                  completed_shift=result['summary']['events_done'] == result['summary']['parts'])
    (OUT / 'visual-replay.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({k: v for k, v in result.items() if k not in {'summary', 'controller_manifest'}}), flush=True)
    print(json.dumps({k: v for k, v in result['summary'].items() if k not in {'records', 'constants'}}), flush=True)
finally:
    if sim is not None:
        sim.close()
    if solver is not None:
        solver.close()
    stderr.close()
