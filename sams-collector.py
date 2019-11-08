#!/usr/bin/env python

"""
Data Aggregator for SAMS Software accounting
"""

from __future__ import print_function

from optparse import OptionParser
import logging
import os
import platform
import signal
import sys
import threading

import sams.core

logger = logging.getLogger(__name__)

id = 'sams.collector'

class Main:

    def __init__(self):
        # Options
        parser = OptionParser()
        parser.add_option("--config", type="string", action="store", dest="config", default="/etc/sams/sams-collector.yaml", help="Config file [%default]")
        parser.add_option("--logfile", type="string", action="store", dest="logfile", help="Log file")
        parser.add_option("--loglevel", type="string", action="store", dest="loglevel", help="Loglevel")
        parser.add_option("--jobid", type="int", action="store", dest="jobid", help="Slurm JobID")
        parser.add_option("--node", type="string", action="store", dest="node", default=platform.node().split(".")[0], help="Node name [%default]")
        parser.add_option("--daemon", action="store_true", dest="daemon", default=False, help="Send to background as daemon")
        parser.add_option("--pidfile", type="string", action="store", dest="pidfile", help="Pidfile")

        (self.options,self.args) = parser.parse_args()

        if not self.options.jobid:
            print("Missing option --jobid")
            parser.print_help()
            exit(1)

        self.config = sams.core.Config(self.options.config, {
            'options': {
                'jobid': self.options.jobid,
                'node': self.options.node,
            }
        })

        # Put process into background as daemon.
        # stdout/stderr will be closed.
        if self.options.daemon:
            try:
                sams.core.createDaemon()
            except Exception as e:
                logger.exception(e)
                exit(1)

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
        if logfile:
            logfile = logfile % { 'jobid': self.options.jobid, 'node': self.options.node }           
        logformat = self.config.get([id,'logformat'],'%(asctime)s %(name)s:%(levelname)s %(message)s')
        if logfile:
            logging.basicConfig(filename=logfile, filemode='a',
                                format=logformat,level=loglevel_n)
        else:
            logging.basicConfig(format=logformat,level=loglevel_n)
        
        logger.debug("Loglevel: %s", loglevel)

        # Write pidfile.
        if self.options.pidfile:
            try:
                with open(self.options.pidfile,"w") as f:
                    f.write(str(os.getpid()))
            except Exception as e:
                logger.exception(e)
                exit(1)

        self.exit = threading.Event()
        # Trap signals
        signal.signal(signal.SIGHUP, self.sigHupHandler)
        signal.signal(signal.SIGINT, self.sigHupHandler)

    def sigHupHandler(self,signum,frame):
        self.exit.set()

    def cleanup(self):
        # Tell all samplers to exit
        for s in self.samplers:
            s.exit()

        # Wait for all samplers to finish
        for s in filter(lambda t: t.isAlive(),self.samplers):
            s.join()

        # Tell all output to exit
        for o in self.outputs:
            o.exit()

        # Wait for all outputs to finish
        for o in filter(lambda t: t.isAlive(),self.outputs):
            o.join()

        # exit queues
        self.pidQueue.exit()
        self.outQueue.exit()

    def start(self):
        self.samplers = []
        self.outputs = []
        self.pidQueue = sams.core.OneToN("pidQueue")
        self.outQueue = sams.core.OneToN("outQueue")

        for o in self.config.get([id,'outputs'],[]):
            logger.info("Load: %s",o)
            try:
                Output = sams.core.ClassLoader.load(o,'Output')
                output = Output(o,self.config)
                self.outputs.append(output)
                self.outQueue.addQueue(output.dataQueue)
                output.start()
            except Exception as e:
                logger.error("Failed to initialize: %s" % o)
                logger.error(e)
                self.cleanup()
                exit(1)

        for s in self.config.get([id,'samplers'],[]):
            logger.info("Load: %s",s)
            try:
                Sampler = sams.core.ClassLoader.load(s,'Sampler')
                sampler = Sampler(s,self.outQueue.inQueue,self.config)
                self.samplers.append(sampler)
                self.pidQueue.addQueue(sampler.pidQueue)
                sampler.start()
            except Exception as e:
                logger.error("Failed to initialize: %s" % s)
                logger.error(e)
                self.cleanup()
                exit(1)
 
        # load PIDFinder class
        PidFinder = sams.core.ClassLoader.load(self.config.get([id,'pid_finder']),'PIDFinder')        
        try:
            pid_finder = PidFinder(self.config.get([id,'pid_finder']),self.options.jobid,self.config)
        except Exception as e:
            logger.error("Failed to initialize: %s" % self.config.get([id,'pid_finder']))
            logger.error(e)
            self.cleanup()
            exit(1)

        while not self.exit.is_set() and not pid_finder.done():
            pids = pid_finder.find()
            if len(pids):
                self.pidQueue.put(pids)
            self.exit.wait(self.config.get([id,'pid_finder_update_interval'],30))

        self.cleanup()

if __name__ == "__main__":
    Main().start()
