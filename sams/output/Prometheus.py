"""
Sends output from Samplers via prometheus node-exporter

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

sams.output.Prometheus:
    # Where to write prometheus prom files.
    path: /var/lib/prometheus/node-exporter/slurm_%(jobid)s.prom

    # Fetches the value from dict-value and put into dict-key
    # This can be used in the 'metrics' dict-value with %(key)s
    map:
        jobid: sams.sampler.Core/jobid
        node: sams.sampler.Core/node
        user: sams.sampler.SlurmInfo/username
        account: sams.sampler.SlurmInfo/account

    # Sets the value from dict-value and put into dict-key
    # This can be used in the 'metrics' dict-value with %(key)s
    static_map:
        cluster: kebnekaise

    # Metrics matching dict-key will be written to output path
    metrics:
        '^sams.sampler.SlurmCGroup/(?P<metric>[^/]+)$' : sa_metric{cluster="%(cluster)s", jobid="%(jobid)s", metric="%(metric)s"}
"""

import logging
import os
import re

import sams.base

logger = logging.getLogger(__name__)


class Output(sams.base.Output):
    """File output Class"""

    def __init__(self, id, config):
        super(Output, self).__init__(id, config)
        self.static_map = self.config.get([self.id, "static_map"], {})
        self.map = self.config.get([self.id, "map"], {})
        self.metrics = self.config.get([self.id, "metrics"], {})
        self.path = self.config.get([self.id, "path"], "/var/lib/prometheus/node-exporter/slurm_%(jobid)s.prom")
        self.jobid = self.config.get(["options", "jobid"], 0)

        self.output_file = self.path % dict(jobid=self.jobid)

        self.data = {}
        self.promdata = {}

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
            for metric, destination in self.metrics.items():
                reg = re.compile(metric)
                m = reg.match(d["match"])
                if m:
                    self.save(d["value"], destination, m.groupdict())

        self.write_prom()

    def write_prom(self):
        if not self.promdata:
            logger.debug("Nothing to write")
            return

        try:
            helped = {}
            metric_re = re.compile(r"^(\S+){")
            with open(self.output_file + ".new", "w") as f:
                for m in sorted(self.promdata.keys()):
                    match = metric_re.match(m)
                    if not match:
                        continue
                    if match.group(1) not in helped:
                        helped[match.group(1)] = True
                        f.write("# HELP %s Job Usage Metrics\n" % match.group(1))
                        f.write("# TYPE %s gauge\n" % match.group(1))

                    v = self.promdata[m]
                    f.write(m + " " + str(v) + "\n")
            os.rename(self.output_file + ".new", self.output_file)
        except Exception as e:
            logger.exception(e)
            logger.warning("Failed to write: %s", self.output_file)

        try:
            if os.path.exists(self.output_file + ".new"):
                os.unlink(self.output_file + ".new")
        except Exception:
            pass

    def save(self, value, destination, di):
        d = self.static_map.copy()
        d.update(di)
        for k, v in self.map.items():
            m = self.safe_metric(self.data, v.split("/"))
            if not m:
                logger.warning("map: %s: %s is missing", k, v)
                return
            d[k] = m

        try:
            dest = destination % d
        except Exception as e:
            logger.error(e)
            return

        if value is None:
            logger.warning("%s got no metric", dest)
            return

        self.promdata[dest] = value
        logger.debug("Store: %s = %s", dest, str(value))

    def write(self):
        if not self.promdata:
            logger.debug("Nothing to remove")
            return

        try:
            os.unlink(self.output_file)
        except Exception:
            pass
