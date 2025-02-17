#!/usr/bin/env python

"""
Simple POST receiver for SAMS Software accounting

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
import sys
from optparse import OptionParser

from flask import Flask, request
from flask.views import MethodView

import sams.core
from sams import __version__

logger = logging.getLogger(__name__)

id = "sams.post-receiver"


class Receiver(MethodView):
    def __init__(self, base_path, jobid_hash_size):
        super(Receiver, self).__init__()
        self.base_path = base_path
        self.jobid_hash_size = jobid_hash_size

    def post(self, jobid, filename):
        base_path = self.base_path

        if self.jobid_hash_size is not None:
            base_path = os.path.join(base_path, str(int(int(jobid) / int(self.jobid_hash_size))))

            if not os.path.isdir(base_path):
                try:
                    os.makedirs(base_path)
                except Exception:
                    # Handle possible raise from other process
                    if not os.path.isdir(base_path):
                        assert False, "Failed to makedirs '%s' " % base_path

        tfilename = ".%s" % filename
        try:
            with open(os.path.join(base_path, tfilename), "wb") as file:
                file.write(request.data)
            os.rename(os.path.join(base_path, tfilename), os.path.join(base_path, filename))
        except Exception as err:
            logger.debug("Failed to write file")
            try:
                os.unlink(os.path.join(base_path, tfilename))
            except Exception:
                # Just log unlink errors
                logger.error("Failed to unlink tmp file")
            raise Exception("Failed to write") from err
        return "OK"


class Main:
    def __init__(self):
        # Options
        parser = OptionParser()
        parser.add_option(
            "--version",
            action="store_true",
            dest="show_version",
            default=False,
            help="Show version",
        )
        parser.add_option(
            "--config",
            type="string",
            action="store",
            dest="config",
            default="/etc/sams/sams-post-receiver.yaml",
            help="Config file [%default]",
        )
        parser.add_option("--logfile", type="string", action="store", dest="logfile", help="Log file")
        parser.add_option(
            "--loglevel",
            type="string",
            action="store",
            dest="loglevel",
            help="Loglevel",
        )

        (self.options, self.args) = parser.parse_args()

        if self.options.show_version:
            print("SAMS Software Accounting version %s" % __version__)
            sys.exit(0)

        self.config = sams.core.Config(self.options.config, {})

        # Logging
        loglevel = self.options.loglevel
        if not loglevel:
            loglevel = self.config.get([id, "loglevel"], "ERROR")
        if not loglevel:
            loglevel = self.config.get(["common", "loglevel"], "ERROR")
        loglevel_n = getattr(logging, loglevel.upper(), None)
        if not isinstance(loglevel_n, int):
            raise ValueError("Invalid log level: %s" % loglevel)
        logfile = self.options.logfile
        if not logfile:
            logfile = self.config.get([id, "logfile"])
        if not logfile:
            logfile = self.config.get(["common", "logfile"])
        logformat = self.config.get([id, "logformat"], "%(asctime)s %(name)s:%(levelname)s %(message)s")
        if logfile:
            logging.basicConfig(filename=logfile, filemode="a", format=logformat, level=loglevel_n)
        else:
            logging.basicConfig(format=logformat, level=loglevel_n)

    def start(self):
        app = Flask(__name__)
        view_func = Receiver.as_view(
            "receiver",
            base_path=self.config.get([id, "base_path"], "/tmp"),
            jobid_hash_size=self.config.get([id, "jobid_hash_size"]),
        )
        app.add_url_rule("/<int:jobid>/<filename>", view_func=view_func)
        app.run(
            host=self.config.get([id, "bind"], "127.0.0.1"),
            port=self.config.get([id, "port"], 8080),
        )


if __name__ == "__main__":
    Main().start()
