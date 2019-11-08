
# SAMS software updater

The *sams-software-updater* is run on the collecting machine and updates the
software information in the database.

If not options are provided to the software updater the database will be updated based
on the updater module rules.

# Parts

The *software updater* contains of two parts. The *updater* and the *backend*.

## updater

This module converts the path used in for the software into software information.

## backend

This plugin shows and updates software information from the backend.

# Command line arguments

## --config=<file>

Path to configuration file.

Default: /etc/sams/sams-software-extractor.yaml

## --logfile=<filename>

[See logging](logging.md)

## --loglevel=

[See logging](logging.md)

## --dry-run

Do a dry run

## --reset-path=<path>

Reset the path of <path> to be able to update the path.

<path> uses SQL LIKE to update multiple paths.

## --show-path=<path>

Show software information about the <path>.

<path> uses SQL LIKE to show multiple paths.

## --show-paths

Show all the paths.

Same as --show-path=%

## --show-undetermined

Show paths that are undetermined.

## --test-path=<path>

Testing the path against the backend without updating anything.

# Configuration

Core options of SAMS software updater.

## backend

Name of the plugin that shows and updates software information.

## updater

Name of the plugin that converts paths into software.

## logfile

[See logging](logging.md)

## loglevel

[See logging](logging.md)

# Configuration Example

```
---
sams.software-updater:
  loglevel: ERROR

  backend: sams.backend.SoftwareAccounting
  updater: sams.software.Regexp

sams.backend.SoftwareAccounting:
  file_pattern: 'sa-\d+.db'
  db_path: /data/softwareaccounting/db

sams.software.Regexp:
  rules:
    - match: '^/bin/bash'
      software: bash
      version: "system"
      versionstr: ""
      ignore: true
```
