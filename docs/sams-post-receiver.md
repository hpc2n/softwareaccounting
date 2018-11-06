
= SAMS POST receiver

The POST receiver is run on the main node to collect information from the SAMS collector sent via the sams.output.Http plugin.

The POST reciver does not have any kind of security. Use for example nginx to add security via for example IP, basic-auth and/or certificate.

Example nginx configuration provided at the bottom of this page.

= Command line arguments

== --config=<file>

Path to configuration file.

Default: /etc/sams/sams-post-receiver.yaml

== --logfile=<filename>

[See logging](logging.md)

== --loglevel=

[See logging](logging.md)

== --daemon

Send collector into background.

Daemon can also be set via the configuration file. If provided on command line the command line option will be used.

== --pidfile=<path>

Create pid file at <path>.

Pidfile can also be set via the configuration file. If provided on command line the command line option will be used.

= Configuration

Core options of SAMS POST receiver.

== port

TCP port to listen to.

Default: 8080

== base_path

Path to save incomming data to.

== jobid_hash_size

The number of files to put in any directory.

== logfile

[See logging](logging.md)

== loglevel

[See logging](logging.md)

= Configuration Example

```
---
sams.post-receiver:  
  port: 8081
  base_path: /data/softwareaccounting/data
  jobid_hash_size: 10000
  logfile: /var/log/sams-post-receiver.log
  loglevel: ERROR
```

= Example nginx configuration

This configuration uses basic auth to secure the POST receiver

```
#
# SAMS POST receiver nginx configuration
#

server {
    listen       [::]:8443;
    listen       *:8443;
    server_name  server.example.com;

    access_log   /var/log/nginx/sams-post-receiver.access.log;
    error_log   /var/log/nginx/sams-post-receiver.error.log info; 

    ssl on;
    ssl_certificate      /etc/certificates/server.cert.pem;
    ssl_certificate_key  /etc/certificates/server.key.pem;

    # Makes hardy FF fail to load these pages
    ssl_protocols  TLSv1 TLSv1.1 TLSv1.2;

    client_max_body_size 512m;

    location /cluster {
        rewrite /cluster/(.*) /$1  break;

        auth_basic           "Basic auth";
        auth_basic_user_file /etc/nginx/htpasswd; 

        proxy_pass         http://127.0.0.1:8080/;
        proxy_redirect     off;
        proxy_read_timeout 900;
    }
}
```
