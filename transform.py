import functools

def dfs_visit(f, rules):
    for rule_rhs in rules.values():
        rule_rhs.dfs_visit(f)

def dfs_map(f, rules):
    for lhs in rules.keys():
        rules[lhs].dfs_map(f)
        rules[lhs] = f(rules[lhs])

def concat_adj_literals(rules, module):
    def reducer(acc, part):
        if len(acc) > 0 and isinstance(acc[-1], module.Literal) and isinstance(part, module.Literal):
            return acc[:-1] + [module.Literal(acc[-1].literal + part.literal)]
        else:
            return acc + [part]
    def f(node):
        if isinstance(node, module.Sequence):
            return module.Sequence(functools.reduce(reducer, node._contents, []))
        else:
            return node
    dfs_map(f, rules)

def remove_dup_alternatives(rules, module):
    def f(node):
        if isinstance(node, module.Alternative):
            return module.Alternative(list(set(node._contents)))
        else:
            return node
    dfs_map(f, rules)

def name_parts(rules, module):
    for rhs in rules.values():
        rhs.name_parts()

def fix_quotes(rules, module):
    def f(node):
        flt = isinstance(node, module.Identifier) and node.ident == 'double_quote'
        return module.Literal('\"') if flt else node
    dfs_map(f, rules)

def pad_literals(rules, module):
    def f(node):
        # NOTE: this is VHDL-specific, for VHDL keywords
        flt = isinstance(node, module.Literal) and node.literal.replace(' ', '').isalpha()
        return module.Literal(' %s ' % node.literal) if flt else node
    dfs_map(f, rules)

def simplify_lists(rules, module):
    def f(node):
        if isinstance(node, module.Sequence) and \
            len(node._contents) == 2 and \
            isinstance(node._contents[1], module.List) and \
            isinstance(node._contents[1]._contents[0], module.Sequence) and \
            len(node._contents[1]._contents[0]._contents) == 2 and \
            isinstance(node._contents[1]._contents[0]._contents[0], module.Literal) and \
            node._contents[0] == node._contents[1]._contents[0]._contents[1]:
            sep = node._contents[1]._contents[0]._contents[0].literal
            return module.Sequence([module.List(node._contents[0], sep)])
        else:
            return node
    dfs_map(f, rules)

def remove_aliases(rules, module):
    aliases = dict()
    for lhs, rhs in rules.items():
        if isinstance(rhs, module.Sequence) \
            and len(rhs._contents) == 1 \
            and isinstance(rhs._contents[0], module.Identifier):
            aliases[lhs] = rhs._contents[0].ident
    print('# Found', len(aliases), 'alias rules:', aliases)
    keep_going = True
    while keep_going:
        keep_going = False
        for k in aliases.keys():
            if aliases[k] in aliases.keys():
                aliases[k] = aliases[aliases[k]]
                keep_going = True
    def replacer(node):
        if isinstance(node, module.Identifier):
            rep = aliases.get(node.ident)
            return module.Identifier(rep) if rep != None else node
        else:
            return node
    dfs_map(replacer, rules)

def find_idents(rules, module, root = None):
    ids = {root: 1} if root != None else dict()
    def find_ident_usages(x):
        if isinstance(x, module.Identifier):
            ids[x.ident] = ids.get(x.ident, 0) + 1
    dfs_visit(find_ident_usages, rules)
    return ids

def remove_unreferenced(rules, module, root):
    def find_unreferenced_rules():
        ids = find_idents(rules, module, root)
        result = set(filter(lambda x: x not in ids.keys(), rules.keys()))
        print('# Found', len(result), 'unreferenced rules:', result)
        return result
    unused_rules = find_unreferenced_rules()
    while len(unused_rules) > 0:
        print('# Deleting', len(unused_rules), 'unreferenced rules')
        for r in unused_rules:
            del rules[r]
        unused_rules = find_unreferenced_rules()

def report_undef_idents(rules, module):
    ids = find_idents(rules, module)
    print('# Found a total of', len(ids), 'identifiers')
    undef_ids = set(filter(lambda x: x not in rules.keys(), ids.keys()))
    if len(undef_ids) > 0:
        print('# Found', len(undef_ids), 'undefined identifiers:', undef_ids)

all_transforms = [
    remove_dup_alternatives,
    pad_literals,
    concat_adj_literals,
    fix_quotes,
    simplify_lists,
    remove_aliases,
    name_parts,
    remove_unreferenced,
    report_undef_idents
]
