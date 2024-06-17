"""
Fetches the path and cpu usage of the running processes.

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

sams.sampler.Software:
    # in seconds
    sampler_interval: 100

    # Map current running execs into softwares for live reporting
    # software_mapper: sams.software.Regexp

Output:
Every sample:
{
    current: {
        user: 0,
        system: 0
    }
}
summary:
{
    execs: {
        PATH: {
            user: 0,
            system: 0,
        },
        PATH2: {
            user: 0,
            system 0,
        },
    },
    start_time: 0,
    end_time: 1,
}
"""
import logging
import os
import re
import time
from typing import Dict, Iterable, Tuple

import sams.base
import sams.core

logger = logging.getLogger(__name__)


class Process:
    """ Object representing a single process with a single PID.

    Parameters
    ----------
    pid : int
        Process ID.
    jobid : int
        Slurm job ID.
    """
    def __init__(self,
                 pid: int,
                 jobid: int):
        self.pid = pid
        self.tasks = dict()
        self.clock_tics = os.sysconf(os.sysconf_names['SC_CLK_TCK'])
        self.starttime = time.time()
        self.ignore = False
        self.done = False
        self.uptime = None
        self.updated = None

        try:
            self.exe = os.readlink(f'/proc/{self.pid:d}/exe')
            logger.debug(f'Pid: {pid} (JobId: {jobid}) has exe: {self.exe}')
        except Exception:
            logger.debug(f'Pid: {pid} (JobId: {jobid}) has no exe or pid has disapeared')
            self.ignore = True

    def _get_parsed_stats(self, stat) -> dict:
        """Parse the relevant content from /proc/***/stat"""

        m = re.search(r'^\d+ \(.*\) [RSDZTyEXxKWPI] (.*)', stat)
        stats = m.group(1).split(r' ')
        return dict(user=float(stats[14 - 4]) / self.clock_tics,  # User CPU time in s.
                    system=float(stats[15 - 4]) / self.clock_tics)  # System CPU time in s.

    def update(self, uptime) -> None:
        """Update information about pids"""
        if self.done:
            logger.debug(f'Pid: {self.pid:d} is done')
            return
        logger.debug(f'Update pid: {self.pid:d}')
        self.uptime = uptime

        try:
            tasks = [int(f) for f in os.listdir(f'/proc/{self.pid:d}/task') if re.match(r"^\d+$", f)]
        except Exception:
            logger.debug(f'Failed to read /proc/{self.pid:d}/task, most likely due to process ending')
            self.done = True
            return

        for task in tasks:
            try:
                with open(f'/proc/{self.pid:d}/task/{task:d}/stat') as f:
                    stat = f.read()
                    stats = self._get_parsed_stats(stat)
                    self.tasks[task] = dict(
                        user=stats["user"],
                        system=stats["system"])
                    logger.debug(f'Task usage for pid: {self.pid}, task: {task},'
                                 f' user: {stats["user"]}, system: {stats["system"]}')
            except Exception:
                logger.debug(f'Ignore missing task for pid: {self.pid}')

        self.updated = time.time()

    def get_aggregated_task_info(self) -> Dict:
        """Return the aggregated information for all tasks"""
        return dict(starttime=self.starttime,
                    exe=self.exe,
                    user=sum(t["user"] for t in self.tasks.values()),
                    system=sum(t["system"] for t in self.tasks.values()))


class Sampler(sams.base.Sampler):
    def __init__(self, id, outQueue, config):
        super(Sampler, self).__init__(id, outQueue, config)
        self.processes = {}
        self.create_time = time.time()
        self.previous_total = None
        self.previous_sample_time = None
        self.software_mapper = None

        software_mapper = self.config.get([id, 'software_mapper'], None)
        if software_mapper is not None:
            logger.debug(f'Loading software_mapper: {software_mapper}')
            try:
                Software = sams.core.ClassLoader.load(software_mapper, 'Software')
                self.software_mapper = Software(software_mapper, config)
            except Exception as e:
                logger.error(f'Failed to initialize: {software_mapper}')
                logger.exception(e)

    def map_software(self,
                     aggr: Dict) -> Dict:
        """Map usage to softwares"""
        output = dict()
        if not self.software_mapper:
            logger.debug('No software_mapper loaded...')
            return output
        for exe, data in aggr.items():
            try:
                sw = self.software_mapper.get(exe)
                if sw['ignore']:
                    continue
                if sw['software'] not in output:
                    output[sw['software']] = dict(user=0, system=0)
                output[sw['software']]['user'] += data['user']
                output[sw['software']]['system'] += data['system']
            except Exception as e:
                logger.debug(e)
        return output

    def _collect_sample(self) -> Tuple[Dict, Dict]:
        logger.debug('_collect_sample()')
        with open('/proc/uptime', 'r') as f:
            uptime = float(f.readline().split()[0])
        for pid in self.pids:
            logger.debug(f'evaluate pid: {pid}')
            if pid not in self.processes.keys():
                logger.debug(f'Create new instance of Process for pid: {pid}')
                self.processes[pid] = Process(pid, self.jobid)
            self.processes[pid].update(uptime)
        # Send information about current usage
        return self._get_aggregated_processes()

    def sample(self) -> None:
        logger.debug('sample()')
        aggr, total = self._collect_sample()
        # Initial call
        if self.previous_sample_time is None:
            self.previous_total = total
            self.previous_sample_time = time.time()
            return
        time_diff = time.time() - self.previous_sample_time
        previous_user = self.previous_sample['total']['user']
        previous_system = self.previous_sample['total']['system']
        if time_diff > self.sampler_interval / 2:
            sample = dict(current=dict(
                software=self.map_software(aggr),
                total_user=total["user"],
                total_system=total["system"],
                user=(total["user"] - previous_user) / time_diff,
                system=(total["system"] - previous_system) / time_diff))
            self.store(sample)
            self.previous_total = total
            self.previous_sample_time = time.time()
            self._most_recent_sample = self.storage_wrapping(sample)

    @property
    def valid_procs(self) -> Iterable:
        """ List of procs for which p.ignore is False """
        logger.debug(f'procs: {[p for p in self.processes.values()]}')
        logger.debug(f'valid_procs: {[p for p in self.processes.values() if not p.ignore]}')
        return [p for p in self.processes.values() if not p.ignore]

    def get_update_time(self) -> int:
        procs = self.valid_procs
        if len(procs) == 0:
            return self.create_time
        return int(max(p.updated for p in procs))

    def get_start_time(self) -> int:
        procs = self.valid_procs
        if not procs:
            return 0
        return int(min(p.starttime for p in procs))

    def _get_aggregated_processes(self) -> Tuple[Dict, Dict]:
        aggr = dict()
        total = dict(user=0.0,
                     system=0.0)
        aggregated_procs = [p.get_aggregated_task_info() for p in self.valid_procs]
        for a in aggregated_procs:
            logger.debug(f'_get_aggregated_processes: exe: {a["exe"]}, '
                         f'user: {a["user"]}, system: {a["system"]}')
            exe = a['exe']
            if exe not in aggr:
                aggr[exe] = dict(user=0.0, system=0.0)
            aggr[exe]['user'] += a['user']
            aggr[exe]['system'] += a['system']
            total['user'] += a['user']
            total['system'] += a['system']
        return aggr, total

    def final_data(self) -> Dict:
        logger.debug('{self.id} final_data')
        aggr, _ = self._get_aggregated_processes()
        return dict(execs=aggr,
                    start_time=self.get_start_time(),
                    end_time=self.get_update_time())
