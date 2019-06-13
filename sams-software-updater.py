#!/usr/bin/env python

"""
Software updater for SAMS Software accounting
"""

from __future__ import print_function

import getopt
import logging
import sys

import sams.core

logger = logging.getLogger(__name__)

id = 'sams.software-updater'

class Options:
    def usage(self):
        print("usage....")

    def __init__(self,inargs):
        try:
            opts, args = getopt.getopt(inargs, "", ["help", "config=","logfile=",
                                                    "loglevel=","dry-run","test-path="])
        except getopt.GetoptError as err:
            # print help information and exit:
            print(str(err))  # will print something like "option -a not recognized"
            self.usage()
            sys.exit(2)

        self.config = '/etc/sams/sams-software-updater.yaml'
        self.logfile = None
        self.loglevel = None
        self.dry_run = False
        self.test_path = None
        
        for o, a in opts:
            if o in "--config":
                self.config = a
            elif o in "--logfile":
                    self.logfile = a
            elif o in "--loglevel":
                self.loglevel = a
            elif o in "--test-path":
                self.test_path = a
            elif o in "--dry-run":
                self.dry_run = True
            else:
                assert False, "unhandled option %s = %s" % (o,a)
     
class Main:

    def __init__(self):
        self.options = Options(sys.argv[1:])
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
            exit()
        else:
            try:
                self.backend.update(self.updater)
            except Exception as e:
                logger.exception("Failed to update",e)

if __name__ == "__main__":
    Main().start()
