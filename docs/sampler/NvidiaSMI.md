# sams.sampler.NvidiaSMI

Fetches metrics about Nvidia graphics processing units.

## Configuration

### sampler_interval

How long to wait (in seconds) for next time the sampling will be executed.

Default value: 60

### nvidia_smi_command

Path to the nvidia-smi command.

Default vaule: /usr/bin/nvidia-smi

### gpu_index_environment

Environment variable with comma-separated indexes of GPUs.

Default value: SLURM_JOB_GPUS

### nvidia_smi_metrics

List of metrics to collect.

For a list of available metrics run `nvidia-smi --help-query-gpu`.

Default value:
```
- power.draw
- power.limit
- clocks.applications.memory
- clocks.applications.graphics
- clocks.current.graphics
- clocks.current.sm
- utilization.gpu
- utilization.memory
```

## Output

Output contains metrics per GPU from nvidia-smi.

## Example configuration

```
sams.sampler.NvidiaSMI:
  sampler_interval: 30
  nvidia_smi_command: /usr/bin/nvidia-smi
  gpu_index_environment: SLURM_JOB_GPUS
  nvidia_smi_metrics:
    - power.draw
    - power.limit
    - clocks.applications.memory
    - clocks.applications.graphics
    - clocks.current.graphics
    - clocks.current.sm
    - utilization.gpu
    - utilization.memory
```
