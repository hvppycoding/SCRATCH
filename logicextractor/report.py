import os
from jinja2 import Environment, FileSystemLoader, select_autoescape
import shutil

# 예시 모듈 데이터
modules = [
    {
        "name": "adder",
        "inputs": ["A", "B"],
        "outputs": ["Y"],
        "num_ffs": 0,
        "connected": True,
        "issues": [],
        "assigns": ["assign Y = (A & ~B) | (~A & B);"],
        "gates": {"AND": 2, "OR": 1, "NOT": 2},
        "verilog_code": """module adder(input A, input B, output Y);
  assign Y = A ^ B;
endmodule""",
        "graph_image": "module_adder.png",  # optional
    },
    {
        "name": "fsm_ctrl",
        "inputs": ["clk", "reset", "in1", "in2"],
        "outputs": ["out"],
        "num_ffs": 3,
        "connected": False,
        "issues": ["Disconnected net", "Unused input: in2"],
        "assigns": ["assign out = state[0] & ~reset;"],
        "gates": {"AND": 1, "NOT": 1},
        "verilog_code": """module fsm_ctrl(input clk, input reset, input in1, input in2, output out);
// FSM logic here
endmodule""",
        "graph_image": "module_fsm_ctrl.png",
    }
]

# 디렉터리 생성
report_dir = "report"
os.makedirs(report_dir, exist_ok=True)

# 템플릿 문자열 정의
index_template_str = """
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

detail_template_str = """
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

# Jinja2 템플릿 엔진 준비
env = Environment(loader=FileSystemLoader("."), autoescape=select_autoescape(['html']))
index_template = env.from_string(index_template_str)
detail_template = env.from_string(detail_template_str)

# index.html 생성
with open(os.path.join(report_dir, "index.html"), "w") as f:
    f.write(index_template.render(modules=modules))

# 각 모듈 상세 페이지 생성
for mod in modules:
    html = detail_template.render(mod=mod)
    with open(os.path.join(report_dir, f"module_{mod['name']}.html"), "w") as f:
        f.write(html)

    # graph 이미지가 있다면 복사 (실제 생성은 사용자가 수행해야 함)
    if "graph_image" in mod:
        image_path = mod["graph_image"]
        if os.path.exists(image_path):
            shutil.copy(image_path, os.path.join(report_dir, image_path))
