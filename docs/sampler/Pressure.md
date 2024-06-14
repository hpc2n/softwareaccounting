
# sams.sampler.Pressure

Fetches {cpu,io,memory}.pressure metrics from CGroup (Experimental)

Reads path to files from /proc/*pid*/cgroup

# Config options

## sampler_interval

How long to wait (in seconds) for next time the sampling will be executed.

Default value: 60

## cgroup_base

Path to CGroup base

Default: /sys/fs/cgroup/unified

# Output

Each metric contains a dict of:

```
{
  "avg10": 0.0,
  "avg60": 0.0,
  "avg300": 0.0,
  "total": 0,
}
```

## cpu

Account name used in job.

## memory

Total number of CPUS used in the job.

## io

Total number of Nodes used in the job.

# Example configuration

```
sams.sampler.Pressure:
  sampler_interval: 60
  cgroup_base: /sys/fs/cgroup/unified

```
