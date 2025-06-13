.from pyverilog.vparser.parser import parse
from pyverilog.ast_code_generator.codegen import ASTCodeGenerator
import sys


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
    if len(sys.argv) != 5:
        print("Usage: python script.py <verilog_file> <top_module> <new_module> <instance_names(comma-separated)>")
        sys.exit(1)

    verilog_file = sys.argv[1]
    top_module = sys.argv[2]
    new_module = sys.argv[3]
    instance_names = sys.argv[4].split(',')

    ast, _ = parse([verilog_file])
    instances = extract_instances(ast, top_module, instance_names)
    ports = {conn.argname for inst in instances for conn in inst.instances[0].portlist}

    new_module_code = create_new_module(new_module, instances)

    modify_top_module(ast, top_module, new_module, ports)

    generator = ASTCodeGenerator()
    modified_top_code = generator.visit(ast)

    with open(f"{new_module}.v", 'w') as f:
        f.write(new_module_code)

    with open(f"modified_{verilog_file}", 'w') as f:
        f.write(modified_top_code)

    print(f"Created module {new_module}.v and modified_{verilog_file}")
