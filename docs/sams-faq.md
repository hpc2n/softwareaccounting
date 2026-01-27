# Frequently asked questions

## I have updated the config but all my old jobs are still wrong!

Only new paths are evaluated. Old paths needs to be reset using the --reset-path argument to sams-software-updater.

## How to I find the paths for a software?

Using the sams-software-updater script you can show all known paths for a software with the argument --show-software="software".

## Reset a lots of paths is hard work!

All --\*-path arguments to sams-software-updater can make use of the GLOB. "\*" and "?" can be used to find and reset path in bulk.

## How do I reset/resend all software?

Using the sams-software-updater program, you can reset all known paths with the argument --reset-path="\*".

Next time sams-software-updater is run all paths will be evaluated again and the sams-software-extractor will export all jobs again.

## How do I handle softwares run from user writable directory like /tmp?

Using %(user)s and/or %(project)s in local version will work well.

If used with the [*sams.software.Regexp*](software/Regexp.md) module you will have to write %%(user)s and %%(project)s to prevent Regexp module to try to replace them locally.
