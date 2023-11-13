#!/usr/bin/env python3

"""Add SlurmInfo to collector files

Use FileSlurmInfoFallback loader to load JSON files from
sams-collector, add SlurmInfo from sacct and save the result in new
JSON files that can later be fed to sams-aggregator. Files in input
directory are removed.

add-slurminfo --in=/input/dir --out=/output/dir --error=/error/dir
"""

import logging
import sys
import tempfile
from argparse import ArgumentParser

import yaml

import sams.core

logger = logging.getLogger(__name__)

id = "add-slurminfo"

CONFIG = {
    "add-slurminfo": {"loader": "sams.loader.FileSlurmInfoFallback"},
    "sams.loader.FileSlurmInfoFallback": {
        "environment": {"TZ": "UTC"},
        "file_pattern": "^.*\\.json$",
    },
}


class Main:
    def __init__(self):
        self.loader = None

        # Options
        parser = ArgumentParser(
            prog="add-slurminfo",
            description="Add SlurmInfo to JSON files from sams-collector",
            epilog=(
                "New JSON files are created in 'out' dir with SlurmInfo added. "
                "Files in 'in'-dir is removed, or moved to 'error' dir if they "
                "could not be loaded."
            ),
        )
        parser.add_argument("--loglevel", default="ERROR")
        # dest= to avoid using keyword "in":
        parser.add_argument(
            "--in", help="Input directory", required=True, dest="in_dir"
        )
        parser.add_argument("--out", help="Output directory", required=True)
        parser.add_argument("--error", help="Error directory", required=True)
        args = parser.parse_args()

        # Add arguments to CONFIG
        for k, v in {
            "in_path": args.in_dir,
            "archive_path": args.out,
            "error_path": args.error,
        }.items():
            CONFIG["sams.loader.FileSlurmInfoFallback"][k] = v

        # Write CONFIG out to temporary config file, just so it can be loaded using sams.core.Config
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf8") as tmp:
            yaml.dump(CONFIG, tmp)
            tmp.flush()
            self.config = sams.core.Config(tmp.name, {})

        # Logging
        logging.basicConfig(
            format="%(asctime)s %(name)s:%(levelname)s %(message)s",
            level=logging.getLevelName(args.loglevel.upper()),
        )

        # Initialize loader
        l = self.config.get([id, "loader"], None)
        try:
            Loader = sams.core.ClassLoader.load(l, "Loader")
            self.loader = Loader(l, self.config)
        except Exception as e:
            logger.error("Failed to initialize: %s", l)
            logger.exception(e)
            sys.exit(1)

    def start(self):
        logger.debug("Start loading %s", self.loader)
        loader = self.loader
        loader.load()

        while True:
            try:
                data = loader.next()
                if not data:
                    break
                logger.debug("Data: %s", data)
                loader.commit()
            except Exception as e:
                logger.error(e)
                loader.error()
                continue


if __name__ == "__main__":
    Main().start()
