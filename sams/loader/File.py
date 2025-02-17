"""
File Loader

SAMS Software accounting
Copyright (C) 2018-2021  Swedish National Infrastructure for Computing (SNIC)

This program is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License
as published by the Free Software Foundation; either version 2
of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; If not, see <http://www.gnu.org/licenses/>.
"""

import json
import logging
import os
import re
import shutil

import sams.base

logger = logging.getLogger(__name__)


class Loader(sams.base.Loader):
    def __init__(self, id, config):
        super(Loader, self).__init__(id, config)
        self.in_path = self.config.get([self.id, "in_path"])
        self.archive_path = self.config.get([self.id, "archive_path"])
        self.error_path = self.config.get([self.id, "error_path"])
        self.file_pattern = re.compile(self.config.get([self.id, "file_pattern"], "^.*$"))
        self.files = []
        self.current_file = None

    def load(self):
        """Find files in in_path matching file_pattern"""
        for root, _, files in os.walk(self.in_path):
            for file in files:
                logger.debug("Found file: %s", file)
                if self.file_pattern.match(file):
                    logger.debug("Add %s to files[]", os.path.join(root, file))
                    self.files.append({"file": file, "path": os.path.relpath(root, self.in_path)})

    def next(self):
        if len(self.files) == 0:
            return None
        self.current_file = self.files[0]
        self.files = self.files[1:]
        logger.debug(self.current_file)
        filename = os.path.join(self.in_path, self.current_file["path"], self.current_file["file"])
        try:
            with open(filename, "r") as file:
                return json.load(file)
        except Exception as e:
            raise Exception("Failed to load: %s due to %s" % (filename, str(e))) from e
        return None

    def error(self):
        """move file from in_path -> error_path/"""
        logger.info(
            "Error: %s",
            os.path.join(self.current_file["path"], self.current_file["file"]),
        )

        out_path = os.path.join(self.error_path, self.current_file["path"])
        if not os.path.isdir(out_path):
            try:
                os.makedirs(out_path)
            except Exception:
                # Handle possible raise from other process
                if not os.path.isdir(out_path):
                    assert False, "Failed to makedirs '%s' " % out_path

        # Rename file to error directory
        shutil.move(
            os.path.join(self.in_path, self.current_file["path"], self.current_file["file"]),
            os.path.join(out_path, self.current_file["file"]),
        )

        self.current_file = None

    def commit(self):
        """move file from in_path -> archive_path/"""
        logger.info(
            "Commit: %s",
            os.path.join(self.current_file["path"], self.current_file["file"]),
        )

        out_path = os.path.join(self.archive_path, self.current_file["path"])
        if not os.path.isdir(out_path):
            try:
                os.makedirs(out_path)
            except Exception:
                # Handle possible raise from other process
                if not os.path.isdir(out_path):
                    assert False, "Failed to makedirs '%s' " % out_path

        # Rename file to archive directory
        shutil.move(
            os.path.join(self.in_path, self.current_file["path"], self.current_file["file"]),
            os.path.join(out_path, self.current_file["file"]),
        )

        self.current_file = None
