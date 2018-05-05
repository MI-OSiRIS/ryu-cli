Setup for netdev workflow and re-production of Netsys paper.

# On Container running Openvswitch
- ssh onto the netsys 'router' container.
- attach to router
- ensure init script is configured correctly
- configure your ovs bridge as needed
- add two controllers to the ovs bridge, ensure controllers are pointing to right ports/IP in `ovs-vsctl show`
- check to make sure ovs-vsctl bridge has a system-id `ovs-vsctl get Open_vSwitch . external_ids:system-id
- if it does not, restart ovs-vsctl using this command `/usr/share/openvswitch/scripts/ovs-ctl --system-id=random --protocol=OpenFlow13


# On host controller location (netdev)
- enable port forwarding from host location to container running Openvswitch `ssh <container creds> -L <ovsdb port-number>:<Ip of container interface>:<ovsdb port-number> -N` eg - `ssh router -L 6650:10.0.3.42:6650 -N`
- start up this controller in one session of your host. `ryu-manager ryu.app.rest_qos ryu.app.rest_conf_switch --ofp-tcp-listen-port <your controller port> --wsapi-port 8081`. This controller runs the rest api's needed to talk to OVSDB.
- in another session start the simple switch controller on the other configured controller port to your OVS instance `ryu-manager ryu.app.simple_switch_13 --ofp-tcp-listen-port <your other controller port>`. It is important to keep this switch separate from the api controllers.
- in another ssh session, you may begin using the ryu-cli

# Notes on Ryu-Controller
- for Qos api endpoints you need to make sure that the rest\_qos and rest\_conf\_switch are both configured applications or else their services will not be available even after importing the modules
- for whatever reason, QoS and Conf module api services *will not work* if there is more than one ovs instance pointed at your controller

# Ryu-Cli configuration
- on start up tell the tool to listen to the exposed wsapi port defined when you start the controller in the `--wsapi-port` parameter. Eg - start using `python ryu-cli http://localhost:8081`
- the QoS switch-id is NOT the datapath id returned by calling `get_nodes` in the cli, you can find the correct switch id while actually inspecting what the id gets registered as in the Ryu Controller output when it gets registered with the QoS service (development task)
- first thing the controller needs to do is set the switch to listen to the right ovsdb port

# Important patch to make to Ryu 
- if you have LLDP frames going through your network and any flow whatsoever matches on them you need to perform this patch in the `ryu/app/rest_qos.py` source file - https://sourceforge.net/p/ryu/mailman/message/35795138/. If you dont do this the rest QoS will break every time an LLDP frame gets matched on.
