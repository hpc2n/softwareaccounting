#!/usr/bin/env python

"""
Software extractor for SAMS Software accounting

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
import sys
from optparse import OptionParser

import sams.core
from sams import __version__

logger = logging.getLogger(__name__)

id = "sams.software-extractor"


class Main:
    def __init__(self):
        self.xmlwriter = None
        self.backend = None

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
            default="/etc/sams/sams-software-extractor.yaml",
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
        xmlwriter = self.config.get([id, "xmlwriter"])
        try:
            XMLWriter = sams.core.ClassLoader.load(xmlwriter, "XMLWriter")
            self.xmlwriter = XMLWriter(xmlwriter, self.config)
        except Exception as e:
            logger.error("Failed to initialize: %s", xmlwriter)
            logger.exception(e)
            sys.exit(1)

        backend = self.config.get([id, "backend"])
        try:
            Backend = sams.core.ClassLoader.load(backend, "Backend")
            self.backend = Backend(backend, self.config)
        except Exception as e:
            logger.error("Failed to initialize: %s", backend)
            logger.exception(e)
            sys.exit(1)

        try:
            data = self.backend.extract()
        except Exception as e:
            logger.error("Failed to extract")
            logger.exception(e)
            sys.exit(1)

        try:
            self.xmlwriter.write(data)
        except Exception as e:
            logger.error("Failed to write")
            logger.exception(e)
            sys.exit(1)

        # commit extraction.
        self.backend.commit()


if __name__ == "__main__":
    Main().start()
