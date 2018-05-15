import sqlite3
import os
import sams.base

import logging
logger = logging.getLogger(__name__)

FIND_SOFTWARE = '''SELECT id,path FROM software WHERE software IS NULL'''
UPDATE_SOFTWARE = '''
    UPDATE software 
    SET software = ?, version = ?, versionstr = ?, user_provided = ? 
    WHERE id = ?
'''


class Backend(sams.base.Backend):
    """ SAMS Software accounting aggregator """
    def __init__(self,id,config):
        super().__init__(id,config)
        self.db_path = self.config.get([self.id,'db_path'])
        self.file_pattern = self.config.get([self.id,'file_pattern'],"sa-\d+.db")

    def _open_db(self,db):
        """ Open database object """
        dbh = sqlite3.connect(db)
        dbh.isolation_level = None
        return dbh

    def get_databases(self):
        return ['/data/softwareaccounting/kebnekaise/db/sa-99.db',
                '/data/softwareaccounting/abisko/db/sa-99.db']

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
                    c.execute(UPDATE_SOFTWARE,(info['software'],info['version']
                                             ,info['versionstr'],info['user_provided'],row[0],))
            
            logger.info("Done")
            # Commit data to disk
            c.execute('COMMIT')
            dbh.commit()
            dbh.close()
