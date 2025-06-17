from pyverilog.vparser.parser import parse
from collections import defaultdict, deque
import pygraphviz as pgv

def extract_edges_and_modules(ast):
    edges = set()
    defined_modules = set()
    description = ast.description

    # 모듈 정의 수집
    for definition in description.definitions:
        if definition.__class__.__name__ != 'ModuleDef':
            continue
        module_name = definition.name
        defined_modules.add(module_name)

        # 모듈 내 instantiation 관계 수집
        for item in definition.items:
            if item.__class__.__name__ == 'InstanceList':
                for instance in item.instances:
                    edges.add((module_name, item.module))  # parent, child

    return edges, defined_modules

def find_reachable_nodes(edges, top_module):
    graph = defaultdict(list)
    for parent, child in edges:
        graph[parent].append(child)

    reachable = set()
    queue = deque([top_module])
    while queue:
        node = queue.popleft()
        if node in reachable:
            continue
        reachable.add(node)
        for child in graph[node]:
            queue.append(child)
    return reachable

def filter_edges(edges, reachable, defined_modules):
    # primitive (moduleDef 없는 것)으로 향하는 edge 제거
    return set(
        (p, c) for (p, c) in edges
        if p in reachable and c in reachable and c in defined_modules
    )

def compute_depths(edges, top_module):
    graph = defaultdict(list)
    indegree = defaultdict(int)

    for parent, child in edges:
        graph[parent].append(child)
        indegree[child] += 1
        if parent not in indegree:
            indegree[parent] = 0

    # Topological sort
    queue = deque()
    for node, deg in indegree.items():
        if deg == 0:
            queue.append(node)

    topo_order = []
    while queue:
        node = queue.popleft()
        topo_order.append(node)
        for child in graph[node]:
            indegree[child] -= 1
            if indegree[child] == 0:
                queue.append(child)

    # Depth DP
    depth = defaultdict(int)
    for node in topo_order:
        for child in graph[node]:
            depth[child] = max(depth[child], depth[node] + 1)

    return depth

def build_graphviz(edges, depths):
    G = pgv.AGraph(directed=True)

    # 노드 추가 + label + rank group
    rank_groups = defaultdict(list)
    nodes_in_graph = set()
    for parent, child in edges:
        nodes_in_graph.add(parent)
        nodes_in_graph.add(child)

    for node in nodes_in_graph:
        rank = depths.get(node, 0)
        G.add_node(node, label=f"{node}\n(rank {rank})", shape='box')
        rank_groups[rank].append(node)

    # edge 추가 (set이므로 중복 없음)
    for parent, child in edges:
        G.add_edge(parent, child)

    # rank group 설정
    for rank, nodes in rank_groups.items():
        with G.subgraph() as s:
            s.graph_attr['rank'] = 'same'
            for n in nodes:
                s.add_node(n)

    # 옵션
    G.graph_attr.update({
        'rankdir': 'TB',
        'overlap': 'false',
        'splines': 'false',
        'nodesep': '0.5',
        'ranksep': '0.5',
        'concentrate': 'true'
    })

    G.layout(prog='dot')
    G.draw('module_hierarchy.svg')
    print("Graph saved as module_hierarchy.svg")

def main():
    verilog_files = ['top.v']  # Verilog 파일 리스트 수정
    top_module = 'TOP'         # TOP 모듈 이름 수정

    ast, _ = parse(verilog_files)
    edges, defined_modules = extract_edges_and_modules(ast)

    reachable = find_reachable_nodes(edges, top_module)
    filtered_edges = filter_edges(edges, reachable, defined_modules)
    depths = compute_depths(filtered_edges, top_module)

    build_graphviz(filtered_edges, depths)

if __name__ == "__main__":
    main()
