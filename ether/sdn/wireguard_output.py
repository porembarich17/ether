from string import Template
import networkx as nx

from ether.topology import Topology
from ether.core import Node, Link, Connection, Route, NetworkNode

def create_output(topology):
    conf_template_interface = Template("[Interface]\nAddress = $interface_address \nPrivateKey = $interface_private \nListenPort = $interface_port\n\n")
    conf_template_peer = Template("[Peer]\nPublicKey = $peer_public \nEndpoint = $peer_endpoint \nAllowedIPs = $peer_allowed \nPersistentKeepalive = $peer_persistent_keep_alive\n\n")

    links = [node for node in topology.nodes if isinstance(node, Link)]
    nodes = [node for node in topology.nodes if isinstance(node, Node)]

    #TODO: Get all connections to check on clusters (Cells)
    #TODO: Create some type of IP-Pool to get adresses from (possible input as range)
    #TODO: Iterate all nodes and create one config each containing all connected nodes it can interact with
    #TODO: Get latency to work somehow

    edges = nx.edges(topology)

    for l in links:
        conf_temp = conf_template_interface.substitute(interface_address=str(l), interface_private=str(l), interface_port=str(1))
        print("Working on Link:")
        print(l)
        for e in edges:
            if (e[0] == l):
                print("to: " + str(e[1]))
                conf_temp += conf_template_peer.substitute(peer_public=str(e[1]), peer_endpoint=str(e[1]), peer_allowed=str(e[1]), peer_persistent_keep_alive=str(21))
            elif (e[1] == l):
                print("from: " + str(e[0]))
                conf_temp += conf_template_peer.substitute(peer_public=str(e[1]), peer_endpoint=str(e[1]), peer_allowed=str(e[1]), peer_persistent_keep_alive=str(21))

        print(conf_temp)
        print("------------")



    for n in nodes:
        conf_temp = conf_template_interface.substitute(interface_address=str(n), interface_private=str(n), interface_port=str(1))
        print("Working on Node:")
        print(n)
        for e in edges:
            if (e[0] == n):
                print("to: " + str(e[1]))
                conf_temp += conf_template_peer.substitute(peer_public=str(e[1]), peer_endpoint=str(e[1]), peer_allowed=str(e[1]), peer_persistent_keep_alive=str(21))
            elif (e[1] == n):
                print("from: " + str(e[0]))
                conf_temp += conf_template_peer.substitute(peer_public=str(e[0]), peer_endpoint=str(e[0]), peer_allowed=str(e[0]), peer_persistent_keep_alive=str(21))

        print(conf_temp)
        print("------------")

    #return null

