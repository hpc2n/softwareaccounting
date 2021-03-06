"""
Base classes

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

import time

import threading

try:
    import queue
except ImportError:
    import Queue as queue


import logging
logger = logging.getLogger(__name__)

class PIDFinder(object):
    """ PIDFinder base class """

    def __init__(self,id,jobid,config):
        self.id = id
        self.jobid = jobid
        self.config = config

    def find(self):
        raise Exception("Not implemented")
        # return []

class Sampler(threading.Thread):
    """ Sampler base class """

    def __init__(self,id,outQueue,config):
        super(Sampler,self).__init__()
        self.id = id
        self.outQueue = outQueue
        self.config = config
        self.jobid = self.config.get(['options','jobid'])
        self.pidQueue = queue.Queue()
        self.pids = []
        self.sampler_interval = self.config.get([self.id,"sampler_interval"],60)

    def init(self):
        pass

    def run(self):
        try:
            self.init()
        except Exception as e:
            logger.exception("Failed to do self.init in %s" % self.id,e)
        while True:
            try:
                pids = self.pidQueue.get(timeout = self.sampler_interval)
                if not pids:
                    self.pidQueue.task_done()
                    break
                logger.debug("Received new pids: %s", pids)
                self.pids.extend(pids)
                self.pidQueue.task_done()
            except queue.Empty as e:
                logger.debug("%s queue.Empty timeout" % self.id)
                pass
            try:
                if self.do_sample():
                    self.sample()
            except Exception as e:
                logger.exception("Failed to do self.sample in %s" % self.id,e)
            
        try:
            self.store(self.final_data(),'final')
        except Exception as e:
            logger.exception("Failed to do self.final_data in %s" % self.id,e)
        self.outQueue.join()
    
    def store(self,data,type='now'):
        self.outQueue.put({
                'id': self.id,
                'data': data,
                'type': type
            })

    # this should be implemented in the real Sampler..
    def sample(self):
        raise Exception("Not implemented")

    def do_sample(self):
        return len(self.pids) > 0

    def exit(self):
        logger.debug("%s exit" % self.id)
        self.pidQueue.put(None)

class Aggregator(object):
    """ Aggregator base class """

    def __init__(self,id,config):
        self.id = id
        self.config = config

    def aggregate(self,data):
        raise Exception("Not implemented")

class Loader(object):
    """ Loader base class """

    def __init__(self,id,config):
        self.id = id
        self.config = config        

    def load(self):
        raise Exception("Not implemented")
    
    def next(self):
        raise Exception("Not implemented")

    def commit(self):
        raise Exception("Not implemented")

class Backend(object):
    """ Backend base class """

    def __init__(self,id,config):
        self.id = id
        self.config = config

    def update(self,updater):
        raise Exception("Not implemented")

    def extract(self,xyz):
        raise Exception("Not implemented")

class Software(object):
    """ Software base class """

    def __init__(self,id,config):
        self.id = id
        self.config = config

    def update(self):
        raise Exception("Not implemented")
        
class Output(threading.Thread):
    """ Output base class """
        
    def __init__(self,id,config):
        super(Output,self).__init__()
        self.id = id
        self.config = config

        self.dataQueue = queue.Queue()
        self.jobid = self.config.get(['options','jobid'])

    def run(self):
        while True:
            data = self.dataQueue.get()
            if data is None:
                self.dataQueue.task_done()
                break
            try:
                self.store({ data['id']: data['data'] })
            except Exception as e:
                logger.exception("Failed to store",e)
            if 'type' in data and data['type'] == 'final':
                try:
                    self.final({ data['id']: data['data'] })
                except Exception as e:
                    logger.exception("Failed to do self.final in %s" % self.id,e)
            self.dataQueue.task_done()

        for t in range(int(self.config.get([self.id,'retry_count'],3))):
            try:
                self.write()
                break
            except Exception as e:
                logger.exception("Failed to do self.write in %s" % self.id,e)
            time.sleep(int(self.config.get([self.id,'retry_sleep'],3)))

    def store(self,data):
        raise Exception("Not implemented")

    def final(self,data):
        self.store(data)

    def write(self):
        raise Exception("Not implemented")

    def exit(self):
        self.dataQueue.put(None)

class XMLWriter(object):
    """ XMLWriter base class """

    def __init__(self,id,config):
        self.id = id
        self.config = config

    def write(self,data):
        raise Exception("Not implemented")
