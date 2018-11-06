
# sams.sampler.Core

Saves core information about a job from the collector command line options.

# Config options

## sampler_interval

How long to wait (in seconds) for next time the sampling will be executed.

Default value: 60

Note: This is an configuration option that is used on every module and the value is not used in this module.

# Output

## jobid

The --jobid command line option

## node

Name of the current node. Either ''hostname'' or --node.

# Example configuration

```
sams.sampler.Core:
  sampler_interval: 60
```
