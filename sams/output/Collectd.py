"""
Sends output from Samplers to collectd

Config Options:

sams.output.Collectd:
    socket: /run/collectd.socket

    # Fetches the value from dict-value and put into dict-key
    # This can be used in the 'metrics' dict-value with %(key)s
    map:
        jobid: sams.sampler.Core/jobid
        node: sams.sampler.Core/node

    # Sets the value from dict-value and put into dict-key
    # This can be used in the 'metrics' dict-value with %(key)s
    static_map:
        cluster: kebnekaise

    # Metrics matching dict-key will be sent to collectd via PUTVAL
    metrics:    
        '^sams.sampler.SlurmCGroup/(?P<metric>\S+)$' : '%(cluster)s/%(jobid)s/%(node)s/%(metric)s'

"""
import sams.base
import time
import socket
import re

import logging
logger = logging.getLogger(__name__)

class Output(sams.base.Output):
    """ File output Class """

    def __init__(self,id,config):
        super(Output,self).__init__(id,config)
        self.static_map = self.config.get([self.id,"static_map"],{})
        self.map = self.config.get([self.id,"map"],{})
        self.metrics = self.config.get([self.id,"metrics"],{})
        self.socket = self.config.get([self.id,"socket"],'/run/collectd.socket')
        self.data = {}

    def dict2str(self,dct,base="",delim="/"):   
        out = []
        for key in dct.keys():
            nb = "/".join([base,key])
            if key in dct and type(dct[key]) is dict:
                out = out + self.dict2str(dct[key],base=nb)
            else:
                out = out + [{'match': nb, 'value':dct[key]}]
        return out

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

        flatdict = self.dict2str(data)
        for d in flatdict:           
            for metric,destination in self.metrics.items():                
                reg = re.compile(metric)
                m = reg.match(d['match'])
                if m:
                    di = m.groupdict()
                    self.send(d['value'],destination,di)


    def send(self,value,destination,di):
        d = self.static_map.copy()
        d.update(di)
        for k,v in self.map.items():
            m = self.safe_metric(self.data,v.split('/'))
            if not m:
                logger.warning("map: %s: %s is missing" % (k,v))
                return
            d[k] = m

        try:
            d['metric'] = d['metric'].replace("/", "_")
            dest = destination % d
        except Exception as e:
            logger.error(e)
            return

        if not value:
            logger.warning("%s got no metric" % (dest))
            return

        message = "PUTVAL %s %d:%s" % (dest,int(time.time()),value)
        logger.debug("Sending: %s" % (message))

        try:
            sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            sock.connect(self.socket)
            sock.send(str.encode(message + "\n"))
            reply = sock.recv(1024)
            logger.debug("Reply from collectd: %s" % (reply))
            sock.close()
        except socket.error as e:
            logger.error("Failed to send: %s to %s" % (message,self.socket))
        
    def write(self):
        pass

