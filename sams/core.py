"""
Core classes

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
"""

import logging
import os
import queue
import resource  # Resource usage information.
import sys
import threading

import yaml

logger = logging.getLogger(__name__)


class Config:
    """Config class, reads config_file.yaml"""

    def __init__(self, config_file, extra=None):
        self._cfg = {}
        with open(config_file, "r") as file:
            self._cfg = yaml.load(file, Loader=yaml.SafeLoader)

        if extra:
            self._cfg = self._merge(extra, self._cfg)

    def _merge(self, source, destination):
        """Merges two dicts"""
        for key, value in source.items():
            if isinstance(value, dict):
                # get node or create one
                node = destination.setdefault(key, {})
                self._merge(value, node)
            else:
                destination[key] = value

        return destination

    def _get(self, cfg, items):
        """Helper function to do the recursive fetch of values from cfg"""
        item = items[0]
        if item in cfg and cfg[item]:
            if len(items) > 1:
                return self._get(cfg[item], items[1:])
            else:
                return cfg[item]
        return None

    def get(self, items, default=None):
        """get config value"""
        value = self._get(self._cfg, items)
        if value is None:
            return default
        return value


class OneToN(threading.Thread):
    """Class that takes one Queue and forwards into N other queues"""

    def __init__(self, id="OneToN"):
        super(OneToN, self).__init__()
        self.id = id

        self.inQueue = queue.Queue()
        self.outQueue = []
        self._lock = threading.Lock()

        self.start()

    def run(self):
        """Thread that forwards data from inQueue to outQueue[]"""
        while True:
            value = self.inQueue.get()
            logger.debug("%s received: %s", self.id, value)
            if value is None:
                break
            # Lock the outQueue so that is will not change during sending.
            self._lock.acquire()
            for q in self.outQueue:
                q.put(value)
            self._lock.release()
            self.inQueue.task_done()

        logger.debug("%s is waiting for outQueue to be done", self.id)
        for q in self.outQueue:
            q.join()
        logger.debug("%s is done", self.id)

    def addQueue(self, queue):
        """Add an new output queue"""
        # Lock the outQueue list so that it is consistent
        self._lock.acquire()
        self.outQueue.append(queue)
        self._lock.release()

    def put(self, value):
        """Put value into the queue"""
        logger.debug("%s put(%s)", self.id, value)
        self.inQueue.put(value)

    def exit(self):
        """Enters an None value into the queue to exit"""
        logger.debug("%s got exit message", self.id)
        self.inQueue.put(None)
        self.join()


class ClassLoader:
    """Static class that loads an class by name"""

    @staticmethod
    def load(package, class_name):
        module = __import__(package, globals(), locals(), [class_name])
        new_class = getattr(module, class_name)
        return new_class


# The standard I/O file descriptors are redirected to /dev/null by default.
if hasattr(os, "devnull"):
    REDIRECT_TO = os.devnull
else:
    REDIRECT_TO = "/dev/null"


def createDaemon(umask=0, workdir="/", maxfds=1024):
    """Detach a process from the controlling terminal and run it in the
    background as a daemon.
    """

    try:
        pid = os.fork()
    except OSError as e:
        raise Exception("%s [%d]" % (e.strerror, e.errno)) from e

    if pid == 0:  # The first child.
        os.setsid()

        try:
            pid = os.fork()  # Fork a second child.
        except OSError as e:
            raise Exception("%s [%d]" % (e.strerror, e.errno)) from e

        if pid == 0:  # The second child.
            os.chdir(workdir)
            os.umask(umask)
        else:
            # Exit parent (the first child) of the second child.
            os._exit(0)  # pylint: disable=protected-access
    else:
        # Exit parent of the first child.
        os._exit(0)  # pylint: disable=protected-access

    maxfd = resource.getrlimit(resource.RLIMIT_NOFILE)[1]
    if maxfd == resource.RLIM_INFINITY:
        maxfd = maxfds

    # Iterate through and close all file descriptors.
    for fd in range(0, maxfd):
        try:
            os.close(fd)
        except OSError:  # ERROR, fd wasn't open to begin with (ignored)
            pass

    # This call to open is guaranteed to return the lowest file descriptor,
    # which will be 0 (stdin), since it was closed above.
    os.open(REDIRECT_TO, os.O_RDWR)  # standard input (0)

    # Duplicate standard input to standard output and standard
    # error.
    os.dup2(0, 1)  # standard output (1)
    os.dup2(0, 2)  # standard error (2)
    return 0


class JobSoftware:
    def __init__(self, jobid, recordid):
        self._softwares = []
        self._jobid = jobid
        self._recordid = recordid

        if self._recordid is None:
            print("%s has no recordid" % (self._jobid))
            sys.exit()

    def addSoftware(self, software):
        if software.software is None:
            print("%s has no software" % (self._recordid))
            sys.exit()
        if software.version is None:
            print("%s has no version" % (self._recordid))
            sys.exit()
        if software.versionstr is None:
            print("%s has no versionstr" % (self._recordid))
            sys.exit()
        if software.user_provided is None:
            print("%s has no user_provided" % (self._recordid))
            sys.exit()
        if software.cpu is None:
            print("%s has no cpu" % (self._recordid))
            sys.exit()
        self._softwares.append(software)

    def softwares(self, remove_less_then=1.0):
        t = self.total_cpu()
        if t == 0.0:
            return self._softwares
        return [x for x in self._softwares if 100 * x.cpu / t >= remove_less_then]

    def jobid(self):
        return self._jobid

    def recordid(self):
        return self._recordid

    def total_cpu(self, remove_less_then=1.0):
        t = sum([x.cpu for x in self._softwares])
        if t == 0.0 or remove_less_then == 0.0:
            return t
        return sum([x.cpu for x in self._softwares if 100 * x.cpu / t >= remove_less_then])

    def __str__(self):
        return "JobSoftware: %s (%s) - %s = %f" % (
            self._jobid,
            self._recordid,
            ",".join([x.__str__() for x in self._softwares]),
            self.total_cpu(),
        )

    def __repr__(self):
        return self.__str__()


class Software:
    def __init__(self, software, version, versionstr, user_provided, cpu):
        self.software = software
        self.version = version
        self.versionstr = versionstr
        self.user_provided = user_provided
        self.cpu = cpu

    def __str__(self):
        return "Software: %s (%s/%s) = %f" % (
            self.software,
            self.version,
            self.versionstr,
            self.cpu,
        )

    def __repr__(self):
        return self.__str__()
