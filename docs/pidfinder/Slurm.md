
# sams.pidfinder.Slurm

Pid finder using the slurm cgroup information in /proc

# Config options

## grace_period

How long to wait (in seconds) after process was removed.

Default value: 600

# Example configuration

```
sams.pidfinder.Slurm:
  # How long to wait (in seconds) after process was removed.
  grace_period: 600
```
