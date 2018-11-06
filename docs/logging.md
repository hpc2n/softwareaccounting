
# Logging

Logging can be specified on three(3) different places and are picked up in this order (first match).

* Command line
* part specific block in config file.
* *common* block in config file.

# Command line

## --logfile=<filename>

If set a logfile will be created at <filename>.

The logfile have substitions ''%(jobid)s'' and ''%(node)s'' to create more unique names (only on sams-collector).

Logfile can also be set via the configuration file. If provided on command line the command line option will be used.

## --loglevel=

Sets the loglevel for the logfile.

Loglevel can also be set via the configuration file. If provided on command line the command line option will be used.

Available options: CRITICAL, ERROR, WARNING, INFO, DEBUG 

Default: ERROR

# Part specifik part in configuration

## logfile

If set a logfile will be created.

The logfile have substitions ''%(jobid)s'' and ''%(node)s'' to create more unique names.

Logfile can also be set via the command line. If provided on command line the command line option will be used.

## loglevel

Sets the loglevel for the logfile.

Loglevel can also be set via the command line. If provided on command line the command line option will be used.

Available options: CRITICAL, ERROR, WARNING, INFO, DEBUG 

Default: ERROR

# common part in configuration

Same as the part specifik part.

# Configuration Example

In this example the sams-collector will use the sams-collector.NNNN.NODE.log file on loglevel ERROR
and all other will use the sams-common.log file on loglevel INFO if they use the same config file.

```
---
common:  
  logfile: /var/log/sams-common.log
  loglevel: INFO

sams.collector:
  logfile: /var/log/sams-collector.%(jobid)s.%(node)s.log
  loglevel: ERROR
```
