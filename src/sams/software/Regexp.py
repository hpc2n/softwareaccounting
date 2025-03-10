"""
Matches a path using an regexp rule into a software

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


Config Options:

sams.software.Regexp:
    stop_on_rewrite_match: false
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
        # Must match all "match" to do update.
        - match:
            software: '(?P<software>)',
          update:
            version: '%(software)s'


"""

import logging
import re

import sams.base

logger = logging.getLogger(__name__)


class Software(sams.base.Software):
    """SAMS Software accounting aggregator"""

    def __init__(self, id, config):
        super(Software, self).__init__(id, config)
        self.rules = self.config.get([self.id, "rules"], [])
        self.rewrite = self.config.get([self.id, "rewrite"], [])
        self.stop_on_rewrite_match = self.config.get([self.id, "stop_on_rewrite_match"], False)

    @classmethod
    def _handle_rewrite(cls, software, rw):
        """Handle rewrite transformation"""
        input = dict(software)

        if "match" not in rw:
            logging.error("rewrite rule has no 'match' entry ignoring")
            return (software, False)

        if "update" not in rw:
            logging.error("rewrite rule has no 'update' entry ignoring")
            return (software, False)

        match = False
        for k in ["software", "version", "versionstr"]:
            if k in rw["match"]:
                reg = re.compile(rw["match"][k])
                m = reg.match(software[k])
                if not m:
                    return (software, False)
                input.update(m.groupdict())
                match = True

        # If no match don't update
        if not match:
            return (software, False)

        for k in ["software", "version", "versionstr"]:
            if k in rw["update"]:
                software[k] = rw["update"][k] % input

        return (software, True)

    def _handle_rewrites(self, software):
        """Handle rewrite transformations"""
        for rw in self.rewrite:
            (software, match) = self._handle_rewrite(software, rw)
            if match and self.stop_on_rewrite_match:
                break

        return software

    def _handle_rule(self, rule, path):
        """Handle rule transformation"""
        reg = re.compile(rule["match"])
        m = reg.match(path)
        if m:
            d = m.groupdict()
            up = False
            if "user_provided" in rule:
                up = rule["user_provided"]
            ig = False
            if "ignore" in rule:
                ig = rule["ignore"]
            return self._handle_rewrites(
                {
                    "software": rule["software"] % d,
                    "version": rule["version"] % d,
                    "versionstr": rule["versionstr"] % d,
                    "user_provided": up,
                    "ignore": ig,
                }
            )
        return None

    def get(self, path):
        """Information aggregate method"""

        for rule in self.rules:
            s = self._handle_rule(rule, path)
            if s:
                return s

        logging.info("Path not found: %s", path)

        return None
