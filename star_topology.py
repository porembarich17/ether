import matplotlib.pyplot as plt
import networkx as nx

from ether.scenarios.industrialiot import IndustrialIoTScenario
from ether.topology import Topology
from ether.vis import draw_basic
from ether.blocks.nodes import create_nuc_node, create_rpi3_node
from ether.core import Connection, Link, Node
from ether.sdn import wireguard_output

def main():
    topology = Topology()

    n0 = create_rpi3_node()
    n1 = create_rpi3_node()
    n2 = create_rpi3_node()
    n3 = create_rpi3_node()
    n4 = create_rpi3_node()
    n5 = create_rpi3_node()

    l0 = Link(tags={'name': 'Router', 'type': 'Router'})
    #l1 = Link(tags={'name': 'link_%s' % n1.name})
    #l2 = Link(tags={'name': 'link_%s' % n2.name})
    #l3 = Link(tags={'name': 'link_%s' % n3.name})
    #l4 = Link(tags={'name': 'link_%s' % n4.name})
    #l5 = Link(tags={'name': 'link_%s' % n5.name})

    topology.add_connection(Connection(n0, l0, 10))
    topology.add_connection(Connection(n1, l0, 10))
    topology.add_connection(Connection(n2, l0, 10))
    topology.add_connection(Connection(n3, l0, 10))
    topology.add_connection(Connection(n4, l0, 10))
    topology.add_connection(Connection(n5, l0, 10))



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
    plt.show()  # display

    print('num nodes:', len(topology.nodes))


    wireguard_output.create_output(topology)

if __name__ == '__main__':
    main()
