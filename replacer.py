import argparse
from pyverilog.vparser.parser import parse
from pyverilog.vparser.ast import InstanceList, Instance
from pyverilog.ast_code_generator.codegen import ASTCodeGenerator


def replace_module_instance(ast, replace_dict):
    changed = False
    for desc in ast.description.definitions:
        for item in desc.items:
            if isinstance(item, InstanceList):
                for inst in item.instances:
                    if isinstance(inst, Instance):
                        if inst.module in replace_dict:
                            old = inst.module
                            new = replace_dict[old]
                            print(f"Replacing instance '{inst.name}': {old} → {new}")
                            inst.module = new
                            changed = True
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
