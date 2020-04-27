
# Master

- Enables to use --show-software and --show-path together in [*sams-software-updater*](docs/sams-software-updater.md).

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
