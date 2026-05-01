#!/usr/bin/env python3
"""
3806ICT Assignment 1 - Naive and improved backward proof search for first-order logic.
Implements the alternative sequent calculus LK' rules from Hou, Algorithm 2.

Input syntax examples:
  forall x. P(x) -> exists x. P(x)
  exists x. forall y. R(x,y) -> forall y. exists x. R(x,y)
  (P(a) or Q(a)) -> (Q(a) or P(a))

Connectives accepted:
  not, ~, ¬
  and, &, ∧
  or, |, ∨
  ->, =>, →
  forall, all, ∀
  exists, some, ∃
  top, true, ⊤
  bot, false, ⊥
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Tuple, List, Set, Dict, Iterable, Optional, FrozenSet
import argparse, csv, re, time, itertools, sys

# ------------------------------- AST ---------------------------------------
@dataclass(frozen=True)
class Term:
    name: str
    args: Tuple['Term', ...] = ()
    def __str__(self):
        return self.name if not self.args else f"{self.name}(" + ",".join(map(str,self.args)) + ")"

@dataclass(frozen=True)
class Formula:
    pass

@dataclass(frozen=True)
class Top(Formula):
    def __str__(self): return "⊤"
@dataclass(frozen=True)
class Bot(Formula):
    def __str__(self): return "⊥"
@dataclass(frozen=True)
class Atom(Formula):
    pred: str
    args: Tuple[Term, ...] = ()
    def __str__(self):
        return self.pred if not self.args else f"{self.pred}(" + ",".join(map(str,self.args)) + ")"
@dataclass(frozen=True)
class Not(Formula):
    a: Formula
    def __str__(self): return f"¬{paren(self.a)}"
@dataclass(frozen=True)
class And(Formula):
    a: Formula; b: Formula
    def __str__(self): return f"({self.a} ∧ {self.b})"
@dataclass(frozen=True)
class Or(Formula):
    a: Formula; b: Formula
    def __str__(self): return f"({self.a} ∨ {self.b})"
@dataclass(frozen=True)
class Imp(Formula):
    a: Formula; b: Formula
    def __str__(self): return f"({self.a} → {self.b})"
@dataclass(frozen=True)
class Forall(Formula):
    var: str; body: Formula
    def __str__(self): return f"∀{self.var}.{self.body}"
@dataclass(frozen=True)
class Exists(Formula):
    var: str; body: Formula
    def __str__(self): return f"∃{self.var}.{self.body}"

def paren(f: Formula) -> str:
    return str(f) if isinstance(f,(Atom,Top,Bot)) else f"({f})"

# ------------------------------- Lexer/parser ------------------------------
TOKEN_RE = re.compile(r"\s*(->|=>|[(),.]|[~¬!]|[&∧]|[|∨]|[A-Za-z_][A-Za-z0-9_]*|∀|∃|⊤|⊥|→)")
class Parser:
    def __init__(self, text: str):
        self.tokens = [t for t in TOKEN_RE.findall(text) if t.strip()]
        self.i = 0
    def peek(self) -> Optional[str]:
        return self.tokens[self.i] if self.i < len(self.tokens) else None
    def pop(self, expected=None) -> str:
        if self.i >= len(self.tokens): raise SyntaxError("unexpected end of input")
        t = self.tokens[self.i]
        if expected is not None and t != expected: raise SyntaxError(f"expected {expected}, got {t}")
        self.i += 1
        return t
    def parse(self) -> Formula:
        f = self.parse_imp()
        if self.peek() is not None: raise SyntaxError(f"unexpected token {self.peek()}")
        return f
    def parse_imp(self) -> Formula:
        left = self.parse_or()
        if self.peek() in ('->','=>','→'):
            self.pop(); right = self.parse_imp()
            return Imp(left, right)
        return left
    def parse_or(self) -> Formula:
        f = self.parse_and()
        while self.peek() in ('or','|','∨'):
            self.pop(); f = Or(f, self.parse_and())
        return f
    def parse_and(self) -> Formula:
        f = self.parse_unary()
        while self.peek() in ('and','&','∧'):
            self.pop(); f = And(f, self.parse_unary())
        return f
    def parse_unary(self) -> Formula:
        t = self.peek()
        if t in ('not','~','¬','!'):
            self.pop(); return Not(self.parse_unary())
        if t in ('forall','all','∀'):
            self.pop(); v = self.pop(); self.pop('.')
            return Forall(v, self.parse_imp())
        if t in ('exists','some','∃'):
            self.pop(); v = self.pop(); self.pop('.')
            return Exists(v, self.parse_imp())
        if t == '(':
            self.pop(); f = self.parse_imp(); self.pop(')'); return f
        if t in ('top','true','⊤'):
            self.pop(); return Top()
        if t in ('bot','false','⊥'):
            self.pop(); return Bot()
        return self.parse_atom()
    def parse_term(self) -> Term:
        name = self.pop()
        if self.peek() == '(':
            self.pop('('); args=[]
            if self.peek() != ')':
                while True:
                    args.append(self.parse_term())
                    if self.peek() == ',': self.pop(','); continue
                    break
            self.pop(')')
            return Term(name, tuple(args))
        return Term(name)
    def parse_atom(self) -> Formula:
        name = self.pop()
        args=[]
        if self.peek() == '(':
            self.pop('(')
            if self.peek() != ')':
                while True:
                    args.append(self.parse_term())
                    if self.peek() == ',': self.pop(','); continue
                    break
            self.pop(')')
        return Atom(name, tuple(args))

def parse_formula(s: str) -> Formula:
    return Parser(s).parse()

# ------------------------------- Utilities ---------------------------------
def substitute_term(t: Term, var: str, repl: Term) -> Term:
    if not t.args and t.name == var: return repl
    return Term(t.name, tuple(substitute_term(a,var,repl) for a in t.args))
def substitute(f: Formula, var: str, repl: Term) -> Formula:
    if isinstance(f, Atom): return Atom(f.pred, tuple(substitute_term(a,var,repl) for a in f.args))
    if isinstance(f, (Top,Bot)): return f
    if isinstance(f, Not): return Not(substitute(f.a,var,repl))
    if isinstance(f, And): return And(substitute(f.a,var,repl), substitute(f.b,var,repl))
    if isinstance(f, Or): return Or(substitute(f.a,var,repl), substitute(f.b,var,repl))
    if isinstance(f, Imp): return Imp(substitute(f.a,var,repl), substitute(f.b,var,repl))
    if isinstance(f, Forall): return f if f.var == var else Forall(f.var, substitute(f.body,var,repl))
    if isinstance(f, Exists): return f if f.var == var else Exists(f.var, substitute(f.body,var,repl))
    raise TypeError(f)

def terms_in_term(t: Term) -> Set[Term]:
    s={t}
    for a in t.args: s |= terms_in_term(a)
    return s
def terms_in_term_free(t: Term, bound: Set[str]) -> Set[Term]:
    if not t.args and t.name in bound:
        return set()
    s={t}
    for a in t.args:
        s |= terms_in_term_free(a, bound)
    return s
def terms_in_formula(f: Formula, bound: Optional[Set[str]]=None) -> Set[Term]:
    bound = set() if bound is None else set(bound)
    if isinstance(f, Atom):
        out=set()
        for a in f.args: out |= terms_in_term_free(a, bound)
        return out
    if isinstance(f, (Top,Bot)): return set()
    if isinstance(f, Not): return terms_in_formula(f.a, bound)
    if isinstance(f, (And,Or,Imp)): return terms_in_formula(f.a, bound) | terms_in_formula(f.b, bound)
    if isinstance(f, (Forall,Exists)):
        return terms_in_formula(f.body, bound | {f.var})
    return set()
def atoms(f: Formula) -> Set[Atom]:
    if isinstance(f, Atom): return {f}
    if isinstance(f, Not): return atoms(f.a)
    if isinstance(f, (And,Or,Imp)): return atoms(f.a) | atoms(f.b)
    if isinstance(f, (Forall,Exists)): return atoms(f.body)
    return set()

def complexity(f: Formula) -> int:
    if isinstance(f, (Atom,Top,Bot)): return 1
    if isinstance(f, Not): return 1 + complexity(f.a)
    if isinstance(f, (And,Or,Imp)): return 1 + complexity(f.a) + complexity(f.b)
    if isinstance(f, (Forall,Exists)): return 2 + complexity(f.body)
    return 1

@dataclass(frozen=True)
class Sequent:
    left: FrozenSet[Formula]
    right: FrozenSet[Formula]
    def __str__(self):
        L = ", ".join(map(str, sorted(self.left, key=str))) or "·"
        R = ", ".join(map(str, sorted(self.right, key=str))) or "·"
        return f"{L} ⊢ {R}"
    def is_closed(self) -> bool:
        return bool(self.left & self.right) or any(isinstance(x,Bot) for x in self.left) or any(isinstance(x,Top) for x in self.right)
    def terms(self) -> Set[Term]:
        out=set()
        for f in itertools.chain(self.left,self.right): out |= terms_in_formula(f)
        return out

@dataclass
class Result:
    valid: bool
    status: str
    steps: int
    closed_branches: int
    open_branches: int
    max_depth: int
    generated_terms: int
    time_ms: float

# ------------------------------- Prover ------------------------------------
class Prover:
    def __init__(self, strategy='baseline', max_steps=5000, max_depth=80, max_terms=8):
        self.strategy=strategy; self.max_steps=max_steps; self.max_depth=max_depth; self.max_terms=max_terms
        self.steps=0; self.closed=0; self.open=0; self.max_seen_depth=0; self.fresh_count=0
        self.cache=set(); self.inst_used: Dict[Tuple[str,str,str], Set[str]] = {}
    def prove(self, f: Formula) -> Result:
        start=time.perf_counter()
        self.steps=0; self.closed=0; self.open=0; self.max_seen_depth=0; self.fresh_count=0; self.cache=set(); self.inst_used={}
        root=Sequent(frozenset(), frozenset({f}))
        status='unknown'
        try:
            valid=self._prove_sequent(root,0)
            status='valid' if valid else 'not proved'
        except TimeoutError:
            valid=False; status='step/depth limit'
        return Result(valid,status,self.steps,self.closed,self.open,self.max_seen_depth,self.fresh_count,(time.perf_counter()-start)*1000)
    def _prove_sequent(self, s: Sequent, depth:int) -> bool:
        self.steps += 1; self.max_seen_depth=max(self.max_seen_depth, depth)
        if self.steps > self.max_steps or depth > self.max_depth: raise TimeoutError()
        if s.is_closed(): self.closed += 1; return True
        key=(s.left,s.right)
        if self.strategy!='baseline':
            if key in self.cache: self.open += 1; return False
            self.cache.add(key)
        apps=self.applicable(s)
        if not apps:
            self.open += 1; return False
        # In LK', non-branching safe rules are preferred, then branching, then quantifier-copying rules.
        if self.strategy=='baseline':
            apps.sort(key=lambda a: (a[0], a[1]))
        else:
            apps.sort(key=self.score_app)
        choices = apps[:1] if self.strategy == 'baseline' else apps
        for _,_,branches,_ in choices:
            # A branch-creating rule succeeds only if every branch closes.
            try:
                if all(self._prove_sequent(b, depth+1) for b in branches):
                    return True
            except TimeoutError:
                raise
            # Baseline is intentionally naive and does not backtrack over alternative rules.
            if self.strategy == 'baseline':
                return False
        return False
    def score_app(self, app):
        group, name, branches, main = app
        # Improved: prefer smaller sequents, formulas containing atoms that also occur on opposite side, and fewer branches.
        branch_penalty=len(branches)*3
        comp=complexity(main) if main else 1
        return (group, branch_penalty, -comp, name)
    def fresh(self) -> Term:
        self.fresh_count += 1
        return Term(f"c{self.fresh_count}")
    def candidate_terms(self, s: Sequent) -> List[Term]:
        terms = sorted(s.terms(), key=str)
        if not terms: terms=[Term('a')]
        if self.strategy!='baseline':
            # Prefer constants/simple terms, then complex terms; cap to avoid infinite quantifier churn.
            terms=sorted(terms, key=lambda t:(len(t.args), str(t)))[:self.max_terms]
        return terms
    def applicable(self, s: Sequent):
        apps=[]
        L=set(s.left); R=set(s.right)
        # Non-branching rules: group 1
        for f in sorted(L, key=str):
            if isinstance(f, And):
                apps.append((1,'∧L',[Sequent(frozenset((L-{f})|{f.a,f.b}),s.right)],f))
            elif isinstance(f, Not):
                apps.append((1,'¬L',[Sequent(frozenset(L-{f}),frozenset(R|{f.a}))],f))
            elif isinstance(f, Exists):
                t=self.fresh()
                apps.append((1,'∃L',[Sequent(frozenset((L-{f})|{substitute(f.body,f.var,t)}),s.right)],f))
        for f in sorted(R, key=str):
            if isinstance(f, Or):
                apps.append((1,'∨R',[Sequent(s.left,frozenset((R-{f})|{f.a,f.b}))],f))
            elif isinstance(f, Imp):
                apps.append((1,'→R',[Sequent(frozenset(L|{f.a}),frozenset((R-{f})|{f.b}))],f))
            elif isinstance(f, Not):
                apps.append((1,'¬R',[Sequent(frozenset(L|{f.a}),frozenset(R-{f}))],f))
            elif isinstance(f, Forall):
                t=self.fresh()
                apps.append((1,'∀R',[Sequent(s.left,frozenset((R-{f})|{substitute(f.body,f.var,t)}))],f))
        # Branching rules: group 2
        for f in sorted(R, key=str):
            if isinstance(f, And):
                apps.append((2,'∧R',[Sequent(s.left,frozenset((R-{f})|{f.a})), Sequent(s.left,frozenset((R-{f})|{f.b}))],f))
        for f in sorted(L, key=str):
            if isinstance(f, Or):
                apps.append((2,'∨L',[Sequent(frozenset((L-{f})|{f.a}),s.right), Sequent(frozenset((L-{f})|{f.b}),s.right)],f))
            elif isinstance(f, Imp):
                apps.append((2,'→L',[Sequent(frozenset(L-{f}),frozenset(R|{f.a})), Sequent(frozenset((L-{f})|{f.b}),s.right)],f))
        # Copying quantifier rules: group 3 (existing terms first, then fresh if none unused)
        for f in sorted(L, key=str):
            if isinstance(f, Forall):
                terms=self.candidate_terms(s); made=False
                for t in terms:
                    k=('∀L',str(f),f.var); used=self.inst_used.setdefault(k,set())
                    if str(t) not in used:
                        used.add(str(t)); made=True
                        apps.append((3,'∀L',[Sequent(frozenset(L|{substitute(f.body,f.var,t)}),s.right)],f))
                        break
                if not made and len(terms)<self.max_terms:
                    t=self.fresh(); apps.append((3,'∀L fresh',[Sequent(frozenset(L|{substitute(f.body,f.var,t)}),s.right)],f))
        for f in sorted(R, key=str):
            if isinstance(f, Exists):
                terms=self.candidate_terms(s); made=False
                for t in terms:
                    k=('∃R',str(f),f.var); used=self.inst_used.setdefault(k,set())
                    if str(t) not in used:
                        used.add(str(t)); made=True
                        apps.append((3,'∃R',[Sequent(s.left,frozenset(R|{substitute(f.body,f.var,t)}))],f))
                        break
                if not made and len(terms)<self.max_terms:
                    t=self.fresh(); apps.append((3,'∃R fresh',[Sequent(s.left,frozenset(R|{substitute(f.body,f.var,t)}))],f))
        return apps

def read_formulas(path: str) -> List[Tuple[str,Formula]]:
    out=[]
    with open(path, encoding='utf8') as f:
        for line in f:
            raw=line.strip()
            if not raw or raw.startswith('#'): continue
            name, text = raw.split(':',1) if ':' in raw else (f'f{len(out)+1}', raw)
            out.append((name.strip(), parse_formula(text.strip())))
    return out

def run_file(path, outcsv, max_steps=5000):
    rows=[]
    for name,f in read_formulas(path):
        for strat in ['baseline','improved']:
            r=Prover(strat, max_steps=max_steps, max_depth=60 if strat=='baseline' else 60, max_terms=5).prove(f)
            rows.append({'dataset':path,'formula':name,'strategy':strat,'status':r.status,'valid':r.valid,'steps':r.steps,'closed_branches':r.closed_branches,'open_branches':r.open_branches,'max_depth':r.max_depth,'fresh_terms':r.generated_terms,'time_ms':f'{r.time_ms:.3f}'})
    with open(outcsv,'w',newline='',encoding='utf8') as f:
        w=csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader(); w.writerows(rows)
    return rows

if __name__=='__main__':
    ap=argparse.ArgumentParser()
    ap.add_argument('input')
    ap.add_argument('--csv', default='results.csv')
    ap.add_argument('--max-steps', type=int, default=5000)
    args=ap.parse_args()
    rows=run_file(args.input,args.csv,args.max_steps)
    for row in rows:
        print(row)
