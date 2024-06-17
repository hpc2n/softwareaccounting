"""
Fetches Metrics from CGroup (Experimental)

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

sams.sampler.Pressure:
    # in seconds
    sampler_interval: 60

    cgroup_base: /sys/fs/cgroup/unified

Output:
{
}
"""

import logging
import os
import re
from typing import Dict

import sams.base

logger = logging.getLogger(__name__)


class Sampler(sams.base.Sampler):
    def __init__(self, id, outQueue, config):
        super(Sampler, self).__init__(id, outQueue, config)
        self.processes = dict()
        self.cgroups = dict()
        self.cgroup_base = self.config.get([self.id, 'cgroup_base'], '/sys/fs/cgroup/unified')
        self.extract_pressure = re.compile(
            r'^(?P<type>some|full)\s+avg10=(?P<avg10>[\d\.]+)\s+avg60='
            r'(?P<avg60>[\d\.]+)\s+avg300=(?P<avg300>[\d\.]+)\s+total=(?P<total>[\d]+)\s*$')

    def do_sample(self) -> bool:
        return self._get_cgroup()

    def sample(self) -> None:
        logger.debug('sample()')

        cpu_pressure = self.read_pressure('cpu.pressure')
        io_pressure = self.read_pressure('io.pressure')
        memory_pressure = self.read_pressure('memory.pressure')
        sample = dict(cpu=cpu_pressure,
                      io=io_pressure,
                      memory=memory_pressure)
        self.store(sample)
        self._most_recent_sample = self.storage_wrapping(sample)

    def _get_cgroup(self) -> bool:
        """Get the cgroup base path for the slurm job"""
        for pid in [pid for pid in self.pids if pid not in self.cgroups]:
            try:
                with open('/proc/{pid:s}/cgroup', 'r') as file:
                    for line in file.readlines():
                        m = re.search(r'^0::/(.*)$', line)
                        if m:
                            self.cgroups[pid] = m.group(1)
            except Exception as e:
                logger.debug('Failed to fetch cgroup for pid: {self.pids[0]:d}')
                logger.debug(e)
        if self.cgroups:
            return True
        return False

    def read_pressure(self, name) -> Dict:
        cgroups = set(self.cgroups.values())
        output = {}
        types = set()
        for cgroup in cgroups:
            try:
                logger.debug(os.path.join(self.cgroup_base, cgroup, name))
                with open(os.path.join(self.cgroup_base, cgroup, name), "r") as file:
                    output[cgroup] = {}
                    for line in file.readlines():
                        logger.debug(line)
                        m = self.extract_pressure.search(line)
                        if m:
                            data = m.groupdict()
                            type = data["type"]
                            del data["type"]
                            output[cgroup][type] = data
                            types.add(type)
            except IOError as err:
                path = os.path.join(self.cgroup_base, type, cgroup, id)
                logger.debug(f'Failed to open {path:s} for reading')
                logger.debug(err)
        ret = dict()
        for t in types:
            ret.update(dict(type=dict(
                avg10=max(float(v[t]['avg10']) for v in output.values()),
                avg60=max(float(v[t]['avg60']) for v in output.values()),
                avg300=max(float(v[t]['avg300']) for v in output.values()),
                total=sum(int(v[t]['total']) for v in output.values()))))
        logger.debug(ret)
        return ret

    @staticmethod
    def final_data() -> Dict:
        return dict()
