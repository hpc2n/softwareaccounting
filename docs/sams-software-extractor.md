
# Software Extractor

The *sams-software-extractor* is run on the collecting machine and extracts the software information into XML files used to send to SAMS. The *software extractor* uses two types of modules, the *backend* and the *xmlwriter*.

The backend module loads software information from the backend.

The xmlwriter modules takes the data loaded from the *backend* module and writes it as XML files.

## Configuration

| Key | Description |
| - | - |
| backend | Name of the plugin that loads software information. |
| xmlwriter | Name of the plugin that writes XML data for SAMS. |

Here is an example configuration file.

```
---
sams.software-extractor:
  loglevel: ERROR

  backend: sams.backend.SoftwareAccounting
  xmlwriter: sams.xmlwriter.File

sams.backend.SoftwareAccounting:
  file_pattern: 'sa-\d+.db'
  db_path: /data/softwareaccounting/cluster/db

sams.xmlwriter.File:
  output_path: /var/spool/softwareaccounting/records
```
