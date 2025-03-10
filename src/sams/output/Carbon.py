"""
Sends output from Samplers to carbon server

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

sams.output.Carbon:
    server: carbon.server.example.com
    port: 2003

    # Server list
    servers:
      - carbon.server.example.com:2003

    # Fetches the value from dict-value and put into dict-key
    # This can be used in the 'metrics' dict-value with %(key)s
    map:
        jobid: sams.sampler.Core/jobid
        node: sams.sampler.Core/node

    # Sets the value from dict-value and put into dict-key
    # This can be used in the 'metrics' dict-value with %(key)s
    static_map:
        cluster: kebnekaise

    # Metrics matching dict-key will be sent to carbon server as dict-value
    metrics:
        '^sams.sampler.SlurmCGroup/(?P<metric>.*)$' : 'sa/%(cluster)s/%(jobid)s/%(node)s/%(metric)s'

"""

import logging
import re
import socket
import time

import sams.base

logger = logging.getLogger(__name__)


class Output(sams.base.Output):
    """File output Class"""

    def __init__(self, id, config):
        super(Output, self).__init__(id, config)
        self.static_map = self.config.get([self.id, "static_map"], {})
        self.map = self.config.get([self.id, "map"], {})
        self.metrics = self.config.get([self.id, "metrics"], {})
        server = self.config.get([self.id, "server"], "localhost")
        port = self.config.get([self.id, "port"], 2003)
        self.servers = self.config.get([self.id, "servers"], ["localhost:2003"])
        self.servers.append("%s:%d" % (server, port))
        self.data = {}

        # UDP Socket
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def dict2str(self, dct, base=""):
        out = []
        for key in dct.keys():
            nb = "/".join([base, key])
            if key in dct and isinstance(dct[key], dict):
                out = out + self.dict2str(dct[key], base=nb)
            else:
                out = out + [{"match": nb, "value": dct[key]}]
        return out

    @classmethod
    def safe_metric(cls, dct, keys):
        for key in keys:
            if key in dct:
                dct = dct[key]
            else:
                return None
        return dct

    def store(self, data):
        logger.debug("store: %s", data)
        for k, v in data.items():
            self.data[k] = v

        flatdict = self.dict2str(data)
        for d in flatdict:
            logger.debug("flatdict: %s", d)
            for metric, destination in self.metrics.items():
                reg = re.compile(metric)
                m = reg.match(d["match"])
                if m:
                    di = m.groupdict()
                    self.send(d["value"], destination, di)

    def send(self, value, destination, di):
        d = self.static_map.copy()
        d.update(di)
        for k, v in self.map.items():
            m = self.safe_metric(self.data, v.split("/"))
            if not m:
                logger.warning("map: %s: %s is missing", k, v)
                return
            d[k] = m

        dest = destination % d

        if not value:
            logger.warning("%s got no metric", dest)
            return

        message = "%s %s %d\n" % (dest, value, int(time.time()))

        for server_str in self.servers:
            (server, port) = server_str.split(":", 2)
            try:
                logger.debug("Sending: %s to %s:%s", message, server, port)
                self.sock.sendto(str.encode(message), (server, int(port)))
                logger.debug("Sending OK: %s to %s:%s", message, server, port)
            except Exception as e:
                logger.debug(e)

    @classmethod
    def write(cls):
        pass
