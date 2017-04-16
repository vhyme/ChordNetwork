import networkx as nx
import matplotlib.pyplot as plt
import os
import math

pic_count = 0


def draw(nodes):
    plt.figure(figsize=(7, 7))
    G = nx.DiGraph()
    nodes = list(filter(lambda x: x.partially_online, nodes))
    length = len(nodes)
    if length < 1:
        length = 1
    index = 0
    nodes = sorted(nodes, key=lambda x: x.id)
    for node in nodes:
        angle = (1 / 4 - index / length) * math.pi * 2
        x = math.cos(angle)
        y = math.sin(angle)
        if not node.fully_online:
            x = math.cos(angle) * 1.3
            y = math.sin(angle) * 1.3
        G.add_node(node, pos=(x, y), lblpos=(x*1.25, y*1.15))
        index += 1
    for node in nodes:
        if node != node.successor and node.successor.partially_online:
            G.add_edge(node, node.successor)
        if node != node.predecessor and node.predecessor.partially_online:
            G.add_edge(node.predecessor, node)

    plt.axis('off')
    plt.set_cmap('hot')
    nx.draw_networkx(G, nx.get_node_attributes(G, 'pos'), node_color='orange', edge_color='orange', node_size=40, with_labels=False)
    nx.draw_networkx_labels(G, nx.get_node_attributes(G, 'lblpos'), font_size=12 - length / 15)
    plt.xlim(-1.8, 1.8)
    plt.ylim(-1.8, 1.8)

    plt.show()
