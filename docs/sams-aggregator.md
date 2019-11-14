
# SAMS aggregator

The *sams-aggregator* is run on the collecting machine and aggregates the information from
*sams-collector* with the *sams.aggregator* plugins. The current version uses a SQL-lite database.

# Parts

The collector contains of two parts. The *loader* and the *aggregator*.

## loader

This plugin loads data from the json files created with the *sams-collector*.

## aggregator

This plugin takes the data loaded from the *loader* module to get all data from
the different nodes into one place.

# Command line arguments

## --help

Usage information

## --config=<file>

Path to configuration file.

Default: /etc/sams/sams-aggregator.yaml

## --logfile=<filename>

[See logging](logging.md)

## --loglevel=

[See logging](logging.md)

# Configuration

Core options of SAMS collector.

## loaders

A list of plugins that loads *collector* data.

## aggregators

A list of plugins that aggregates the data.

## logfile

[See logging](logging.md)

## loglevel

[See logging](logging.md)

# Configuration Example

```
sams.aggregator:  
  loaders:
    - sams.loader.File
  aggregators:
    - sams.aggregator.SoftwareAccounting

  loglevel: ERROR

sams.loader.File:
  in_path: /data/softwareaccounting/data
  archive_path: /data/softwareaccounting/archive
  error_path: /data/softwareaccounting/error
  file_pattern: '^.*\.json$'

sams.aggregator.SoftwareAccounting:
  # zero to disable (default)
  jobid_hash_size: 0
  file_pattern: "sa-%(jobid_hash)d.db"
  db_path: /data/softwareaccounting/db
  cluster: CLUSTER.example.com
```
