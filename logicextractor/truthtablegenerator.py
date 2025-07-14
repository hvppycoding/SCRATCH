# eda/transistor_extractor.py

import itertools
import pandas as pd

class TransistorLogicExtractor:
    def __init__(self, input_nodes, output_nodes, internal_nodes, vdd_nodes, gnd_nodes, conditional_edges):
        self.input_nodes = input_nodes
        self.output_nodes = output_nodes
        self.internal_nodes = internal_nodes
        self.vdd_nodes = vdd_nodes
        self.gnd_nodes = gnd_nodes
        self.conditional_edges = conditional_edges

    def simulate(self, input_state):
        node_values = {k: input_state.get(k, 'X') for k in self.input_nodes + self.internal_nodes + self.output_nodes}
        node_values.update({vdd: 1 for vdd in self.vdd_nodes})
        node_values.update({gnd: 0 for gnd in self.gnd_nodes})

        edges = []
        for ctrl_node, cond_fn, a, b in self.conditional_edges:
            if cond_fn(node_values):
                edges.append((a, b))
                edges.append((b, a))

        changed = True
        while changed:
            changed = False
            for src, dst in edges:
                if node_values.get(src) in [0, 1] and node_values.get(dst, 'X') == 'X':
                    node_values[dst] = node_values[src]
                    changed = True
        return {k: node_values.get(k, 'X') for k in self.output_nodes}

    def generate_truth_table(self):
        rows = []
        for bits in itertools.product([0, 1], repeat=len(self.input_nodes)):
            input_state = dict(zip(self.input_nodes, bits))
            output_state = self.simulate(input_state)
            row = {**input_state, **output_state}
            rows.append(row)
        return pd.DataFrame(rows)
