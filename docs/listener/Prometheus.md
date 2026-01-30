# sams.listener.Prometheus

Provide Prometheus data on a UNIX socket.


## Configuration

### socketdir

Path where the listener socket is created.

### map

Mapping from key name to sampler data values.

### static_map

Mapping from key name to static values.

### metrics

Mapping from sampler pattern to Prometheus output.


## Example configuration

```
sams.listener.Prometheus:
  # Where to put UNIX socket.
  socketdir: /var/run/softwareaccounting

  # Fetches the value from dict-value and put into dict-key
  # This can be used in the 'metrics' dict-value with %(key)s
  map:
    jobid: sams.sampler.Core/jobid
    node: sams.sampler.Core/node
    user: sams.sampler.SlurmInfo/username
    account: sams.sampler.SlurmInfo/account

  # Sets the value from dict-value and put into dict-key
  # This can be used in the 'metrics' dict-value with %(key)s
  static_map:
    cluster: cluster1

  # Metrics matching dict-key will be written to socket
  metrics:
    '^/sams.sampler.SlurmCGroup/(?P<metric>[^/]+)$': sa_metric{cluster="%(cluster)s", jobid="%(jobid)s", metric="%(metric)s"}
```
