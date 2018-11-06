
= SAMS collector

The collector is run on the compute-node and collects information about the running jobs.

= Parts

The collector contains of three parts. The pidfinder, the sampler and the outputs.

== pidfinder

This plugin finds process ids (PID) of a job.

== sampler

This plugins gets the PIDs from pidfinder and collects metrics about the processes.

== output

This plugins output the result of the samplers info different kinds of ways.

= Command line arguments

== --jobid=

Jobid to collect information about. 

Note: In slurm this must be the ''JobIDRaw'' and not the jobid with job array extension (NNNNNN_A)

== --config=<file>

Path to configuration file.

Default: /etc/sams/sams-collector.yaml

== --node=

Name of the current node. 

Default: ''hostname'' of the machine.

== --logfile=<filename>

[See logging](logging.md)

== --loglevel=

[See logging](logging.md)

== --daemon

Send collector into background.

== --pidfile=<path>

Create pid file at <path>.

= Configuration

Core options of SAMS collector.

== pid_finder_update_interval

The number of seconds to wait before trying to find new pids.

== pid_finder

Name of the plugin that finds PIDs.

== samplers

A list of plugins that sample metrics about the PIDs.

== outputs

A list of plugins that stores the metrics from the samplers.

== logfile

[See logging](logging.md)

== loglevel

[See logging](logging.md)

= Configuration Example

```
---
sams-collector:  
  pid_finder_update_interval: 30
  pid_finder: sams.pidfinder.Slurm
  samplers:
    - sams.sampler.Core
    - sams.sampler.Software
    - sams.sampler.SlurmInfo
  outputs:
    - sams.output.File

  logfile: /var/log/sams-collector.%(jobid)s.%(node)s.log
  loglevel: ERROR

sams.pidfinder.Slurm:
  grace_period: 600

sams.sampler.SlurmInfo:
  sampler_interval: 30

sams.sampler.Software:
  sampler_interval: 30

sams.output.File:
  base_path: /var/spool/softwareaccounting/data
  file_pattern: "%(jobid)s.%(node)s.json"
  jobid_hash_size: 1000
```
