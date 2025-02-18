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

sams.backend.SoftwareAccountingPW:
    # clustername (used for calculating SGAS recordid)
    clustername: CLUSTER

    # Create tables in database
    create_tables: yes

    # See: https://docs.peewee-orm.com/en/latest/peewee/database.html#using-postgresql
    database: postgresql
    database_options:
        database: softwareaccounting
        user: username

    # See: https://docs.peewee-orm.com/en/latest/peewee/database.html#using-sqlite
    database: sqlite
    database_options:
        database: tmp/db/pw.db
        pragmas:
            temp_store: MEMORY

"""

import logging
from datetime import datetime

from peewee import (
    BooleanField,
    DateTimeField,
    DoubleField,
    ForeignKeyField,
    IntegerField,
    Model,
    MySQLDatabase,
    PostgresqlDatabase,
    Proxy,
    SqliteDatabase,
    TextField,
    fn,
)

import sams.base
import sams.core

logger = logging.getLogger(__name__)

db = Proxy()


# Models
class BaseModel(Model):
    class Meta:
        database = db


class Project(BaseModel):
    name = TextField(unique=True)

    class Meta:
        table_name = "projects"


class User(BaseModel):
    name = TextField(unique=True)

    class Meta:
        table_name = "users"


class Node(BaseModel):
    name = TextField(unique=True)

    class Meta:
        table_name = "nodes"


class Job(BaseModel):
    jobid = TextField(index=True)
    recordid = TextField(null=True)
    user = ForeignKeyField(User, backref="jobs", null=True)
    project = ForeignKeyField(Project, backref="projects", null=True)
    ncpus = IntegerField(null=True)
    wall_time = IntegerField(null=True)
    start_time = DateTimeField(null=True)
    end_time = DateTimeField(null=True)
    user_time = DoubleField(null=True)
    system_time = DoubleField(null=True)

    class Meta:
        table_name = "jobs"


class Software(BaseModel):
    path = TextField(index=True, unique=True)
    software = TextField(null=True, index=True)
    version = TextField(null=True)
    versionstr = TextField(null=True)
    user_provided = BooleanField(null=True)
    ignore = BooleanField(null=True)
    last_updated = DateTimeField(null=True, index=True)

    class Meta:
        table_name = "softwares"


class LastSent(BaseModel):
    timestamp = DateTimeField()

    class Meta:
        table_name = "last_sent"


class Command(BaseModel):
    job = ForeignKeyField(Job, backref="commands")
    node = ForeignKeyField(Node, backref="commands")
    software = ForeignKeyField(Software, backref="commands", index=True)
    start_time = DateTimeField()
    end_time = DateTimeField()
    user_time = DoubleField()
    system_time = DoubleField()
    last_updated = DateTimeField(index=True)

    class Meta:
        table_name = "commands"


class Backend(sams.base.Backend):
    """SAMS Software accounting backend"""

    def __init__(self, id, config):
        super(Backend, self).__init__(id, config)
        self.cluster = self.config.get([self.id, "cluster"])
        self.inserted = {}
        self._dry_run = False

        self.database = self.config.get([self.id, "database"], "sqlite")
        self.database_options = self.config.get([self.id, "database_options"], {})

        if self.database == "sqlite":
            sdb = SqliteDatabase(**self.database_options)
        elif self.database == "postgresql":
            sdb = PostgresqlDatabase(**self.database_options)
        elif self.database == "mysql":
            sdb = MySQLDatabase(**self.database_options)
        else:
            raise sams.base.BackendException("A valid database config is not provided. Use: sqlite, postgresql or mysql")

        db.initialize(sdb)
        self.db = db

        # create tables
        create_tables = self.config.get([self.id, "create_tables"], "no")
        if create_tables == "yes":
            self.db.create_tables([User, Project, Job, Software, Command, Node, LastSent])

    def dry_run(self, dry):
        self._dry_run = dry

    def aggregate(self, data):
        """Information aggregate method"""

        jobid = int(data["sams.sampler.Core"]["jobid"])
        node_name = data["sams.sampler.Core"]["node"]

        for module in ["sams.sampler.Software", "sams.sampler.SlurmInfo"]:
            if module not in data:
                logger.info("Jobid: %d on node %s has no %s", jobid, node_name, module)
                raise sams.base.AggregatorException(f"Jobid: {jobid} on node {node_name} has no {module}")

        if len(data["sams.sampler.Software"]["execs"]) == 0:
            raise sams.base.AggregatorException("Jobid: {jobid} on node {node_name} has no execs")

        with self.db.atomic():
            # If project (account) is defined in data insert into table
            project = None
            if "account" in data["sams.sampler.SlurmInfo"]:
                project_name = data["sams.sampler.SlurmInfo"]["account"]
                try:
                    project = Project.get(Project.name == project_name)
                except Project.DoesNotExist:
                    project = Project(name=project_name)
                    project.save()

            # If username is defined in data insert into table
            user = None
            if "username" in data["sams.sampler.SlurmInfo"]:
                user_name = data["sams.sampler.SlurmInfo"]["username"]
                try:
                    user = User.get(User.name == user_name)
                except User.DoesNotExist:
                    user = User(name=user_name)
                    user.save()

            recordid = "%s:%s" % (self.cluster, jobid)
            if "starttime" in data["sams.sampler.SlurmInfo"]:
                starttime = data["sams.sampler.SlurmInfo"]["starttime"]
                starttime = starttime.replace("-", "").replace("T", "").replace(":", "")
                recordid = "%s:%s:%s" % (self.cluster, jobid, starttime)

            # If username is defined in data insert into table
            ncpus = None
            if "cpus" in data["sams.sampler.SlurmInfo"]:
                ncpus = data["sams.sampler.SlurmInfo"]["cpus"]

            # Insert information about job
            try:
                job = Job.get(Job.jobid == jobid)
            except Exception:
                job = Job(
                    jobid=jobid,
                    user=user,
                    project=project,
                    ncpus=ncpus,
                    recordid=recordid,
                )
                job.save()

            # Insert node
            node = None
            try:
                node = Node.get(Node.name == node_name)
            except Node.DoesNotExist:
                node = Node(name=node_name)
                node.save()

            # Insert information about running commands
            for path, info in data["sams.sampler.Software"]["execs"].items():
                # Insert software
                software = None
                try:
                    software = Software.get(Software.path == path)
                except Software.DoesNotExist:
                    software = Software(path=path)
                    software.save()

                try:
                    command = Command.get(
                        Command.job == job,
                        Command.software == software,
                        Command.node == node,
                    )
                except Exception:
                    command = Command(
                        job=job,
                        software=software,
                        node=node,
                        start_time=datetime.fromtimestamp(int(data["sams.sampler.Software"]["start_time"])),
                        end_time=datetime.fromtimestamp(int(data["sams.sampler.Software"]["end_time"])),
                        user_time=info["user"],
                        system_time=info["system"],
                        last_updated=datetime.now(),
                    )
                    command.save()

                    # Mark job for update
                    job.start_time = None
                    job.end_time = None
                    job.user_time = None
                    job.system_time = None
                    job.wall_time = None
                    job.save()

    def cleanup(self):
        pass

    def close(self):
        with self.db.atomic():
            q = (
                Command.select(
                    Command.job,
                    fn.MIN(Command.start_time).alias("start_time"),
                    fn.MAX(Command.end_time).alias("end_time"),
                    fn.SUM(Command.system_time).alias("system_time"),
                    fn.SUM(Command.user_time).alias("user_time"),
                )
                .join(Job)
                .where(Job.start_time.is_null() | Job.end_time.is_null() | Job.system_time.is_null() | Job.user_time.is_null())
                .group_by(Command.job)
            )
            for x in q:
                x.job.start_time = x.start_time
                x.job.end_time = x.end_time
                x.job.system_time = x.system_time
                x.job.user_time = x.user_time
                x.job.wall_time = (x.end_time - x.start_time).total_seconds()
                x.job.last_updated = datetime.now()
                x.job.save()

    def update(self, software):
        """Information aggregate method"""

        with self.db.atomic():
            softwares = Software.select().where(Software.software.is_null())
            for s in softwares:
                info = software.get(s.path)
                if info is not None:
                    s.software = info["software"]
                    s.version = info["version"]
                    s.versionstr = info["versionstr"]
                    s.user_provided = info["user_provided"]
                    s.ignore = info["ignore"]
                    s.last_updated = datetime.now()
                    if not self._dry_run:
                        s.save()

    @staticmethod
    def _print_software(software):
        print("Path: %s" % software.path)
        if software.software is not None:
            print("\tSoftware     : %s" % software.software)
            print("\tVersion      : %s" % software.version)
            print("\tLocal Version: %s" % software.versionstr)
            print("\tUser Provided: %s" % software.user_provided)
            print("\tIgnore       : %s" % software.ignore)
            print("\tCore Hours   : %.1f" % (software.core_time / 3600.0 if software.core_time is not None else 0.0))
            print("\tJob Count    : %d" % software.jobcount)
        else:
            print("\tSoftware is not determined")

    def show_software(self, software=None, path=None):
        if software is None:
            software = "%"
        if path is None:
            path = "%"
        query = (
            Software.select(
                Software,
                fn.SUM(Job.ncpus * Job.wall_time * (Command.system_time + Command.user_time) / (Job.user_time + Job.system_time)).alias(
                    "core_time"
                ),
                fn.Count(fn.Distinct(Job.id)).alias("jobcount"),
            )
            .join(Command, on=(Command.software == Software.id))
            .join(Job, on=(Job.id == Command.job))
            .where((Job.user_time + Job.system_time > 0) & (Software.software % software) & (Software.path % path))
            .order_by(fn.SUM(Job.ncpus * Job.wall_time * (Command.system_time + Command.user_time) / (Job.user_time + Job.system_time)))
            .group_by(Software.id, Software.path)
        )

        for s in query:
            self._print_software(s)

    def show_undetermined(self):
        query = Software.select().where(Software.software.is_null()).order_by(Software.path)
        for software in query:
            print(software.path)

    def reset_path(self, path):
        self.show_software(path=path)
        if not self._dry_run:
            with self.db.atomic():
                query = Software.select().where(Software.path % path)
                for software in query:
                    software.software = None
                    software.save()

    def reset_software(self, software):
        self.show_software(software=software)
        if not self._dry_run:
            with self.db.atomic():
                query = Software.select().where(Software.software % software)
                for software in query:
                    software.software = None
                    software.save()

    def extract(self):
        """Software extract method"""

        try:
            updated = LastSent.get()
        except LastSent.DoesNotExist:
            updated = LastSent(timestamp=datetime.fromtimestamp(0))

        updated_jobs = (
            Command.select(Command.job).where(Command.last_updated > updated.timestamp).distinct()
            | Command.select(Command.job)
            .join(Software, on=Command.software == Software.id)
            .where((Software.last_updated > updated.timestamp) & (Software.ignore is False))
            .distinct()
        )

        query = (
            Job.select(
                Job,
                User,
                Project,
                Software.software,
                Software.version,
                Software.versionstr,
                Software.user_provided,
                fn.SUM(Command.system_time + Command.user_time).alias("cpu"),
                fn.MAX(Command.last_updated).alias("command_last_updated"),
                fn.MAX(Command.software.last_updated).alias("software_last_updated"),
            )
            .join(Command, on=(Command.job == Job.id))
            .join(Software, on=(Command.software == Software.id), attr="software")
            .join(User, on=(Job.user == User.id))
            .join(Project, on=(Job.project == Project.id))
            .where((Command.software.ignore == False) & (Command.job.in_(updated_jobs)))  # noqa: E712
            .group_by(
                Job,
                User,
                Project,
                Software.software,
                Software.version,
                Software.versionstr,
                Software.user_provided,
            )
            .prefetch(User, Project)
        )

        jobs = {}

        for job in query:
            logger.info("Job: %s", job.jobid)
            if job.jobid not in jobs:
                jobs[job.jobid] = sams.core.JobSoftware(job.jobid, job.recordid)

            software = job.command.software.software % dict(user=job.user, project=job.project)
            version = job.command.software.version % dict(user=job.user, project=job.project)
            versionstr = job.command.software.versionstr % dict(user=job.user, project=job.project)

            jobs[job.jobid].addSoftware(
                sams.core.Software(
                    software,
                    version,
                    versionstr,
                    job.command.software.user_provided,
                    job.cpu,
                )
            )

            if job.software_last_updated is not None:
                updated.timestamp = max(updated.timestamp, job.software_last_updated)
            if job.command_last_updated is not None:
                updated.timestamp = max(updated.timestamp, job.command_last_updated)

        self.updated = updated

        return jobs.values()

    def commit(self):
        """Commits last used timestamp to database."""
        self.updated.save()
