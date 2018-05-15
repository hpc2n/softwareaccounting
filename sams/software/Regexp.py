
import sams.base
import re

import logging
logger = logging.getLogger(__name__)

class Software(sams.base.Software):
    """ SAMS Software accounting aggregator """
    def __init__(self,id,config):
        super().__init__(id,config)
        self.rules = self.config.get([self.id,'rules'],[])

    def get(self,path):
        """ Information aggregate method """

        for rule in self.rules:
            reg = re.compile(rule['match'])
            m = reg.match(path)
            if m:
                d = m.groupdict()
                up = False
                if 'user_provided' in rule:
                    up = rule['user_provided']
                return {
                    'software': rule['software'] % d,
                    'version': rule['version'] % d,
                    'versionstr': rule['versionstr'] % d,
                    'user_provided': up,
                }
            
        logging.info("Path not found: %s" % path)

        return None
            

