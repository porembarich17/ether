from string import Template
import networkx as nx
import os
import subprocess

from ether.topology import Topology
from ether.core import Node, Link, Connection, Route, NetworkNode

def ips_to_string(ip_list):
    ips = ""

    for ip in ip_list:
        ips += ip + ', '

    return ips[0:-2]


def create_output(topology):
    conf_template_interface = Template("[Interface]\nAddress = $interface_address \nPrivateKey = $interface_private ListenPort = $interface_port\n\n")
    conf_template_peer_link = Template("[Peer]\nPublicKey = $peer_public Endpoint = $peer_endpoint \nAllowedIPs = $peer_allowed \nPersistentKeepalive = $peer_persistent_keep_alive\n\n")
    conf_template_peer_node = Template("[Peer]\nPublicKey = $peer_public Endpoint = $peer_endpoint \nPersistentKeepalive = $peer_persistent_keep_alive\n\n")

    links = [node for node in topology.nodes if isinstance(node, Link)]
    nodes = [node for node in topology.nodes if isinstance(node, Node)]

    devices_user = "pirate"
    devices_pswd = "hypriot"


    #TODO: Create some type of IP-Pool to get adresses from (possible input as range)
    #TODO: Get latency to work somehow (Linux TC via command line)
    #TODO: distribute each configuration via scp/ssh on nodes with matching IP addresses (also rollback)

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



    edges = nx.edges(topology)

    for l in links:
        conf_temp = conf_template_interface.substitute(interface_address=str(l.ip_address), interface_private=privateKeys[str(l.tags['name'])], interface_port=str(51820))
        print("Working on Link:")
        print(l)
        for e in edges:
            if (e[0] == l):
                print("to: " + str(e[1]))
                if(type(e[1]) is Node):
                    conf_temp += conf_template_peer_link.substitute(peer_public=publicKeys[str(e[1])], peer_endpoint=str(e[1].ip_address) + ":51820", peer_allowed=ips_to_string(l.allowed_ip_range), peer_persistent_keep_alive=str(21))
                elif(type(e[1]) is Link):
                    conf_temp += conf_template_peer_link.substitute(peer_public=publicKeys[str(e[1])], peer_endpoint=str(e[1].ip_address) + ":51820", peer_allowed=ips_to_string(e[1].allowed_ip_range), peer_persistent_keep_alive=str(21))

        conf_temp = conf_temp.replace(" Endpoint", "Endpoint")
        conf_temp = conf_temp.replace(" ListenPort", "ListenPort")

        f = open("wg0.conf", "w")
        f.write(conf_temp)
        f.close()

        command = "ssh -tt -i ~/.ssh/id_rsa.pub pirate@" + l.ip_address
        args = command.split(' ')
        sshProcess = subprocess.Popen(args, stdin=subprocess.PIPE,
                                     stdout = subprocess.PIPE,
                                     universal_newlines=True,
                                     bufsize=0)

        sshProcess.stdin.write("cd ~/../../etc/wireguard \n")
        sshProcess.stdin.write("wg-quick down wg0 \n")
        sshProcess.stdin.write("cp wg0.conf wg_tmp.conf \n")
        sshProcess.stdin.write("exit\n")
        sshProcess.stdin.close()
        sshProcess.wait()

        os.system("scp wg0.conf pirate@" + l.ip_address + ":~/../../etc/wireguard/")

        sshProcess = subprocess.Popen(args, stdin=subprocess.PIPE,
                                             stdout = subprocess.PIPE,
                                             universal_newlines=True,
                                             bufsize=0)

        sshProcess.stdin.write("cd ~/../../etc/wireguard \n")
        sshProcess.stdin.write("wg-quick up wg0 \n")
        sshProcess.stdin.write("exit\n")
        sshProcess.stdin.close()
        sshProcess.wait()

        print(conf_temp)
        print("------------")



    for n in nodes:
        conf_temp = conf_template_interface.substitute(interface_address=str(n.ip_address), interface_private=privateKeys[str(n)], interface_port=str(51820))
        print("Working on Node:")
        print(n)
        for e in edges:
            if (e[0] == n):
                print("to: " + str(e[1]))
                if(type(e[1]) is Node):
                    conf_temp += conf_template_peer_node.substitute(peer_public=publicKeys[str(e[1])], peer_endpoint=str(e[1]) + ":51820", peer_persistent_keep_alive=str(21))
                elif(type(e[1]) is Link):
                    conf_temp += conf_template_peer_link.substitute(peer_public=publicKeys[str(e[1].tags['name'])], peer_endpoint=str("192.168.0.220:51820"), peer_allowed=ips_to_string(e[1].allowed_ip_range), peer_persistent_keep_alive=str(21))

        conf_temp = conf_temp.replace(" Endpoint", "Endpoint")
        conf_temp = conf_temp.replace(" ListenPort", "ListenPort")

        f = open("wg0.conf", "w")
        f.write(conf_temp)
        f.close()

        command = "ssh -tt -i ~/.ssh/id_rsa.pub pirate@" + n.ip_address
        args = command.split(' ')
        sshProcess = subprocess.Popen(args, stdin=subprocess.PIPE,
                                     stdout = subprocess.PIPE,
                                     universal_newlines=True,
                                     bufsize=0)

        sshProcess.stdin.write("cd ~/../../etc/wireguard \n")
        sshProcess.stdin.write("wg-quick down wg0 \n")
        sshProcess.stdin.write("cp wg0.conf wg_tmp.conf \n")
        sshProcess.stdin.write("exit\n")
        sshProcess.stdin.close()
        sshProcess.wait()

        os.system("scp wg0.conf pirate@" + n.ip_address + ":~/../../etc/wireguard/")

        sshProcess = subprocess.Popen(args, stdin=subprocess.PIPE,
                                             stdout = subprocess.PIPE,
                                             universal_newlines=True,
                                             bufsize=0)

        sshProcess.stdin.write("cd ~/../../etc/wireguard \n")
        sshProcess.stdin.write("wg-quick up wg0 \n")
        sshProcess.stdin.write("exit\n")
        sshProcess.stdin.close()
        sshProcess.wait()


        print(conf_temp)
        print("------------")


    #return null

