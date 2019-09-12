#!/usr/bin/env python

"""
Software extractor for SAMS Software accounting
"""

from __future__ import print_function

import getopt
import logging
import sys

import sams.core

logger = logging.getLogger(__name__)

id = 'sams.software-extractor'

class Options:
    def usage(self):
        print("usage....")

    def __init__(self,inargs):
        try:
            opts, args = getopt.getopt(inargs, "", ["help", "config=","logfile=","loglevel="])
        except getopt.GetoptError as err:
            # print help information and exit:
            print(str(err))  # will print something like "option -a not recognized"
            self.usage()
            sys.exit(2)

        self.config = '/etc/sams/sams-software-extractor.yaml'
        self.logfile = None
        self.loglevel = None
        
        for o, a in opts:
            if o in "--config":
                self.config = a
            elif o in "--logfile":
                    self.logfile = a
            elif o in "--loglevel":
                self.loglevel = a
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
        xmlwriter = self.config.get([id,'xmlwriter'])
        try:
            XMLWriter = sams.core.ClassLoader.load(xmlwriter,'XMLWriter')
            self.xmlwriter = XMLWriter(xmlwriter,self.config)
        except Exception as e:
            logger.error("Failed to initialize: %s" % xmlwriter)
            logger.exception(e)
            exit(1)

        backend = self.config.get([id,'backend'])
        try:
            Backend = sams.core.ClassLoader.load(backend,'Backend')
            self.backend = Backend(backend,self.config)
        except Exception as e:
            logger.error("Failed to initialize: %s" % backend)
            logger.exception(e)
            exit(1)

        try:
            data = self.backend.extract()
        except Exception as e:
            logger.error("Failed to extract")
            logger.exception(e)
            exit()

        try:
            self.xmlwriter.write(data)
        except Exception as e:
            logger.error("Failed to write")
            logger.exception(e)
            exit()

        # commit extraction.
        self.backend.commit()

if __name__ == "__main__":
    Main().start()
