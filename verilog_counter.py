from pyverilog.vparser.parser import parse
from pyverilog.vparser.ast import ModuleDef, InstanceList, Instance
import csv

def build_module_defs(ast):
    return {d.name: d for d in ast.description.definitions if isinstance(d, ModuleDef)}

def is_leaf_module(module_name):
    if module_name in leaf_cache:
        return leaf_cache[module_name]
    module = module_defs[module_name]
    for item in module.items:
        if isinstance(item, InstanceList):
            leaf_cache[module_name] = False
            return False
    leaf_cache[module_name] = True
    return True

def recursive_tranif_count(module_name):
    if module_name in tranif_cache:
        return tranif_cache[module_name]
    
    tcount = {'tranif0': 0, 'tranif1': 0}
    module = module_defs[module_name]
    
    for item in module.items:
        if isinstance(item, InstanceList):
            for inst in item.instances:
                if inst.module == 'tranif0':
                    tcount['tranif0'] += 1
                elif inst.module == 'tranif1':
                    tcount['tranif1'] += 1
                elif inst.module in module_defs:
                    child_tcount = recursive_tranif_count(inst.module)
                    tcount['tranif0'] += child_tcount['tranif0']
                    tcount['tranif1'] += child_tcount['tranif1']
                # primitive는 tranif 아닌 경우 무시
    tranif_cache[module_name] = tcount
    return tcount

def traverse_for_depth(module_name, path, depth):
    tcount = recursive_tranif_count(module_name)
    global max_depth, max_depth_path
    if tcount['tranif0'] > 0 or tcount['tranif1'] > 0:
        if depth > max_depth:
            max_depth = depth
            max_depth_path = ' > '.join(path)

    module = module_defs[module_name]
    for item in module.items:
        if isinstance(item, InstanceList):
            for inst in item.instances:
                if inst.module in module_defs:
                    traverse_for_depth(inst.module, path + [inst.name], depth + 1)

def main(top_module_name, verilog_files, leaf_output_csv):
    ast, _ = parse(verilog_files)
    global module_defs, leaf_cache, tranif_cache, max_depth, max_depth_path
    module_defs = build_module_defs(ast)
    leaf_cache = {}
    tranif_cache = {}
    max_depth = -1
    max_depth_path = ""

    if top_module_name not in module_defs:
        print(f"Error: Top module '{top_module_name}' not found.")
        return

    # 디자인 전체 leaf module + 재귀 tranif count
    leaf_modules = []
    for modname in module_defs:
        if is_leaf_module(modname):
            tcount = recursive_tranif_count(modname)
            leaf_modules.append({
                'ModuleName': modname,
                'tranif0_count': tcount['tranif0'],
                'tranif1_count': tcount['tranif1']
            })

    # leaf module 출력
    with open(leaf_output_csv, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=['ModuleName', 'tranif0_count', 'tranif1_count'])
        writer.writeheader()
        writer.writerows(leaf_modules)
    print(f"Design-wide unique leaf modules with recursive tranif count written to {leaf_output_csv}")

    # 최대 tranif 깊이 + 경로 탐색
    traverse_for_depth(top_module_name, [top_module_name], 0)
    if max_depth >= 0:
        print(f"Maximum tranif depth: {max_depth}")
        print(f"Path: {max_depth_path}")
    else:
        print("No tranif0 or tranif1 found in design hierarchy.")

if __name__ == '__main__':
    import sys
    if len(sys.argv) < 4:
        print("Usage: python script.py <top_module_name> <leaf_output_csv> <verilog_file1> [<verilog_file2> ...]")
    else:
        top_module_name = sys.argv[1]
        leaf_output_csv = sys.argv[2]
        verilog_files = sys.argv[3:]
        main(top_module_name, verilog_files, leaf_output_csv)
