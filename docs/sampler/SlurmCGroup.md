# sams.sampler.SlurmCGroup

Fetches metrics from a Slurm version 1 CGroup.

## Configuration

### sampler_interval

How long to wait (in seconds) for next time the sampling will be executed.

Default value: 60

### cgroup_base

Default vaule: /cgroup

## Output

## Example configuration

```
sams.sampler.SlurmCGroup:
  sampler_interval: 30
  cgroup_base: /sys/fs/cgroup
```
