import datetime
import sqlite3
import sys

import sams.core
from sams.backend.SoftwareAccountingPW import Backend as Backend
from sams.backend.SoftwareAccountingPW import Command, Job, LastSent, Node, Project, Software, User

config = sams.core.Config("convert.yaml", {})

b = Backend("sams.backend.SoftwareAccountingPW", config)

db = b.db

sc = sqlite3.connect(sys.argv[1])
sc.isolation_level = None
c = sc.cursor()
c.execute("PRAGMA temp_store = MEMORY")
sc.commit()

print("Update last_sent")
try:
    ls = LastSent.get()
except LastSent.DoesNotExist:
    ls = LastSent(timestamp=datetime.fromtimestamp(0))

for ts in c.execute("SELECT * FROM last_sent"):
    timestamp = datetime.datetime.fromtimestamp(ts[0])
    if timestamp > ls.timestamp:
        print("Timestamp updated")
        ls.timestamp = timestamp
        ls.save()


all_softwares = {x.path: x for x in Software.select()}
c = sc.cursor()
n = 0
with db.atomic() as txn:
    cnt = [x for x in c.execute("select count(*) from software")][0][0]
    print(f"Software count: {cnt}")
    for ts in c.execute("""
    SELECT s.path, s.software, s.version, s.versionstr,
        s.user_provided, s.ignore, s.last_updated
        FROM software s

        -- WHERE s.ignore
        -- limit 10000
    """):
        n += 1
        if n % int(cnt / 10) == 0:
            print(f"Software @ {n} {100 * n / cnt:.1f}%")
        (path, software, version, versionstr, user_provided, ignore, last_updated) = ts

        # we only need one :-)
        if path in all_softwares:
            continue

        if last_updated is not None:
            last_updated = datetime.datetime.fromtimestamp(last_updated)

        software = Software(
            path=path,
            software=software,
            version=version,
            versionstr=versionstr,
            user_provided=user_provided,
            ignore=ignore,
            last_updated=last_updated,
        )
        software.save()
        all_softwares[software.path] = software

print("Software Done!")

all_users = {x.name: x for x in User.select()}
all_projects = {x.name: x for x in Project.select()}
all_jobs = {}
n = 0
with db.atomic() as txn:
    cnt = [x for x in c.execute("select count(*) from jobs")][0][0]
    print(f"Job count: {cnt}")
    for ts in c.execute("""
    SELECT j.id, j.jobid,j.recordid,u.user,p.project,j.ncpus,
            j.start_time,j.end_time,j.user_time,j.system_time
        FROM jobs j
        INNER JOIN projects p ON p.id = j.project
        INNER JOIN users u ON u.id = j.user

        order by j.id desc

        -- limit 100000
    """):
        (id, jobid, recordid, user_name, project_name, ncpus, start_time, end_time, user_time, system_time) = ts
        n += 1
        if n % int(cnt / 100) == 0:
            print(f"Jobs @ {n} {100 * n / cnt:.1f}%")

        if recordid in all_jobs:
            continue

        project = None
        if project_name is not None:
            if project_name in all_projects:
                project = all_projects[project_name]
            else:
                project = Project(name=project_name)
                project.save()
                all_projects[project_name] = project

        user = None
        if user_name is not None:
            if user_name in all_users:
                user = all_users[user_name]
            else:
                user = User(name=user_name)
                user.save()
                all_users[user_name] = user

        if start_time is not None:
            start_time = datetime.datetime.fromtimestamp(start_time)

        if end_time is not None:
            end_time = datetime.datetime.fromtimestamp(end_time)

        job = Job(
            jobid=jobid,
            recordid=recordid,
            user=user,
            project=project,
            ncpus=ncpus,
            start_time=start_time,
            end_time=end_time,
            user_time=user_time,
            system_time=system_time,
        )

        job.save()
        if id in all_jobs:
            print("Dup ID in jobs...???")
        all_jobs[id] = job

print("Jobs Done!")

n = 0
all_nodes = {x.name: x for x in Node.select()}
with db.atomic() as txn:
    cnt = [x for x in c.execute("select count(*) from command")][0][0]
    print(f"Command count: {cnt}")
    for ts in c.execute("""
    SELECT c.id, c.jobid,n.node,s.path,
            c.start_time,c.end_time,c.user,c.sys,c.updated,s.ignore
        FROM command c
        INNER JOIN node n ON n.id = c.node
        INNER JOIN software s ON s.id = c.software

        -- where s.ignore

        order by c.jobid desc
        -- limit 10000
    """):
        (id, jobid, node_name, path, start_time, end_time, user_time, system_time, last_updated, ignore) = ts
        n += 1
        if n % int(cnt / 100) == 0:
            print(f"Command @ {n} {100 * n / cnt:.1f}%")

        if jobid not in all_jobs:
            continue

        if path not in all_softwares:
            continue

        node = None
        if node_name is not None:
            if node_name in all_nodes:
                node = all_nodes[node_name]
            else:
                node = Node(name=node_name)
                node.save()
                all_nodes[node_name] = node

        job = all_jobs[jobid]

        last_updated = datetime.datetime.fromtimestamp(last_updated)
        start_time = datetime.datetime.fromtimestamp(start_time)
        end_time = datetime.datetime.fromtimestamp(end_time)

        software = all_softwares[path]

        command = Command(
            job=job,
            node=node,
            software=software,
            start_time=start_time,
            end_time=end_time,
            user_time=user_time,
            system_time=system_time,
            last_updated=last_updated,
        )
        command.save()

print("Command Done!")
