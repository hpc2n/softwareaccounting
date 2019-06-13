
# SAMS software extractor

The *sams-software-extractor* is run on the collecting machine and extracts the
software information into xml files used to send to SAMS.

# Parts

The *software extractor* contains of two parts. The *backend* and the *xmlwriter*.

## backend

This plugin loads software information from the backend.

## xmlwriter

This plugin takes the data loaded from the *backend* module and writes with the
xmlwriter plugin.

# Command line arguments

## --config=<file>

Path to configuration file.

Default: /etc/sams/sams-software-extractor.yaml

## --logfile=<filename>

[See logging](logging.md)

## --loglevel=

[See logging](logging.md)

# Configuration

Core options of SAMS collector.

## backend

Name of the plugin that loads software information.

## xmlwriter

Name of the plugin that writes XML data for SAMS.

## logfile

[See logging](logging.md)

## loglevel

[See logging](logging.md)

# Configuration Example

```
---
sams.software-extractor:
  loglevel: ERROR

  backend: sams.backend.SoftwareAccounting
  xmlwriter: sams.xmlwriter.File

sams.backend.SoftwareAccounting:
  file_pattern: 'sa-\d+.db'
  db_path: /data/softwareaccounting/CLUSTER/db

sams.xmlwriter.File:
  output_path: /var/spool/software_accounting/records
```
