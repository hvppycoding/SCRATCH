# Re-imports after code execution environment reset
import re
from typing import List, Tuple, Optional, Dict
import difflib

class VerilogModule:
    def __init__(self, name: str, start_line: int):
        self.name = name
        self.start_line = start_line
        self.end_line = None
        self.lines = []

    def add_line(self, line: str):
        self.lines.append(line)

    def finalize(self, end_line: int):
        self.end_line = end_line

    def get_text(self) -> str:
        return '\n'.join(self.lines)

def fsm_parse_verilog_modules(lines: List[str]) -> List[VerilogModule]:
    modules = []
    in_module = False
    in_block_comment = False
    current_module: Optional[VerilogModule] = None

    for idx, line in enumerate(lines):
        stripped = line.strip()

        if in_block_comment:
            if '*/' in stripped:
                in_block_comment = False
            if in_module:
                current_module.add_line(line)
            continue

        if '/*' in stripped:
            if '*/' not in stripped:
                in_block_comment = True
            if in_module:
                current_module.add_line(line)
            continue

        if not in_module:
            mod_match = re.match(r'\s*module\s+(\w+)', line)
            if mod_match:
                mod_name = mod_match.group(1)
                current_module = VerilogModule(mod_name, idx)
                current_module.add_line(line)
                in_module = True
        else:
            current_module.add_line(line)
            if re.match(r'\s*endmodule\b', line):
                current_module.finalize(idx)
                modules.append(current_module)
                current_module = None
                in_module = False

    return modules

def replace_modules_in_text(
    original_lines: List[str],
    replacement_modules: Dict[str, str]
) -> Tuple[List[str], Dict[str, List[str]]]:
    modules = fsm_parse_verilog_modules(original_lines)
    replaced_modules = {}
    output_lines = []
    current_line = 0

    for mod in modules:
        while current_line < mod.start_line:
            output_lines.append(original_lines[current_line])
            current_line += 1

        if mod.name in replacement_modules:
            original_mod_lines = mod.lines
            new_mod_lines = replacement_modules[mod.name].splitlines()
            diffed = []

            matcher = difflib.SequenceMatcher(None, original_mod_lines, new_mod_lines)
            for tag, i1, i2, j1, j2 in matcher.get_opcodes():
                if tag == 'equal':
                    diffed.extend(original_mod_lines[i1:i2])
                elif tag in ('replace', 'delete'):
                    diffed.extend([f"// {line}" for line in original_mod_lines[i1:i2]])
                if tag in ('replace', 'insert'):
                    diffed.extend(new_mod_lines[j1:j2])

            output_lines.extend(diffed)
            replaced_modules[mod.name] = new_mod_lines
        else:
            output_lines.extend(mod.lines)

        current_line = mod.end_line + 1

    output_lines.extend(original_lines[current_line:])
    return output_lines, replaced_modules

# Sample original Verilog content
demo_verilog = """
// This is a comment
/* multi-line
   comment */
module A(input wire x); // inline comment
  assign y = ~x;
endmodule

module B;
  // simple body
  wire z;
endmodule
"""

demo_replacements = {
    'A': """module A(input wire x);
  not n1(y, x);
endmodule"""
}

lines = demo_verilog.splitlines()
new_lines, replaced = replace_modules_in_text(lines, demo_replacements)

import pandas as pd
from ace_tools import display_dataframe_to_user

df = pd.DataFrame({
    "Module": list(replaced.keys()),
    "Updated Code": ["\n".join(v) for v in replaced.values()]
})
display_dataframe_to_user("Updated Verilog Modules", df)

"\n".join(new_lines)
