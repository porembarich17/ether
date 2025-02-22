from string import Template
import networkx as nx
import os
import subprocess

from ether.topology import Topology
from ether.core import Node, WgRouter, Connection, Route, NetworkNode

def ips_to_string(ip_list, ip_list_default=None):
    ips = ""

    for ip in ip_list:
        ips += ip + ', '

    print(ip_list_default)

    if ip_list_default != None:
        for ip in ip_list_default:
                ips += ip + ', '

    return ips[0:-2]


def create_output(topology, dry_run = False):
    conf_template_interface = Template("[Interface]\nAddress = $interface_address \nPrivateKey = $interface_private ListenPort = $interface_port\n\n")
    conf_template_interface_link = Template("[Interface]\nAddress = $interface_address \nPrivateKey = $interface_private PostUp = iptables -A FORWARD -i wg0 -j ACCEPT; iptables -A FORWARD -o wg0 -j ACCEPT; iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE \nPostDown = iptables -D FORWARD -i wg0 -j ACCEPT; iptables -D FORWARD -o wg0 -j ACCEPT; iptables -t nat -D POSTROUTING -o eth0 -j MASQUERADE \nListenPort = $interface_port\n\n")
    conf_template_peer_link = Template("[Peer]\nPublicKey = $peer_public Endpoint = $peer_endpoint \nAllowedIPs = $peer_allowed \nPersistentKeepalive = $peer_persistent_keep_alive\n\n")
    conf_template_peer_node = Template("[Peer]\nPublicKey = $peer_public Endpoint = $peer_endpoint \nPersistentKeepalive = $peer_persistent_keep_alive\n\n")

    links = [node for node in topology.nodes if isinstance(node, WgRouter)]
    nodes = [node for node in topology.nodes if isinstance(node, Node)]

    devices_user = "pirate"
    devices_pswd = "hypriot"

    #TODO: Get latency to work somehow (Linux TC via command line)
    #TODO: Rollback

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
        conf_temp = conf_template_interface_link.substitute(interface_address=str(l.virtual_ip_address) + "/32", interface_private=privateKeys[str(l.tags['name'])], interface_port=str(51820))
        print("Working on WgRouter:")
        print(l)
        latency = {}

        for e in edges:
            if (e[0] == l):
                print("to: " + str(e[1]))
                if(type(e[1]) is Node):
                    conf_temp += conf_template_peer_link.substitute(peer_public=publicKeys[str(e[1])], peer_endpoint=str(e[1].ip_address) + ":51820", peer_allowed=str(e[1].virtual_ip_address) + "/32", peer_persistent_keep_alive=str(21))
                elif(type(e[1]) is WgRouter):
                    if(e[1].default_gateway != None):
                        conf_temp += conf_template_peer_link.substitute(peer_public=publicKeys[str(e[1].tags['name'])], peer_endpoint=str(e[1].ip_address) + ":51820", peer_allowed=ips_to_string(e[1].allowed_ip_range, e[1].default_gateway.allowed_ip_range), peer_persistent_keep_alive=str(21))
                    else:
                        conf_temp += conf_template_peer_link.substitute(peer_public=publicKeys[str(e[1].tags['name'])], peer_endpoint=str(e[1].ip_address) + ":51820", peer_allowed=ips_to_string(e[1].allowed_ip_range, ""), peer_persistent_keep_alive=str(21))

                lat = topology.latency(n, e[1])
                if (lat < 0):
                    lat *= -1

                latency[e[1].virtual_ip_address] = lat

        #add default gateway
        #if l.default_gateway != None:
        #    conf_temp += conf_template_peer_link.substitute(peer_public=publicKeys[str(l.default_gateway.tags['name'])], peer_endpoint=str(l.default_gateway.ip_address) + ":51820", peer_allowed=ips_to_string(l.default_gateway.allowed_ip_range), peer_persistent_keep_alive=str(21))

        conf_temp = conf_temp.replace(" Endpoint", "Endpoint")
        conf_temp = conf_temp.replace(" PostUp", "PostUp")

        if(not dry_run):
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
            sshProcess.stdin.write("sudo tc qdisc del dev wg0 root \n") #TC RESET
            sshProcess.stdin.write('{}\n'.format(devices_pswd))
            sshProcess.stdin.write("exit\n")
            sshProcess.stdin.close()
            sshProcess.wait()

            print("yessir")
            os.system("scp wg0.conf pirate@" + l.ip_address + ":~/../../etc/wireguard/")

            sshProcess = subprocess.Popen(args, stdin=subprocess.PIPE,
                                                 stdout = subprocess.PIPE,
                                                 universal_newlines=True,
                                                 bufsize=0)

            sshProcess.stdin.write("cd ~/../../etc/wireguard \n")
            sshProcess.stdin.write("wg-quick up wg0 \n")
            #sshProcess.stdin.write("sudo tc qdisc add dev wg0 root handle 1: prio \n")
            #sshProcess.stdin.write("sudo tc qdisc add dev wg0 parent 1:3 handle 30: netem delay " + str(500) + "ms \n") #LATSET todo

            #for key in latency:
                #sshProcess.stdin.write("sudo tc filter add dev wg0 protocol ip parent 1:0 prio 3 u32 match ip dst " + key + " flowid 1:3 \n")

            sshProcess.stdin.write("exit\n")
            sshProcess.stdin.close()
            sshProcess.wait()
        else:
            f = open("wg_" + l.virtual_ip_address + ".conf", "w")
            f.write(conf_temp)
            f.close()




    for n in nodes:
        conf_temp = conf_template_interface.substitute(interface_address=str(n.virtual_ip_address) + "/32", interface_private=privateKeys[str(n)], interface_port=str(51820))
        print("Working on Node:")
        print(n)
        latency = {}

        for e in edges:
            if (e[0] == n):
                print("to: " + str(e[1]))
                if(type(e[1]) is Node):
                    #conf_temp += conf_template_peer_node.substitute(peer_public=publicKeys[str(e[1])], peer_endpoint=str(e[1].virtual_ip_address) + ":51820", peer_persistent_keep_alive=str(21))
                    conf_temp += conf_template_peer_node.substitute(peer_public=publicKeys[str(e[1])], peer_endpoint="", peer_persistent_keep_alive=str(21))
                elif(type(e[1]) is WgRouter):
                    if(e[1].default_gateway != None):
                        conf_temp += conf_template_peer_link.substitute(peer_public=publicKeys[str(e[1].tags['name'])], peer_endpoint=str(e[1].ip_address) + ":51820", peer_allowed=ips_to_string(e[1].allowed_ip_range, e[1].default_gateway.allowed_ip_range), peer_persistent_keep_alive=str(21))
                    else:
                        conf_temp += conf_template_peer_link.substitute(peer_public=publicKeys[str(e[1].tags['name'])], peer_endpoint=str(e[1].ip_address) + ":51820", peer_allowed=ips_to_string(e[1].allowed_ip_range, ""), peer_persistent_keep_alive=str(21))

                lat = topology.latency(n, e[1])
                if (lat < 0):
                    lat *= -1

                latency[e[1].virtual_ip_address] = lat

        conf_temp = conf_temp.replace(" Endpoint", "Endpoint")
        conf_temp = conf_temp.replace(" ListenPort", "ListenPort")

        if(not dry_run):
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
            if(lat > 0): #CHANGE BACK
                sshProcess.stdin.write("sudo tc qdisc del dev wg0 root \n") #TC RESET
                sshProcess.stdin.write("sudo tc qdisc del dev wg0 handle ffff: ingress \n")
                sshProcess.stdin.write("sudo ip link set dev ifb0 down \n")
                sshProcess.stdin.write("sudo modprobe -r ifb \n")



            #sshProcess.stdin.write('{}\n'.format(devices_pswd))
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
            if(lat > 0):
                #OUTGOING
                sshProcess.stdin.write("sudo tc qdisc add dev wg0 root handle 1: prio \n")
                sshProcess.stdin.write("sudo tc qdisc add dev wg0 parent 1:3 handle 30: netem delay " + str(lat) + "ms \n") #LAT set todo
                sshProcess.stdin.write("sudo tc filter add dev wg0 protocol ip parent 1:0 prio 3 u32 match ip dst " + "10.0.0.0/8" + " flowid 1:3 \n")

                #INCOMING
                sshProcess.stdin.write("sudo modprobe ifb numifbs=1 \n")
                sshProcess.stdin.write("sudo ip link set dev ifb0 up \n")
                sshProcess.stdin.write("sudo tc qdisc add dev wg0 handle ffff: ingress \n")
                sshProcess.stdin.write("sudo tc filter add dev wg0 parent ffff: protocol ip u32 match u32 0 0 action mirred egress redirect dev ifb0 \n")
                sshProcess.stdin.write("sudo tc qdisc add dev ifb0 root handle 2: prio \n")
                #sshProcess.stdin.write("sudo tc class add dev ifb0 parent 2: classid 2:1 prio rate " + str(lat) + "kbit \n")
                #sshProcess.stdin.write("sudo tc qdisc add dev ifb0 parent 2:1 handle 20: netem delay " + str(lat) + "ms \n")
                sshProcess.stdin.write("sudo tc filter add dev ifb0 protocol ip parent 2: prio 1 u32 match ip src " + "10.0.0.0/8" + " flowid 2:1 \n")



            sshProcess.stdin.write("exit\n")
            sshProcess.stdin.close()
            sshProcess.wait()
        else:
            f = open("wg_" + n.virtual_ip_address + ".conf", "w")
            f.write(conf_temp)
            f.close()



    #return null

