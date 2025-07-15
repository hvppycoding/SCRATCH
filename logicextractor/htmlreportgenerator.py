import os
import shutil
from typing import List, Dict
from jinja2 import Environment, FileSystemLoader, select_autoescape


class HTMLReportGenerator:
    def __init__(self, output_dir: str = "report"):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)
        self.modules = []

        # 템플릿 문자열
        self.index_template_str = """
        <!DOCTYPE html>
        <html>
        <head>
          <meta charset="UTF-8"><title>Module Summary</title>
          <style> table, th, td { border: 1px solid black; border-collapse: collapse; padding: 4px; } </style>
        </head>
        <body>
        <h1>Module Summary</h1>
        <table>
        <thead>
        <tr><th>Module</th><th>Inputs</th><th>Outputs</th><th>FFs</th><th>Connected</th><th>Issues</th></tr>
        </thead>
        <tbody>
        {% for m in modules %}
        <tr>
          <td><a href="module_{{ m.name }}.html">{{ m.name }}</a></td>
          <td>{{ m.inputs|length }}</td>
          <td>{{ m.outputs|length }}</td>
          <td>{{ m.num_ffs }}</td>
          <td>{{ "Yes" if m.connected else "No" }}</td>
          <td>{{ ", ".join(m.issues) if m.issues else "None" }}</td>
        </tr>
        {% endfor %}
        </tbody>
        </table>
        </body>
        </html>
        """

        self.detail_template_str = """
        <!DOCTYPE html>
        <html>
        <head>
          <meta charset="UTF-8"><title>Module: {{ mod.name }}</title>
          <style> pre { background: #f0f0f0; padding: 8px; border: 1px solid #ccc; } </style>
        </head>
        <body>
        <h1>Module: {{ mod.name }}</h1>

        <p><strong>Inputs:</strong> {{ mod.inputs }}</p>
        <p><strong>Outputs:</strong> {{ mod.outputs }}</p>
        <p><strong>Flip-Flops:</strong> {{ mod.num_ffs }}</p>
        <p><strong>Connected:</strong> {{ "Yes" if mod.connected else "No" }}</p>

        {% if mod.issues %}
        <h3>Issues</h3>
        <ul>{% for issue in mod.issues %}<li>{{ issue }}</li>{% endfor %}</ul>
        {% endif %}

        <h3>Assign Statements</h3>
        <pre>{% for a in mod.assigns %}{{ a }}
        {% endfor %}</pre>

        <h3>Gate Usage</h3>
        <ul>{% for gate, count in mod.gates.items() %}<li>{{ gate }}: {{ count }}</li>{% endfor %}</ul>

        {% if mod.graph_image %}
        <h3>Graph Visualization</h3>
        <img src="{{ mod.graph_image }}" alt="Graph for {{ mod.name }}" style="max-width:100%;">
        {% endif %}

        {% if mod.verilog_code %}
        <h3>Original Verilog Code</h3>
        <pre><code>{{ mod.verilog_code }}</code></pre>
        {% endif %}

        <p><a href="index.html">← Back to Summary</a></p>
        </body>
        </html>
        """

        self.env = Environment(
            loader=FileSystemLoader("."),
            autoescape=select_autoescape(['html'])
        )
        self.index_template = self.env.from_string(self.index_template_str)
        self.detail_template = self.env.from_string(self.detail_template_str)

    def add_module(self, mod_info: Dict):
        """Add a module dict with keys: name, inputs, outputs, num_ffs, connected, issues, assigns, gates, verilog_code, graph_image"""
        self.modules.append(mod_info)

    def generate(self):
        """Generate the full report to the output_dir"""
        # index.html
        with open(os.path.join(self.output_dir, "index.html"), "w") as f:
            f.write(self.index_template.render(modules=self.modules))

        # module detail pages
        for mod in self.modules:
            html = self.detail_template.render(mod=mod)
            with open(os.path.join(self.output_dir, f"module_{mod['name']}.html"), "w") as f:
                f.write(html)

            # copy image if present
            if "graph_image" in mod and mod["graph_image"]:
                src = mod["graph_image"]
                dst = os.path.join(self.output_dir, os.path.basename(src))
                if os.path.exists(src):
                    shutil.copy(src, dst)
