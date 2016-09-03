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

from ryu_models.exceptions import RYU404, FlowNotFound

import re

class RYUFlow(object):
    """
    This class represents a flow in Ryu
    """
    def __init__(self, ind, json, table):
        self.index = str(ind)
        self.json = json
        self.table = table

    def __repr__(self):
        return "<RYUFlow: %s>" % self.id

    @property
    def id(self):
        return self.index

    @property
    def clean_id(self):
        return str(re.sub(r'#|\$|-|\*','', self.id))

    @property
    def priority(self):
        return self.json['priority']

    @property
    def idle_timeout(self):
        try:
            return self.json['idle_timeout']
        except KeyError:
            return {}

    @property
    def name(self):
        try:
            return self.json['name']
        except KeyError:
            return self.id

    @property
    def hard_timeout(self):
        try:
            return self.json['hard_timeout']
        except KeyError:
            return {}

    @property
    def cookie(self):
        try:
            return self.json['cookie']
        except KeyError:
            return {}

    def _get_match(self):
        """
        Return the match fields of this flow.
        """
        try:
            return self.json['match']
        except KeyError:
            return {}

    def get_ethernet_type(self):
        ethernet_match = self._get_match()
        try:
            return ethernet_match['eth_type']
        except KeyError:
            return "*"

    def get_ethernet_source(self):
        ethernet_match = self._get_match()
        try:
            return ethernet_match['eth_src']
        except KeyError:
            return "*"

    def get_ethernet_destination(self):
        ethernet_match = self._get_match()
        try:
            return ethernet_match['eth_dst']
        except KeyError:
            return "*"

    def get_ipv4_source(self):
        match = self._get_match()
        try:
            return match['ipv4_src']
        except KeyError:
            return "*"

    def get_ipv4_destination(self):
        match = self._get_match()
        try:
            return match['ipv4_dst']
        except KeyError:
            return "*"

    def get_actions(self):
        try:
            actions = self.json['actions']
        except KeyError as e:
            actions = []
        return actions

    def to_dict(self):
        base = {self.id: {'priority': self.priority,
                          'idle_timeout': self.idle_timeout,
                          'hard_timeout': self.hard_timeout,
                          'cookie': self.cookie,
                          'name': self.name,
                          'id': self.id,
                          'node_id': self.table.node.id,
                          'table_id': self.table.id,
                          'clean_id': self.clean_id,
                          'match': self._get_match(),
                          'ethernet_match': {'type': self.get_ethernet_type(),
                                             'source': self.get_ethernet_source(),
                                             'destination': self.get_ethernet_destination()},
                          'ipv4_source': self.get_ipv4_source(),
                          'ipv4_destination': self.get_ipv4_destination(),
                          'actions': self.get_actions(),
                          'stats': {'bytes': self.get_byte_count(),
                                    'packets': self.get_packet_count()}}}
        return base

    def get_long_id(self):
        """
        Return a long ID number.
        """
        return "%s-%s-%s-%s-%s-%s" % (self.table.node.id,
                                      self.table.id,
                                      self.id,
                                      self.priority,
                                      self.idle_timeout,
                                      self.hard_timeout)

    def get_stats_seconds(self):
        """
        Return the number of seconds in flow stats.
        """
        try:
            return self.json['duration_sec']
        except KeyError:
            return 0

    def get_byte_count(self):
        """
        Return the number of bytes that matches with this flow.
        """
        try:
            return self.json['byte_count']
        except KeyError:
            return None

    def get_packet_count(self):
        """
        Return the number of packets that matches with this flow.
        """
        try:
            return self.json['packet_count']
        except KeyError:
            return None

    def delete(self):
        """
        Delete a specific flow
        """
        ryu_instance = self.table.node.ryu_instance
        endpoint = '/stats/flowentry/delete_strict'
        data = json.dumps(self.json)
        try:
            ryu_instance.post(endpoint,
                              data=data,
                              content="application/json")
        except RYU404:
            raise FlowNotFound("Flow %s not found" % self.id)

