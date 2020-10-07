# FAQ

## Python 2 or Python 3?

Python 2 should work but we have seen strange behaviour on some systems using Python 2.

Python 3 is recommended.

## I have updated the config but all my old jobs are still wrong!

Only new paths are evaulated. Old paths needs to be reseted using the --reset-path argument
to ''sams-software-updater''

## How to I find the paths for a software?

Using the ''sams-software-updater'' script you can show all known paths for a software
with the argument --show-software="software".

## Reset a lots of paths is hard work!

All --*-path arguments to ''sams-software-updater'' can make use of the GLOB.
"*" and "?" can be used to find and reset path in bulk.

## How do I reset/resend all software?

Using the ''sams-software-updater'' script you can reset all known paths with the
argument --reset-path="*".

Next time ''sams-software-updater'' is run all paths will be evaluated again and
the ''sams-software-extractor'' will export all jobs again.


