
# Needed packages

## Ununtu

### Python3

python3-yaml
python3-json
python3-httplib2
python3-flask	(for sams-post-receiver.py)

### Python2

python-yaml
python-json
python-httplib2
python-flask	(for sams-post-receiver.py)

## CentOS/RedHat

+### 6 (Python 2.6)

python-simplejson
PyYAML
python-flask   (for sams-post-receiver.py, not tested)

### 7

# Usage:

## On cluster nodes.

In slurm prolog start

	sams-collector.py --config=/path/config.yaml --jobid=$SLURM_JOB_ID

The sams-collector needs to run as root. 

In slurm epilog kill -HUP.

If HUP i missing the collector will exit after 10 minutes without active processes.

See the sampler and output modules for more information.

## Aggregator (sams-aggregator.py)

On server run the aggregator on the files received either on shared filessystem
with the sams.output.File module or via http/https via the sams.output.Http module.

sams.output.Http needs an post receiver for example the sams-post-receiver.py.
Security for sams-post-receiver.py should be provided with for example an nginx 
reverse proxy with client certificate and/or user/password.

sams.output.File can write on root-squash filesystems using the setfsuid() syscall on Linux.
This seems to not work on Lustre file systems.

See the loader and aggregator modules for more information.

## Software updater (sams-software-updater.py)

After the aggregator has inserted things the Software updater needs to update the
list of available paths into software.

This uses the software.backend.* and sams.software.* modules to process the information.

See the backend and software modules for more information.

# nginx setup for sams-post-reciver.py

  server {
    listen       [::]:8443;
    listen       *:8443;
    server_name  server.hpc2n.umu.se;

    access_log   /var/log/nginx/server.hpc2n.umu.se.se.access.log;
    # use this if debugging any errors
    #error_log   /var/log/nginx/server.hpc2n.umu.debug.log debug; 
    error_log   /var/log/nginx/server.hpc2n.umu.se.error.log info; 

    ssl on;
    ssl_certificate      /etc/grid-security/server.hpc2n.umu.se.cert.pem;
    ssl_certificate_key  /etc/grid-security/server.hpc2n.umu.se.key.pem;

    #ssl_client_certificate /etc/nginx/allowed.ca.pem;
    #ssl_verify_client on;

    # Makes hardy FF fail to load these pages
    ssl_protocols  TLSv1 TLSv1.1 TLSv1.2;

    client_max_body_size 512m;
    ssl_verify_depth 4;

    location / {
        auth_basic           "Basic auth";
        auth_basic_user_file /etc/nginx/htpasswd; 

        proxy_pass         http://127.0.0.1:8080/;
        proxy_redirect     off;
        proxy_read_timeout 900;
    }
  }

# systemd

Starting and stopping the software accounting with
systemd is easy


create the file: /etc/systemd/system/softwareaccounting@.service
wit the following content:
'''
[Unit]
Description=SAMS Software Accounting (%i)

[Service]
Environment=PYTHONPATH=/lap/softwareaccounting/lib/python3.5/site-packages
PIDFile=/var/run/software-accounting.%i.pid
ExecStart=/lap/softwareaccounting/bin/sams-collector.py --jobid=%i --config=/etc/slurm/softwareaccounting.yaml
KillSignal=SIGHUP
KillMode=process
'''

To start the accounting process just run: systemctl start softwareaccounting@${SLURM_JOB_ID}.service
in the slurm prolog and put: systemctl stop softwareaccounting@${SLURM_JOB_ID}.service
in the slurm epilog.
