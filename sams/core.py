
import yaml
try:
    from yaml import CLoader as YamlLoader, CDumper as YamlDumper
except ImportError:
    from yaml import YamlLoader, YamlDumper
import threading
import queue

import logging
logger = logging.getLogger(__name__)

class Config():
    """ Config class, reads config_file.yaml """
    
    def __init__(self,config_file,extra={}):
        self._cfg = {}
        with open(config_file,"r") as file:
            self._cfg = yaml.load(file, Loader=YamlLoader)

        self._cfg = self._merge(extra,self._cfg)
    
    def _merge(self,source, destination):
        """ Merges two dicts """
        for key, value in source.items():
            if isinstance(value, dict):
                # get node or create one
                node = destination.setdefault(key, {})
                self._merge(value, node)
            else:
                destination[key] = value

        return destination

    def _get(self,cfg,items):
        """ Helper function to do the recursive fetch of values from cfg """
        item = items[0]
        if item in cfg:
            if len(items) > 1:
                return self._get(cfg[item],items[1:])
            else:
                return cfg[item]
        return None

    def get(self,items,default=None):
        """ get config value """
        value = self._get(self._cfg,items)
        if value is None:
            return default
        return value


class OneToN(threading.Thread):    
    """ Class that takes one Queue and forwards into N other queues """

    def __init__(self,id="OneToN"):
        super().__init__()
        self.id = id
        
        self.inQueue = queue.Queue()
        self.outQueue = []
        self._lock = threading.Lock()
        
        self.start()

    def run(self):
        """ Thread that forwards data from inQueue to outQueue[] """
        while True:
            value = self.inQueue.get()
            if value is None:
                break
            # Lock the outQueue so that is will not change during sending.
            self._lock.acquire()
            for q in self.outQueue:
                q.put(value)
            self._lock.release()
            self.inQueue.task_done()

        for q in self.outQueue:
            q.join()

    def addQueue(self,queue):
        """ Add an new output queue """
        # Lock the outQueue list so that it is consistent
        self._lock.acquire()
        self.outQueue.append(queue)
        self._lock.release()

    def put(self,value):
        """ Put value into the queue """
        self.inQueue.put(value)

    def exit(self):
        """ Enters an None value into the queue to exit """
        self.inQueue.put(None)
        self.join()

class ClassLoader():
    """ Static class that loads an class by name """

    @staticmethod
    def load(package,class_name):
        module = __import__(package,globals(),locals(),[class_name])
        new_class = getattr(module,class_name)
        return new_class
