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

from ryu_models.flow import RYUFlow
from ryu_models.node import RYUNode
from ryu_models.table import RYUTable

from ryu_models.exceptions import *

import json
import sys
import requests

class RYUInstance(object):
    def __init__(self, server, credentials):
        self.server = server
        self.credentials = credentials
        self.headers = { 'Content-type' : 'application/json' }
        self.json = {}
        self.nodes = {}

    def to_dict(self):
        # All switches nodes in dict format
        base = {'nodes': [ node.to_dict() for node in self.get_nodes().values() ]}
        return base

    def request(self, method, endpoint, auth, data=None, content=None):
        """
        Tries to connect to the endpoint using a given method
        PUT, GET or DELETE. Return the response code.
        """
        if content:
            headers = {'Content-type': content}
        else:
            headers = self.headers

        if method == "GET":
            try:
                response = requests.get(endpoint,
                                        headers = headers,
                                        auth = auth)
            except requests.exceptions.RequestException as e:
                raise RYUErrorOnGET(e)
        elif method == "POST":
            try:
                response = requests.post(endpoint,
                                        headers = headers,
                                        data = data,
                                        auth = auth)
            except requests.exceptions.RequestException as e:
                raise RYUErrorOnPOST(e)
        elif method == "PUT":
            try:
                response = requests.put(endpoint,
                                        headers = headers,
                                        data = data,
                                        auth = auth)
            except requests.exceptions.RequestException as e:
                raise RYUErrorOnPUT(e)
        elif method == "DELETE":
            try:
                response = requests.delete(endpoint,
                                           headers = headers,
                                           auth = auth)
            except requests.exceptions.RequestException as e:
                raise RYUErrorOnDELETE(e)
        else:
            raise NotImplemented("Method %s not implemented." % method)

        if response.status_code == 404:
            raise RYU404("Endpoint not found: %s" % endpoint)

        # Consider any status other than 2xx an error
        if not response.status_code // 100 == 2:
            raise UnexpectedResponse(format(response))
        
        return response

    def get(self, endpoint):
        """
        Requests a GET to endpoint and returns the json.
        """
        response = self.request(method = "GET",
                                endpoint = self.server + endpoint,
                                auth = self.credentials)
        return response.json()

    def post(self, endpoint, data, content="application/json"):
        """
        Requests a GET to endpoint and returns the json.
        """
        response = self.request(method = "POST",
                                endpoint = self.server + endpoint,
                                data = data,
                                auth = self.credentials)
        ret = None
        try:
            ret = response.json()
        except:
            pass
        return ret
    
    def put(self, endpoint, data, content="application/json"):
        """
        Sends data via PUT to endpoint.
        """
        response = self.request(method = "PUT",
                                endpoint = self.server + endpoint,
                                data = data,
                                auth = self.credentials,
                                content = content)

    def delete(self, endpoint):
        """
        Sends a DELETE to endpoint.
        """
        response = self.request(method = "DELETE",
                                endpoint = self.server + endpoint,
                                auth = self.credentials)

    def update(self):
        endpoint = "/stats/switches"
        try:
            switches = self.get(endpoint)
            for s in switches:
                sw = self.get("/stats/desc/"+str(s))
                self.json.update(sw)
                node = RYUNode(sw.keys()[0],
                               sw.values()[0], self)
                node.update()
                self.nodes[node.id] = node
        except RYU404:
            self.json = {}

    def get_nodes(self):
        self.update()
        return self.nodes

    def get_node_by_id(self, id):
        nodes = self.get_nodes()
        try:
            return nodes[id]
        except KeyError:
            raise NodeNotFound("Node %s not found" % id)
