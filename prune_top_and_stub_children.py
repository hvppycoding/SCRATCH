#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PyVerilog로 다음을 수행:
  - TOP 모듈은 그대로 유지
  - TOP이 직접 인스턴스화한 하위 모듈들은 시그니처(파라미터, 포트)만 남기고 본문 제거
  - 나머지 모듈은 전부 제거
"""

import argparse
from pyverilog.vparser.parser import parse
from pyverilog.vparser.ast import (
    NodeVisitor, ModuleDef, Decl, Input, Output, Inout,
    Parameter, Localparam, InstanceList
)
from pyverilog.ast_code_generator.codegen import ASTCodeGenerator

# --- 1) TOP의 직접 자식 모듈 수집기 -----------------------------------------
class InstModuleCollector(NodeVisitor):
    def __init__(self):
        self.children = set()

    def visit_InstanceList(self, node: InstanceList):
        # InstanceList.module: 인스턴스화된 모듈의 이름 (str)
        if hasattr(node, 'module'):
            self.children.add(node.module)
        self.generic_visit(node)

# --- 2) TOP 추정(명시가 없을 때) ---------------------------------------------
def autodetect_top(ast_root, explicit_top=None):
    if explicit_top:
        return explicit_top

    modules = set()
    instantiated = set()
    for d in getattr(ast_root.description, 'definitions', []):
        if isinstance(d, ModuleDef):
            modules.add(d.name)
            col = InstModuleCollector()
            col.visit(d)
            instantiated |= col.children

    # 인스턴스되지 않은 정의를 TOP 후보로 보고 첫 번째를 선택
    candidates = [m for m in modules if m not in instantiated]
    return candidates[0] if candidates else None

# --- 3) 시그니처(포트/파라미터)만 남기기 --------------------------------------
def keep_signature_only(items):
    kept = []
    for item in items or []:
        if isinstance(item, Decl):
            # Decl 내부 요소 중 포트/파라미터 선언만 유지
            allowed_kinds = (Input, Output, Inout, Parameter, Localparam)
            filtered = [decl for decl in item.list if isinstance(decl, allowed_kinds)]
            if filtered:
                kept.append(Decl(filtered))
        # 그 외(Always, Assign, InstanceList, Generate 등)는 버림
    return kept

# --- 4) 메인 ---------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser(description="Keep TOP, stub its direct children, drop others (PyVerilog).")
    ap.add_argument('sources', nargs='+', help='Verilog sources (*.v)')
    ap.add_argument('-t', '--top', help='Top module name (if omitted, auto-detect)')
    ap.add_argument('-I', '--incdir', action='append', default=[], help='include search dir')
    ap.add_argument('-D', '--define', action='append', default=[], help='macro define (e.g. FOO=1)')
    ap.add_argument('-o', '--out', default='pruned.v', help='output verilog file')
    args = ap.parse_args()

    # PyVerilog 전처리 define 형식 맞추기
    defines = []
    for d in args.define:
        if '=' in d:
            k, v = d.split('=', 1)
            defines.append((k, v))
        else:
            defines.append((d, None))

    ast, _ = parse(
        args.sources,
        preprocess_include=args.incdir,
        preprocess_define=defines
    )

    top_name = autodetect_top(ast, args.top)
    if not top_name:
        raise SystemExit("ERROR: TOP을 찾지 못했습니다. --top 으로 지정하세요.")

    # TOP 정의 찾기
    top_def = None
    for d in ast.description.definitions:
        if isinstance(d, ModuleDef) and d.name == top_name:
            top_def = d
            break
    if top_def is None:
        raise SystemExit(f"ERROR: 지정한 TOP '{top_name}' 모듈 정의를 찾을 수 없습니다.")

    # TOP의 직접 하위 모듈 수집
    col = InstModuleCollector()
    col.visit(top_def)
    direct_children = col.children

    # 정의 목록 재구성
    new_defs = []
    for d in ast.description.definitions:
        if not isinstance(d, ModuleDef):
            # 모듈 외 정의는 모두 삭제
            continue

        if d.name == top_name:
            # TOP은 그대로 유지
            new_defs.append(d)
        elif d.name in direct_children:
            # 자식 모듈은 시그니처만 남김
            d.items = keep_signature_only(d.items)
            new_defs.append(d)
        else:
            # 그 외 모듈은 버림
            pass

    # 결과를 AST에 반영하고 코드 생성
    ast.description.definitions = tuple(new_defs)
    codegen = ASTCodeGenerator()
    verilog_out = codegen.visit(ast)

    with open(args.out, 'w', encoding='utf-8') as f:
        f.write(verilog_out)

    kept = [d.name for d in new_defs]
    print(f"[OK] Wrote {args.out}")
    print(f" Top      : {top_name}")
    print(f" Kept mods: {', '.join(kept)}")

if __name__ == '__main__':
    main()
