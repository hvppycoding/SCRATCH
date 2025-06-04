import argparse
from pyverilog.vparser.parser import parse
from pyverilog.vparser.ast import InstanceList, Instance
from pyverilog.ast_code_generator.codegen import ASTCodeGenerator


def replace_module_instance(ast, replace_dict):
    changed = False
    for desc in ast.description.definitions:
        new_items = []
        for item in desc.items:
            if isinstance(item, InstanceList):
                old_module_name = item.module
                new_module_name = replace_dict.get(old_module_name, old_module_name)

                if old_module_name != new_module_name:
                    print(f"Replacing module: {old_module_name} → {new_module_name}")
                    changed = True

                    # 인스턴스 내부도 같이 바꿔주기
                    new_instances = []
                    for inst in item.instances:
                        new_inst = Instance(
                            name=inst.name,
                            module=new_module_name,  # ✅ 같이 바꿔줌
                            portlist=inst.portlist,
                            parameterlist=inst.parameterlist
                        )
                        new_instances.append(new_inst)

                    new_item = InstanceList(
                        module=new_module_name,
                        parameterlist=item.parameterlist,
                        instances=new_instances
                    )
                    new_items.append(new_item)
                else:
                    new_items.append(item)
            else:
                new_items.append(item)
        desc.items = new_items
    return ast if changed else None


def main():
    parser = argparse.ArgumentParser(description="Replace Verilog module instances.")
    parser.add_argument(
        "-i", "--inputs",
        nargs="+",
        help="Input Verilog file(s)",
        required=True
    )
    parser.add_argument(
        "-o", "--output",
        help="Output Verilog file (single merged output)",
        required=True
    )
    parser.add_argument(
        "--replace",
        nargs="+",
        help="Replacement pairs: old1=new1 old2=new2 ...",
        required=True
    )

    args = parser.parse_args()

    # Parse replacement pairs
    replace_dict = {}
    for pair in args.replace:
        if "=" not in pair:
            raise ValueError(f"Invalid format for replace pair: {pair}")
        old, new = pair.split("=", 1)
        replace_dict[old] = new

    # Parse multiple Verilog files
    ast, _ = parse(args.inputs)
    modified_ast = replace_module_instance(ast, replace_dict)

    if modified_ast:
        codegen = ASTCodeGenerator()
        new_code = codegen.visit(modified_ast)
        with open(args.output, 'w') as f:
            f.write(new_code)
        print(f"Modified file written to: {args.output}")
    else:
        print("No module instances replaced.")


if __name__ == "__main__":
    main()
