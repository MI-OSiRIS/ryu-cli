# README

This project contains a CLI utility that allows one to navigate the Ryu of_ctl REST API
and its returned JSON dictionaries in a manner similar to a *NIX filesystem.

The CLI makes use of a refactored python-odl module available at
https://github.com/SPRACE/python-odl


## Example Usage

```
$ ryu-cli http://localhost:8081
Server: http://localhost:8081
User  : admin
Passwd: admin
ryu-cli> get_nodes
OK
ryu-cli> ls
openflow:223189291260227: ("dev", "None", "Nicira, Inc.")
controller-config: ("None", "None", "None")
ryu-cli> cd openflow:223189291260227
ryu-cli> ls
tables
description: None
hardware: Open vSwitch
connectors
manufacturer: Nicira, Inc.
ip_address: 192.168.1.30
software: 2.1.0
ryu-cli> 
EOF        add_flow   cd         del_flow   get_nodes  get_topo   help       ls         lsd        pwd        update     
ryu-cli> 
```
