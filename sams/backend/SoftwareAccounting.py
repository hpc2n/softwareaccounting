"""
Software accounting storage "backend" for updating the list of softwares

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

Config options:

sams.backend.SoftwareAccounting:
    # sqlite file pattern (regexp)
    file_pattern: 'sa-\\d+.db'

    # Path to sqlite db files
    db_path: /data/softwareaccounting/CLUSTER/db

    # sqlite temp_store pragma (DEFAULT, FILE or MEMORY)
    # DEFAULT is normally FILE but is dependent on compile time
    # options of the sqlite library.
    sqlite_temp_store: DEFAULT
"""

import logging
import os
import re
import sqlite3

import sams.base
from sams.core import JobSoftware, Software

logger = logging.getLogger(__name__)

FIND_SOFTWARE = """SELECT id,path FROM software WHERE software IS NULL"""
UPDATE_SOFTWARE = """
    UPDATE software 
    SET software = :software, version = :version, versionstr = :versionstr, 
        user_provided = :user_provided, ignore = :ignore, last_updated = strftime('%s','now')
    WHERE id = :id and software is NULL
"""
EXTRACT_SOFTWARE = """
SELECT x.software,x.version,x.versionstr,x.jobid,x.recordid,
        sum(x.cpu) as cpu,max(x.updated) as updated,x.user_provided, users.user,projects.project
FROM (
             SELECT s.software,s.version,s.versionstr,j.jobid,j.user,j.project,sum(c.user+c.sys) as cpu, j.recordid, j.id,
                    max(max(s.last_updated,c.updated)) as updated,s.user_provided
             FROM software s, command c, jobs j
             WHERE c.software = s.id and c.jobid = j.id and NOT s.ignore and
                j.id in (select DISTINCT jobid from command where updated > :updated UNION
                    select DISTINCT jobid from command where software in (
                                select DISTINCT id from software where last_updated > :updated and NOT ignore
                        )
                )
             GROUP BY s.software,s.version,s.versionstr,s.user_provided,j.jobid,j.recordid,j.id,j.user,j.project
          ) x
LEFT JOIN users ON x.user = users.id
LEFT JOIN projects ON x.project = projects.id
WHERE x.recordid is not null
GROUP BY x.software,x.version,x.versionstr,x.jobid,recordid,x.user_provided,users.user,projects.project
ORDER BY x.jobid
"""

RESET_PATH = """
UPDATE software SET software = NULL where path GLOB :path
"""

RESET_SOFTWARE = """
UPDATE software SET software = NULL where software GLOB :software
"""

SHOW_SOFTWARE = """
SELECT s.path,s.software,s.version,s.versionstr,s.user_provided,s.ignore,s.last_updated,
            sum(j.ncpus*(j.end_time-j.start_time)*(c.user+c.sys)/(j.user_time+j.system_time)) as cpu,
            count(distinct j.id) as jobcount
        FROM command c,jobs j,software s
        WHERE c.jobid = j.id AND c.software = s.id AND s.path GLOB :path AND s.software GLOB :software AND j.user_time+j.system_time > 0
        GROUP BY path
        ORDER BY cpu
"""

SHOW_UNDETERMINED_SOFTWARE = """
SELECT path from software where software IS NULL order by path
"""


class Backend(sams.base.Backend):
    """SAMS Software accounting aggregator"""

    def __init__(self, id, config):
        super(Backend, self).__init__(id, config)
        self.db_path = self.config.get([self.id, "db_path"])
        self.file_pattern = re.compile(self.config.get([self.id, "file_pattern"], r"sa-\d+.db"))
        self.sqlite_temp_store = self.config.get([self.id, "sqlite_temp_store"], "DEFAULT")

        if self.sqlite_temp_store not in ["DEFAULT", "FILE", "MEMORY"]:
            sams.base.BackendException("sqlite_temp_store must be one of DEFAULT, FILE or MEMORY")

        self.dry_run(False)
        self.updated = {}

    @classmethod
    def _open_db(cls, db):
        """Open database object"""
        dbh = sqlite3.connect(db)
        dbh.isolation_level = None
        return dbh

    def get_databases(self):
        dbs = os.listdir(self.db_path)
        dbs = filter(self.file_pattern.match, dbs)
        dbs = map(lambda file: os.path.join(self.db_path, file), dbs)
        return list(dbs)

    def dry_run(self, dry):
        self._dry_run = dry

    def update(self, software):
        """Information aggregate method"""

        # Get databases
        dbs = self.get_databases()
        for db in dbs:
            dbh = self._open_db(db)
            c = dbh.cursor()

            # Begin transaction
            c.execute("BEGIN TRANSACTION")
            c.execute("PRAGMA temp_store = %s" % self.sqlite_temp_store)

            rows = [row for row in c.execute(FIND_SOFTWARE)]
            for row in rows:
                logger.debug("Software: %s (ID: %s)", row[1], row[0])
                info = software.get(row[1])
                if info:
                    logger.debug(info)
                    if not self._dry_run:
                        c.execute(
                            UPDATE_SOFTWARE,
                            {
                                "software": info["software"],
                                "version": info["version"],
                                "versionstr": info["versionstr"],
                                "user_provided": info["user_provided"],
                                "id": row[0],
                                "ignore": info["ignore"],
                            },
                        )

            logger.info("Done")
            # Commit data to disk
            if not self._dry_run:
                c.execute("COMMIT")
                dbh.commit()
            dbh.close()

    def extract(self):
        """Software extract method"""

        jobs = {}
        self.updated = {}
        for db in self.get_databases():
            dbh = self._open_db(db)
            c = dbh.cursor()
            c.execute("PRAGMA temp_store = %s" % self.sqlite_temp_store)
            updated = [ts for ts in c.execute("SELECT timestamp from last_sent")][0][0]
            rows = [row for row in c.execute(EXTRACT_SOFTWARE, {"updated": updated})]
            dbh.close()

            for row in rows:
                if row[3] not in jobs:
                    jobs[row[3]] = JobSoftware(row[3], row[4])

                software = row[0] % dict(user=row[8], project=row[9])
                version = row[1] % dict(user=row[8], project=row[9])
                versionstr = row[2] % dict(user=row[8], project=row[9])

                jobs[row[3]].addSoftware(Software(software, version, versionstr, row[7], row[5]))

                if updated < row[6]:
                    updated = row[6]

            self.updated[db] = updated

        return jobs.values()

    def commit(self):
        """Commits last used timestamp to database."""
        for db in self.get_databases():
            dbh = self._open_db(db)
            c = dbh.cursor()
            c.execute("PRAGMA temp_store = %s" % self.sqlite_temp_store)
            c.execute(
                "UPDATE last_sent set timestamp = :timestamp",
                {"timestamp": self.updated[db]},
            )
            dbh.commit()
            dbh.close()

    @classmethod
    def _print_software(cls, software):
        print("Path: %s" % software[0])
        if software[1]:
            print("\tSoftware     : %s" % software[1])
            print("\tVersion      : %s" % software[2])
            print("\tLocal Version: %s" % software[3])
            print("\tUser Provided: %s" % software[4])
            print("\tIgnore       : %s" % software[5])
            print("\tCore Hours   : %.1f" % (software[7] / 3600.0 if software[7] is not None else 0.0))
            print("\tJob Count    : %d" % software[8])
        else:
            print("\tSoftware is not determined")

    def show_software(self, software=None, path=None):
        if not software:
            software = "*"
        if not path:
            path = "*"
        for db in self.get_databases():
            dbh = self._open_db(db)
            c = dbh.cursor()
            c.execute("PRAGMA temp_store = %s" % self.sqlite_temp_store)
            for s in c.execute(SHOW_SOFTWARE, dict(software=software, path=path)):
                self._print_software(s)
            dbh.close()

    def show_undetermined(self):
        for db in self.get_databases():
            dbh = self._open_db(db)
            c = dbh.cursor()
            c.execute("PRAGMA temp_store = %s" % self.sqlite_temp_store)
            for software in c.execute(SHOW_UNDETERMINED_SOFTWARE):
                print(software[0])
            dbh.close()

    def reset_path(self, path):
        self.show_software(path=path)
        if not self._dry_run:
            for db in self.get_databases():
                dbh = self._open_db(db)
                c = dbh.cursor()
                c.execute("PRAGMA temp_store = %s" % self.sqlite_temp_store)
                c.execute(RESET_PATH, {"path": path})
                dbh.commit()
                dbh.close()

    def reset_software(self, software):
        self.show_software(software=software)
        if not self._dry_run:
            for db in self.get_databases():
                dbh = self._open_db(db)
                c = dbh.cursor()
                c.execute("PRAGMA temp_store = %s" % self.sqlite_temp_store)
                c.execute(RESET_SOFTWARE, {"software": software})
                dbh.commit()
                dbh.close()
