from pyverilog.vparser.parser import parse
import pygraphviz as pgv
from collections import defaultdict

def extract_instantiations_with_counts(ast):
    """
    AST에서 모듈 간 instantiation 관계와 카운트를 추출
    :return: {(parent_module, child_module): count}
    """
    edge_counter = defaultdict(int)
    description = ast.description

    for module_def in description.definitions:
        if module_def.__class__.__name__ != 'ModuleDef':
            continue
        parent_name = module_def.name
        for item in module_def.items:
            if item.__class__.__name__ == 'InstanceList':
                child_module_name = item.module
                for _ in item.instances:
                    edge_counter[(parent_name, child_module_name)] += 1
    return edge_counter

def build_module_graph(verilog_files, output_file='module_graph.svg', layout_prog='sfdp'):
    """
    Verilog 파일들을 파싱하고, instantiation graph를 생성 후 SVG로 출력
    :param verilog_files: Verilog 파일 리스트
    :param output_file: 출력 파일명 (SVG 권장)
    :param layout_prog: graphviz 레이아웃 프로그램 ('dot', 'sfdp', 'fdp', 'neato')
    """
    print(f"Parsing Verilog files: {verilog_files}")
    ast, _ = parse(verilog_files)

    edge_counter = extract_instantiations_with_counts(ast)

    G = pgv.AGraph(directed=True)
    print(f"Adding {len(edge_counter)} edges...")

    for (parent, child), count in edge_counter.items():
        if count > 1:
            G.add_edge(parent, child, label=str(count))
        else:
            G.add_edge(parent, child)

    print(f"Layout using {layout_prog}...")
    G.layout(prog=layout_prog)
    G.draw(output_file)
    print(f"Graph saved to {output_file}")

if __name__ == "__main__":
    # 예시: 여러 파일을 넣을 수도 있음
    # verilog_files = ['top.v', 'sub1.v', 'sub2.v', ...]
    verilog_files = ['top.v']  # 여기 원하는 파일 목록 넣으세요
    build_module_graph(verilog_files)
