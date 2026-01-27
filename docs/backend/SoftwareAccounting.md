# sams.backend.SoftwareAccounting

Manages information in the Software Accounting database.

Used by the [*sams-software-updater*](../sams-software-updater.md)

Related to [*sams.aggregator.SoftwareAccounting*](../aggregator/SoftwareAccounting.md)

## Configuration

### db_path

Path to where the sqlite database files are stored.

### file_pattern

Sqlite file pattern (regexp).

Default: sa-\d+.db

### sqlite_temp_store

sqlite temp_store pragma (DEFAULT, FILE or MEMORY)
DEFAULT is normally FILE but is dependent on compile time
options of the sqlite library.

Default: DEFAULT

## Extract user/project specific data for a software.

If software, version, local version contains a %(user)s or %(project)s string it will be replaced with the user/project of the running job.

## Example configuration

```
sams.backend.SoftwareAccounting:
  file_pattern: 'sa-\d+.db'
  db_path: /data/softwareaccounting/db
  sqlite_temp_store: DEFAULT
```
