# Collector

The *sams-collector* is run on the compute-node and collects information about the running jobs. The collector uses three types of modules, a *pidfinder*, *sampler* and the *outputs*.

The pidfinder module finds process ids (PID) of a job.

The sampler modules gets the PIDs from pidfinder and collects metrics about the processes.

The output modules outputs the result of the samplers.

The collector needs to know which Slurm job it is collecting information about, provide it with the *--jobid* command line option. In slurm this must be the *JobIDRaw*''* and not the jobid with job array extension (NNNNNN_A)

## Configuration

| Key | Description |
| - | - |
| pid_finder_update_interval | The number of seconds to wait before trying to find new pids. |
| pid_finder | Name of the plugin that finds PIDs. |
| samplers | A list of plugins that sample metrics about the PIDs. |
| outputs | A list of plugins that stores the metrics from the samplers. |

Here is an example configuration file.

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

## Invoking from Slurm

In Slurm prolog start

    sams-collector.py --config=/path/config.yaml --jobid=$SLURM_JOB_ID --daemon \
      --pidfile=/var/run/sams-collector.$SLURM_JOB_ID

The sams-collector needs to run as root. 

In Slurm epilog use kill -HUP. If HUP i missing the collector will exit after 10 minutes without active processes.

### Using Systemd

Starting and stopping the collector with systemd is easy.

Create the file: /etc/systemd/system/softwareaccounting@.service with the following content:

```
[Unit]
Description=Software Accounting (%i)

[Service]
PIDFile=/var/run/softwareaccounting.%i.pid
ExecStart=/opt/softwareaccounting/bin/sams-collector.py --jobid=%i --config=/etc/slurm/softwareaccounting.yaml
KillSignal=SIGHUP
KillMode=process
```

To start the accounting process just run

    systemctl start softwareaccounting@${SLURM_JOB_ID}.service

in the slurm prolog and

    systemctl stop softwareaccounting@${SLURM_JOB_ID}.service

in the slurm epilog.
