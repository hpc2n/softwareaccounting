
# sams.sampler.SlurmInfo

Fetches Metrics from Slurm ''scontrol show job'' command

# Config options

## sampler_interval

How long to wait (in seconds) for next time the sampling will be executed.

Default value: 60

## scontrol

path to scontrol command

Default: /usr/bin/scontrol

## environtment

Extra environtment for command.

An hash of key-value with envname-value.

Can for example be used to set the TZ option to get output in UTC.

# Output

## account

Account name used in job.

## cpus

Total number of CPUS used in the job.

## nodes

Total number of Nodes used in the job.

## username

Username the user running the job.

## uid

UserID of username

# Example configuration

> sams.sampler.SlurmInfo:
>   sampler_interval: 60
>
>   # path to scontrol command
>   scontrol: /usr/bin/scontrol
>
>   # extra environments for command
>   environment:
>     TZ: "UTC"


