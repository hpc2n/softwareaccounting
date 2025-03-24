# Aggregator

The *sams-aggregator* is run on the collecting machine and aggregates the information from
*sams-collector*. The aggregator uses two types of modules, *loaders* and the *aggregators*.

The loader modules loads data from the json files created by the collector program.

The aggregator modules takes the data loaded from the loaders and aggregates them into one place.

## Configuration

| Key | Description |
| - | - |
| loaders | A list of modules that loads *collector* data. |
| aggregators | A list of modules that aggregates the data. |

Here is an example configuration file.

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
