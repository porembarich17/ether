from string import Template
import networkx as nx
import os


from ether.topology import Topology
from ether.core import Node, Link, Connection, Route, NetworkNode

def ips_to_string(ip_list):
    ips = ""

    for ip in ip_list:
        ips += ip + ', '

    return ips[0:-2]


def create_output(topology):
    conf_template_interface = Template("[Interface]\nAddress = $interface_address \nPrivateKey = $interface_private ListenPort = $interface_port\n\n")
    conf_template_peer = Template("[Peer]\nPublicKey = $peer_public Endpoint = $peer_endpoint \nAllowedIPs = $peer_allowed \nPersistentKeepalive = $peer_persistent_keep_alive\n\n")

    links = [node for node in topology.nodes if isinstance(node, Link)]
    nodes = [node for node in topology.nodes if isinstance(node, Node)]

    #TODO: Create some type of IP-Pool to get adresses from (possible input as range)
    #TODO: Get latency to work somehow

    #create a list of key pairs for each node
    privateKeys = {}
    publicKeys = {}

    for l in links:
        #create rsa key pair for links
        privatekey = ""
        publickey = ""
        os.system("wg genkey | tee privatekey | wg pubkey > publickey")
        f = open("privatekey", "r")
        privatekey = f.read()
        f = open("publickey", "r")
        publickey = f.read()
        privateKeys.update({str(l.tags['name']): privatekey})
        publicKeys.update({str(l.tags['name']): publickey})

    for n in nodes:
        #create rsa key pair for nodes
        privatekey = ""
        publickey = ""
        os.system("wg genkey | tee privatekey | wg pubkey > publickey")
        f = open("privatekey", "r")
        privatekey = f.read()
        f = open("publickey", "r")
        publickey = f.read()
        print("-----" + str(privatekey))

        privateKeys.update({str(n): privatekey})
        publicKeys.update({str(n): publickey})

        #privateKeys.update({str(n): private_key})
        #publicKeys.update({str(n): public_key})



    edges = nx.edges(topology)

    for l in links:
        conf_temp = conf_template_interface.substitute(interface_address=str(l.ip_address), interface_private=privateKeys[str(l.tags['name'])], interface_port=str(1))
        print("Working on Link:")
        print(l)
        for e in edges:
            if (e[0] == l):
                print("to: " + str(e[1]))
                if(type(e[1]) is Node):
                    conf_temp += conf_template_peer.substitute(peer_public=publicKeys[str(e[1])], peer_endpoint=str(e[1]), peer_allowed=str(e[1]), peer_persistent_keep_alive=str(21))
                elif(type(e[1]) is Link):
                    conf_temp += conf_template_peer.substitute(peer_public=publicKeys[str(e[1].tags['name'])], peer_endpoint=str(e[1].ip_address), peer_allowed=ips_to_string(e[1].allowed_ip_range), peer_persistent_keep_alive=str(21))
            #elif (e[1] == l):
            #    print("from: " + str(e[0]))
            #    if(type(e[0]) is Node):
            #        conf_temp += conf_template_peer.substitute(peer_public=publicKeys[str(e[0])], peer_endpoint=str(e[0]), peer_allowed=str(e[0]), peer_persistent_keep_alive=str(21))
            #    elif(type(e[0]) is Link):
            #        conf_temp += conf_template_peer.substitute(peer_public=publicKeys[str(e[0].tags['name'])], peer_endpoint=str(e[0].ip_address), peer_allowed=ips_to_string(e[0].allowed_ip_range), peer_persistent_keep_alive=str(21))


        print(conf_temp)
        print("------------")



    for n in nodes:
        conf_temp = conf_template_interface.substitute(interface_address=str(n.ip_address), interface_private=privateKeys[str(n)], interface_port=str(1))
        print("Working on Node:")
        print(n)
        for e in edges:
            if (e[0] == n):
                print("to: " + str(e[1]))
                if(type(e[1]) is Node):
                    conf_temp += conf_template_peer.substitute(peer_public=publicKeys[str(e[1])], peer_endpoint=str(e[1]), peer_allowed=str(e[1]), peer_persistent_keep_alive=str(21))
                elif(type(e[1]) is Link):
                    conf_temp += conf_template_peer.substitute(peer_public=publicKeys[str(e[1].tags['name'])], peer_endpoint=str(e[1].ip_address), peer_allowed=ips_to_string(e[1].allowed_ip_range), peer_persistent_keep_alive=str(21))
            #elif (e[1] == n):
            #    print("from: " + str(e[0]))
            #    if(type(e[0]) is Node):
            #        conf_temp += conf_template_peer.substitute(peer_public=publicKeys[str(e[0])], peer_endpoint=str(e[0]), peer_allowed=str(e[0]), peer_persistent_keep_alive=str(21))
            #    elif(type(e[0]) is Link):
            #        conf_temp += conf_template_peer.substitute(peer_public=publicKeys[str(e[0].tags['name'])], peer_endpoint=str(e[0].ip_address), peer_allowed=ips_to_string(e[0].allowed_ip_range), peer_persistent_keep_alive=str(21))

        print(conf_temp)
        print("------------")


    #return null

