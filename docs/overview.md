# Overview

Here is a chart showing the flow of data between programs in Software Accounting.

![flow](flow.png "flow")

## Collector

The [*sams-collector*](sams-collector.md) is using a *pidfinder* module to detect PIDs related to the running job.

The default *pidfinder* ([*sams.pidfinder.Slurm*](pidfinder/Slurm.md)) uses the Linux CGroup and how it is used within Slurm to group processes in an job to collect PIDs.

The PIDs are feeded into the *sampler* modules to gather metrics from the job.

During and after the job the data sent from the *samplers* are sent to the *output* modules.

One or more output module can be used at any time.

The two basic output modules are [*sams.output.File*](output/File.md) and [*sams.output.Http*](output/Http.md).

The first one writes files to a filesystem. Either an shared filesytem or to a local filesystem that needs to be transported to a master node after the completed job for further processing with for example rsync or simular.

The [*sams.output.Http*](output/Http.md) module sends the same data using the http:// protocol to a receiving web service.

The [*sams-collector*](sams-collector.md) can also send data to other serviecs like graphite or other graphing services to provide real time usage of different metrics.

## Post Receiver

The [*sams-post-receiver*](sams-post-receiver.md) can be used to receive the output 
from the [*sams.output.Http*](output/Http.md) module and collected to disk.

## Aggregator

The [*sams-aggregator*](sams-aggregator.md) is used to parse the output from the [*sams-collector*](sams-collector.md) using a set of  aggreagors.

To pick up the files from the [*sams-collector*](sams-collector.md) or [*sams-post-receiver*](sams-post-receiver.md) a *loader* is used. Currently only [*sams.loader.File*](loader/File.md) is available.

[*sams.aggregator.SoftwareAccounting*](aggregator/SoftwareAccounting.md) store the output of the aggregation into a Sqlite3 database that are later used with the [*sams-software-updater*](sams-software-updater.md).

## Software Updater

[*sams-software-updater*](sams-software-updater.md) uses two type of modules to convert executable paths into software.

The [*sams.backend.SoftwareAccounting*](backend/SoftwareAccounting.md) is used to fetch non updated path and convert them into softwares with the help of the [*sams.software.Regexp*](software/Regexp.md) that uses regexps to match different paths into software.

## Software Extractor

[*sams-software-extractor*](sams-software-extractor.md) is used to extractor softwares from the database and write the XML files that can be sent to SAMS.

The [*sams.backend.SoftwareAccounting*](backend/SoftwareAccounting.md) is used to fetch jobs and softwares and with help of *sams.xmlwriter.File* convert them into XML files.

Send the XML files with the [*sgas-sa-registrant*](https://github.com/hpc2n/sams) also provided in the extras folder.
