
# sams.output.Http

Posts output using web service.

Can use both basic auth and client cert for auth.

# Config options

## uri

uri to write to.
Available data for replace is: jobid, node & jobid_hash

## jobid_hash_size

"Hash" the output based on --jobid / jobid_hash_size

## key_file

If set using the following key for client cert auth

## cert_file

If set using the following cert for client cert auth

## username

If set using the folloing usernameas basic auth

## password

If set using the folloing password as basic auth

## exclude

List of sampler modules to skip.

# Example configuration


> sams.output.Http:
>   # uri to write to.  
>   # Available data for replace is: jobid, node & jobid_hash
>   uri: "https://server.example.com:8443/%(jobid_hash)d/%(jobid)s.%(node)s.yaml"
> 
>   # "Hash" the output based on --jobid / jobid_hash_size
>   jobid_hash_size: 1000
> 
>   # if set using the following key/cert for client cert auth
>   key_file: /etc/certificates/sa.key.pem
>   cert_file: /etc/certificates/sa.cert.pem
> 
>   # if set using the folloing username/password as basic auth
>   username: 'sams'
>   password: 'topSecret!'
> 
>   # Skip the list of modules.
>   exclude: ['sams.sampler.ModuleName']
