"""
Software accounting storage "backend" for updating the list of softwares

Config options:

sams.backend.SoftwareAccounting:
    # sqlite file pattern (regexp)
    file_pattern: 'sa-\d+.db'

    # Path to sqlite db files
    db_path: /data/softwareaccounting/CLUSTER/db

"""

import sqlite3
import os
import re
import sams.base

import logging
logger = logging.getLogger(__name__)

FIND_SOFTWARE = '''SELECT id,path FROM software WHERE software IS NULL'''
UPDATE_SOFTWARE = '''
    UPDATE software 
    SET software = :software, version = :version, versionstr = :versionstr, 
        user_provided = :user_provided, ignore = :ignore, last_updated = strftime('%s','now')
    WHERE id = :id
'''


class Backend(sams.base.Backend):
    """ SAMS Software accounting aggregator """
    def __init__(self,id,config):
        super(Backend,self).__init__(id,config)
        self.db_path = self.config.get([self.id,'db_path'])
        self.file_pattern = re.compile(self.config.get([self.id,'file_pattern'],"sa-\d+.db"))

    def _open_db(self,db):
        """ Open database object """
        dbh = sqlite3.connect(db)
        dbh.isolation_level = None
        return dbh

    def get_databases(self):
        dbs = [file for file in os.listdir(self.db_path)]
        dbs = filter(lambda file: self.file_pattern.match(file),dbs)
        dbs = map(lambda file: os.path.join(self.db_path,file), dbs)        
        return list(dbs)

    def update(self,software):
        """ Information aggregate method """

        # Get database for jobid
        dbs = self.get_databases()
        for db in dbs:
            dbh = self._open_db(db)
            c = dbh.cursor()

            # Begin transaction
            c.execute('BEGIN TRANSACTION')

            rows = [row for row in c.execute(FIND_SOFTWARE)]
            for row in rows:
                info = software.get(row[1])
                if info:
                    logger.debug(info) 
                    c.execute(UPDATE_SOFTWARE,{ 'software': info['software'],'version': info['version']
                                             ,'versionstr': info['versionstr'],'user_provided': info['user_provided'], 
                                             'id': row[0], 'ignore': info['ignore'] })
            
            logger.info("Done")
            # Commit data to disk
            c.execute('COMMIT')
            dbh.commit()
            dbh.close()
