"""
Saves core information about a job from the collector command line options.

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

Config options:

sams.sampler.Core:
    # in seconds
    sampler_interval: 100

Output:
{
    jobid: 0,
    node: 0,
}
"""

import logging

from typing import Dict

import sams.base

logger = logging.getLogger(__name__)


class Sampler(sams.base.Sampler):
    def __init__(self, id, outQueue, config):
        super(Sampler, self).__init__(id, outQueue, config)
        self.core = dict()

    def init(self) -> None:
        logger.debug('init()')
        self.core = dict(jobid=self.config.get(['options', 'jobid']),
                         node=self.config.get(['options', 'node']))
        self.store(self.core)
        self._most_recent_sample = self.storage_wrapper(self.core)

    def do_sample(self) -> bool:
        return False

    def sample(self) -> None:
        logger.debug('sample()')

    def final_data(self) -> Dict:
        return self.core
