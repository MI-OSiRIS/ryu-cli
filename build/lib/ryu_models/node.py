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

from ryu_models.port import RYUPort
from ryu_models.table import RYUTable
from ryu_models.exceptions import TableNotFound, PortNotFound

class RYUNode(object):
    """
    This class represents a node (or a switch) in Ryu
    """
    def __init__(self, ind, json, ryu_instance):
        self.index = ind
        self.json = json
        self.tables = {}
        self.ports = {}
        self.ryu_instance = ryu_instance

    def __repr__(self):
        return "<RYUNode: %s>" % self.id

    @property
    def id(self):
        return self.index

    @property
    def description(self):
        try:
            return self.json['dp_desc']
        except KeyError as e:
            return None

    @property
    def ip_address(self):
        try:
            return self.json['ip_addr']
        except KeyError as e:
            return None

    @property
    def manufacturer(self):
        try:
            return self.json['mfr_desc']
        except KeyError as e:
            return None

    @property
    def serial_number(self):
        return self.json['serial_num']

    @property
    def hardware(self):
        try:
            return self.json['hw_desc']
        except KeyError as e:
            return None

    @property
    def software(self):
        try:
            return self.json['sw_desc']
        except KeyError as e:
            return None

    def to_dict(self):
        tables = self.get_tables().values()
        ports = self.get_ports().values()
        base = {self.id: {
                'description': self.description,
                'ip_address': self.ip_address,
                'manufacturer': self.manufacturer,
                'hardware': self.hardware,
                'software': self.software,
                'tables': [ table.to_dict() for table in tables],
                'ports': [ port.to_dict() for port in ports]}}

        return base

    def update(self):
        """
        Update this Node's tables and ports
        """
        tables = self.ryu_instance.get("/stats/table/"+self.id)
        for table in list(tables.values())[0]:
            obj = RYUTable(None, table, self)
            obj.update()
            self.tables[obj.id] = obj

        ports = self.ryu_instance.get("/stats/portdesc/"+self.id)
        ind = 0
        for port in list(ports.values())[0]:
            obj = RYUPort(ind, port, self)
            self.ports[obj.id] = obj
            ind += 1

    def get_tables(self):
        """
        Return a dict with all tables of this node.
        """
        return self.tables

    def get_table_by_id(self, id):
        """
        Return a table based on id.
        """
        tables = self.get_tables()
        try:
            return tables[int(id)]
        except KeyError:
            raise TableNotFound("Table %s not found" % id)

    def get_ports(self):
        """
        Return a dict with all ports of this node.
        """
        return self.ports

    def get_port_by_id(self, id):
        """
        Return a port based on id.
        """
        ports = self.get_ports()
        try:
            return ports[id]
        except KeyError:
            raise PortNotFound("Port %s not found" % id)

    def clear_flows(self):
        """
        Delete all flows in this datapath 
        """
        endpoint = '/stats/flowentry/clear'+node.id
        return ryu_instance.delete(endpoint,
                                   content="application/json")

        pass

    def add_flow(self, flow):
        pass

