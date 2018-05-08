
# Needed ubuntu packages

python3-yaml
python3-json
python3-httplib2
python3-flask	(for sams-post-receiver.py)

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
