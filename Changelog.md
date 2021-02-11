# Version 1.4 - 2021-02-11

- Fix/cleanup of yaml module import. Fixes Issue#17
- New sams.sampler.FSStats module. Fetches Metrics from a filesystem
- New sams.sampler.IOStats. Fetches metrics from iostat command about block devices
- Updated setup.py. Patches from Pär Lindfors <par.lindfors@uppmax.uu.se>
- Make nvidia-smi metrics configurable.
- New sams.sampler.ZFSStats. ZFS metrics sampler.
- Updated Collectd module.
- Removed write_as_uid/setfsuid due to license problems.
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
