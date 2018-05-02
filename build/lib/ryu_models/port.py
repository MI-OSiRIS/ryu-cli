#!/usr/bin/env python
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# Authors:
#          - Beraldo Leal <beraldo AT ncc DOT unesp DOT br>
#
# Modified by:
#          - Ezra Kissel <ezkissel AT indiana DOT edu>
#
# -*- coding: utf-8 -*-
# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4

class RYUPort(object):
    """
    This class represents a port in Ryu
    """
    def __init__(self, ind, port, node):
        self.index = ind
        self.port = port
        self.node = node
        self.stats = {}

    def __repr__(self):
        return "<RYUPort: %s>" % self.id

    def to_dict(self):
        base = {self.id: {
            'status': self.status,
            'port_number': self.port_number,
            'hardware_address': self.hardware_address,
            'addresses': self.get_addresses(),
            'configuration': self.configuration,
            'name': self.name,
            'curr_speed': self.curr_speed,
            'stats': self.stats}}

        return base

    def update(self):
        self.stats = self.node.ryu_instance.get("/stats/port/"+str(self.node.id)+"/"+str(self.id))

    def get_port_stats(self):
        return self.stats

    @property
    def id(self):
        return self.index

    @property
    def status(self):
        try:
            return self.port['state']
        except KeyError:
            return None

    @property
    def port_number(self):
        return self.port['port_no']

    @property
    def hardware_address(self):
        return self.port['hw_addr']

    @property
    def name(self):
        return self.port['name']

    @property
    def curr_speed(self):
        return self.port['curr_speed']

    @property
    def configuration(self):
        return self.port['config']

    def get_addresses(self):
        return None
