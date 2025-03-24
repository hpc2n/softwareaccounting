
# Logging

Logging can be specified on three different places and are picked up in this order using the first match.

1. Command line options.
2. Program block in the configuration file.
3. *common* block in the configuration file.

## Logfile

Set this to the name of the file where logs should be written.

The logfile have substitions ''%(jobid)s'' and ''%(node)s'' to create more unique names (only on sams-collector).

## Loglevel

Set this to the level of logging that should be written to the log file.

Available options: CRITICAL, ERROR, WARNING, INFO, DEBUG 

Default: ERROR

## Example

In this example the sams-collector will use the sams-collector.NNNN.NODE.log file on loglevel ERROR and all other will use the sams-common.log file on loglevel INFO if they use the same config file.

```
---
common:  
  logfile: /var/log/sams-common.log
  loglevel: INFO

sams.collector:
  logfile: /var/log/sams-collector.%(jobid)s.%(node)s.log
  loglevel: ERROR
```
