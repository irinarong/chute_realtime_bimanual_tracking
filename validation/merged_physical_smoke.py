"""One merged-reference shift in the exact Docker-derived SIF.

Author-only adapter: replaces only the solver's root-to-user launcher because
Apptainer runs under one non-root UID. It does not validate ALE isolation.
No task files, timings, lock, seeds, assistance or actions are modified.
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
if os.geteuid() == 0:
    raise RuntimeError('Author adapter must never run the controller as root')
os.environ.update(ALE_HOME='/home/user', ALE_STAGE_DIR=str(TASK / 'tests'),
                  PYTHONDONTWRITEBYTECODE='1')
sys.path.insert(0, str(TASK / 'tests'))
from verify import oracle_token, run_shift
from robotics_grader import ProbeLock, Solver, SolverAborted, seed_rng
from sim_client import SimClient

subprocess.run(['bash', str(TASK / 'solution/solve_physical.sh')], check=True)
submission = Path('/home/user/submission')
assert not (submission / 'ideal_answer.json').exists()
assert oracle_token()
files = {str(p.relative_to(submission)): hashlib.sha256(p.read_bytes()).hexdigest()
         for p in sorted(submission.rglob('*')) if p.is_file()}
stderr = (OUT / 'controller-stderr.log').open('w')


class AuthorSolver(Solver):
    def _spawn(self):
        return subprocess.Popen(
            ['bash', self.entry], cwd=self.submission, stdin=subprocess.PIPE,
            stdout=subprocess.PIPE, stderr=stderr, text=True, bufsize=1,
            start_new_session=True, env=dict(os.environ))


config = json.loads((TASK / 'tests/grader_config.json').read_text())
hidden = json.loads((TASK / 'tests/hidden/shifts.json').read_text())
lock = ProbeLock(seed_rng(), rate=config.get('probe_rate', .01),
                 pass_fraction=config.get('probe_pass_fraction', .1), dims=61)
result = dict(scope='Merged solve_physical.sh; first hidden shift through unchanged run_shift',
              official_ale_validate=False, autonomous_agent_run=False,
              uid_isolation_tested=False, privileged_state=True,
              assisted_grasping=True, match_lock_tested=True,
              task_source='960d2c32f247443b5a4fb057e6bb15c2dbfe39e4',
              submitted_files=files, seed=hidden['seeds'][0])
solver = sim = None
started = time.monotonic()
try:
    solver = AuthorSolver(step_timeout=config.get('step_timeout_s', 30),
                          submission=str(submission), clear_account=False)
    sim = SimClient(str(TASK / 'tests/cell_server.py'),
                    env=dict(os.environ, CELL_TOKEN_SHA256=(TASK / 'tests/oracle_token.sha256').read_text().strip()),
                    log_path=str(OUT / 'physical-isaac.log'))
    try:
        summary = run_shift(sim, solver, lock, config, hidden['seeds'][0], hidden.get('salt', 0))
        result.update(summary=summary, canonical_episode_score=summary['score'])
    except SolverAborted as exc:
        result.update(solver_aborted=str(exc), canonical_episode_score=0.0, summary=sim.summary())
    result.update(lock=lock.rewards(), elapsed_s=time.monotonic()-started,
                  completed_shift=result['summary']['events_done'] == result['summary']['parts'])
except Exception as exc:
    result.update(task_error=str(exc), elapsed_s=time.monotonic()-started)
    raise
finally:
    (OUT / 'merged-physical-smoke.json').write_text(json.dumps(result, indent=2) + '\n')
    if sim is not None:
        sim.close()
    if solver is not None:
        solver.close()
    stderr.close()
print(json.dumps({k: v for k, v in result.items() if k not in {'summary', 'submitted_files'}}), flush=True)
