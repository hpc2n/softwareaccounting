"""
Pid finder using the slurm cgroup information in /proc

SAMS Software accounting
Copyright (C) 2018-2021  Swedish National Infrastructure for Computing (SNIC)

This program is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License
as published by the Free Software Foundation; either version 2
of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; If not, see <http://www.gnu.org/licenses/>.


Config options:

sams.pidfinder.Slurm:
    # How long to wait (in seconds) after process was removed.
    grace_period: 600

"""

import logging
import os
import re
import time

import sams.base

logger = logging.getLogger(__name__)


class Pids:
    def __init__(self, pid, jobid):
        self._pid = pid
        self.jobid = jobid
        self.injob = self.check_job()
        self.update()

    def update(self):
        self.last_seen = time.time()

    def check_job(self):
        try:
            with open("/proc/%d/cpuset" % self._pid) as file:
                cpuset = file.read()
                m = re.search(r"/job_([0-9]+)/", cpuset)
                if m:
                    if int(m.group(1)) == self.jobid:
                        return True
        except Exception:
            pass

        # This pid is not within the Slurm CGroup.
        return False


class PIDFinder(sams.base.PIDFinder):
    def __init__(self, id, jobid, config):
        super(PIDFinder, self).__init__(id, jobid, config)
        self.processes = {}
        self.procdir = "/proc"
        self.create_time = time.time()

    def find(self):
        pids = filter(lambda f: re.match(r"^\d+$", f), os.listdir(self.procdir))
        pids = map(int, pids)

        new_pids = []

        for pid in pids:
            if pid not in self.processes.keys():
                self.processes[pid] = Pids(pid, self.jobid)
                if self.processes[pid].injob:
                    new_pids.append(pid)
            self.processes[pid].update()

        return new_pids

    def done(self):
        procs = list(filter(lambda p: p.injob, self.processes.values()))
        if not procs:
            return self.create_time < time.time() - self.config.get([self.id, "grace_period"], 600)
        return max(p.last_seen for p in procs) < time.time() - self.config.get([self.id, "grace_period"], 600)
