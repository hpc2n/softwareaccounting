# sams.aggregator.SoftwareAccounting

Stores aggregated informtion into the Software Accounting database.

Used by the [*sams-aggregator*](../sams-aggregator.md)

Related to [*sams.backend.SoftwareAccounting*](../backend/SoftwareAccounting.md)

# Config options

## jobid_hash_size

Number of jobs in each database

Default: All in one file.

## db_path

Path to where the sqlite database files are stored.

## clustername

clustername (used for calculating SGAS recordid)

## file_pattern

Name of the database based on the jobid_hash.

Default: sa-%(jobid_hash)d.db

# Example configuration

```
sams.aggregator.SoftwareAccounting:
  jobid_hash_size: 0
  file_pattern: "sa-%(jobid_hash)d.db"
  db_path: /data/softwareaccounting/db
  cluster: CLUSTER.example.com
```
