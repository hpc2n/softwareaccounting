# sams.sampler.ZFSStats

Fetches statistics about ZFS file systems.

## Configuration

### sampler_interval

How long to wait (in seconds) for next time the sampling will be executed.

Default value: 60

### volumes

List of monitored ZFS volumes.

If a volume name contains %(jobid)s then it will be replaced with the job id.

This options is required.

### zfs_command

Path to the zfs command.

Default vaule: /sbin/zfs

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
sams.sampler.ZFSStats:
  sampler_interval: 30
  volumes: ['local/tmp.%(jobid)s']
  zfs_command: /sbin/zfs
```
