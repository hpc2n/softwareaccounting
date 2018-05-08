"""
"""

import sqlite3
import os
import sams.base

import logging
logger = logging.getLogger(__name__)

""" Create tables unless exists """
TABLES = [
    ''' 
    CREATE TABLE IF NOT EXISTS projects (
        id              INTEGER PRIMARY KEY AUTOINCREMENT,
        project         TEXT NOT NULL
    );
    ''',
    ''' 
    CREATE TABLE IF NOT EXISTS users (
        id              INTEGER PRIMARY KEY AUTOINCREMENT,
        user            TEXT NOT NULL
    );
    ''',
    ''' 
    CREATE TABLE IF NOT EXISTS jobs (
        id              INTEGER PRIMARY KEY AUTOINCREMENT,
        jobid           TEXT NOT NULL,
        user            INTEGER,
        project         INTEGER,
        start_time      INTEGER,
        end_time        INTEGER
    );
    ''',
    '''
    CREATE TABLE IF NOT EXISTS software (
        id              INTEGER PRIMARY KEY AUTOINCREMENT,
        path            TEXT NOT NULL,
        software        TEXT,
        version         TEXT,
        versionstr      TEXT
    );
    ''',
    '''
    CREATE INDEX IF NOT EXISTS software_path_idx on software(path);
    ''',
    '''
    CREATE TABLE IF NOT EXISTS node (
        id              INTEGER PRIMARY KEY AUTOINCREMENT,
        node            TEXT NOT NULL
    );
    ''',
    '''
    CREATE INDEX IF NOT EXISTS node_node_idx on node(node);
    ''',
    '''
    CREATE TABLE IF NOT EXISTS command (
        id              INTEGER PRIMARY KEY AUTOINCREMENT,
        jobid           INTEGER NOT NULL,
        node            INTEGER,
        software        INTEGER,
        start_time      INTEGER,
        end_time        INTEGER,
        user            REAL,
        sys             REAL,
        updated         INTEGER,
        FOREIGN KEY(node) REFERENCES node(node),
        FOREIGN KEY(software) REFERENCES software(software)
    );
    ''',
    '''
    CREATE INDEX IF NOT EXISTS command_jobid_node_software_idx on command(jobid,node,software);
    ''',
]

# Update/Insert SQL
INSERT_USER=''' insert or replace into users (id,user) values ((select ID from users where user = ?), ?); '''
INSERT_PROJECT=''' insert or replace into projects (id,project) values ((select ID from projects where project = ?), ?); '''
INSERT_JOBS=''' insert or replace into jobs (id,jobid,user,project) values ((select ID from jobs where jobid = ?), ?, ? ,?); '''
INSERT_NODE=''' insert or replace into node (id,node) values ((select ID from node where node = ?), ?); '''
INSERT_SOFTWARE=''' insert or replace into software (id,path) values ((select ID from software where path = ?), ?); '''
INSERT_COMMAND='''
insert or replace into command (id,jobid,node,software,start_time,end_time,user,sys,updated) values
(
        (
                select ID from command 
                        where 
                                jobid = (select id from jobs where jobid = ?)
                        and 
                                node  = (select id from node where node = ?)
                        and
                                software = (select id from software where path = ?)
        )
, 
        (select id from jobs where jobid = ?),
        (select id from node where node = ?),
        (select id from software where path = ?),
        ?,?,
        ?,?,
        strftime('%s','now')
);
'''

class Aggregator(sams.base.Aggregator):
    """ SAMS Software accounting aggregator """
    def __init__(self,id,config):
        super().__init__(id,config)
        self.db = {}
        self.db_path = self.config.get([self.id,'db_path'])
        self.file_pattern = self.config.get([self.id,'file_pattern'],"sa-%(jobid_hash)d.db")
        self.jobid_hash_size = self.config.get([self.id,'jobid_hash_size'],1000000000)
        self.inserted = {}

    def _open_db(self,jobid_hash):
        """ Open database object """
        db = os.path.join(self.db_path,self.file_pattern % { 'jobid_hash': int(jobid_hash) })        
        self.db[jobid_hash] = sqlite3.connect(db)
        self.db[jobid_hash].isolation_level = None
        c = self.db[jobid_hash].cursor()
        for sql in TABLES:
            logger.debug(sql)
            c.execute(sql)
        self.db[jobid_hash].commit()
        return self.db[jobid_hash]

    def get_db(self,jobid):
        """ get db connection based on jobid / jobid_hash_size """
        jobid_hash = int(jobid / self.jobid_hash_size)
        if jobid_hash in self.db:
            return self.db[jobid_hash]
        return self._open_db(jobid_hash)

    def do_insert(self,jobid,table,value):
        """ Only try to insert once / session """
        jobid_hash = int(jobid / self.jobid_hash_size)
        if jobid_hash not in self.inserted:
            self.inserted[jobid_hash] = {}
        if table not in self.inserted[jobid_hash]:
            self.inserted[jobid_hash][table] = {}
        if value not in self.inserted[jobid_hash][table]:
            self.inserted[jobid_hash][table][value] = True
            return True
        return False

    def aggregate(self,data):
        """ Information aggregate method """

        jobid = int(data['sams.sampler.Core']['jobid'])
        node = data['sams.sampler.Core']['node']

        # Get database for jobid
        db = self.get_db(jobid)
        c = db.cursor()

        # Begin transaction
        c.execute('BEGIN TRANSACTION')

        # If project (account) is defined in data insert into table
        project = None        
        if 'account' in data['sams.sampler.SlurmInfo']:
            project = data['sams.sampler.SlurmInfo']['account']
            if self.do_insert(jobid,'projects',project):
                c.execute(INSERT_PROJECT,(project,project,))

        # If username is defined in data insert into table
        user = None
        if 'username' in data['sams.sampler.SlurmInfo']:
            user = data['sams.sampler.SlurmInfo']['username']
            if self.do_insert(jobid,'users',user):
                c.execute(INSERT_USER,(user,user,))
    
        # Insert information about job
        c.execute(INSERT_JOBS,(jobid,jobid,user,project,))

        # Insert node
        if self.do_insert(jobid,'nodes',node):        
            c.execute(INSERT_NODE,(node,node,))

        # Insert information about running commands
        for sw,info in data['sams.sampler.Software']['execs'].items():
            # Insert software
            if self.do_insert(jobid,'softwares',sw):
                c.execute(INSERT_SOFTWARE,(sw,sw,))
            c.execute(INSERT_COMMAND,(jobid,node,sw,jobid,node,sw,
                                        int(data['sams.sampler.Software']['start_time']),
                                        int(data['sams.sampler.Software']['end_time']),
                                        info['user'],info['system'],))

        # Commit data to disk
        c.execute('COMMIT')
        db.commit()

    def close(self):
        for c in self.db:
            c.close()