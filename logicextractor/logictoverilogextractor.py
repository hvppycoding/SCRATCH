# eda/logic_netlist_generator.py

from pyeda.inter import exprvars, truthtable, espresso_tts, expr
import itertools


from typing import List, Dict
import pandas as pd
from pyeda.inter import expr, truthtable

class LogicToVerilogNetlist:

    @staticmethod
    def boolean_exprs_from_df(df: pd.DataFrame,
                              input_vars: List[str],
                              output_vars: List[str]) -> Dict[str, 'Expr']:
        """
        Converts a DataFrame truth table into PyEDA boolean expressions.
        
        df: pd.DataFrame with input/output columns
        input_vars: list of column names to use as inputs
        output_vars: list of column names to use as outputs

        Returns: Dict mapping each output var name to a PyEDA Expr
        """
        expr_vars = [expr(name) for name in input_vars]
        num_rows_expected = 2 ** len(input_vars)
        if len(df) != num_rows_expected:
            raise ValueError(f"Expected {num_rows_expected} rows, got {len(df)}")

        exprs = {}
        for out_var in output_vars:
            if out_var not in df.columns:
                raise ValueError(f"Output variable '{out_var}' not found in DataFrame")

            values = df[out_var].tolist()
            tt = truthtable(expr_vars, values)
            exprs[out_var] = tt.to_expr()

        return exprs


class LogicToVerilogNetlist:
    def __init__(self, output_wire_name="Y"):
        self.output_wire_name = output_wire_name

    def boolean_expr_from_truth_table(self, df, input_vars, output_var):
        input_exprs = exprvars('x', len(input_vars))
        minterms = []
        for _, row in df.iterrows():
            val = row[output_var]
            if val == 1:
                bits = tuple(row[var] for var in input_vars)
                minterms.append(bits)

        if not minterms:
            return expr(0)

        tt = truthtable(input_exprs, minterms=[
            1 if tuple(row[var] for var in input_vars) in minterms else 0
            for _, row in df.iterrows()
        ])
        simplified = espresso_tts(tt)[0].to_expr()
        return simplified

    def expr_to_verilog_netlist(self, e, module_name="example"):
        wires = []
        gate_count = itertools.count()

        def emit(e):
            if e.is_one():
                return "1'b1"
            elif e.is_zero():
                return "1'b0"
            elif e.is_var():
                return str(e)
            elif e.is_not():
                in1 = emit(e.x)
                out = f"w{next(gate_count)}"
                wires.append(f"not g{next(gate_count)}({out}, {in1});")
                return out
            elif e.is_and():
                inputs = [emit(arg) for arg in e.xs]
                out = f"w{next(gate_count)}"
                wires.append(f"and g{next(gate_count)}({out}, {', '.join(inputs)});")
                return out
            elif e.is_or():
                inputs = [emit(arg) for arg in e.xs]
                out = f"w{next(gate_count)}"
                wires.append(f"or g{next(gate_count)}({out}, {', '.join(inputs)});")
                return out
            elif e.is_xor():
                inputs = [emit(arg) for arg in e.xs]
                out = f"w{next(gate_count)}"
                wires.append(f"xor g{next(gate_count)}({out}, {', '.join(inputs)});")
                return out
            else:
                raise ValueError(f"Unsupported expression: {e}")

        output = emit(e)
        inputs = sorted(set(str(v) for v in e.support))
        ports = f"input {', '.join(inputs)}, output {self.output_wire_name}"
        verilog = f"module {module_name}({ports});\n"
        wire_names = [w.split()[1].split('(')[0] for w in wires if w.startswith(('and', 'or', 'not', 'xor'))]
        if wire_names:
            verilog += "  wire " + ", ".join(sorted(set(wire_names))) + ";\n"
        verilog += "  " + "\n  ".join(wires) + "\n"
        verilog += f"  assign {self.output_wire_name} = {output};\nendmodule"
        return verilog
