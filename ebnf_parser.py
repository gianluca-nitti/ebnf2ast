#!/usr/bin/env python3

# source: https://karmin.ch/ebnf/index
# TODO: usare NodeVisitor
ebnf_in_ebnf = '''
syntax     = production+
production = identifier ws \"::=\" expression ( \".\" / \";\" ) ws
expression = ws term ( ws \"|\" term )* ws
term       = (ws factor)+
factor     = (identifier)
           / (literal)
           / (optional)
           / (\"(\" expression \")\")
           / (list)
optional = \"[\" expression \"]\"
list = \"{\" expression \"}\"
identifier = ~\"[a-zA-Z0-9_]+\"
title      = literal
comment    = literal
literal    = ~\"\\\".*?\\\"\"
ws         = ~\"\s*\"
'''

import itertools, parsimonious

ebnf_grammar = parsimonious.Grammar(ebnf_in_ebnf)
with open('vhdl.ebnf', 'r') as f:
    input_ebnf = f.read()

class Ident:
    def __init__(self, ident):
        self.ident = ident
    def pp(self):
        return 'Ident( ' + self.ident + ' )'
class Literal:
    def __init__(self, literal):
        self.literal = literal
    def pp(self):
        return 'Literal( ' + self.literal + ' )'
class Optional:
    def __init__(self, content):
        self.content = content
    def pp(self):
        return 'Optional( ' + self.content.pp() + ' )'
class List:
    def __init__(self, content):
        self.content = content
    def pp(self):
        return 'List( ' + self.content.pp() + ' )'
class Sequence:
    def __init__(self, parts):
        self.parts = parts
    def pp(self):
        return 'Sequence( ' + ', '.join(map(lambda x: x.pp(), self.parts)) + ' )'
class Alternative:
    def __init__(self, alts):
        self.alts = alts
    def pp(self):
        return 'Alternative( ' + ', '.join(map(lambda x: x.pp(), self.alts)) + ' )'
class Rule:
    def __init__(self, lhs, rhs):
        self.lhs = lhs
        self.rhs = rhs
    def pp(self):
        return self.lhs + ' ::= ' + self.rhs.pp()
class EbnfASTVisitor(parsimonious.NodeVisitor):
    def generic_visit(self, node, children):
        return (node.text, children, node.expr_name) #node.text
    def visit_syntax(self, node, children):
        return children # list of productions
    def visit_production(self, node, children):
        children = self.nospaces(children)
        assert len(children) == 4
        assert isinstance(children[0], Ident)
        assert children[1][0] == '::='
        # assert isinstance(children[2], Sequence)
        assert children[3][0] in [';', '.']
        return Rule(children[0].ident, children[2])
    def visit_expression(self, node, children):
        children = self.nospaces(children)
        assert len(children) == 2
        alts = [children[0]]
        for alt in children[1][1]:
            alt_children = self.nospaces(alt[1])
            assert len(alt_children) == 2
            assert alt_children[0][0] == '|'
            alts.append(alt_children[1])
        if len(alts) > 1:
            return Alternative(alts)
        else:
            return alts[0]
    def visit_term(self, node, children):
        return Sequence(map(lambda x: x[1][1], children))
    def visit_factor(self, node, children):
        children = self.nospaces(children)
        assert len(children) in [0, 1]
        if len(children) == 0:
            return None
        return children[0]
    def visit_optional(self, node, children):
        assert len(children) == 3 and children[0][0] == '[' and children[2][0] == ']'
        return Optional(children[1])
    def visit_list(self, node, children):
        assert len(children) == 3 and children[0][0] == '{' and children[2][0] == '}'
        return List(children[1])
    def visit_identifier(self, node, children):
        return Ident(node.text)
    def visit_literal(self, node, children):
        return Literal(node.text)
    def visit_ws(self, node, children):
        return None
    def nospaces(self, nodes):
        return list(filter(lambda x: x != None, nodes))

parseTree = ebnf_grammar.parse(input_ebnf)
ast = EbnfASTVisitor().visit(parseTree)
for prod in ast:
    print(prod.pp())
