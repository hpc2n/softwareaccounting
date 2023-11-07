"""
FileSlurmInfoFallback Loader

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
"""

import logging
import os
import subprocess

from sams.loader.File import Loader as File

logger = logging.getLogger(__name__)


class SacctLoader:
    def __init__(self, sacct, env):
        self.sacct_bin = sacct
        # setup environment for running sacct
        self.env = os.environ.copy()
        for k, v in env.items():
            self.env[k] = v

    def run(self, jobid):
        process = subprocess.run(
            [
                self.sacct_bin,
                "-P",
                "-j",
                str(jobid),
                "-X",
                "-n",
                "-o",
                "Account,Start,User,NNodes,NCPU,Partition,UID",
            ],
            check=True,
            env=self.env,
            encoding="utf8",
            stdout=subprocess.PIPE,
        )
        (
            account,
            starttime,
            username,
            nodes,
            cpus,
            partition,
            uid,
        ) = process.stdout.strip().split("|")
        return dict(
            account=account,
            starttime=starttime,
            username=username,
            nodes=nodes,
            cpus=cpus,
            partition=partition,
            uid=uid,
        )


class Loader(File):
    def __init__(self, id, config):
        super(Loader, self).__init__(id, config)
        sacct_bin = self.config.get([self.id, "sacct"], "/usr/bin/sacct")
        sacct_env = self.config.get([self.id, "environment"], {})
        self.sacct = SacctLoader(sacct_bin, sacct_env)

    def next(self):
        data = super(Loader, self).next()
        if data is None:
            return None
        if not "sams.sampler.SlurmInfo" in data:
            jobid = int(data["sams.sampler.Core"]["jobid"])
            data["sams.sampler.SlurmInfo"] = self.sacct.run(jobid)

        return data
