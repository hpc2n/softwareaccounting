
# sams.output.File

Write outputs into the file system.

# Config options

## base_path

Path where the output files are written.

## file_pattern

Write files in file pattern.
Available data for replace is: jobid & node

Default: "%(jobid)s.%(node)s.json"

## jobid_hash_size

"Hash" the output based on --jobid / jobid_hash_size

## write_as_uid

If set uses the sysfsuid() syscall to write files as uid.
This does not work on lustre.

## exclude

List of sampler modules to skip.

# Example configuration

```
sams.output.File:
  # Path where the output files are written.
  base_path: /outout/softwareaccounting/data

  # Write files in file pattern. 
  # Available data for replace is: jobid & node
  file_pattern: "%(jobid)s.%(node)s.json"

  # "Hash" the output based on --jobid / jobid_hash_size
  jobid_hash_size: 1000

  # If set uses the sysfsuid() syscall to write files as uid.
  # This does not work on lustre.
  # write_as_uid: 1234

  # Skip the list of modules.
  exclude: ['sams.sampler.ModuleName']
```
