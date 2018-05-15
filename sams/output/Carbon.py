
import sams.base
import time
import socket

import logging
logger = logging.getLogger(__name__)

class Output(sams.base.Output):
    """ File output Class """

    def __init__(self,id,config):
        super().__init__(id,config)
        self.static_map = self.config.get([self.id,"static_map"],{})
        self.map = self.config.get([self.id,"map"],{})
        self.metrics = self.config.get([self.id,"metrics"],{})
        self.server = self.config.get([self.id,"server"],'localhost')
        self.port = self.config.get([self.id,"port"],2003)
        self.data = {}

        # UDP Socket
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def safe_metric(self, dct, keys):        
        for key in keys:
            if key in dct:
                dct = dct[key]
            else:
                return None
        return dct

    def store(self,data):
        logger.debug("store: %s" % data)        
        for k,v in data.items():
            self.data[k] = v

        for metric,destination in self.metrics.items():
            m = self.safe_metric(data,metric.split('/'))            
            if m:
                logger.debug("M is %s" % m)
                self.send(m,destination)


    def send(self,value,destination):
        d = self.static_map.copy()
        for k,v in self.map.items():
            m = self.safe_metric(self.data,v.split('/'))
            if not v:                
                return
            d[k] = m

        dest = destination % d
        message = "%s %s %d\n" % (dest,value,int(time.time()))
        logger.debug("Sending: %s to %s:%s" % (message,self.server,self.port))
        self.sock.sendto(str.encode(message), (self.server, self.port))
        
    def write(self):
        pass

