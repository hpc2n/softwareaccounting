# POST Receiver

The POST receiver is run on the main node to collect information from the collector sent via the [*sams.output.Http*](output/Http.md) module.

The POST receiver does not have any kind of security. Use for example nginx to add security via for example IP limitation, HTTP authentication, or client certificates.

## Configuration

| Key | Description |
| - | - |
| port | TCP port to listen to. |
| base_path | Path to save incoming data to. |
| jobid_hash_size | The number of files to put in any directory. |

Here is an example configuration file.


```
---
sams.post-receiver:  
  port: 8081
  base_path: /data/softwareaccounting/data
  jobid_hash_size: 10000
  logfile: /var/log/sams-post-receiver.log
  loglevel: ERROR
```

## Using with Nginx

This is an example snippet of an nginx configuration file, passing on requests to the POST receiver.

```
server {
    ...

    location /cluster {
        rewrite /cluster/(.*) /$1  break;

        auth_basic           "Basic auth";
        auth_basic_user_file /etc/nginx/htpasswd; 

        proxy_pass         http://127.0.0.1:8080/;
        proxy_redirect     off;
        proxy_read_timeout 900;
    }

    ...
}
```
