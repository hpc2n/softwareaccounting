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
        self.sacct = sacct
        self.env = env

    def run(self, jobid):
        local_env = os.environ.copy()
        for k, v in self.env.items():
            local_env[k] = v

        process = subprocess.run(
            [
                self.sacct,
                "-P",
                "-j",
                str(jobid),
                "-X",
                "-n",
                "-o",
                "Account,Start,User,NNodes,NCPU,Partition,UID",
            ],
            check=True,
            env=local_env,
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
        self.sacct = self.config.get([self.id, "sacct"], "/usr/bin/sacct")
        self.env = self.config.get([self.id, "environment"], {})

    def next(self):
        data = super(Loader, self).next()
        if data is None:
            return None
        if not data.get("sams.sampler.SlurmInfo", {}):
            jobid = int(data["sams.sampler.Core"]["jobid"])
            sacct = SacctLoader(self.sacct, self.env)
            data["sams.sampler.SlurmInfo"] = sacct.run(jobid)

        return data
