"""
Module that writes XML files for SAMS into files.

Config Options:

sams.xmlwriter.File:
    # Where to write output files.
    output_path: "/var/spool/softwareaccounting/records"

    # Software that uses less then 1% cpu of the job are removed
    remove_less_then: 1.0

    # Jobs / File
    jobs_per_file: 1000

"""
import sams.base
import re
import pprint
import time
import os
from xml.etree.ElementTree import Element
from xml.etree import ElementTree
from xml.dom import minidom

import logging
logger = logging.getLogger(__name__)

SA_NAMESPACE       = 'http://sams.snic.se/namespaces/2019/01/softwareaccountingrecords'
ISO_TIME_FORMAT    = "%Y-%m-%dT%H:%M:%S"

class XMLWriter(sams.base.XMLWriter):
    """ SAMS Software accounting xml output """
    def __init__(self,id,config):
        super(XMLWriter,self).__init__(id,config)
        self.create_time = time.time()
        self.remove_less_then = self.config.get([self.id,'remove_less_then'],1.0)
        self.jobs_per_file = self.config.get([self.id,'jobs_per_file'],1000)

    def prettify(self,elem):
        """Return a pretty-printed XML string for the Element.
        """
        rough_string = ElementTree.tostring(elem, 'utf-8')
        reparsed = minidom.parseString(rough_string)
        return reparsed.toprettyxml(indent="  ", encoding="UTF-8")

    def write(self,data):
        """ Data write method """

        # If no data awailable don't do anything
        if len(data) == 0:
            return

        # Create output 
        output_path = self.config.get([self.id,'output_path'],"/var/spool/softwareaccounting/records")
        n = 0
        while len(data):
            output_file = os.path.join(output_path,"%s.%d.xml") % (str(self.create_time),n)
            n = n + 1

            # Create files with 'self.jobs_per_file' jobs
            (output,data) = (data[:self.jobs_per_file],data[self.jobs_per_file:])

            # Write file
            with open(output_file,"w") as f:
                f.write(self.generate_xml(output))

    def generate_xml(self,data):
        """ Generate XML output for SAMS """
        ElementTree.register_namespace('sa', SA_NAMESPACE)
        sa_records = Element('{%s}SoftwareAccountingRecords' % SA_NAMESPACE)

        for j in data:
            if j.total_cpu() == 0.0:
                continue
            sa_records.append(self.generate_job(j))

        return self.prettify(sa_records)

    def generate_job(self,job):
        """ Generate XML output for each job """
        r = Element('{%s}SoftwareAccountingRecord' % SA_NAMESPACE)

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
            user_provided.text = { 0: "false", 1: "true" }[sw.user_provided]
            s.append(user_provided)
            # Usage in %
            usage = Element("{%s}Usage" % SA_NAMESPACE)
            usage.text = "%.2f" % ( 100*sw.cpu/job.total_cpu(self.remove_less_then) )
            s.append(usage)

            r.append(s)

        return r    

    def gm2isoTime(self,timestamp):
        return time.strftime(ISO_TIME_FORMAT, time.gmtime(timestamp)) + "Z"




