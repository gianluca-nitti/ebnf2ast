#!/usr/bin/env python3

import ebnf_parser, python_class_generator

if __name__ == '__main__':
    with open('vhdl.ebnf', 'r') as f:
        input_ebnf = f.read()
    rules = ebnf_parser.parse(input_ebnf)
    nodeTypes = []
    for (lhs, rhs) in rules.items():
        c = python_class_generator.NodeType(lhs)
        additional = rhs.populate_node_type(c, python_class_generator.NodeType)
        nodeTypes.append(c)
        nodeTypes.extend(additional)
    for nt in nodeTypes:
        print(nt)
