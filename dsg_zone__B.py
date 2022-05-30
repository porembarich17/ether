import matplotlib.pyplot as plt
import networkx as nx

from ether.scenarios.industrialiot import IndustrialIoTScenario
from ether.topology import Topology
from ether.vis import draw_basic
from ether.blocks.nodes import create_nuc_node, create_rpi3_node
from ether.core import Connection, WgRouter, Node
from ether.sdn import wireguard_output


def main():
    topology = Topology()

    #na0 = create_rpi3_node(name='eb-a-rockpi-0', ip_address='192.168.1.51', virtual_ip_address='10.0.1.51')
    #na1 = create_rpi3_node(name='eb-a-rpi4-0', ip_address='192.168.1.53', virtual_ip_address='10.0.1.53')
    #na3 = create_rpi3_node(name='eb-a-jetson-tx2-0', ip_address='192.168.1.57', virtual_ip_address='10.0.1.57')
    #na4 = create_rpi3_node(name='eb-a-jetson-nano-0', ip_address='192.168.1.59', virtual_ip_address='10.0.1.59')
    #na5 = create_rpi3_node(name='eb-a-nuc7-0', ip_address='192.168.1.60', virtual_ip_address='10.0.1.60')

    nb0 = create_rpi3_node(name='eb-b-xeon-0', ip_address='192.168.0.102', virtual_ip_address='10.0.1.102')
    nb1 = create_rpi3_node(name='eb-b-xeon-1', ip_address='192.168.0.103', virtual_ip_address='10.0.1.103')
    nb2 = create_rpi3_node(name='eb-b-xeon-2', ip_address='192.168.0.104', virtual_ip_address='10.0.1.104')
    nb3 = create_rpi3_node(name='eb-b-xeongpu-0', ip_address='192.168.0.122', virtual_ip_address='10.0.2.60')
    nb4 = create_rpi3_node(name='eb-b-nuc7-0', ip_address='192.168.0.105', virtual_ip_address='10.0.2.105')


    #nc0 = create_rpi3_node(name='eb-c-vm-1', ip_address='128.131.57.150', virtual_ip_address='10.0.3.150')
    #nc1 = create_rpi3_node(name='eb-c-vm-2', ip_address='128.131.57.151', virtual_ip_address='10.0.3.151')
    #nc2 = create_rpi3_node(name='eb-c-vm-3', ip_address='128.131.57.152', virtual_ip_address='10.0.3.152')

    gtw = WgRouter(tags={'name': 'eb-gateway', 'type': 'Router'}, ip_address='128.131.57.147', virtual_ip_address='10.0.1.1', allowed_ip_range=["10.0.0.0/16"])

    #ca0 = WgRouter(tags={'name': 'eb-a-controller', 'type': 'Router'}, ip_address='192.168.1.2', virtual_ip_address='10.0.1.2', allowed_ip_range=["10.0.1.0/26"], default_gateway=gtw)
    cb0 = WgRouter(tags={'name': 'eb-b-controller', 'type': 'Router'}, ip_address='192.168.1.101', virtual_ip_address='10.0.1.12', allowed_ip_range=["10.0.1.64/26, 10.0.2.0/24"], default_gateway=gtw)
    #cc0 = WgRouter(tags={'name': 'eb-c-vm-0', 'type': 'Router'}, ip_address='128.131.57.149', virtual_ip_address='10.0.3.1', allowed_ip_range=["10.0.3.0/24"], default_gateway=gtw)
    #k3s = WgRouter(tags={'name': 'eb-k3s-master', 'type': 'Router'}, ip_address='128.131.57.148', virtual_ip_address='10.0.1.3', allowed_ip_range=["10.0.0.0/16"], default_gateway=gtw)

    #topology.add_connection(Connection(na0, ca0, 0))
    #topology.add_connection(Connection(na1, ca0, 0))
    #topology.add_connection(Connection(na3, ca0, 0))
    #topology.add_connection(Connection(na4, ca0, 0))
    #topology.add_connection(Connection(na5, ca0, 0))

    topology.add_connection(Connection(nb0, cb0, 0))
    topology.add_connection(Connection(nb1, cb0, 0))
    topology.add_connection(Connection(nb2, cb0, 0))
    topology.add_connection(Connection(nb3, cb0, 0))
    topology.add_connection(Connection(nb4, cb0, 0))

    #topology.add_connection(Connection(nc0, cc0, 0))
    #topology.add_connection(Connection(nc1, cc0, 0))
    #topology.add_connection(Connection(nc2, cc0, 0))

    #topology.add_connection(Connection(ca0, cb0, 100))
    #topology.add_connection(Connection(ca0, cc0, 100))
    #topology.add_connection(Connection(cb0, cc0, 100))

    #topology.add_connection(Connection(gtw, ca0, 0))
    topology.add_connection(Connection(gtw, cb0, 0))
    #topology.add_connection(Connection(gtw, cc0, 0))
    #topology.add_connection(Connection(gtw, k3s, 0))


    gen = nx.all_pairs_shortest_path(topology)
    #for p in gen:
        #print('-----')
        #print(p)

    #print('path', topology.path(n0, n5))

    #r = topology.route(n0, n5)
    #print('route', r)

    draw_basic(topology)
    fig = plt.gcf()
    fig.set_size_inches(18.5, 10.5)
    plt.show()  # display

    print('num nodes:', len(topology.nodes))


    wireguard_output.create_output(topology, True)

if __name__ == '__main__':
    main()
