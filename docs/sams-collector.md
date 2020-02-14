
# SAMS collector

The *sams-collector* is run on the compute-node and collects information about the running jobs.

# Parts

The collector contains of three parts. The *pidfinder*, the *sampler* and the *outputs*.

## pidfinder

This plugin finds process ids (PID) of a job.

## sampler

This plugins gets the PIDs from pidfinder and collects metrics about the processes.

## output

This plugins output the result of the samplers info different kinds of ways.

# Command line arguments

## --help

Usage information

## --jobid=

Jobid to collect information about. 

Note: In slurm this must be the ''JobIDRaw'' and not the jobid with job array extension (NNNNNN_A)

## --config=<file>

Path to configuration file.

Default: /etc/sams/sams-collector.yaml

## --node=

Name of the current node. 

Default: ''hostname'' of the machine.

## --logfile=<filename>

[See logging](logging.md)

## --loglevel=

[See logging](logging.md)

## --daemon

Send collector into background.

## --pidfile=<path>

Create pid file at <path>.

# Configuration

Core options of SAMS collector.

## pid_finder_update_interval

The number of seconds to wait before trying to find new pids.

## pid_finder

Name of the plugin that finds PIDs.

## samplers

A list of plugins that sample metrics about the PIDs.

## outputs

A list of plugins that stores the metrics from the samplers.

## logfile

[See logging](logging.md)

## loglevel

[See logging](logging.md)

# Configuration Example

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

  umask: '077' # only used in daemon mode.
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

# Example usage

In Slurm prolog start

	sams-collector.py --config=/path/config.yaml --jobid=$SLURM_JOB_ID --daemon --pidfile=/var/run/sams-collector.$SLURM_JOB_ID

The sams-collector needs to run as root. 

In Slurm epilog kill -HUP.

If HUP i missing the collector will exit after 10 minutes without active processes.

See below for example usage with systemd.

## Systemd startup example

Starting and stopping the software accounting with systemd is easy

create the file: /etc/systemd/system/softwareaccounting@.service
with the following content:

'''
[Unit]
Description=SAMS Software Accounting (%i)

[Service]
Environment=PYTHONPATH=/lap/softwareaccounting/lib/python3.5/site-packages
PIDFile=/var/run/software-accounting.%i.pid
ExecStart=/lap/softwareaccounting/bin/sams-collector.py --jobid=%i --config=/etc/slurm/softwareaccounting.yaml
KillSignal=SIGHUP
KillMode=process
'''

To start the accounting process just run: systemctl start softwareaccounting@${SLURM_JOB_ID}.service
in the slurm prolog and put: systemctl stop softwareaccounting@${SLURM_JOB_ID}.service
in the slurm epilog.
