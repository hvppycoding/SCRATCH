import re
import argparse
import difflib
from typing import Dict, List

def parse_replacement_modules(path: str) -> Dict[str, List[str]]:
    """Reads the replacement Verilog file and returns a dict of {module_name: lines}"""
    modules = {}
    with open(path, 'r') as f:
        lines = f.readlines()

    in_module = False
    current_name = ""
    current_lines = []
    in_block_comment = False

    for line in lines:
        stripped = line.strip()

        # Handle block comments
        if in_block_comment:
            current_lines.append(line)
            if '*/' in stripped:
                in_block_comment = False
            continue
        if '/*' in stripped and '*/' not in stripped:
            in_block_comment = True
            current_lines.append(line)
            continue

        if not in_module:
            match = re.match(r'\s*module\s+(\w+)', line)
            if match:
                in_module = True
                current_name = match.group(1)
                current_lines = [line]
        else:
            current_lines.append(line)
            if re.match(r'\s*endmodule\b', line) and not in_block_comment:
                in_module = False
                modules[current_name] = current_lines

    return modules

def stream_refactor_with_diff(original_path: str, replacement_modules: Dict[str, List[str]], output_path: str):
    """Stream process with difflib and comment out original if replaced."""
    with open(original_path, 'r') as infile, open(output_path, 'w') as outfile:
        in_module = False
        in_block_comment = False
        current_name = ""
        current_lines = []

        for line in infile:
            stripped = line.strip()

            # Handle block comments
            if in_block_comment:
                current_lines.append(line)
                if '*/' in stripped:
                    in_block_comment = False
                continue
            if '/*' in stripped and '*/' not in stripped:
                in_block_comment = True
                current_lines.append(line)
                continue

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
                if re.match(r'\s*endmodule\b', line) and not in_block_comment:
                    in_module = False
                    if current_name in replacement_modules:
                        original_mod = current_lines
                        new_mod = replacement_modules[current_name]
                        matcher = difflib.SequenceMatcher(None, original_mod, new_mod)
                        for tag, i1, i2, j1, j2 in matcher.get_opcodes():
                            if tag == 'equal':
                                for l in original_mod[i1:i2]:
                                    outfile.write(l)
                            elif tag in ('replace', 'delete'):
                                for l in original_mod[i1:i2]:
                                    outfile.write(f"// {l.rstrip()}\n")
                            if tag in ('replace', 'insert'):
                                for l in new_mod[j1:j2]:
                                    outfile.write(l)
                    else:
                        for l in current_lines:
                            outfile.write(l)
                    current_lines = []

def main():
    parser = argparse.ArgumentParser(description="Verilog module replacer with difflib")
    parser.add_argument("original", help="Path to the original Verilog file")
    parser.add_argument("replacement", help="Path to the replacement Verilog file")
    parser.add_argument("output", help="Path to write the modified Verilog file")

    args = parser.parse_args()

    replacements = parse_replacement_modules(args.replacement)
    stream_refactor_with_diff(args.original, replacements, args.output)

if __name__ == "__main__":
    main()
