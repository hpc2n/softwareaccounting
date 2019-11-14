# sams.loader.File

Loads files from the filsystem.

Used by the [*sams-aggregator*](../sams-aggregator.md)

# Config options

## in_path

Path where the input files are.

## archive_path

Files that are processed correctly ends up here.

## error_path

Files that are broken in some way ends up here.

## file_pattern

Read files that matches the file pattern.

Default: ".*"

# Example configuration

```
sams.loader.File:
  in_path: /data/softwareaccounting/data
  archive_path: /data/softwareaccounting/archive
  error_path: /data/softwareaccounting/error
  file_pattern: '^.*\.json$'
```
