"""
Module that writes XML files for SAMS into files.

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


Config Options:

sams.xmlwriter.File:
    # Where to write output files.
    output_path: "/var/spool/softwareaccounting/records"

    # Software that uses less then 1% cpu of the job are removed
    remove_less_then: 1.0

    # Jobs / File
    jobs_per_file: 1000

"""

import logging
import os
import time
from xml.dom import minidom
from xml.etree import ElementTree
from xml.etree.ElementTree import Element

import sams.base

logger = logging.getLogger(__name__)

SA_NAMESPACE = "http://sams.snic.se/namespaces/2019/01/softwareaccountingrecords"
ISO_TIME_FORMAT = "%Y-%m-%dT%H:%M:%S"


class XMLWriter(sams.base.XMLWriter):
    """SAMS Software accounting xml output"""

    def __init__(self, id, config):
        super(XMLWriter, self).__init__(id, config)
        self.create_time = time.time()
        self.remove_less_then = self.config.get([self.id, "remove_less_then"], 1.0)
        self.jobs_per_file = self.config.get([self.id, "jobs_per_file"], 1000)

    @classmethod
    def prettify(cls, elem):
        """Return a pretty-printed XML string for the Element."""
        rough_string = ElementTree.tostring(elem, "utf-8")
        reparsed = minidom.parseString(rough_string)
        return reparsed.toprettyxml(indent="  ", encoding="UTF-8")

    def write(self, data):
        """Data write method"""

        data = list(data)

        # If no data awailable don't do anything
        if len(data) == 0:
            return

        # Create output
        output_path = self.config.get([self.id, "output_path"], "/var/spool/softwareaccounting/records")
        n = 0
        while data:
            output_file = os.path.join(output_path, "%s.%d.xml") % (
                str(self.create_time),
                n,
            )
            n = n + 1

            # Create files with 'self.jobs_per_file' jobs
            (output, data) = (data[: self.jobs_per_file], data[self.jobs_per_file :])

            # Write file
            with open(output_file, "wb") as f:
                f.write(self.generate_xml(output))

    def generate_xml(self, data):
        """Generate XML output for SAMS"""
        ElementTree.register_namespace("sa", SA_NAMESPACE)
        sa_records = Element("{%s}SoftwareAccountingRecords" % SA_NAMESPACE)

        for j in data:
            if j.total_cpu() == 0.0:
                continue
            sa_records.append(self.generate_job(j))

        return self.prettify(sa_records)

    def generate_job(self, job):
        """Generate XML output for each job"""
        r = Element("{%s}SoftwareAccountingRecord" % SA_NAMESPACE)

        # RecordIdentity
        ri = Element("{%s}RecordIdentity" % SA_NAMESPACE)
        ri.set("{%s}createTime" % SA_NAMESPACE, self.gm2isoTime(self.create_time))
        ri.set("{%s}recordId" % SA_NAMESPACE, job.recordid())
        r.append(ri)

        # JobRecordID
        jri = Element("{%s}JobRecordID" % SA_NAMESPACE)
        jri.text = job.recordid()
        r.append(jri)

        # Software
        for sw in job.softwares(self.remove_less_then):
            s = Element("{%s}Software" % SA_NAMESPACE)
            # Software Name
            name = Element("{%s}Name" % SA_NAMESPACE)
            name.text = sw.software
            s.append(name)
            # Version
            version = Element("{%s}Version" % SA_NAMESPACE)
            version.text = sw.version
            s.append(version)
            # Local version
            local_version = Element("{%s}LocalVersion" % SA_NAMESPACE)
            local_version.text = sw.versionstr
            s.append(local_version)
            # User Provided
            user_provided = Element("{%s}UserProvided" % SA_NAMESPACE)
            user_provided.text = {0: "false", 1: "true"}[sw.user_provided]
            s.append(user_provided)
            # Usage in %
            usage = Element("{%s}Usage" % SA_NAMESPACE)
            usage.text = "%.2f" % (100 * sw.cpu / job.total_cpu(self.remove_less_then))
            s.append(usage)

            r.append(s)

        return r

    @classmethod
    def gm2isoTime(cls, timestamp):
        return time.strftime(ISO_TIME_FORMAT, time.gmtime(timestamp)) + "Z"
