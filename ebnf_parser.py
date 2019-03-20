ebnf_in_ebnf = '''
syntax = production+
production = identifier ws \"::=\" expression ( \".\" / \";\" ) ws
expression = ws term ( ws \"|\" term )* ws
term = (ws factor)+
factor = identifier / literal / optional / list
optional = \"[\" expression \"]\"
list = \"{\" expression \"}\"
identifier = ~\"[a-zA-Z0-9_]+\"
literal = ~\"\\\".*?\\\"\"
ws = ~\"\s*\"
'''

import parsimonious
from ebnf_nodes import *

class EbnfASTVisitor(parsimonious.NodeVisitor):
    def generic_visit(self, node, children):
        return (node.text, children, node.expr_name)
    def visit_syntax(self, node, children):
        result = dict()
        result.update(children)
        return result
    def visit_production(self, node, children):
        children = self.nospaces(children)
        assert len(children) == 4
        assert isinstance(children[0], Identifier)
        assert children[1][0] == '::='
        # assert isinstance(children[2], Sequence)
        assert children[3][0] in [';', '.']
        return (children[0].ident, children[2])
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
        return Identifier(node.text)
    def visit_literal(self, node, children):
        return Literal(node.text)
    def visit_ws(self, node, children):
        return None
    def nospaces(self, nodes):
        return list(filter(lambda x: x != None, nodes))

_ebnf_grammar = parsimonious.Grammar(ebnf_in_ebnf)

def parse(source):
    return EbnfASTVisitor().visit(_ebnf_grammar.parse(source))
