import networkx as nx
import matplotlib.pyplot as plt

G = nx.Graph()
G.add_edge(1, 2)
G.add_edge(2, 3)
nx.set_node_attributes(G, {1: 'red', 2: 'blue', 3: 'green'}, 'color')

colors = [G.nodes[n]['color'] for n in G.nodes]

nx.draw(G, with_labels=True, node_color=colors)
plt.show()
