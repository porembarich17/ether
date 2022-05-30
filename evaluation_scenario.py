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

    na0 = create_rpi3_node(name='NodeA', ip_address='192.168.0.7', virtual_ip_address='10.0.1.10')
    nb0 = create_rpi3_node(name='NodeB', ip_address='192.168.0.8', virtual_ip_address='10.0.2.20')
    nc0 = create_rpi3_node(name='NodeC', ip_address='192.168.0.9', virtual_ip_address='10.0.3.30')
    nd0 = create_rpi3_node(name='NodeD', ip_address='192.168.0.10', virtual_ip_address='10.0.4.40')
    ne0 = create_rpi3_node(name='NodeE', ip_address='192.168.0.11', virtual_ip_address='10.0.5.50')

    gtw = WgRouter(tags={'name': 'Gateway', 'type': 'Router'}, ip_address='192.168.0.1', virtual_ip_address='10.0.10.1', allowed_ip_range=["10.0.0.0/16"])
    ra = WgRouter(tags={'name': 'A', 'type': 'Router'}, ip_address='192.168.0.2', virtual_ip_address='10.0.1.1', allowed_ip_range=["10.0.10.0/24, 10.0.1.0/24, 10.0.2.0/24, 10.0.3.0/24"], default_gateway=gtw)
    rb = WgRouter(tags={'name': 'B', 'type': 'Router'}, ip_address='192.168.0.3', virtual_ip_address='10.0.2.1', allowed_ip_range=["10.0.1.0/24, 10.0.2.0/24"], default_gateway=gtw)
    rc = WgRouter(tags={'name': 'C', 'type': 'Router'}, ip_address='192.168.0.4', virtual_ip_address='10.0.3.1', allowed_ip_range=["10.0.1.0/24, 10.0.3.0/24, 10.0.4.0/24"], default_gateway=gtw)
    rd = WgRouter(tags={'name': 'D', 'type': 'Router'}, ip_address='192.168.0.5', virtual_ip_address='10.0.4.1', allowed_ip_range=["10.0.3.0/24, 10.0.4.0/24"], default_gateway=gtw)
    re = WgRouter(tags={'name': 'E', 'type': 'Router'}, ip_address='192.168.0.6', virtual_ip_address='10.0.5.1', allowed_ip_range=["10.0.10.0/24, 10.0.5.0/24"], default_gateway=gtw)

    topology.add_connection(Connection(na0, ra, 1))
    topology.add_connection(Connection(nb0, rb, 1))
    topology.add_connection(Connection(nc0, rc, 1))
    topology.add_connection(Connection(nd0, rd, 1))
    topology.add_connection(Connection(ne0, re, 1))

    topology.add_connection(Connection(gtw, re, 100))
    topology.add_connection(Connection(gtw, ra, 100))
    topology.add_connection(Connection(ra, rb, 10))
    topology.add_connection(Connection(ra, rc, 10))
    topology.add_connection(Connection(rc, rd, 10))


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
