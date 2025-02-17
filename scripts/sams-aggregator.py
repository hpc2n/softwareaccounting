#!/usr/bin/env python

"""
Data Aggregator for SAMS Software accounting

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

id = "sams.aggregator"


class Main:
    def __init__(self):
        self.loaders = []
        self.aggregators = []

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
            default="/etc/sams/sams-aggregator.yaml",
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
        for loader_config in self.config.get([id, "loaders"], []):
            try:
                Loader = sams.core.ClassLoader.load(loader_config, "Loader")
                loader = Loader(loader_config, self.config)
                self.loaders.append(loader)
            except Exception as e:
                logger.error("Failed to initialize: %s", loader_config)
                logger.exception(e)
                sys.exit(1)

        for a in self.config.get([id, "aggregators"], []):
            try:
                Aggregator = sams.core.ClassLoader.load(a, "Aggregator")
                aggregator = Aggregator(a, self.config)
                self.aggregators.append(aggregator)
            except Exception as e:
                logger.error("Failed to initialize: %s", a)
                logger.exception(e)
                sys.exit(1)

        logger.debug("Start loading %s", self.loaders)
        for loader_config in self.loaders:
            loader_config.load()
            while True:
                try:
                    data = loader_config.next()
                    if not data:
                        break
                except Exception as e:
                    logger.error(e)
                    loader_config.error()
                    continue

                try:
                    logger.debug("Data: %s", data)
                    for a in self.aggregators:
                        a.aggregate(data)
                    loader_config.commit()
                except Exception as e:
                    logger.error("Failed to do aggregation")
                    logger.exception(e)

                    # Cleanup of the aggregators.
                    for a in self.aggregators:
                        a.cleanup()
                    loader_config.error()

        # Close down the aggregagors.
        for a in self.aggregators:
            a.close()


if __name__ == "__main__":
    Main().start()
