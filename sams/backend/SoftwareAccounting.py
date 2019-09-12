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
from sams.core import Software, JobSoftware

import logging
logger = logging.getLogger(__name__)

FIND_SOFTWARE = '''SELECT id,path FROM software WHERE software IS NULL'''
UPDATE_SOFTWARE = '''
    UPDATE software 
    SET software = :software, version = :version, versionstr = :versionstr, 
        user_provided = :user_provided, ignore = :ignore, last_updated = strftime('%s','now')
    WHERE id = :id and software is NULL
'''
EXTRACT_SOFTWARE = '''
SELECT x.software,x.version,x.versionstr,x.jobid,x.recordid,
        sum(x.cpu) as cpu,max(x.updated) as updated,x.user_provided
FROM (
             SELECT s.software,s.version,s.versionstr,j.jobid,sum(c.user+c.sys) as cpu, j.recordid, j.id,
                    max(max(s.last_updated,c.updated)) as updated,s.user_provided
             FROM software s, command c, jobs j
             WHERE c.software = s.id and c.jobid = j.id and NOT s.ignore and
                j.id in (select DISTINCT jobid from command where updated > :updated UNION
                    select DISTINCT jobid from command where software in (
                                select DISTINCT id from software where last_updated > :updated and NOT ignore
                        )
                )
             GROUP BY s.software,s.version,s.versionstr,s.user_provided,j.jobid,j.recordid,j.id
          ) x
WHERE x.recordid is not null
GROUP BY x.software,x.version,x.versionstr,x.jobid,recordid,x.user_provided
ORDER BY x.jobid
'''


class Backend(sams.base.Backend):
    """ SAMS Software accounting aggregator """
    def __init__(self,id,config):
        super(Backend,self).__init__(id,config)
        self.db_path = self.config.get([self.id,'db_path'])
        self.file_pattern = re.compile(self.config.get([self.id,'file_pattern'],"sa-\d+.db"))
        self.dry_run(False)

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

    def dry_run(self,dry):
        self._dry_run = dry

    def update(self,software):
        """ Information aggregate method """

        # Get databases
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
                    if not self._dry_run:
                        c.execute(UPDATE_SOFTWARE,{ 'software': info['software'],'version': info['version']
                                             ,'versionstr': info['versionstr'],'user_provided': info['user_provided'], 
                                             'id': row[0], 'ignore': info['ignore'] })
            
            logger.info("Done")
            # Commit data to disk
            if not self._dry_run: 
                c.execute('COMMIT')
                dbh.commit()
            dbh.close()

    def extract(self):
        """ Software extract method """

        jobs = {}
        self.updated = {}
        for db in self.get_databases():
            dbh = self._open_db(db)
            c = dbh.cursor()
            updated = [ts for ts in c.execute('SELECT timestamp from last_sent')][0][0]
            rows = [row for row in c.execute(EXTRACT_SOFTWARE,{'updated': updated})]
            dbh.close()

            for row in rows:
                if not row[3] in jobs:
                    jobs[row[3]] = JobSoftware(row[3],row[4])

                jobs[row[3]].addSoftware(
                    Software(row[0],row[1],row[2],row[7],row[5])
                )

                if updated < row[6]:
                    updated = row[6]

            self.updated[db] = updated

        return jobs.values()

    def commit(self):
        """ Commits last used timestamp to database. """
        for db in self.get_databases():
            dbh = self._open_db(db)
            c = dbh.cursor()
            c.execute('UPDATE last_sent set timestamp = :timestamp', {'timestamp': self.updated[db]})
            dbh.commit()
            dbh.close()
