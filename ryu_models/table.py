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
#          - Artur Baruchi <abaruchi AT ncc DOT unesp DOT br>
#
# Modified by:
#          - Ezra Kissel <ezkissel AT indiana DOT edu>
#
# -*- coding: utf-8 -*-
# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4

from ryu_models.flow import RYUFlow
from ryu_models.exceptions import RYU404, FlowNotFound
from jinja2 import Template

import json
import os

import uuid

class GenericFlow(object):
    """
    This class represents a generic Flow (not related to Ryu).
    In the context of this library, this is a flow before be installed on Ryu.
    So first you should create object of this class and after that send to Ryu.
    """
    
    def __init__(self, name, table, priority = 100):
        self.id = "%s" % uuid.uuid1()
        self.name = name
        self.table = table
        self.hard_timeout = 0
        self.idle_timeout = 0
        self.cookie = 10
        self.priority = priority


class RYUTable(object):
    """
    This class represents a switch table in Ryu
    """
    def __init__(self, ind, json, node):
        self.json = json
        self.flows = {}
        self.node = node
        self.endpoint = None

    def __repr__(self):
        return "<RYUTable: %s>" % self.id

    @property
    def id(self):
        return self.json['table_id']

    def to_dict(self):
        config = self.get_flows().values()
        base = {self.id:
                {'flows': [flow.to_dict() for flow in config]}}
        return base

    def update(self):
        """
        Queries the server and retrieve a updated table.
        """
        try:
            filt = json.dumps({'table_id': self.id})
            self.flows = self.node.ryu_instance.post("/stats/flow/"+self.node.id, filt)
        except KeyError:
            pass

    def get_aggregate_byte(self):
        """
        Return the number of aggregate byte count for a table
        """
        stats = self._get_aggregate_stats()
        try:
            return stats['byte-count']
        except KeyError:
            return None

    def get_aggregate_packets(self):
        """
        Returns the number of aggregate packets for a table
        """
        stats = self._get_aggregate_stats()
        try:
            return stats['packet-count']
        except KeyError:
            return None

    def get_flows(self):
        """
        Return a dict with all flows in config endpoint (in this table).
        """
        result = {}
        ind = 0
        for flow in self.flows.values()[0]:
            obj = RYUFlow(ind, flow, self)
            result[obj.id] = obj
            ind += 1
        return result

    def post_flow_from_data(self, data, flow):
        """
        Insert a flow in this table (config endpoint) based on raw json data.
        """
        ryu_instance = self.node.ryu_instance
        endpoint = '/stats/flowentry/add'
        return ryu_instance.put(endpoint,
                                data=data,
                                content="application/json")

    def put_flow_from_data(self, data, flow):
        """
        Insert a flow in this table (config endpoint) based on raw json data.
        """
        ryu_instance = self.node.ryu_instance
        endpoint = '/stats/flowentry/add'
        return ryu_instance.put(endpoint,
                                data=data,
                                content="application/json")

    def delete_low_priority_flows(self, priority = 100):
        """
        This method will delete all flows on this table (config endpoint), but
        only with low priority. Default is 100.
        """
        flows = self.get_flows()
        for flow in flows.values():
            if flow.priority <= priority:
                flow.delete()

    def get_flow_by_id(self, id):
        """
        Return a flow based on id.
        """
        flows = self.get_flows()
        try:
            return flows[id]
        except KeyError:
            raise FlowNotFound("Flow %s not found" % id)

    def delete_flows(self):
        """
        Delete all flows in this table (config endpoint).
        """
        ryu_instance = self.node.ryu_instance
        endpoint = '/stats/flowentry/delete'
        data = json.dumps({'dpid': self.node.id,
                           'table_id': self.id})
        print data
        return ryu_instance.post(endpoint,
                                 data=data,
                                 content="application/json")


