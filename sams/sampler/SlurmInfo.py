"""
Fetches Metrics from Slurm command

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

sams.sampler.SlurmInfo:
    # in seconds
    sampler_interval: 100

    # path to scontrol command
    scontrol: /usr/local/bin/scontrol

    # extra environments for command
    environment:
      PATH: "/bin:/usr/bin"

Output:
{
    account: "",
    cpus: 0,
    nodes: 0,
    username: "user",
    uid: 65535,
}
"""
import logging
import os
import re
import subprocess
from typing import Dict

import sams.base

logger = logging.getLogger(__name__)

COMMAND = '{:s} show job {:d} -o'


class Sampler(sams.base.Sampler):
    data = dict()
    keys = ['account', 'cpus', 'nodes', 'starttime', 'username', 'uid']

    def do_sample(self):
        if all(k in self.data for k in self.keys):
            return False
        return True

    def init(self):
        self.sample()

    def sample(self):
        logger.debug('sample()')

        scontrol = self.config.get([self.id, 'scontrol'], '/usr/bin/scontrol')
        jobid = self.config.get(['options', 'jobid'], 0)

        command = COMMAND.format(scontrol, jobid)

        try:
            local_env = os.environ.copy()
            environment = self.config.get([self.id, 'environment'], dict())
            for env, value in environment.items():
                local_env[env] = value
            process = subprocess.Popen(command, env=local_env, shell=True, stdout=subprocess.PIPE).stdout
            data = process.readlines()
        except Exception as e:
            logger.exception(e)
            logger.debug(f'Fail to run: {command}, will try again in a while')
            # Try again next time
            return

        data = data[0].decode().strip()

        # Find account in string
        account = re.search(r'Account=([^ ]+)', data)
        if account is not None:
            self.data['account'] = account.group(1)

        # Find username/uid in string\((\d+)\)
        userid = re.search(r'UserId=([^\(]+)\((\d+)\)', data)
        if userid is not None:
            self.data['username'] = userid.group(1)
            self.data['uid'] = userid.group(2)

        # Find username/uid in string
        nodes = re.search(r'NumNodes=(\d+)', data)
        if nodes is not None:
            self.data['nodes'] = nodes.group(1)

        # Find NumCPUs in string
        cpus = re.search(r'NumCPUs=(\d+)', data)
        if cpus is not None:
            self.data['cpus'] = cpus.group(1)

        # Find partition in string
        partition = re.search(r'Partition=(\S+) ', data)
        if partition is not None:
            self.data['partition'] = partition.group(1)

        # Find StartTime
        starttime = re.search(r'StartTime=(\d\d\d\d-\d\d-\d\dT\d\d:\d\d:\d\d)', data)
        if starttime is not None:
            self.data['starttime'] = starttime.group(1)

        # Find JobName
        jobname = re.search(r'JobName=([^ ]+)', data)
        if jobname is not None:
            self.data['jobname'] = jobname.group(1)

        if not self.do_sample():
            self.store(self.data)

    def most_recent_sample(self) -> Dict:
        return self.data

    def final_data(self) -> Dict:
        return self.data
