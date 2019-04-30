#!/usr/bin/env python3

import ebnf_parser, ebnf_nodes, transform, python_class_generator

ebnf_file = 'vhdl.ebnf'
generator = python_class_generator
transform_opts = {
    'remove_unreferenced': {'root': 'design_file'}
}

if __name__ == '__main__':
    with open(ebnf_file, 'r') as f:
        input_ebnf = f.read()
    rules = ebnf_parser.parse(input_ebnf, generator)
    for t in transform.all_transforms:
        t(rules, generator, **transform_opts.get(t.__name__, dict()))
    print(generator.header, end='')
    for (lhs, rhs) in rules.items():
        assert isinstance(rhs, ebnf_nodes.Sequence) or isinstance(rhs, ebnf_nodes.Alternative)
        print(rhs.render(lhs), end='')
        # print(lhs, '::=', rhs.pp())
