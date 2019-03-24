#!/usr/bin/env python3

import ebnf_parser, ebnf_nodes, transform, python_class_generator

if __name__ == '__main__':
    with open('vhdl.ebnf', 'r') as f:
        input_ebnf = f.read()
    rules = ebnf_parser.parse(input_ebnf, python_class_generator)
    transform.apply_all(rules)
    for (lhs, rhs) in rules.items():
        assert isinstance(rhs, ebnf_nodes.Sequence) or isinstance(rhs, ebnf_nodes.Alternative)
        print(rhs.render(lhs), end='')
