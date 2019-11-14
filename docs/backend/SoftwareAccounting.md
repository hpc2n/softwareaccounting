# sams.backend.SoftwareAccounting

Manages informtion in the Software Accounting database.

Used by the [*sams-software-updater*](../sams-software-updater.md)

Related to [*sams.aggregator.SoftwareAccounting*](../aggregator/SoftwareAccounting.md)

# Config options

## db_path

Path to where the sqlite database files are stored.

## file_pattern

Sqlite file pattern (regexp).

Default: sa-\d+.db

# Example configuration

```
sams.backend.SoftwareAccounting:
  file_pattern: 'sa-\d+.db'
  db_path: /data/softwareaccounting/db
```
