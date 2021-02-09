
# sams.software.Regexp

Matches a path using an regexp rule into a software.

# Config options

## stop_on_rewrite_match

Break rewrite rules if match is found.

Default: false

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

## rewrite

Rewrite rules can be used to fine tune names and/or versions of a software and
all rules will be applied after each match i the order of appearens in the config file.

### rewrite rule

A rewrite rule consists of the following parts.

#### match

The 'match' element can have one or more of the following keys: 'software', 'version', 'versionstr'.

The keys are regexps that can have named groups that can be used in the update section (see below).

Named groups are the same constructs used in the match rules (see above).

#### update

The 'update' element have one or more of the following keys: 'software', 'version', 'versionstr' that will update the software object with the value of the update keys.

The ''%(name)s'' construct can be used. Valid names are matches from the 'match' element and the input strings.

# Example configuration

```
sams.software.Regexp:
    rules:
        # Things matched in "match" can used in software, version and versionstr to update
        # the items.
        - match: '^/pfs/software/eb/[^/]+/software/Core/(?P<software>[^/]+)/(?P<version>[^/]+)/'
          software: "%(software)s"
          version: "%(version)s"
          versionstr: "Core/%(software)s/%(version)s"
          user_provided: true
          ignore: false

    rewrite:
        - match:
            software: '^VASP$'
            version: '^(?P<newver>\d+\.\d+)'
          update:
            version: '%(newver)s'
```
