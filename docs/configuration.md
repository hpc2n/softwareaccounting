
# Configuration

Configuration uses the YAML file format.

All modules the module name (include namespace) as base for 
all configuration.

All parts of the process uses an config file. Defaults to /etc/sams/$program_name.yaml

All configuration files has an ''common'' part that is shared with all modules.
Currently ''loglevel'' and ''logfile'' are the only things that uses the common options.

Each part has an configuration block named ''sams.$program_name'', for example ''sams.collector'',
with configurations about the specific part.

All parts can use the same configuration file as all options are in different namespace.

More information about the specific configuration needed for each part in the parts documentation.

# Example config file

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
