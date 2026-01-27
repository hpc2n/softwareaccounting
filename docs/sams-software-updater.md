# Software Updater

The *sams-software-updater* is run on the collecting machine and updates the software information in the database. The *software updater* uses two types of modules, the *updater* and the *backend*.

The updater module converts the path used in for the software into software information.

The backend module shows and updates software information from the backend.

If no options are provided to the software updater the database will be updated based on the updater module rules.

## Configuration

| Key | Description |
| - | - |
| backend | Name of the plugin that shows and updates software information. |
| updater | Name of the plugin that converts paths into software. |

Here is an example configuration file.

```
---
sams.software-updater:
  loglevel: ERROR

  backend: sams.backend.SoftwareAccounting
  updater: sams.software.Regexp

sams.backend.SoftwareAccounting:
  file_pattern: 'sa-\d+.db'
  db_path: /data/softwareaccounting/db

sams.software.Regexp:
  rules:
    - match: '^/usr/'
      software: system
      version: "/usr/"
      versionstr: ""
    - match: '^/scratch/'
      software: user
      version: "/scratch/"
      versionstr: ""
      user_provided: true
    - match: '^/tmp/'
      software: user
      version: "/tmp/"
      versionstr: ""
      user_provided: true
    - match: '^/(?P<path>s?bin)/'
      software: "system"
      version: "/%(path)s/"
      versionstr: ""
      ignore: true
    - match: '^/home/./(?P<username>[^/]+)/'
      software: "unclassified"
      version: ""
      versionstr: "%(username)s"
      user_provided: true
    - match: '^/cvmfs/ebsw/[^/]+/software/Core/(?P<software>[^/]+)/(?P<version>[^/]+)/'
      software: "%(software)s"
      version: "%(version)s"
      versionstr: "Core/%(software)s/%(version)s"
    - match: '^/cvmfs/ebsw/[^/]+/software/Compiler/(?P<vstr>[^/]+/[^/]+)/(?P<software>[^/]+)/(?P<version>[^/]+)'
      software: "%(software)s"
      version: "%(version)s"
      versionstr: "Core/%(vstr)s/%(software)s/%(version)s"
    - match: '^/cvmfs/ebsw/[^/]+/software/MPI/(?P<vstr>[^/]+/[^/]+/[^/]+/[^/]+)/(?P<software>[^/]+)/(?P<version>[^/]+)'
      software: "%(software)s"
      version: "%(version)s"
      versionstr: "MPI/%(vstr)s/%(software)s/%(version)s"
    - match: '^/cvmfs/ebsw/[^/]+/software/(?P<software>[^/]+)/(?P<version>[^/]+)'
      software: "%(software)s"
      version: "%(version)s"
      versionstr: "%(software)s/%(version)s"

  # Rewrite rules.
  rewrite:  
    # Catch all common types
    # Convert 1.2.3 => 1.2, 1.2-local-stuff => 1.2
    - match:
        software: '^.*$'
        version: '^(?P<newver>\d+\.\d+)[^\d]'
      update:
        version: '%(newver)s'
```
