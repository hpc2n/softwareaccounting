
= Contrib scripts

== sams-reporter.py

Script contributed from Thomas Svedberg, C3SE, Chalmers.

Script will output usage of software from the local database files.

== add-slurminfo.py

Add SlurmInfo to JSON files from sams-collector.

UPPMAX don't have the SlurmInfo sampler enabled on the collector. Our
users typically run large numbers of small jobs. We try to avoid Slurm
commands in Prolog/Epilog and similar as we have had performance
issues with the Slurm controller.

Normally it is best to use sams.loader.FileSlurmInfoFallback which
loads SlurmInfo from sacct when running sams-aggregator.

Some times it is useful to be able to do this step separately. For
example when having millions of record files. Or to test/debug the
FileSlurmInfoFallback loader separately.
