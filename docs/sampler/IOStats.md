# sams.sampler.IOStats

Fetches statistics about device IO.

## Configuration

### sampler_interval

How long to wait (in seconds) for next time the sampling will be executed.

Default value: 60

### iostat_command

Path to the iostat command.

Default vaule: /usr/bin/iostat

### iostat_devs

List of paths to monitored IO devices.

If a path contains %(jobid)s then it will be replaced with the job id. A * can be used for globbing.

This options is required.

## Output

Output contains output from the iostat command per device.

See iostat documentation for further details.

## Example configuration

```
sams.sampler.IOStats:
  sampler_interval: 30
  iostat_devs: ['/dev/rootvg/slurm_%(jobid)s_*']
```
