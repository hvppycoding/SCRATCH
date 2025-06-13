import argparse
from pyverilog.vparser.parser import parse
from pyverilog.ast_code_generator.codegen import ASTCodeGenerator
from pyverilog.vparser.ast import Decl, Input, Output, Inout
from collections import defaultdict

# Extract specified instances from a given module and remove them from the original module
def extract_instances(ast, module_name, instance_names):
    instances = []
    for module in ast.description.definitions:
        if module.name == module_name:
            new_items = []
            for item in module.items:
                if item.__class__.__name__ == "InstanceList" and item.instances[0].name in instance_names:
                    instances.append(item)
                else:
                    new_items.append(item)
            module.items = new_items
    return instances

# Build a lookup table for all module port directions (from Decl list containing Input/Output/Inout)
def build_module_port_directions(ast):
    port_directions = defaultdict(dict)
    for module in ast.description.definitions:
        if not hasattr(module, 'items'):
            continue
        for item in module.items:
            if isinstance(item, Decl):
                for decl in item.list:
                    if isinstance(decl, (Input, Output, Inout)):
                        direction = decl.__class__.__name__.lower()
                        port_directions[module.name][decl.name] = direction
    return port_directions

# Determine port directions based on instance port connections and module declarations
# Handles both named and positional port connections
def determine_port_direction(instances, port_directions):
    net_dir_map = defaultdict(set)

    for inst in instances:
        module_name = inst.module
        module_ports = list(port_directions[module_name].items())
        for conn_index, conn in enumerate(inst.instances[0].portlist):
            net = conn.argname.name
            if conn.portname is not None:
                port = conn.portname
            else:
                if conn_index < len(module_ports):
                    port = module_ports[conn_index][0]
                else:
                    continue

            direction = port_directions[module_name].get(port, None)
            if direction:
                net_dir_map[net].add(direction)

    final_ports = {}
    for net, directions in net_dir_map.items():
        if 'output' in directions:
            final_ports[net] = 'output'
        elif 'inout' in directions:
            final_ports[net] = 'inout'
        else:
            final_ports[net] = 'input'

    return final_ports

# Create a new Verilog module by grouping instances and determining nets as ports
def create_new_module(module_name, instances, ports):
    port_list = ', '.join(f'{ports[p]} {p}' for p in ports)
    module_code = f"module {module_name}({port_list});\n"

    for inst in instances:
        inst_code = ASTCodeGenerator().visit(inst)
        module_code += f"    {inst_code}\n"

    module_code += "endmodule\n"
    return module_code

# Modify the original top-level module to instantiate the newly created module
def modify_top_module(ast, top_module_name, new_module_name, ports):
    for module in ast.description.definitions:
        if module.name == top_module_name:
            port_map = ', '.join(f".{p}({p})" for p in ports)
            instantiation = f"module dummy; {new_module_name} u_{new_module_name}({port_map}); endmodule"
            inst_ast, _ = parse([instantiation])
            module.items.append(inst_ast.description.definitions[0].items[0])


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-v', '--verilog', required=True, help='Input Verilog file')
    parser.add_argument('-top', '--top_module', required=True, help='Top module name')
    parser.add_argument('-insta_list', required=True, help='File containing instance names to extract')

    args = parser.parse_args()

    with open(args.insta_list, 'r') as f:
        instance_names = [line.strip() for line in f.readlines() if line.strip()]

    ast, _ = parse([args.verilog])
    instances = extract_instances(ast, args.top_module, instance_names)
    module_port_directions = build_module_port_directions(ast)
    ports = determine_port_direction(instances, module_port_directions)

    new_module_name = "new_module"
    new_module_code = create_new_module(new_module_name, instances, ports)

    modify_top_module(ast, args.top_module, new_module_name, ports)

    generator = ASTCodeGenerator()
    modified_top_code = generator.visit(ast)

    with open(f"{new_module_name}.v", 'w') as f:
        f.write(new_module_code)

    with open(f"modified_{args.verilog}", 'w') as f:
        f.write(modified_top_code)

    print(f"Created module {new_module_name}.v and modified_{args.verilog}")
