#!/usr/bin/env python3

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
import python_class_generator

class Alternative:
    next_nt_index = 1
    def __init__(self, alts):
        self.alts = alts
    def populate_node_type(self, nt, node_builder):
        result = []
        for alt in self.alts:
            alt_nt = node_builder('alternative_%d' % Alternative.next_nt_index, nt.name)
            result.extend(alt.populate_node_type(alt_nt, node_builder))
            result.append(alt_nt)
            Alternative.next_nt_index += 1
        return result
    def pp(self):
        return 'Alternative( ' + ', '.join(map(lambda x: x.pp(), self.alts)) + ' )'
class Sequence:
    def __init__(self, parts):
        self.parts = parts
    def populate_node_type(self, nt, node_builder):
        additional = []
        for part in self.parts:
            additional.extend(part.populate_node_type(nt, node_builder))
        return additional # TODO replace loop with some sort of map & reduce
    def pp(self):
        return 'Sequence( ' + ', '.join(map(lambda x: x.pp(), self.parts)) + ' )'
class Optional:
    next_nt_index = 1
    def __init__(self, content):
        self.content = content
    def populate_node_type(self, nt, node_builder):
        opt_nt = node_builder('optional_%d' % Optional.next_nt_index)
        nt.add_optional(opt_nt.name)
        result = [opt_nt]
        result.extend(self.content.populate_node_type(opt_nt, node_builder))
        Optional.next_nt_index += 1
        return result
    def pp(self):
        return 'Optional( ' + self.content.pp() + ' )'
class List:
    def __init__(self, content):
        self.content = content
    def populate_node_type(self, nt, node_builder):
        return [] # TODO
    def pp(self):
        return 'List( ' + self.content.pp() + ' )'
class Identifier:
    def __init__(self, ident):
        self.ident = ident
    def populate_node_type(self, nt, node_builder):
        nt.add_identifier(self.ident)
        return []
    def pp(self):
        return 'Identifier( ' + self.ident + ' )'
class Literal:
    def __init__(self, literal):
        self.literal = literal
    def populate_node_type(self, nt, node_builder):
        nt.add_literal(self.literal)
        return []
    def pp(self):
        return 'Literal( ' + self.literal + ' )'

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

if __name__ == '__main__':
    ebnf_grammar = parsimonious.Grammar(ebnf_in_ebnf)
    with open('vhdl.ebnf', 'r') as f:
        input_ebnf = f.read()
    parseTree = ebnf_grammar.parse(input_ebnf)
    rules = EbnfASTVisitor().visit(parseTree)
    nodeTypes = []
    for (lhs, rhs) in rules.items():
        c = python_class_generator.NodeType(lhs)
        additional = rhs.populate_node_type(c, python_class_generator.NodeType)
        nodeTypes.append(c)
        nodeTypes.extend(additional)
    for nt in nodeTypes:
        print(nt)
