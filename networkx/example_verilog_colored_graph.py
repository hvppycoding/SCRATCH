import networkx as nx
import matplotlib.pyplot as plt

G = nx.Graph()

# --- Nodes ---
G.add_node("u1", type="instance", module="adder")
G.add_node("u2", type="instance", module="multiplier")
G.add_node("n1", type="net")
G.add_node("n2", type="net")

# --- Edges with port ---
G.add_edge("u1", "n1", port="a")
G.add_edge("u2", "n1", port="x")
G.add_edge("u1", "n2", port="b")
G.add_edge("u2", "n2", port="y")

# --- Layout ---
pos = nx.spring_layout(G)

# --- Node colors ---
node_colors = {
    "u1": "orange",
    "u2": "skyblue",
    "n1": "lightgreen",
    "n2": "violet",
}
node_color_list = [node_colors[n] for n in G.nodes]

# --- Edge colors (sorted tuples as keys) ---
edge_colors = {
    tuple(sorted(("u1", "n1"))): "red",
    tuple(sorted(("u2", "n1"))): "blue",
    tuple(sorted(("u1", "n2"))): "green",
    tuple(sorted(("u2", "n2"))): "purple",
}
edges = list(G.edges())
edge_color_list = [edge_colors[tuple(sorted(e))] for e in edges]

# --- Node labels with newline ---
labels = {}
for n in G.nodes:
    if G.nodes[n].get("type") == "instance":
        labels[n] = f"{n}\n({G.nodes[n]['module']})"
    else:
        labels[n] = n

# --- Draw graph ---
nx.draw(G, pos, with_labels=True, labels=labels,
        node_color=node_color_list, edge_color=edge_color_list,
        node_size=2000, font_color="black")

# --- Edge labels (port names) ---
edge_labels = {(u, v): d["port"] for u, v, d in G.edges(data=True)}
nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_color="black")

plt.axis("off")
plt.tight_layout()
plt.show()
