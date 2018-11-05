
# sams.software.Regexp

Matches a path using an regexp rule into a software.

# Config options

## rules

An list of regexp rules that are matched into an software defition.

### rule

A rule consits of the following parts.

#### match

An regexp to match the input path name.

The ''(?P<name>)'' construct can be used to transport matches into software/version/versionstr
with an ''%(name)s''.

#### software

Name of the software that matches the ''match''.

#### version

Version of the software that matches the ''match''.

This should be the major version of the software.

#### versionstr

Version string of the software that matches the ''match''.

This can be the complete version with local patches etc.

#### user_provided (true/false)

This software is installed by the user and not provided via the system/site.

#### ignore (true/false)

This software should be ignored for some reason in future calculations.

# Example configuration

> sams.software.Regexp:
>     rules:
>         # Things matched in "match" can used in software, version and versionstr to update
>         # the items.
>         - match: '^/pfs/software/eb/[^/]+/software/Core/(?P<software>[^/]+)/(?P<version>[^/]+)/'
>           software: "%(software)s"
>           version: "%(version)s"
>           versionstr: "Core/%(software)s/%(version)s"
>           user_provided: true
>           ignore: false
> 
