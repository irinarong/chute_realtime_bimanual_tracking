import os

class CpuMeter(object):
    """CPU seconds used so far by the controller: every process of its process group (the kit starts it in a session
    of its own). A reply's deadline is counted in the controller's CPU time, not in wall time: on a loaded grading
    machine a reply can wait for a core through no fault of the controller, and the same controller must not pass on
    one machine and fail on the other because of the other tenants."""
    TICK = float(os.sysconf('SC_CLK_TCK'))

    def __init__(self, pgid):
        self.pgid, self.pids, self.n = (int(pgid), [], 0)

    def _stat(self, pid):
        try:
            f = open('/proc/{}/stat'.format(pid)).read()
            x = f[f.rindex(')') + 2:].split()
            return (int(x[2]), (int(x[11]) + int(x[12])) / self.TICK)
        except (OSError, ValueError, IndexError):
            return (None, 0.0)

    def seconds(self):
        if self.n % 40 == 0:
            self.pids = [d for d in os.listdir('/proc') if d.isdigit() and self._stat(d)[0] == self.pgid]
        self.n += 1
        return sum((self._stat(p)[1] for p in self.pids))
