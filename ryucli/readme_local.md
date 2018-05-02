Setup for dev workflow:

# On Container running Openvswitch
- ssh onto the netsys 'router' container.
- attach to router
- ensure init script is configured correctly
- ensure controller is pointing to right port/IP in `ovs-vsctl show`
- check to make sure ovs-vsctl bridge has a system-id `ovs-vsctl get Open_vSwitch . external_ids:system-id
- if it does not, restart ovs-vsctl using this command `/usr/share/openvswitch/scripts/ovs-ctl --system-id=randoom --protocol=OpenFlow13

# On host controller location (netdev)
- enable port forwarding from host location to container running Openvswitch `ssh <container creds> -L <ovsdb port-number>:<Ip of container interface>:<ovsdb port-number> -N` eg - `ssh router -L 6650:10.0.3.42:6650 -N`
- start up the controller on the host. Eg - `ryu-manager osiris_main.py --ofp-tcp-listen-port 7000 --wsapi-port 8081 --verbose --install-lldp-flow --observe-links`
- in another ssh session, you may begin using the ryu-cli

# Notes on Ryu-Controller
- for Qos api endpoints you need to make sure that the rest_qos and rest_conf_switch are both configured applications or else their services will not be available even after importing the modules
- for whatever reason, QoS and Conf module api services *will not work* if there is more than one ovs instance pointed at your controller

# Ryu-Cli configuration
- on start up tell the tool to listen to the exposed wsapi port defined when you start the controller in the `--wsapi-port` parameter. Eg - start using `python ryu-cli http://localhost:8081`
- the QoS switch-id is NOT the datapath id returned by calling `get_nodes` in the cli, you can find the correct switch id while actually inspecting what the id gets registered as in the Ryu Controller output when it gets registered with the QoS service (development task)
- first thing the controller needs to do is set the switch to listen to the right ovsdb port

# Important patch to make to Ryu 
do this -
https://sourceforge.net/p/ryu/mailman/message/35795138/
