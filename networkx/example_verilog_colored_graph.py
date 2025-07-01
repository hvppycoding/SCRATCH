import networkx as nx
import matplotlib.pyplot as plt

G = nx.Graph()

# Nodes
G.add_node("u1", type="instance", module="adder")
G.add_node("u2", type="instance", module="multiplier")
G.add_node("n1", type="net")
G.add_node("n2", type="net")

# Edges with port names
G.add_edge("u1", "n1", port="a")
G.add_edge("u2", "n1", port="x")
G.add_edge("u1", "n2", port="b")
G.add_edge("u2", "n2", port="y")

pos = nx.spring_layout(G)

# Node styles
node_colors = {
    "u1": "orange",
    "u2": "skyblue",
    "n1": "lightgreen",
    "n2": "violet",
}
node_sizes = {
    "u1": 2500,
    "u2": 2500,
    "n1": 1000,
    "n2": 1000,
}
node_border_color = 'black'
node_border_width = 2

# Draw nodes manually (for size + border control)
for node in G.nodes:
    nx.draw_networkx_nodes(
        G, pos,
        nodelist=[node],
        node_color=node_colors[node],
        node_size=node_sizes[node],
        edgecolors=node_border_color,
        linewidths=node_border_width
    )

# Draw edges
edge_colors = {
    tuple(sorted(("u1", "n1"))): "red",
    tuple(sorted(("u2", "n1"))): "blue",
    tuple(sorted(("u1", "n2"))): "green",
    tuple(sorted(("u2", "n2"))): "purple",
}
edges = list(G.edges())
edge_color_list = [edge_colors[tuple(sorted(e))] for e in edges]
nx.draw_networkx_edges(G, pos, edgelist=edges, edge_color=edge_color_list, width=2)

# Labels
labels = {
    n: f"{n}\n({G.nodes[n]['module']})" if G.nodes[n].get("type") == "instance" else n
    for n in G.nodes
}
nx.draw_networkx_labels(G, pos, labels=labels, font_color="black")

# Edge labels (port names)
edge_labels = {(u, v): d["port"] for u, v, d in G.edges(data=True)}
nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_color="black")

plt.axis("off")
plt.tight_layout()
plt.show()
