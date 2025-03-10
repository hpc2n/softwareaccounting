"""
Posts output using web service.

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



Config Options:

sams.output.Http:
  # uri to write to.
  # Available data for replace is: jobid, node & jobid_hash
  uri: "https://etui.hpc2n.umu.se:8443/%(jobid_hash)d/%(jobid)s.%(node)s.yaml"

  # "Hash" the output based on --jobid / jobid_hash_size
  jobid_hash_size: 1000

  # if set using the following key/cert for client cert auth
  key_file: /etc/sa.key.pem
  cert_file: /etc/sa.cert.pem

  # if set using the folloing username/password as basic auth
  username: 'sams'
  password: 'sams'

  # Skip the list of modules.
  exclude: ['sams.sampler.ModuleName']
"""

import json
import logging

import requests

import sams.base

logger = logging.getLogger(__name__)


class Output(sams.base.Output):
    """http/https output Class"""

    def __init__(self, id, config):
        super(Output, self).__init__(id, config)
        self.exclude = dict((e, True) for e in self.config.get([self.id, "exclude"], []))
        self.data = {}

    def store(self, data):
        for k, v in data.items():
            if k in self.exclude:
                continue
            logger.debug("Store data for: %s => %s", k, v)
            self.data[k] = v

    def write(self):
        in_uri = self.config.get([self.id, "uri"])
        jobid = self.config.get(["options", "jobid"], 0)
        node = self.config.get(["options", "node"], 0)
        jobid_hash_size = self.config.get([self.id, "jobid_hash_size"])
        cert_file = self.config.get([self.id, "cert_file"])
        key_file = self.config.get([self.id, "key_file"])
        username = self.config.get([self.id, "username"])
        password = self.config.get([self.id, "password"])

        jobid_hash = int(jobid / jobid_hash_size)
        uri = in_uri % {"jobid": jobid, "node": node, "jobid_hash": jobid_hash}

        requests_kwargs = {}

        if username and password:
            logger.debug("Sending data as user: %s with password: ********", username)
            # send username & password
            requests_kwargs["auth"] = (username, password)

        if key_file and cert_file:
            logger.debug("Sending data with cert: %s and key: %s ", cert_file, key_file)
            # send client certificate
            requests_kwargs["cert"] = (cert_file, key_file)

        headers = {"Content-Type": "application/json"}
        body = json.dumps(self.data, sort_keys=True, separators=(",", ":"))

        logger.debug("Sending data to: %s", uri)
        response = requests.post(uri, data=body, headers=headers, **requests_kwargs)

        if response.status_code == 200:
            return True
        logger.error("Failed to send data to: %s", uri)
        logger.debug(response)
        logger.debug(response.content)
        return False
