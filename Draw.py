import networkx as nx
import matplotlib.pyplot as plt


def draw(nodes):
    G = nx.DiGraph()
    for node in nodes:
        G.add_node(node.id)
    for node in nodes:
        G.add_edge(node.id, node.successor.id)
        G.add_edge(node.predecessor.id, node.id)
    nx.draw(G)
    plt.show()
