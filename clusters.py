import matplotlib.pyplot as plt
import networkx as nx

from ether.scenarios.industrialiot import IndustrialIoTScenario
from ether.topology import Topology
from ether.vis import draw_basic
from ether.blocks.nodes import create_nuc_node, create_rpi3_node
from ether.core import Connection, Link, Node
from ether.cell import Cell

def main():
    topology = Topology()

    n0 = create_rpi3_node()
    n1 = create_rpi3_node()
    n2 = create_rpi3_node()
    n3 = create_rpi3_node()

    l0 = Link(tags={'name': 'Router1', 'type': 'Router'})
    l1 = Link(tags={'name': 'Router2', 'type': 'Router'})

    cluster1 = Cell([n0, n1, l0], 2)
    cluster2 = Cell([n2, n3, l1], 2)

    topology.add_connection(Connection(l0, l1, 250))
    topology.add_connection(Connection(n0, l0, 5))
    topology.add_connection(Connection(n1, l0, 5))
    topology.add_connection(Connection(n2, l1, 5))
    topology.add_connection(Connection(n3, l1, 5))



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


if __name__ == '__main__':
    main()
