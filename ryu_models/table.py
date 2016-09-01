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
        self.config_table = {}
        self.node = node
        self.endpoint = None

    def __repr__(self):
        return "<RYUTable: %s>" % self.id

    @property
    def id(self):
        return self.json['table_id']

    def _get_aggregate_stats(self):
        """
        Return a dict with the aggregate statistics when exists, if not return
        an empty dict
        """
        try:
            key = 'opendaylight-flow-statistics:aggregate-flow-statistics'
            return self.json[key]
        except KeyError:
            return {}

    def to_dict(self):
        config = self.get_flows().values()
        base = {self.id:
                {'flows': [flow.to_dict() for flow in config]}}
        return base

    def update(self):
        """
        Queries the server and retrieve a updated table.
        """
        ryu_instance = self.node.ryu_instance
        result = ryu_instance.get(self.endpoint)
        self.json = result['flow-node-inventory:table'][0]

        try:
            result = ryu_instance.get(self.config_endpoint)
            self.config_table = result['flow-node-inventory:table'][0]
        except RYU404 as e:
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
        try:
            filt = json.dumps({'table_id': self.id})
            flows = self.node.ryu_instance.post("/stats/flow/"+self.node.id, filt)
        except KeyError:
            return {}

        result = {}
        ind = 0
        for flow in flows.values()[0]:
            obj = RYUFlow(ind, flow, self)
            result[obj.id] = obj
            ind += 1
        return result

    def get_flow_by_id(self, id):
        """
        Return a flow from this table, based on id.
        """
        # For now, this is only used in config context.
        flows = self.get_config_flows()
        try:
            return flows[id]
        except KeyError:
            raise FlowNotFound("Flow id %s not found" % id)

    def get_flow_by_clean_id(self, clean_id):
        flows = self.get_config_flows()
        for flow in flows.values():
            if flow.clean_id == clean_id:
                return flow

        # Try to get in operational flows
        flows = self.get_operational_flows()
        for flow in flows.values():
            print flow.clean_id, clean_id
            if flow.clean_id == clean_id:
                return flow

    def get_config_flows_by_name(self, name):
        """
        Return a list of config flows based on name.
        """
        result = []
        flows = self.get_config_flows()
        for flow in flows.values():
            if flow.name == name:
                result.append(flow)

        return result

    def put_flow_from_data(self, data, flow):
        """
        Insert a flow in this table (config endpoint) based on raw json data.
        """
        ryu_instance = self.node.ryu_instance
        endpoint = self.config_endpoint + 'flow/' + str(flow.id)
        return ryu_instance.put(endpoint,
                                data=data,
                                content="application/json")

    def put_flow_from_template(self, filename, flow):
        """
        This methods reads a JSON jinja2 template and parse-it before sending to
        Ryu.
        """
        with open(filename, 'r') as f:
            template = Template(f.read())
            parsed = template.render(flow = flow)
            return self.put_flow_from_data(data = parsed,
                                           flow = flow)

    def l2output(self, flow_name, connector_id, source, destination, template_dir):
        """
        This methods insert a flow using source MAC address and destination MAC
        address as match fields.

        connector_id must be a valid ID of the node of this table.
        """
        tpl = os.path.join(template_dir, 'l2output.tpl')

        connector = self.node.get_connector_by_id(connector_id)

        flow = GenericFlow(name = flow_name, table = self)

        with open(tpl, 'r') as f:
            template = Template(f.read())
            parsed = template.render(flow = flow,
                                     source = source,
                                     destination = destination,
                                     connector = connector)

            return self.put_flow_from_data(data = parsed,
                                           flow = flow)

    def l3output(self, flow_name, connector_id, source, destination, template_dir):
        """
        This methods insert a flow using source address and destination address
        as match fields (both in ipv4).

        connector_id must be a valid ID of the node of this table.
        """
        tpl = os.path.join(template_dir, 'l3output.tpl')

        connector = self.node.get_connector_by_id(connector_id)

        flow = GenericFlow(name = flow_name, table = self)

        with open(tpl, 'r') as f:
            template = Template(f.read())
            parsed = template.render(flow = flow,
                                     source = source,
                                     destination = destination,
                                     connector = connector)

            return self.put_flow_from_data(data = parsed,
                                           flow = flow)

    def install_flow(self, priority, name, eth_type, eth_source,
                     eth_destination,  ipv4_source, ipv4_destination,
                     connector_id, template_dir):

        tpl = os.path.join(template_dir, 'complete.tpl')
        flow = GenericFlow(name = name,
                           table = self,
                           priority = priority)

        with open(tpl, 'r') as f:
            template = Template(f.read())
            parsed = template.render(flow = flow,
                                     eth_type = eth_type,
                                     eth_source = eth_source,
                                     eth_destination = eth_destination,
                                     ipv4_source = ipv4_source,
                                     ipv4_destination = ipv4_destination,
                                     connector_id = connector_id)

            print parsed
            return self.put_flow_from_data(data = parsed,
                                           flow = flow)

    def delete_low_priority_flows(self, priority = 100):
        """
        This method will delete all flows on this table (config endpoint), but
        only with low priority. Default is 100.
        """
        flows = self.get_config_flows()
        for flow in flows.values():
            if flow.priority <= priority:
                flow.delete()

    def delete_flows(self):
        """
        Delete all flows in this table (config endpoint).
        """
        flows = self.get_config_flows()
        for flow in flows.values():
           flow.delete()

