from string import Template

from ether.topology import Topology
from ether.core import Node, Link, Connection, Route, NetworkNode

def create_output(topology):
    conf_template_interface = Template("[Interface]\nAddress = $interface_address \nPrivateKey = $interface_private \nListenPort = $interface_port")
    conf_template_peer = Template("[Peer]\nPublicKey = $peer_public \nEndpoint = $peer_endpoint \nAllowedIPs = $peer_allowed \nPersistentKeepalive = $peer_persistent_keep_alive")

    links = [node for node in topology.nodes if isinstance(node, Link)]

    for i in links:
        print(i)

    return null

