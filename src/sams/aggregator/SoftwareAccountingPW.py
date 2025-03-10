"""
Software accounting storage "aggregator" for merging data into database

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

sams.aggregator.SoftwareAccountingPW:
    # Configuration is the same as
    #   sams.backend.SoftwareAccountingPW

"""

import logging

import sams.base
from sams.backend.SoftwareAccountingPW import Backend

logger = logging.getLogger(__name__)


class Aggregator(Backend, sams.base.Aggregator):
    """SAMS Software accounting aggregator"""
