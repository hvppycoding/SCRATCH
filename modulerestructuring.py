import argparse
from pyverilog.vparser.parser import parse
from pyverilog.ast_code_generator.codegen import ASTCodeGenerator


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


def create_new_module(module_name, instances):
    ports = set()
    for inst in instances:
        for conn in inst.instances[0].portlist:
            ports.add(conn.argname)

    port_list = ', '.join(ports)
    module_code = f"module {module_name}({port_list});\n"

    for inst in instances:
        inst_code = ASTCodeGenerator().visit(inst)
        module_code += f"    {inst_code}\n"

    module_code += "endmodule\n"
    return module_code


def modify_top_module(ast, top_module_name, new_module_name, ports):
    for module in ast.description.definitions:
        if module.name == top_module_name:
            port_map = ', '.join(f".{p}({p})" for p in ports)
            instantiation = f"{new_module_name} u_{new_module_name}({port_map});"
            module.items.append(parse(instantiation).description.definitions[0].items[0])


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
    ports = {conn.argname for inst in instances for conn in inst.instances[0].portlist}

    new_module_name = "new_module"
    new_module_code = create_new_module(new_module_name, instances)

    modify_top_module(ast, args.top_module, new_module_name, ports)

    generator = ASTCodeGenerator()
    modified_top_code = generator.visit(ast)

    with open(f"{new_module_name}.v", 'w') as f:
        f.write(new_module_code)

    with open(f"modified_{args.verilog}", 'w') as f:
        f.write(modified_top_code)

    print(f"Created module {new_module_name}.v and modified_{args.verilog}")
