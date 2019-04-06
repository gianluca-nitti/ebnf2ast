_ebnf_spec = r'''
syntax = production+
production = identifier ws "::=" expression ( "." / ";" ) ws
expression = ws term ( ws "|" term )* ws
term = (ws factor)+
factor = identifier / literal / optional / list
optional = "[" expression "]"
list = "{" expression "}"
identifier = ~"[a-zA-Z0-9_]+"
literal = '"' ~'[^\"]*' '"'
ws = ~"\s*"
'''

import parsimonious

class EbnfASTVisitor(parsimonious.NodeVisitor):
    def __init__(self, nodes_mod):
        self._nodes_mod = nodes_mod
    def generic_visit(self, node, children):
        return (node.text, children, node.expr_name)
    def visit_syntax(self, node, children):
        result = dict()
        result.update(children)
        return result
    def visit_production(self, node, children):
        children = self.nospaces(children)
        assert len(children) == 4
        assert isinstance(children[0], self._nodes_mod.Identifier)
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
            return self._nodes_mod.Alternative(alts)
        else:
            return alts[0]
    def visit_term(self, node, children):
        return self._nodes_mod.Sequence(list(map(lambda x: x[1][1], children)))
    def visit_factor(self, node, children):
        children = self.nospaces(children)
        assert len(children) in [0, 1]
        if len(children) == 0:
            return None
        return children[0]
    def visit_optional(self, node, children):
        assert len(children) == 3 and children[0][0] == '[' and children[2][0] == ']'
        return self._nodes_mod.Optional(children[1])
    def visit_list(self, node, children):
        assert len(children) == 3 and children[0][0] == '{' and children[2][0] == '}'
        return self._nodes_mod.List(children[1])
    def visit_identifier(self, node, children):
        return self._nodes_mod.Identifier(node.text)
    def visit_literal(self, node, children):
        assert len(children) == 3 and children[0][0] == '\"' and children[2][0] == '\"'
        return self._nodes_mod.Literal(children[1][0])
    def visit_ws(self, node, children):
        return None
    def nospaces(self, nodes):
        return list(filter(lambda x: x != None, nodes))

_ebnf_grammar = parsimonious.Grammar(_ebnf_spec)

def parse(source, nodes_module):
    return EbnfASTVisitor(nodes_module).visit(_ebnf_grammar.parse(source))
