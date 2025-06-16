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
    tranif_cache[module_name] = tcount
    return tcount

def traverse_and_collect(module_name, path_prefix, rows):
    module = module_defs[module_name]
    for item in module.items:
        if isinstance(item, InstanceList):
            for inst in item.instances:
                if inst.module in module_defs:
                    tcount = recursive_tranif_count(inst.module)
                    rows.append({
                        'InstancePath': path_prefix + inst.name,
                        'ModuleName': inst.module,
                        'tranif0_count': tcount['tranif0'],
                        'tranif1_count': tcount['tranif1']
                    })
                    traverse_and_collect(inst.module, path_prefix + inst.name + ".", rows)
                elif inst.module in ('tranif0', 'tranif1'):
                    # primitive tranif 직접 인스턴스
                    count0 = 1 if inst.module == 'tranif0' else 0
                    count1 = 1 if inst.module == 'tranif1' else 0
                    rows.append({
                        'InstancePath': path_prefix + inst.name,
                        'ModuleName': inst.module,
                        'tranif0_count': count0,
                        'tranif1_count': count1
                    })
                else:
                    # 다른 primitive
                    rows.append({
                        'InstancePath': path_prefix + inst.name,
                        'ModuleName': inst.module,
                        'tranif0_count': 0,
                        'tranif1_count': 0
                    })

def main(top_module_name, verilog_files, csv_output):
    ast, _ = parse(verilog_files)
    global module_defs, leaf_cache, tranif_cache
    module_defs = build_module_defs(ast)
    leaf_cache = {}
    tranif_cache = {}

    if top_module_name not in module_defs:
        print(f"Error: Top module '{top_module_name}' not found.")
        return

    # 디자인 전체 leaf module stdout 출력
    leaf_modules = set()
    for modname in module_defs:
        if is_leaf_module(modname):
            leaf_modules.add(modname)
    print("Leaf modules found in design (unique):")
    for m in sorted(leaf_modules):
        print(m)

    # TOP 하위 instance tranif 집계
    rows = []
    traverse_and_collect(top_module_name, top_module_name + ".", rows)

    # CSV 출력
    with open(csv_output, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=['InstancePath', 'ModuleName', 'tranif0_count', 'tranif1_count'])
        writer.writeheader()
        writer.writerows(rows)
    print(f"TOP hierarchy instance tranif counts written to {csv_output}")

if __name__ == '__main__':
    import sys
    if len(sys.argv) < 4:
        print("Usage: python script.py <top_module_name> <output_csv> <verilog_file1> [<verilog_file2> ...]")
    else:
        top_module_name = sys.argv[1]
        csv_output = sys.argv[2]
        verilog_files = sys.argv[3:]
        main(top_module_name, verilog_files, csv_output)
