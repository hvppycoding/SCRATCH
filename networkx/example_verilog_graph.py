import networkx as nx
import matplotlib.pyplot as plt

G = nx.Graph()

# Add instance nodes with module name
G.add_node("u1", type="instance", module="adder")
G.add_node("u2", type="instance", module="multiplier")

# Add net nodes
G.add_node("n1", type="net")
G.add_node("n2", type="net")

# Add edges with port names as attributes
G.add_edge("u1", "n1", port="a")
G.add_edge("u1", "n2", port="b")
G.add_edge("u2", "n1", port="x")
G.add_edge("u2", "n2", port="y")

# Node label: instance name + module name
node_labels = {}
for n in G.nodes:
    if G.nodes[n]["type"] == "instance":
        node_labels[n] = f"{n}\n({G.nodes[n]['module']})"
    else:
        node_labels[n] = n  # net name 그대로

# Edge label: port name
edge_labels = {(u, v): d["port"] for u, v, d in G.edges(data=True)}

# Draw
pos = nx.spring_layout(G)
nx.draw(G, pos, with_labels=True, labels=node_labels, node_color='lightyellow', node_size=2000)
nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_color='red')
plt.show()
