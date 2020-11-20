"""
Fetches Metrics from a filesystem

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
import re

import sams.base

logger = logging.getLogger(__name__)

import subprocess
import threading

try:
    import queue
except ImportError:
    import Queue as queue


class FSStats:
    def __init__(self, mount_points=[]):
        self.mount_points = mount_points

    def sample(self):
        ret = {}
        for mp in self.mount_points:
            try:
                statvfs = os.statvfs(mp)
                ret[mp] = dict(
                    size=statvfs.f_frsize
                    * statvfs.f_blocks,  # Size of filesystem in bytes
                    free=statvfs.f_frsize
                    * statvfs.f_bavail,  # Number of free bytes that ordinary users
                    # are allowed to use (excl. reserved space)
                    used=statvfs.f_frsize * statvfs.f_blocks
                    - statvfs.f_frsize * statvfs.f_bavail,
                )
            except Exception as e:
                logger.error(e)
        return ret


class Sampler(sams.base.Sampler):
    def __init__(self, id, outQueue, config):
        super(Sampler, self).__init__(id, outQueue, config)
        self.processes = {}
        self.sampler_interval = self.config.get([self.id, "sampler_interval"], 60)
        self.mount_points = self.config.get([self.id, "mount_points"])
        self.jobid = self.config.get(["options", "jobid"], 0)

        if not self.mount_points:
            raise Exception("mount_points not configured")

        mps = []
        for mp in self.mount_points:
            mps += glob.glob(mp % dict(jobid=self.jobid))

        self.fsstat = None
        if mps:
            self.fsstat = FSStats(mps)

    def do_sample(self):
        if not self.fsstat:
            return False
        return True

    def sample(self):
        logger.debug("sample()")
        if self.fsstat:
            self.store(self.fsstat.sample())

    def final_data(self):
        return {}
