# sams.sampler.FSStats

Fetches statistics about file systems.

## Configuration

### sampler_interval

How long to wait (in seconds) for next time the sampling will be executed.

Default value: 60

### mount_points

List of paths to monitored file system mount points.

If a path contains %(jobid)s then it will be replaced with the job id. A * can be used for globbing.

This options is required.

## Output

Output includes the following fields per mount point.

### free

Number of free bytes.

### size

File system size in bytes.

### used

Number of used bytes.

## Example configuration

```
sams.sampler.FSStats:
  sampler_interval: 30
  mount_points: ['/scratch/slurm.%(jobid)s.*']
```
