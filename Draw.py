import networkx as nx
import matplotlib.pyplot as plt
import os
import math

pic_count = 0


def draw(nodes):
    G = nx.DiGraph()
    length = len(list(filter(lambda x: x.partially_online, nodes)))
    if length == 0:
        length = 1
    index = 0
    nodes = sorted(nodes, key=lambda x: x.id)
    for node in nodes:
        angle = (1 / 4 - index / length) * math.pi * 2
        x = math.cos(angle)
        y = math.sin(angle)
        if not node.partially_online:
            x *= 1.5
            y *= 1.5
        G.add_node(node, pos=(x, y))
        index += 1
    for node in nodes:
        G.add_edge(node, node.successor)
        G.add_edge(node.predecessor, node)

    plt.axis('off')
    plt.set_cmap('hot')
    nx.draw_networkx(G, nx.get_node_attributes(G, 'pos'), node_color='blue', edge_color='grey', node_size=5, with_labels=True)
    plt.xlim(-1.6, 1.6)
    plt.ylim(-1.6, 1.6)

    plt.show()
