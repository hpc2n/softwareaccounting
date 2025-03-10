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

import json
import logging
import os
import subprocess
from copy import deepcopy
from tempfile import mkdtemp

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
                "JobIDRaw,Account,Start,User,NNodes,NCPU,Partition,UID",
            ],
            check=True,
            env=self.env,
            encoding="utf8",
            stdout=subprocess.PIPE,
        )
        for line in process.stdout.splitlines():
            (
                jobidraw,
                account,
                starttime,
                username,
                nodes,
                cpus,
                partition,
                uid,
            ) = line.strip().split("|")
            if int(jobidraw) == jobid:
                return dict(
                    account=account,
                    starttime=starttime,
                    username=username,
                    nodes=nodes,
                    cpus=cpus,
                    partition=partition,
                    uid=uid,
                )
        raise Exception(f"jobid {jobid} not found in sacct output")


class Loader(File):
    def __init__(self, id, config):
        super(Loader, self).__init__(id, config)
        sacct_bin = self.config.get([self.id, "sacct"], "/usr/bin/sacct")
        sacct_env = self.config.get([self.id, "environment"], {})
        self.sacct = SacctLoader(sacct_bin, sacct_env)
        self.updated_data = None

    def next(self):
        self.updated_data = None
        data = super(Loader, self).next()
        if data is None:
            return None
        if "sams.sampler.SlurmInfo" not in data:
            jobid = int(data["sams.sampler.Core"]["jobid"])
            data["sams.sampler.SlurmInfo"] = self.sacct.run(jobid)
            self.updated_data = deepcopy(data)
        return data

    def commit(self):
        if self.updated_data:
            # Write new json file, including the SlurmInfo
            in_file = self.current_file
            temp_dir = mkdtemp()
            with open(os.path.join(temp_dir, self.current_file["file"]), mode="w") as new_file:
                new_file.write(json.dumps(self.updated_data))
            in_path_save = self.in_path
            self.in_path = temp_dir
            self.current_file["path"] = ""
        # Call the regular commit() function, to move new json file to archive directory
        super().commit()
        if self.updated_data:
            # Cleanup temp dir and original input file
            self.in_path = in_path_save
            os.remove(os.path.join(self.in_path, in_file["path"], in_file["file"]))
            if os.path.exists(temp_dir):
                os.rmdir(temp_dir)
