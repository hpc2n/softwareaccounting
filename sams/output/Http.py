
import sams.base
import json
import httplib2

import logging
logger = logging.getLogger(__name__)

class Output(sams.base.Output):
    """ http/https output Class """

    def __init__(self,id,config):
        super().__init__(id,config)
        self.exclude = { e: True for e in self.config.get([self.id,"exclude"],[]) }
        self.data = {}

    def store(self,data):
        for k,v in data.items():
            if k in self.exclude:
                continue
            logger.debug("Store data for: %s => %s" % (k,v))
            self.data[k] = v
        
    def write(self):        
        in_uri = self.config.get([self.id,"uri"])
        jobid = self.config.get(['options','jobid'],0)
        node  = self.config.get(['options','node'],0)
        jobid_hash_size = self.config.get([self.id,'jobid_hash_size'])
        cert_file = self.config.get([self.id,'cert_file'])
        key_file = self.config.get([self.id,'key_file'])
        username = self.config.get([self.id,'username'])
        password = self.config.get([self.id,'password'])

        jobid_hash = int(jobid/jobid_hash_size)
        uri = in_uri % { 'jobid': jobid, 
                         'node': node,  
                         'jobid_hash': jobid_hash  
                       }

        http = httplib2.Http()

        if username and password:
            logger.debug("Sending data as user: %s with password: ********" % username)
            # send username & password
            http.add_credentials(username, password)

        if key_file and cert_file:
            logger.debug("Sending data with cert: %s and key: %s " % (cert_file,key_file))
            # send client certificate
            http.add_certificate(key_file,cert_file,'')

        headers = {'Content-Type': 'application/json'}
        body    = json.dumps(self.data,sort_keys=True,separators=(',',':'))

        logger.debug("Sending data to: %s" % uri)
        resp, content = http.request(uri, "POST", body=body, headers=headers)

        if resp['status'] == '200':
            return True
        logger.error("Failed to send data to: %s" % uri)
        logger.debug(resp)
        logger.debug(content)
        return False

