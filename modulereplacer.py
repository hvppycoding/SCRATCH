import re
import argparse
from typing import Dict, List

def parse_replacement_modules(path: str) -> Dict[str, List[str]]:
    """Reads the replacement Verilog file and returns a dict of {module_name: lines}"""
    modules = {}
    with open(path, 'r') as f:
        lines = f.readlines()

    in_module = False
    current_name = ""
    current_lines = []

    for line in lines:
        if not in_module:
            match = re.match(r'\s*module\s+(\w+)', line)
            if match:
                in_module = True
                current_name = match.group(1)
                current_lines = [line]
        else:
            current_lines.append(line)
            if re.match(r'\s*endmodule\b', line):
                in_module = False
                modules[current_name] = current_lines
    return modules

def stream_refactor(original_path: str, replacement_modules: Dict[str, List[str]], output_path: str):
    """Reads original file line-by-line, replaces modules on-the-fly, writes to output."""
    with open(original_path, 'r') as infile, open(output_path, 'w') as outfile:
        in_module = False
        current_name = ""
        current_lines = []

        for line in infile:
            if not in_module:
                match = re.match(r'\s*module\s+(\w+)', line)
                if match:
                    in_module = True
                    current_name = match.group(1)
                    current_lines = [line]
                else:
                    outfile.write(line)
            else:
                current_lines.append(line)
                if re.match(r'\s*endmodule\b', line):
                    in_module = False
                    if current_name in replacement_modules:
                        for orig in current_lines:
                            outfile.write(f"// {orig.rstrip()}\n")
                        for repl in replacement_modules[current_name]:
                            outfile.write(repl)
                    else:
                        for orig in current_lines:
                            outfile.write(orig)
                    current_lines = []

def main():
    parser = argparse.ArgumentParser(description="Verilog module replacer")
    parser.add_argument("original", help="Path to the original Verilog file")
    parser.add_argument("replacement", help="Path to the replacement Verilog file")
    parser.add_argument("output", help="Path to write the modified Verilog file")

    args = parser.parse_args()

    replacements = parse_replacement_modules(args.replacement)
    stream_refactor(args.original, replacements, args.output)

if __name__ == "__main__":
    main()
