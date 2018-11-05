
# sams.sampler.Software

Fetches the path and cpu usage of the running processes.

# Config options

## sampler_interval

How long to wait (in seconds) for next time the sampling will be executed.

Default value: 60

# Output

## current

The cpu usage/s since last sample (user & system).

Sent every sample.

## execs

An hash of every executable used within this job.

### PATH

The path contains the total cpu usage (user & system) for the executable.

## start_time

First time an process appears (s since epoch).

## end_time

Last time an sample was made (s since epoch).

# Example configuration

> sams.sampler.Software:
>   sampler_interval: 60

