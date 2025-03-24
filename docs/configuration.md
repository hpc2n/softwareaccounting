# Configuration

Configuration uses the YAML file format. By default each program uses its own configuration file but it is also possible to reuse the same configuration file between all programs.

To configure Software Accounting, each program and each module should have their own section. For modules, the section should be named after the module. For programs, the section should be named *sams.program*.

Refer to the documentation of each program or module for specific configuration options.

## Example config file

```
---
sams.collector:  
  pid_finder_update_interval: 30
  pid_finder: sams.pidfinder.Slurm
  samplers:
    - sams.sampler.Core
    - sams.sampler.Software
    - sams.sampler.SlurmInfo
  outputs:
    - sams.output.File

  # logfile: /var/log/sams.logfile.%(jobid)s.%(node)s.log
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
