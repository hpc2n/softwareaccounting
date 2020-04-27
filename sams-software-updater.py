#!/usr/bin/env python

"""
Software updater for SAMS Software accounting
"""

from __future__ import print_function

from optparse import OptionParser
import logging
import sys

import sams.core

logger = logging.getLogger(__name__)

id = 'sams.software-updater'
    
class Main:

    def __init__(self):

        # Options
        parser = OptionParser()
        parser.add_option("--config", type="string", action="store", dest="config", default="/etc/sams/sams-software-updater.yaml", help="Config file [%default]")
        parser.add_option("--logfile", type="string", action="store", dest="logfile", help="Log file")
        parser.add_option("--loglevel", type="string", action="store", dest="loglevel", help="Loglevel")
        parser.add_option("--dry-run", action="store_true", dest="dry_run", default=False, help="Dry run")
        parser.add_option("--reset-path", type="string", action="store", dest="reset_path", help="Reset specific path(s), GLOB can be used")
        parser.add_option("--show-paths", action="store_true", dest="show_paths", default=False, help="show all paths in database")
        parser.add_option("--show-path", type="string", action="store", dest="show_path", help="Show specific path(s), GLOB can be used")
        parser.add_option("--show-software", type="string", action="store", dest="show_software", help="Show specific softwares(s), GLOB can be used")
        parser.add_option("--show-undetermined", action="store_true", dest="show_undetermined", default=False, help="show all paths that are undetermined")
        parser.add_option("--test-path", type="string", action="store", dest="test_path", help="Test a path against rules")

        (self.options,self.args) = parser.parse_args()

        self.config = sams.core.Config(self.options.config,{})

        # Logging
        loglevel = self.options.loglevel
        if not loglevel:
            loglevel = self.config.get([id,'loglevel'],'ERROR')
        if not loglevel:
            loglevel = self.config.get(['common','loglevel'],'ERROR')
        loglevel_n = getattr(logging, loglevel.upper(), None)
        if not isinstance(loglevel_n, int):
            raise ValueError('Invalid log level: %s' % loglevel)
        logfile = self.options.logfile
        if not logfile:
            logfile = self.config.get([id,'logfile'])        
        if not logfile:
            logfile = self.config.get(['common','logfile'])        
        logformat = self.config.get([id,'logformat'],'%(asctime)s %(name)s:%(levelname)s %(message)s')
        if logfile:
            logging.basicConfig(filename=logfile, filemode='a',
                                format=logformat,level=loglevel_n)
        else:
            logging.basicConfig(format=logformat,level=loglevel_n) 

    def start(self):                
        updater = self.config.get([id,'updater'])
        try:
            Updater = sams.core.ClassLoader.load(updater,'Software')
            self.updater = Updater(updater,self.config)
        except Exception as e:
            logger.error("Failed to initialize: %s" % updater)
            logger.exception(e)
            exit(1)

        backend = self.config.get([id,'backend'])
        try:
            Backend = sams.core.ClassLoader.load(backend,'Backend')
            self.backend = Backend(backend,self.config)
        except Exception as e:
            logger.error("Failed to initialize: %s" % updater)
            logger.exception(e)
            exit(1)

        self.backend.dry_run(self.options.dry_run)
        if self.options.test_path:
            result = self.updater.get(self.options.test_path)
            print("Testing: %s" % self.options.test_path)
            if not result:
                print("No matching software for path.")
            else:
                print("\tSoftware     : %s" % result['software'])
                print("\tVersion      : %s" % result['version'])
                print("\tLocal Version: %s" % result['versionstr'])
                print("\tUser Provided: %s" % result['user_provided'])
                print("\tIgnore       : %s" % result['ignore'])
        elif self.options.show_software or self.options.show_path:
            self.backend.show_software(software = self.options.show_software,
                                        path = self.options.show_path)
        elif self.options.show_paths:
            self.backend.show_software()
        elif self.options.show_undetermined:
            self.backend.show_undetermined()
        elif self.options.reset_path:
            self.backend.reset_path(self.options.reset_path)
        else:
            try:
                self.backend.update(self.updater)
            except Exception as e:
                logger.error("Failed to update")
                logger.exception(e)

if __name__ == "__main__":
    Main().start()
