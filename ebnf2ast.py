#!/usr/bin/env python3

import ebnf_parser, ebnf_nodes, transform, python_class_generator

# TODO move to an analysis module (maybe transform is appropriate)
def identifiers_stats(rules, root):
    ids = {root: 1}
    def find_ident_usages(x):
        if isinstance(x, ebnf_nodes.Identifier):
            ids[x.ident] = ids.get(x.ident, 0) + 1
    transform.dfs_visit(find_ident_usages, rules)
    print('# Found a total of', len(ids), 'identifiers')
    undef_ids = set(filter(lambda x: x not in rules.keys(), ids.keys()))
    if len(undef_ids) > 0:
        print('# Found', len(undef_ids), 'undefined identifiers:', undef_ids)
    unused_rules = set(filter(lambda x: x not in ids.keys(), rules.keys()))
    print('# Found', len(unused_rules), 'unreferenced rules:', unused_rules)
    while len(unused_rules) > 0:
        print('# Deleting', len(unused_rules))
        for r in unused_rules:
            del rules[r]
        ids = {root: 1}
        transform.dfs_visit(find_ident_usages, rules)
        unused_rules = set(filter(lambda x: x not in ids.keys(), rules.keys()))
        print('# Found', len(unused_rules), 'unreferenced rules:', unused_rules)
    print('# Found a total of', len(ids), 'identifiers')
    undef_ids = set(filter(lambda x: x not in rules.keys(), ids.keys()))
    if len(undef_ids) > 0:
        print('# Found', len(undef_ids), 'undefined identifiers:', undef_ids)


if __name__ == '__main__':
    with open('vhdl.ebnf', 'r') as f:
        input_ebnf = f.read()
    rules = ebnf_parser.parse(input_ebnf, python_class_generator)
    transform.apply_all(rules, python_class_generator)
    identifiers_stats(rules, 'design_file')
    for (lhs, rhs) in rules.items():
        assert isinstance(rhs, ebnf_nodes.Sequence) or isinstance(rhs, ebnf_nodes.Alternative)
        print(rhs.render(lhs), end='')
