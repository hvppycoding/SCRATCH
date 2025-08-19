#!/usr/bin/env python3
"""
submod-like pass using Pyverilog (robust PortArg + params)

Usage:
  python pyverilog_submod.py -f instance.list -t <target_module> [-n <new_module_name>] [-o out.v] netlist1.v [netlist2.v ...]

- Reads instance names from instance.list (one per line, '#' comments allowed)
- Moves those instances from <target_module> into a new submodule
- Replaces external net/slice/concat references with ports on the new submodule
- Connects the new submodule instance back into <target_module>

Key guarantees in this version:
- PortArg 케이스 전부 지원: 이름 기반(.p(x)), 순서 기반(positional), 포인터 a[i], 슬라이스 a[msb:lsb], 멀티비트 식별자 a, 컨캣 {..}, 반복 {N{..}}
- 파라미터 오버라이드: 이름 기반과 순서 기반 모두 원형대로 보존(deepcopy)
- 포트 방향 추론: 모듈 정의(존재 시)에서 방향을 가져오고, positional의 경우 포트 순서 매핑으로 방향 결정. 정의가 없으면 inout
- 슬라이스/포인터/컨캣의 폭 계산 정확화

Notes:
- 대상은 구조적 넷리스트(InstanceList/Decl/Ioport). assign/process/memory는 범위 밖(필요 시 확장 가능)
"""

import argparse
import sys
import copy
import re
from typing import Dict, Set, Tuple, List, Optional

from pyverilog.vparser.parser import parse
from pyverilog.vparser.ast import (
    ModuleDef,
    Ioport,
    Portlist,
    Port,
    Input,
    Output,
    Inout,
    Decl,
    Wire,
    Reg,
    InstanceList,
    Instance,
    PortArg,
    Width,
    IntConst,
    Identifier,
    Pointer,
    Partselect,
    Concat,
    Repeat,
)
from pyverilog.ast_code_generator.codegen import ASTCodeGenerator

# ------------------------------
# Utilities
# ------------------------------

def read_instance_list(path: str) -> Set[str]:
    names: Set[str] = set()
    with open(path) as f:
        for raw in f:
            line = raw.strip()
            if not line or line.startswith('#'):
                continue
            if '#' in line:
                line = line.split('#', 1)[0].strip()
            if line:
                names.add(line.split()[0])
    return names


def build_module_index(ast_root) -> Dict[str, ModuleDef]:
    mods: Dict[str, ModuleDef] = {}
    for d in getattr(ast_root.description, 'definitions', []):
        if isinstance(d, ModuleDef):
            mods[d.name] = d
    return mods


def module_port_directions(mod: ModuleDef) -> Dict[str, Tuple[str, Optional[Width]]]:
    """Return mapping: portname -> (dir, width_node or None)."""
    dirs: Dict[str, Tuple[str, Optional[Width]]] = {}
    for item in getattr(mod, 'items', []):
        if isinstance(item, Ioport):
            pname = item.first.name if isinstance(item.first, Port) else str(item.first)
            dirnode = item.second
            if isinstance(dirnode, Input):
                dirs[pname] = ('input', getattr(dirnode, 'width', None))
            elif isinstance(dirnode, Output):
                dirs[pname] = ('output', getattr(dirnode, 'width', None))
            elif isinstance(dirnode, Inout):
                dirs[pname] = ('inout', getattr(dirnode, 'width', None))
    return dirs


def module_port_order(mod: ModuleDef) -> List[str]:
    order: List[str] = []
    # ANSI-style: ModuleDef.portlist holds ordered Port entries
    pl = getattr(mod, 'portlist', None)
    if isinstance(pl, Portlist) and pl.ports:
        for p in pl.ports:
            if isinstance(p, Port):
                order.append(p.name)
            else:
                # Fallback: stringify
                order.append(str(p))
    else:
        # As a fallback, derive order from Ioport encounter order
        for item in getattr(mod, 'items', []):
            if isinstance(item, Ioport):
                pname = item.first.name if isinstance(item.first, Port) else str(item.first)
                order.append(pname)
    return order


def build_module_meta_index(ast_root) -> Dict[str, Dict[str, object]]:
    """Return mapping: modname -> { 'dirs': {p:(dir,width)}, 'order': [p0,p1,...] }"""
    idx: Dict[str, Dict[str, object]] = {}
    for d in getattr(ast_root.description, 'definitions', []):
        if isinstance(d, ModuleDef):
            idx[d.name] = {
                'dirs': module_port_directions(d),
                'order': module_port_order(d),
            }
    return idx


def decl_width_symtab(mod: ModuleDef) -> Dict[str, Optional[Width]]:
    """Map identifier -> Width node (or None for scalar). Includes ports, wires, regs."""
    sym: Dict[str, Optional[Width]] = {}
    for item in getattr(mod, 'items', []):
        if isinstance(item, Ioport):
            name = item.first.name if isinstance(item.first, Port) else str(item.first)
            dirnode = item.second
            sym[name] = getattr(dirnode, 'width', None)
    for item in getattr(mod, 'items', []):
        if isinstance(item, Decl):
            for obj in item.list:
                if hasattr(obj, 'name') and hasattr(obj, 'width'):
                    sym[obj.name] = getattr(obj, 'width', None)
    return sym


# -------------- numeric helpers --------------

def _parse_intconst_value(val: str) -> Optional[int]:
    """Parse IntConst textual value to Python int if possible.
    Supports decimal ("123"), and sized forms like 8'hFF, 6'o77, 4'b1010.
    Returns None if cannot be parsed.
    """
    val = val.replace('_', '')
    # unsized decimal like "123"
    if re.fullmatch(r"[0-9]+", val):
        return int(val, 10)
    m = re.fullmatch(r"(\d+)?'([bBhHdDoO])([0-9a-fA-FxXzZ]+)", val)
    if m:
        base_ch = m.group(2).lower()
        digits = m.group(3).lower()
        # treat x/z as 0 in numeric evaluation context
        digits = re.sub(r"[xz]", '0', digits)
        base = {'b':2, 'o':8, 'd':10, 'h':16}[base_ch]
        try:
            return int(digits, base)
        except ValueError:
            return None
    return None


def _eval_simple(node) -> Optional[int]:
    """Evaluate very simple constant expressions: IntConst, Plus, Minus, UnaryMinus.
    Return None if not resolvable.
    """
    from pyverilog.vparser.ast import Plus, Minus, Uminus
    if isinstance(node, IntConst):
        return _parse_intconst_value(node.value)
    if isinstance(node, Uminus):
        v = _eval_simple(node.right)
        return -v if v is not None else None
    if isinstance(node, (Plus, Minus)):
        l = _eval_simple(node.left)
        r = _eval_simple(node.right)
        if l is None or r is None:
            return None
        return l + r if node.__class__.__name__ == 'Plus' else l - r
    return None


def width_from_widthnode(width: Optional[Width]) -> int:
    """Compute declared vector width given a Width(msb, lsb). Defaults to 1 if unknown."""
    if width is None:
        return 1
    msb_v = _eval_simple(width.msb)
    lsb_v = _eval_simple(width.lsb)
    if msb_v is not None and lsb_v is not None:
        return abs(msb_v - lsb_v) + 1
    # Unknown params/expr → conservative 1
    return 1


def compute_expr_width(expr, sym: Dict[str, Optional[Width]]) -> int:
    if expr is None:
        return 1
    if isinstance(expr, Identifier):
        return width_from_widthnode(sym.get(expr.name))
    if isinstance(expr, Pointer):
        return 1
    if isinstance(expr, Partselect):
        # constant bounds → exact, else fall back to declared width of base
        msb_v = _eval_simple(expr.msb)
        lsb_v = _eval_simple(expr.lsb)
        if msb_v is not None and lsb_v is not None:
            return abs(msb_v - lsb_v) + 1
        if isinstance(expr.var, Identifier):
            return width_from_widthnode(sym.get(expr.var.name))
        return 1
    if isinstance(expr, IntConst):
        v = _parse_intconst_value(expr.value)
        if v is None:
            return 32  # unknown → 32-bit heuristic
        # minimal bitwidth to encode v (at least 1)
        return max(v.bit_length(), 1)
    if isinstance(expr, Concat):
        return sum(compute_expr_width(c, sym) for c in expr.list)
    if isinstance(expr, Repeat):
        times = _eval_simple(expr.times)
        times = times if times is not None else 1
        return times * compute_expr_width(expr.value, sym)
    # default conservative
    return 1


# -------------- identifier collection --------------

def collect_identifiers(expr, out: Set[str]):
    if expr is None:
        return
    if isinstance(expr, Identifier):
        out.add(expr.name)
    for c in getattr(expr, 'children', lambda: [])():
        collect_identifiers(c, out)


# -------------- instance helpers --------------

def list_instances(mod: ModuleDef):
    res = []
    for item in getattr(mod, 'items', []):
        if isinstance(item, InstanceList):
            for inst in item.instances:
                res.append((item, inst))  # (container InstanceList, Instance)
    return res


def gather_usage_sets(mod: ModuleDef, selected_names: Set[str]):
    sel_ids: Set[str] = set()
    others: Set[str] = set()
    port_names: Set[str] = set()

    for item in getattr(mod, 'items', []):
        if isinstance(item, Ioport):
            pname = item.first.name if isinstance(item.first, Port) else str(item.first)
            port_names.add(pname)

    for item in getattr(mod, 'items', []):
        if isinstance(item, InstanceList):
            for inst in item.instances:
                for arg in (inst.portlist or []):
                    ids: Set[str] = set()
                    collect_identifiers(arg.arg, ids)
                    if inst.name in selected_names:
                        sel_ids |= ids
                    else:
                        others |= ids
        # TODO: Assign 등 필요 시 확장
    return sel_ids, others, port_names


# -------------- external expr rewriter --------------
class ExternalRewriter:
    """Replace purely-external subexpressions with fresh port identifiers.

    external_ids: identifiers that are considered external to the submodule
    symtab: width lookup (declared widths in target module)
    dir_context: 'input' | 'output' | 'inout' from the instance port direction
    port_map: dict[str(expr_code)] -> {name, expr, width, dirs}
    """

    def __init__(self, external_ids: Set[str], symtab: Dict[str, Optional[Width]], dir_context: str, port_map: dict):
        self.external_ids = external_ids
        self.symtab = symtab
        self.dir_context = dir_context
        self.port_map = port_map
        self.codegen = ASTCodeGenerator()

    def is_pure_external(self, expr) -> bool:
        ids: Set[str] = set()
        collect_identifiers(expr, ids)
        return len(ids) > 0 and ids.issubset(self.external_ids)

    def key_for(self, expr) -> str:
        return self.codegen.visit(expr)

    def ensure_port(self, expr):
        key = self.key_for(expr)
        if key not in self.port_map:
            w = compute_expr_width(expr, self.symtab)
            base = self.default_port_name(expr)
            name = base
            i = 0
            existing = {v['name'] for v in self.port_map.values()}
            while name in existing or name is None:
                i += 1
                name = f"p{i}"
            self.port_map[key] = {'name': name, 'expr': expr, 'width': w, 'dirs': set([self.dir_context])}
        else:
            self.port_map[key]['dirs'].add(self.dir_context)
        return Identifier(self.port_map[key]['name'])

    def default_port_name(self, expr) -> Optional[str]:
        if isinstance(expr, Identifier):
            return expr.name
        if isinstance(expr, Pointer):
            if isinstance(expr.var, Identifier) and isinstance(expr.ptr, IntConst):
                return f"{expr.var.name}_{expr.ptr.value}"
        if isinstance(expr, Partselect):
            if (
                isinstance(expr.var, Identifier)
                and isinstance(expr.msb, IntConst)
                and isinstance(expr.lsb, IntConst)
            ):
                return f"{expr.var.name}_{expr.msb.value}_{expr.lsb.value}"
        return None

    def rewrite(self, expr):
        if expr is None:
            return None
        if self.is_pure_external(expr):
            return self.ensure_port(expr)

        # recursive rebuild for known node types
        if isinstance(expr, Identifier):
            return expr
        if isinstance(expr, Pointer):
            var = self.rewrite(expr.var)
            ptr = expr.ptr  # index as-is (usually IntConst/param)
            if var is expr.var:
                return expr
            return Pointer(var, ptr)
        if isinstance(expr, Partselect):
            var = self.rewrite(expr.var)
            msb, lsb = expr.msb, expr.lsb
            if var is expr.var:
                return expr
            return Partselect(var, msb, lsb)
        if isinstance(expr, Concat):
            newlist = [self.rewrite(e) for e in expr.list]
            return Concat(newlist)
        if isinstance(expr, Repeat):
            return Repeat(expr.times, self.rewrite(expr.value))

        # generic: try children, else return as-is
        try:
            _ = [self.rewrite(c) for c in expr.children()]
            return expr
        except Exception:
            return expr


# ------------------------------
# Main flow
# ------------------------------

def main():
    ap = argparse.ArgumentParser(description='submod-like pass using Pyverilog')
    ap.add_argument('-f', '--file', required=True, help='Path to instance list file')
    ap.add_argument('-t', '--target', required=True, help='Target module name')
    ap.add_argument('-n', '--name', default=None, help='New submodule name (optional)')
    ap.add_argument('-o', '--out', default='-', help='Output file (default: stdout)')
    ap.add_argument('verilog', nargs='+', help='Input Verilog files')
    args = ap.parse_args()

    inst_names = read_instance_list(args.file)
    if not inst_names:
        sys.stderr.write('[ERROR] Instance list is empty or not found.\n')
        sys.exit(1)

    ast, _ = parse(args.verilog)
    mod_index = build_module_index(ast)
    if args.target not in mod_index:
        sys.stderr.write(f"[ERROR] Module {args.target} not found.\n")
        sys.exit(1)

    target_mod = mod_index[args.target]
    module_meta = build_module_meta_index(ast)  # dirs + order for all modules
    symtab = decl_width_symtab(target_mod)

    all_insts = list_instances(target_mod)
    selected = [(il, inst) for (il, inst) in all_insts if inst.name in inst_names]
    if not selected:
        sys.stderr.write('[ERROR] No matching instances in target module.\n')
        sys.exit(1)

    sel_ids, other_ids, target_ports = gather_usage_sets(target_mod, inst_names)
    external_ids = (sel_ids & other_ids) | target_ports

    newmod_name = args.name or f"{args.target}_submod"
    # avoid name collision
    if newmod_name in mod_index:
        base = newmod_name
        i = 0
        while newmod_name in mod_index:
            i += 1
            newmod_name = f"{base}_{i}"

    # Rewrite selected instances (replace external subexprs with new ports)
    port_map = {}  # key -> {'name', 'expr', 'width', 'dirs'}
    rewritten_ilists = []
    for il, inst in selected:
        inst_modtype = il.module
        meta = module_meta.get(inst_modtype, {'dirs': {}, 'order': []})
        portdirs = meta['dirs']  # dict name -> (dir,width)
        order: List[str] = meta['order']

        new_portargs: List[PortArg] = []
        for idx, pa in enumerate(inst.portlist or []):
            # Determine effective portname even for positional connections
            pname = pa.portname if pa.portname is not None else (order[idx] if idx < len(order) else None)
            dirstr = 'inout'
            if pname is not None and pname in portdirs:
                dirstr = portdirs[pname][0]
            rewriter = ExternalRewriter(external_ids, symtab, dirstr, port_map)
            new_arg = rewriter.rewrite(pa.arg)
            # Preserve original naming style (named/positional)
            new_portargs.append(PortArg(pa.portname, new_arg))

        # Deepcopy parameter overrides exactly as-is (positional or named)
        new_ilist = InstanceList(inst_modtype, copy.deepcopy(il.paramlist), [Instance(inst_modtype, inst.name, new_portargs, None)])
        rewritten_ilists.append(new_ilist)

    # Build ioports for the new module
    ioports = []
    port_order = []
    for key, info in port_map.items():
        widthN = info['width']
        wnode = None if widthN == 1 else Width(IntConst(str(widthN - 1)), IntConst('0'))
        dirs = info['dirs']
        # Direction resolution
        if 'inout' in dirs or (('input' in dirs) and ('output' in dirs)):
            dirnode = Inout(info['name'], width=wnode)
        elif 'output' in dirs and 'input' not in dirs:
            dirnode = Output(info['name'], width=wnode)
        else:
            dirnode = Input(info['name'], width=wnode)
        ioports.append(Ioport(Port(info['name']), dirnode))
        port_order.append(info['name'])

    # Copy internal net declarations (used by selected but not external)
    internal_ids = sel_ids - external_ids
    decls_to_copy = []
    for item in getattr(target_mod, 'items', []):
        if isinstance(item, Decl):
            keep_objs = []
            for obj in item.list:
                if hasattr(obj, 'name') and obj.name in internal_ids:
                    keep_objs.append(copy.deepcopy(obj))
            if keep_objs:
                decls_to_copy.append(Decl(keep_objs))

    # Assemble the new module
    new_items = []
    new_items.extend(ioports)
    new_items.extend(decls_to_copy)
    new_items.extend(rewritten_ilists)
    newmod = ModuleDef(
        newmod_name,
        paramlist=None,
        portlist=Portlist([Port(n) for n in port_order]),
        items=new_items,
    )

    # Insert the new module into AST
    ast.description.definitions.append(newmod)

    # Remove selected instances from target module
    new_items_target = []
    for item in getattr(target_mod, 'items', []):
        if isinstance(item, InstanceList):
            remaining = [inst for inst in item.instances if inst.name not in inst_names]
            if remaining:
                new_items_target.append(InstanceList(item.module, copy.deepcopy(item.paramlist), remaining))
            # else: drop whole list
        else:
            new_items_target.append(item)
    target_mod.items = new_items_target

    # Add single instance of new module to target module (named connections for clarity)
    new_inst_portargs = []
    for key, info in port_map.items():
        new_inst_portargs.append(PortArg(info['name'], info['expr']))
    new_inst = Instance(newmod_name, f"u_{newmod_name}", new_inst_portargs, None)
    new_ilist = InstanceList(newmod_name, None, [new_inst])
    target_mod.items.append(new_ilist)

    # Emit code
    codegen = ASTCodeGenerator()
    result = codegen.visit(ast)
    if args.out == '-' or args.out == '/dev/stdout':
        sys.stdout.write(result)
    else:
        with open(args.out, 'w') as f:
            f.write(result)


if __name__ == '__main__':
    main()
