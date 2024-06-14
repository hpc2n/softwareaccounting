# sams.aggregator.SoftwareAccountingPW

Stores aggregated informtion into the Software Accounting database using PeeWee.

Used by the [*sams-aggregator*](../sams-aggregator.md)

Related to [*sams.backend.SoftwareAccountingPW*](../backend/SoftwareAccountingPW.md)

NOTE! sams.aggregator.SoftwareAccountingPW is not database compatible
with sams.aggregator.SoftwareAccounting

# Config options

## clustername

Used for calculating SGAS recordid

Default: ""

## database

Select database type

Valid options are: sqlite, postgresql or mysql

Default: sqlite

## database\_options

Options to pass to PeeWee database classes.

See:
[*sqlite*](https://docs.peewee-orm.com/en/latest/peewee/database.html#using-sqlite)
[*postgresql*](https://docs.peewee-orm.com/en/latest/peewee/database.html#using-postgresql)
[*mysql*](https://docs.peewee-orm.com/en/latest/peewee/database.html#using-mysql)

## create\_tables

If set to "yes" tables will be created in database.

Default: no


# Example configuration

```
sams.backend.SoftwareAccountingPW:
  clustername: cluster.example.com
  database: sqlite
  database_options:
    database: /path/to/sqlite.db
    pragmas:
      temp\_store: MEMORY
```
