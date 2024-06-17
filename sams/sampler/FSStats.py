"""
Fetches Metrics from a filesystem

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

sams.sampler.FSStats:
    # in seconds
    sampler_interval: 30

    # path(s) to mountpoints to check (can use %(jobid)s and 'glob')
    mount_points: ['/scratch/slurm.%(jobid)s.*']

Output:
{
    '/mount/point': {
        free: 0,
        used: 0,
        size: 0
    }
}
"""

import glob
import logging
import os

from typing import Dict

import sams.base

logger = logging.getLogger(__name__)


class FSStats:
    def __init__(self, mount_points):
        self.mount_points = mount_points

    def get_sample(self) -> Dict:
        ret = dict()
        for mp in self.mount_points:
            try:
                statvfs = os.statvfs(mp)
                size = statvfs.f_frsize * statvfs.f_blocks
                free = statvfs.f_frsize * statvfs.f_bavail
                ret[mp] = dict(size=size,  # Size of filesystem in bytes
                               free=free,  # Number of free bytes that ordinary users
                                           # are allowed to use (excl. reserved space)
                               used=size - free)
            except Exception as e:
                logger.error(e)
        return ret


class Sampler(sams.base.Sampler):
    def __init__(self, id, outQueue, config):
        super(Sampler, self).__init__(id, outQueue, config)
        self.processes = dict()
        self.sampler_interval = self.config.get([self.id, 'sampler_interval'], 60)
        self.mount_points = self.config.get([self.id, 'mount_points'])
        self.jobid = self.config.get(['options', 'jobid'], 0)
        if not self.mount_points:
            raise sams.base.SamplerException('mount_points not configured')
        mps = []
        for mp in self.mount_points:
            mps += glob.glob(mp % dict(jobid=self.jobid))
        self.fsstat = None
        if mps:
            self.fsstat = FSStats(mps)

    def do_sample(self) -> bool:
        if not self.fsstat:
            return False
        return True

    def sample(self) -> None:
        logger.debug('sample()')
        if self.fsstat:
            sample = self.fsstat.get_sample()
            self.store(sample)
            self._most_recent_sample = self.storage_wrapping(sample)

    @staticmethod
    def final_data() -> Dict:
        return dict()
