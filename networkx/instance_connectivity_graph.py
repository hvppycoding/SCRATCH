from typing import List, Optional
from pyverilog.vparser.parser import parse
from pyverilog.vparser.ast import ModuleDef, InstanceList, PortArg, Input, Output, Inout, Node
import networkx as nx
import matplotlib.pyplot as plt

class ModuleInterface:
    def __init__(self, name: str):
        self.name: str = name
        self.port_order: List[str] = []
        self.port_directions: dict[str, str] = {}

    def __repr__(self) -> str:
        return f"<ModuleInterface {self.name}: ports={self.port_order}>"

    def validate(self) -> None:
        if not self.name or not isinstance(self.name, str):
            raise ValueError("Module name must be a non-empty string")

        for port in self.port_order:
            if port not in self.port_directions:
                raise ValueError(f"Port '{port}' in module '{self.name}' is missing direction info")

        for port, direction in self.port_directions.items():
            if direction not in {"input", "output", "inout"}:
                raise ValueError(f"Port '{port}' in module '{self.name}' has invalid direction '{direction}'")

        if len(self.port_order) != len(self.port_directions):
            raise ValueError(f"Module '{self.name}' has mismatched port count: {len(self.port_order)} in port_order vs {len(self.port_directions)} in port_directions")

    @staticmethod
    def create_from_module_def(module_def: ModuleDef) -> "ModuleInterface":
        interface = ModuleInterface(module_def.name)

        # Port order
        if module_def.portlist:
            for port in module_def.portlist.ports:
                interface.port_order.append(port.name)

        # Port directions
        for item in module_def.items:
            if isinstance(item, (Input, Output, Inout)):
                direction = item.__class__.__name__.lower()
                for name in item.names:
                    interface.port_directions[name] = direction

        interface.validate()
        return interface

def create_module_interfaces(node: Node) -> List[ModuleInterface]:
    interfaces: List[ModuleInterface] = []
    def walk(n: Node):
        if isinstance(n, ModuleDef):
            interface = ModuleInterface.create_from_module_def(n)
            interfaces.append(interface)
        for child in n.children():
            walk(child)
    walk(node)
    return interfaces

def find_module_by_name(ast: Node, target_name: str) -> ModuleDef:
    for definition in ast.description.definitions:
        if isinstance(definition, ModuleDef) and definition.name == target_name:
            return definition
    raise RuntimeError(f"Module {target_name} not found")

class GraphCreator:
    def __init__(self, module_defs: List[ModuleInterface]):
        self.module_defs: List[ModuleInterface] = module_defs
        self.graph: nx.Graph = nx.Graph()

    def create_from_module(self, module_ast: ModuleDef) -> None:
        mod_def = next((m for m in self.module_defs if m.name == module_ast.name), None)
        if not mod_def:
            raise RuntimeError(f"Definition for module {module_ast.name} not found")

        # Step 1: Add external ports as net nodes with direction
        for port in mod_def.port_order:
            direction = mod_def.port_directions.get(port, 'unknown')
            node_name = f"@{port}"
            if node_name in self.graph:
                existing = self.graph.nodes[node_name]
                if 'direction' in existing and existing['direction'] != direction:
                    raise ValueError(f"Direction mismatch on port '{node_name}': existing '{existing['direction']}' vs new '{direction}'")
            else:
                self.graph.add_node(node_name, type='net', direction=direction)

        # Step 2: Add instance connections
        for item in module_ast.items:
            if isinstance(item, InstanceList):
                submod_name = item.module
                submod_def = next((m for m in self.module_defs if m.name == submod_name), None)
                if not submod_def:
                    continue

                for inst in item.instances:
                    inst_name = inst.name
                    self.graph.add_node(inst_name, type='instance', module=submod_name)

                    for idx, conn in enumerate(inst.portlist):
                        # Determine port name
                        if conn.portname is None:
                            if idx >= len(submod_def.port_order):
                                continue
                            portname = submod_def.port_order[idx]
                        else:
                            portname = conn.portname

                        # Determine net name
                        if hasattr(conn.argname, 'name'):
                            netname = conn.argname.name
                        elif isinstance(conn.argname, str):
                            netname = conn.argname
                        else:
                            continue

                        # Check if it's external or internal net
                        if netname in mod_def.port_order:
                            net_dir = mod_def.port_directions.get(netname, 'unknown')
                        else:
                            net_dir = 'internal'

                        net_node_name = f"@{netname}"
                        if net_node_name in self.graph:
                            existing = self.graph.nodes[net_node_name]
                            if 'direction' in existing and existing['direction'] != net_dir:
                                raise ValueError(f"Direction mismatch on net '{net_node_name}': existing '{existing['direction']}' vs new '{net_dir}'")
                        else:
                            self.graph.add_node(net_node_name, type='net', direction=net_dir)

                        self.graph.add_edge(inst_name, net_node_name, port=portname)

    def get_graph(self) -> nx.Graph:
        return self.graph

def draw_connectivity_graph(G: nx.Graph) -> None:
    pos = nx.spring_layout(G, seed=42)

    net_colors = {
        'input': '#f1948a',    # light red
        'output': '#85c1e9',   # light blue
        'inout': '#abebc6',    # light green
        'internal': '#f9e79f'  # light yellow
    }

    # Draw net nodes
    for direction, color in net_colors.items():
        nodes = [n for n, d in G.nodes(data=True) if d['type'] == 'net' and d['direction'] == direction]
        nx.draw_networkx_nodes(G, pos, nodelist=nodes, node_size=500, node_color=color, edgecolors='black', linewidths=1)

    # Draw instance nodes
    inst_nodes = [n for n, d in G.nodes(data=True) if d['type'] == 'instance']
    nx.draw_networkx_nodes(G, pos, nodelist=inst_nodes, node_size=1000, node_color='white', edgecolors='black', linewidths=1)

    # Draw edges with port names
    edge_labels = {(u, v): d['port'] for u, v, d in G.edges(data=True)}
    nx.draw_networkx_edges(G, pos)
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=8)

    # Draw node labels
    labels = {}
    for n, d in G.nodes(data=True):
        if d['type'] == 'instance':
            labels[n] = f"{d['module']}\n{n}"
        else:
            labels[n] = n
    nx.draw_networkx_labels(G, pos, labels=labels, font_size=8)

    plt.axis('off')
    plt.tight_layout()
    plt.show()

def main(filename: str, target_module_name: str) -> nx.Graph:
    ast, _ = parse([filename])

    # Step 1: Create all module interfaces
    module_defs = create_module_interfaces(ast)

    # Step 2: Get target module AST
    target_module_ast = find_module_by_name(ast, target_module_name)

    # Step 3: Create graph
    creator = GraphCreator(module_defs)
    creator.create_from_module(target_module_ast)
    G = creator.get_graph()

    # Step 4: Print graph
    print("Edges:")
    for u, v, attr in G.edges(data=True):
        print(f"{u} -- {v}, port: {attr['port']}")

    print("\nNet directions:")
    for node, data in G.nodes(data=True):
        if data['type'] == 'net':
            print(f"{node}: {data['direction']}")

    return G

# Example usage:
# graph = main("your_file.v", "your_module_name")
# draw_connectivity_graph(graph)
