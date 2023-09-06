# Version 1.7 - 2023-09-06

- Updated sgas-sa-registrant.
  Same as sgas-bart bart-registrant that uses python3 and does not use twisted.

## Upgrading

Upgrading to 1.7 requires using python3 and compatible requests library
for the the sgas-sa-registrant and config file need to be updated.
See example etc/sgas-sa-registrant.conf.

# Version 1.6 - 2023-03-29

- New sams.sampler.Pressure. Fetches pressure metrics from cgroup.
  See: docs/sampler/Pressure.md
- New sams.loader.FileSlurmInfoFallback. Fetches information from sacct
  if Slurm is not responding or does not want to ask slurmctld from nodes.
  See: docs/loader/FileSlurmInfoFallback.md
- Possible to set Sqlite temp\_store pragma to allow use of memory instead
  of /var/tmp or $TMPDIR to store temporary information during queries.
  See: docs/backend/SoftwareAccounting.md and
  docs/aggregator/SoftwareAccounting.md
- Exception cleanup
- Fix in sams.output.Prometheus for None values.
- Fix in sams.output.Carbon and Collectd to check if var is dict.
- Fix in sams.loader.File for moving files to different filesystem.
- Continue code cleanup using isort, black, pylint.

## Upgrading

Upgrading from v1.5 does not require any changes to configurations files.

# Version 1.5 - 2022-02-04

- Cleanup of code using isort, black and pylint.
- Fix crach on empty config key. Fixes Issue#23
- Changed isAlive() to is\_alive() due to deprecation.
- sams-commands now have a --version flag.
- Support for --reset-softare= in sams-software-updater
- After a --reset-command an update is run directly afterwards.
- Updated examples for sams-software-updater.
- Add swap output from sams.sampler.SlurmCGroup module. Fixes issue #24

## Upgrading

Upgrading from v1.4 does not require any changes to configurations files.

# Version 1.4 - 2021-02-11

- Fix/cleanup of yaml module import. Fixes Issue#17
- New sams.sampler.FSStats module. Fetches Metrics from a filesystem
- New sams.sampler.IOStats. Fetches metrics from iostat command about block devices
- Updated setup.py. Patches from Pär Lindfors <par.lindfors@uppmax.uu.se>
- Make nvidia-smi metrics configurable.
- New sams.sampler.ZFSStats. ZFS metrics sampler.
- Updated Collectd module.
- Removed write\_as\_uid/setfsuid due to license problems.
- LICENSE added to the project. Fixes Issue#14
- Experimental output module for Prometheus node-exporter.
- Support for stopping rewrite rules on match.

## Upgrading

Upgrading from v1.3 does not require any changes to configurations files.

# Version 1.3 - 2020-11-05

- --test-output option added to [*sams-collector*](docs/sams-collector.md).
- Collectd output module added.
- Enables to use --show-software and --show-path together in [*sams-software-updater*](docs/sams-software-updater.md).
- Export software with user/project specific information in software/version/local version. [*backend/SoftwareAccounting*](docs/backend/SoftwareAccounting.md)

## Upgrading

Upgrading from v1.2 does not require any changes to configurations files.

# Version 1.2 - 2020-04-06

- Set umask in deamon mode. See: [*sams-collector*](docs/sams-collector.md)
- Adds a [*FAQ*](docs/sams-faq.md)
- sams-software-updater now uses GLOB (\*?) instead of SQLite "LIKE" patterns. See  [*sams-software-updater*](docs/sams-software-updater.md)
- Fixes som problem with setup.py for generating .rpm's.
- Adds a --show-software flag to [*sams-software-updater*](docs/sams-software-updater.md).

## Upgrading

Upgrading from v1.1 does not require any changes to configurations files.


# Version 1.1 - 2020-01-31

- Rewrite feature added to Regexp module. See: [*sams.software.Regexp*](docs/software/Regexp.md)
- sams-post-receiver, sams.loader.File and sams.output.File makes target directory tree.

## Upgrading

Upgrading from v1.0 does not require any changes.


# Version 1.0 - 2019-11-14

First major release.

## Upgrading

Upgrading from a release before v1.0 is possible but not recomended and requires database conversion.
