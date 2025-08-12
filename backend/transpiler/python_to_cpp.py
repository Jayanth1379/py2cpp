import ast

IND = "    "

class Emitter:
    def __init__(self):
        self.lines = []
        self.level = 0
        self.scopes = [set()]
    def write(self, s): self.lines.append(IND*self.level + s)
    def indent(self): self.level += 1
    def dedent(self): self.level -= 1
    def render(self): return "\n".join(self.lines)
    def declare(self, name:str): self.scopes[-1].add(name)
    def is_declared(self, name:str) -> bool: return any(name in s for s in self.scopes)
    def push_scope(self): self.scopes.append(set())
    def pop_scope(self): self.scopes.pop()

def _cpp_string_literal(py: str) -> str:
    s = py.replace("\\", "\\\\").replace("\"", "\\\"")
    s = s.replace("\n", "\\n").replace("\t", "\\t")
    return f"string(\"{s}\")"

def has_return(fn: ast.FunctionDef) -> bool:
    class Finder(ast.NodeVisitor):
        def __init__(self): self.found = False
        def visit_Return(self, node): self.found = True
    f = Finder()
    for n in fn.body: f.visit(n)
    return f.found

def py_to_cpp(py_code: str) -> str:
    tree = ast.parse(py_code)
    em = Emitter()

    em.write('#include <bits/stdc++.h>')
    em.write('using namespace std;')
    em.write('')
    em.write('// ------------------- FAST I/O -------------------')
    em.write('#define fastio ios::sync_with_stdio(false); cin.tie(nullptr)')
    em.write("#define endl '\\n'")
    em.write('')
    em.write('// ------------------- SHORTCUTS -------------------')
    em.write('#define all(x) (x).begin(), (x).end()')
    em.write('#define rall(x) (x).rbegin(), (x).rend()')
    em.write('#define pb push_back')
    em.write('#define ff first')
    em.write('#define ss second')
    em.write('#define sz(x) ((int)(x).size())')
    em.write('using ll = long long;')
    em.write('using ld = long double;')
    em.write('using pii = pair<int,int>;')
    em.write('using pll = pair<ll,ll>;')
    em.write('using vi = vector<int>;')
    em.write('using vll = vector<ll>;')
    em.write('')
    em.write('// ------------------- CONSTANTS -------------------')
    em.write('const ll INF = 1e18;')
    em.write('const int MOD = 1e9 + 7;')
    em.write('const ld EPS = 1e-9;')
    em.write('const int dx[4] = {1, 0, -1, 0};')
    em.write('const int dy[4] = {0, 1, 0, -1};')
    em.write('')
    em.write('// ------------------- DEBUG (comment out in CF) -------------------')
    em.write('#ifdef LOCAL')
    em.write('#define debug(x) cerr << #x << " = " << (x) << endl')
    em.write('#else')
    em.write('#define debug(x)')
    em.write('#endif')
    em.write('')
    em.write('// ---- helpers ----')
    em.write('template<typename T> void _print(const T& x){ cout << x; }')
    em.write('template<typename T, typename... R> void _print(const T& x, const T&... r){ cout << x; ((cout << \' \' << r), ...); }')
    em.write('static inline long long read_int(){ long long x; if(!(cin>>x)) return 0; return x; }')
    em.write('static inline string read_line(){ string s; if(cin.peek()==\'\\n\') cin.get(); getline(cin, s); return s; }')
    em.write('static inline vector<long long> read_int_list(){ string s = read_line(); istringstream iss(s); vector<long long> a; long long x; while(iss>>x) a.push_back(x); return a; }')
    em.write('static inline long long to_ll(const string& s){ try{ size_t p; long long v=stoll(s,&p); return v; }catch(...){ return 0; } }')
    em.write('static inline double to_double(const string& s){ try{ size_t p; double v=stod(s,&p); return v; }catch(...){ return 0; } }')
    em.write('')

    funcs, toplevel = [], []
    for node in tree.body:
        (funcs if isinstance(node, ast.FunctionDef) else toplevel).append(node)

    for fn in funcs: emit_function(fn, em)

    em.write('int main(){')
    em.indent(); em.write('fastio;'); em.write(''); em.push_scope()
    for stmt in toplevel: emit_stmt(stmt, em)
    em.write('return 0;')
    em.pop_scope(); em.dedent(); em.write('}')
    return em.render()

def emit_function(fn: ast.FunctionDef, em: Emitter):
    ret_auto = has_return(fn)
    params = [f"auto {a.arg}" for a in fn.args.args]
    sig = f"{'auto' if ret_auto else 'void'} {fn.name}({', '.join(params)})"
    em.write(sig + " {")
    em.indent(); em.push_scope()
    for s in fn.body: emit_stmt(s, em)
    em.pop_scope(); em.dedent(); em.write("}\n")

def _emit_unpack(names, list_expr, em: Emitter):
    tmp = "__tmp_unpack__"
    em.write(f"auto {tmp} = {list_expr};")
    for i, n in enumerate(names):
        decl = "" if em.is_declared(n) else "auto "
        if not em.is_declared(n): em.declare(n)
        em.write(f"{decl}{n} = {tmp}.size()>{i} ? {tmp}[{i}] : 0;")

def emit_stmt(node, em: Emitter):
    if isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Tuple):
        target = node.targets[0]
        names = []
        for elt in target.elts:
            if isinstance(elt, ast.Name): names.append(elt.id)
            else: em.write("// [unsupported: complex unpack]"); return
        if isinstance(node.value, ast.Call) and isinstance(node.value.func, ast.Name) and node.value.func.id == "map":
            args = node.value.args
            if len(args) == 2 and isinstance(args[0], ast.Name) and args[0].id == "int":
                if isinstance(args[1], ast.Call) and isinstance(args[1].func, ast.Attribute) and args[1].func.attr == "split":
                    _emit_unpack(names, "read_int_list()", em); return
        if isinstance(node.value, ast.List):
            _emit_unpack(names, emit_expr(node.value, em), em); return
        em.write("// [unsupported: tuple unpacking pattern not recognized]")
        return

    if isinstance(node, ast.Assign):
        tgt_node = node.targets[0]
        tgt = emit_expr(tgt_node, em)
        val = emit_expr(node.value, em)
        if isinstance(tgt_node, ast.Name) and not em.is_declared(tgt):
            em.declare(tgt); em.write(f"auto {tgt} = {val};")
        else:
            em.write(f"{tgt} = {val};")
        return

    if isinstance(node, ast.AugAssign):
        em.write(f"{emit_expr(node.target, em)} {emit_op(node.op)}= {emit_expr(node.value, em)};"); return

    if isinstance(node, ast.Expr):
        if isinstance(node.value, ast.Call) and getattr(node.value.func, "id", "") == "print":
            args = [emit_expr(a, em) for a in node.value.args]
            em.write(f"_print({', '.join(args)}); cout << '\\n';" if args else "cout << '\\n';"); return
        em.write(emit_expr(node.value, em) + ";"); return

    if isinstance(node, ast.If):
        em.write(f"if ({emit_expr(node.test, em)}) {{")
        em.indent(); [emit_stmt(s, em) for s in node.body]; em.dedent()
        if node.orelse:
            chain = node.orelse
            while len(chain) == 1 and isinstance(chain[0], ast.If):
                n = chain[0]
                em.write(f"}} else if ({emit_expr(n.test, em)}) {{")
                em.indent(); [emit_stmt(s, em) for s in n.body]; em.dedent()
                chain = n.orelse
            if chain:
                em.write("} else {"); em.indent(); [emit_stmt(s, em) for s in chain]; em.dedent(); em.write("}")
            else:
                em.write("}")
        else:
            em.write("}")
        return

    if isinstance(node, ast.While):
        em.write(f"while ({emit_expr(node.test, em)}) {{"); em.indent()
        [emit_stmt(s, em) for s in node.body]; em.dedent(); em.write("}"); return

    if isinstance(node, ast.For):
        it = node.iter
        if isinstance(it, ast.Call) and getattr(it.func, "id", "") == "range":
            args = [emit_expr(a, em) for a in it.args]
            var = emit_expr(node.target, em)
            decl = ""
            if isinstance(node.target, ast.Name) and not em.is_declared(var):
                em.declare(var); decl = "auto "
            if len(args) == 1:
                em.write(f"for ({decl}{var} = 0; {var} < {args[0]}; ++{var}) {{")
            elif len(args) == 2:
                em.write(f"for ({decl}{var} = {args[0]}; {var} < {args[1]}; ++{var}) {{")
            else:
                step = args[2]; cmp = "<"
                if step.startswith("-") or step.startswith("(-"): cmp = ">"
                em.write(f"for ({decl}{var} = {args[0]}; {var} {cmp} {args[1]}; {var} += {step}) {{")
            em.indent(); [emit_stmt(s, em) for s in node.body]; em.dedent(); em.write("}")
            return
        var = emit_expr(node.target, em)
        if isinstance(node.target, ast.Name) and not em.is_declared(var):
            em.declare(var); em.write(f"for (auto &{var} : {emit_expr(node.iter, em)}) {{")
        else:
            em.write(f"for (auto &{var} : {emit_expr(node.iter, em)}) {{")
        em.indent(); [emit_stmt(s, em) for s in node.body]; em.dedent(); em.write("}")
        return

    if isinstance(node, ast.Return):
        em.write(f"return {emit_expr(node.value, em)};"); return

    if isinstance(node, ast.Pass):
        em.write(";"); return

    em.write("// [unsupported in MVP]")

def emit_expr(node, em: Emitter) -> str:
    if isinstance(node, ast.Constant):
        if isinstance(node.value, bool): return "true" if node.value else "false"
        if isinstance(node.value, str): return _cpp_string_literal(node.value)
        return repr(node.value)
    if isinstance(node, ast.Name): return node.id
    if isinstance(node, ast.BinOp):
        if isinstance(node.op, ast.Pow): return f"pow({emit_expr(node.left, em)}, {emit_expr(node.right, em)})"
        return f"({emit_expr(node.left, em)} {emit_op(node.op)} {emit_expr(node.right, em)})"
    if isinstance(node, ast.UnaryOp): return f"({emit_uop(node.op)}{emit_expr(node.operand, em)})"
    if isinstance(node, ast.Compare):
        left = emit_expr(node.left, em)
        if len(node.ops) == 1:
            return f"({left} {emit_cmp(node.ops[0])} {emit_expr(node.comparators[0], em)})"
        parts, cur = [], left
        for op, rhs in zip(node.ops, node.comparators):
            r = emit_expr(rhs, em); parts.append(f"({cur} {emit_cmp(op)} {r})"); cur = r
        return "(" + " && ".join(parts) + ")"
    if isinstance(node, ast.BoolOp):
        join = " && " if isinstance(node.op, ast.And) else " || "
        return "(" + join.join(emit_expr(v, em) for v in node.values) + ")"
    if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
        fname = node.func.id
        if fname == "print":
            args = ", ".join(emit_expr(a, em) for a in node.args)
            return f"(_print({args}), 0)"
        if fname == "len": return f"((int){emit_expr(node.args[0], em)}.size())"
        if fname == "int":
            if len(node.args) == 1 and isinstance(node.args[0], ast.Call) and getattr(node.args[0].func, "id", "") == "input":
                return "read_int()"
            return f"(long long)({emit_any_to_ll(node.args[0], em)})"
        if fname == "float": return f"(double)({emit_any_to_double(node.args[0], em)})"
        if fname == "input": return "read_line()"
        if fname == "list":
            if len(node.args) == 1 and isinstance(node.args[0], ast.Call) and isinstance(node.args[0].func, ast.Name) and node.args[0].func.id == "map":
                m = node.args[0]
                if len(m.args) == 2 and isinstance(m.args[0], ast.Name) and m.args[0].id == "int":
                    if isinstance(m.args[1], ast.Call) and isinstance(m.args[1].func, ast.Attribute) and m.args[1].func.attr == "split":
                        return "read_int_list()"
            return "vector<long long>{}"
        if fname == "map": return "/*map*/0"
        if fname == "max" and len(node.args) == 2:
            return f"max({emit_expr(node.args[0], em)}, {emit_expr(node.args[1], em)})"
        if fname == "min" and len(node.args) == 2:
            return f"min({emit_expr(node.args[0], em)}, {emit_expr(node.args[1], em)})"
    if isinstance(node, ast.Attribute): return "/*attr*/0"
    if isinstance(node, ast.List):
        elems = ", ".join(emit_expr(e, em) for e in node.elts)
        return f"vector<long long>{{{elems}}}"
    if isinstance(node, ast.Subscript):
        base = emit_expr(node.value, em)
        if isinstance(node.slice, ast.Slice): return "/*slice*/0"
        idx = emit_expr(node.slice, em); return f"{base}[{idx}]"
    return "/*expr?*/0"

def emit_any_to_ll(arg, em: Emitter) -> str:
    if isinstance(arg, ast.Call) and isinstance(arg.func, ast.Name) and arg.func.id == "input":
        return "to_ll(read_line())"
    a = emit_expr(arg, em)
    return f"to_ll({a})" if a.startswith("string(") or a.startswith("read_line()") else a

def emit_any_to_double(arg, em: Emitter) -> str:
    if isinstance(arg, ast.Call) and isinstance(arg.func, ast.Name) and arg.func.id == "input":
        return "to_double(read_line())"
    a = emit_expr(arg, em)
    return f"to_double({a})" if a.startswith("string(") or a.startswith("read_line()") else a

def emit_op(op):
    return {ast.Add:"+", ast.Sub:"-", ast.Mult:"*", ast.Div:"/", ast.FloorDiv:"/", ast.Mod:"%", ast.BitOr:"|", ast.BitAnd:"&", ast.BitXor:"^", ast.LShift:"<<", ast.RShift:">>"}[type(op)]

def emit_uop(op): return {ast.UAdd:"+", ast.USub:"-", ast.Not:"!"}[type(op)]
def emit_cmp(op): return {ast.Lt:"<", ast.Le:"<=", ast.Gt:">", ast.Ge:">=", ast.Eq:"==", ast.NotEq:"!="}[type(op)]
