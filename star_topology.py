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

    n0 = create_rpi3_node(ip_address='192.168.0.144', virtual_ip_address='10.0.0.1')
    n1 = create_rpi3_node(ip_address='192.168.0.10', virtual_ip_address='10.1.1.1')
    #n2 = create_rpi3_node(ip_address='100.100.0.3:51820')
    #n3 = create_rpi3_node(ip_address='100.100.0.4:51820')
    #n4 = create_rpi3_node(ip_address='100.100.0.5:51820')
    #n5 = create_rpi3_node(ip_address='100.100.0.6:51820')

    l0 = WgRouter(tags={'name': 'Router', 'type': 'Router'}, ip_address='192.168.0.192', virtual_ip_address='10.0.0.222', allowed_ip_range=["10.0.0.0/8"])
    #l1 = Link(tags={'name': 'link_%s' % n1.name})
    #l2 = Link(tags={'name': 'link_%s' % n2.name})
    #l3 = Link(tags={'name': 'link_%s' % n3.name})
    #l4 = Link(tags={'name': 'link_%s' % n4.name})
    #l5 = Link(tags={'name': 'link_%s' % n5.name})

    topology.add_connection(Connection(n0, l0, 0))
    topology.add_connection(Connection(n1, l0, 0))
    #topology.add_connection(Connection(n2, l0, 10))
    #topology.add_connection(Connection(n3, l0, 10))
    #topology.add_connection(Connection(n4, l0, 10))
    #topology.add_connection(Connection(n5, l0, 10))



    gen = nx.all_pairs_shortest_path(topology)
    for p in gen:
        print('-----')
        print(p)

    #print('path', topology.path(n0, n5))

    #r = topology.route(n0, n5)
    #print('route', r)

    draw_basic(topology)
    fig = plt.gcf()
    fig.set_size_inches(18.5, 10.5)
    #plt.show()  # display

    print('num nodes:', len(topology.nodes))


    wireguard_output.create_output(topology, False)

if __name__ == '__main__':
    main()
