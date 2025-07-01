import networkx as nx
from networkx.algorithms import isomorphism

# === G1 with node and edge attributes ===
G1 = nx.Graph()
G1.add_node(1, color='red')
G1.add_node(2, color='blue')
G1.add_node(3, color='green')
G1.add_edge(1, 2, weight=10)
G1.add_edge(2, 3, weight=20)

# === G2 with same structure and attributes ===
G2 = nx.Graph()
G2.add_node('x', color='red')
G2.add_node('y', color='blue')
G2.add_node('z', color='green')
G2.add_edge('x', 'y', weight=10)
G2.add_edge('y', 'z', weight=20)

# Define attribute-based matchers
node_match = isomorphism.categorical_node_match('color', None)
edge_match = isomorphism.categorical_edge_match('weight', None)

# GraphMatcher with attribute matching
GM = isomorphism.GraphMatcher(G1, G2, node_match=node_match, edge_match=edge_match)

if GM.is_isomorphic():
    print("Graphs are isomorphic (with attributes).")
    node_map = GM.mapping
    print("Node mapping (G1 -> G2):", node_map)

    # Edge mapping with attributes
    print("Edge mapping with attributes (G1 -> G2):")
    for u, v, data in G1.edges(data=True):
        mapped_u = node_map[u]
        mapped_v = node_map[v]

        # Normalize edge direction
        edge_g2 = (mapped_u, mapped_v)
        if not G2.has_edge(*edge_g2):
            edge_g2 = (mapped_v, mapped_u)

        attr_g1 = data
        attr_g2 = G2.edges[edge_g2]

        print(f"  ({u}, {v}, {attr_g1}) -> {edge_g2}, {attr_g2}")
else:
    print("Graphs are not isomorphic.")
