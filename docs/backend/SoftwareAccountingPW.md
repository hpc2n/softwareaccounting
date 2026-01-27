# sams.backend.SoftwareAccountingPW

Manages information in the Software Accounting database using PeeWee.

Used by the [*sams-software-updater*](../sams-software-updater.md)

Related to [*sams.aggregator.SoftwareAccountingPW*](../aggregator/SoftwareAccountingPW.md)

NOTE! sams.aggregator.SoftwareAccountingPW is not database compatible
with sams.aggregator.SoftwareAccounting

## Configuration

### database

Select database type

Valid options are: sqlite, postgresql or mysql

Default: sqlite

### database\_options

Options to pass to PeeWee database classes.

See:
[*sqlite*](https://docs.peewee-orm.com/en/latest/peewee/database.html#using-sqlite)
[*postgresql*](https://docs.peewee-orm.com/en/latest/peewee/database.html#using-postgresql)
[*mysql*](https://docs.peewee-orm.com/en/latest/peewee/database.html#using-mysql)

### create\_tables

If set to "yes" tables will be created in database.

Default: no

## Extract user/project specific data for a software.

If software, version, local version contains a %(user)s or %(project)s string it will be replaced with the user/project of the running job.

## Example configuration

```
sams.backend.SoftwareAccountingPW:
  clustername: cluster.example.com
  database: sqlite
  database_options:
    database: /path/to/sqlite.db
    pragmas:
      temp\_store: MEMORY
```
