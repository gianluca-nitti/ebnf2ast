import functools

#def map_rhs(f, rules):
#    return {lhs: f(rhs) for lhs, rhs in rules.iteritems()}

def dfs_visit(f, rules):
    for rule_rhs in rules.values():
        rule_rhs.dfs_visit(f)

def dfsMap(f, rules):
    for lhs in rules.keys():
        rules[lhs].dfsMap(f)
        rules[lhs] = f(rules[lhs])

def transform_and_inline(f, rules, module): # TODO: probably not needed, remove
    transformed = dict()
    for lhs, rhs in rules.items():
        new_rhs = f(rhs)
        if new_rhs != None:
            transformed[lhs] = new_rhs
    ids = [module.Identifier(ident) for ident in transformed.keys()]
    def replacer(node):
        return transformed[node.ident] if node in ids else node
    dfsMap(replacer, rules)
    for lhs in transformed.keys():
        del rules[lhs]

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
    dfsMap(f, rules)

def remove_dup_alternatives(rules, module):
    def f(node):
        if isinstance(node, module.Alternative):
            return module.Alternative(list(set(node._contents)))
        else:
            return node
    dfsMap(f, rules)

def name_parts(rules, module):
    for rhs in rules.values():
        rhs.name_parts()

def fix_quotes(rules, module):
    def f(node):
        flt = isinstance(node, module.Identifier) and node.ident == 'double_quote'
        return module.Literal('\'"\'') if flt else node # TODO check with a VHDL string literal
    dfsMap(f, rules)

def pad_literals(rules, module):
    def f(node):
        flt = isinstance(node, module.Literal)
        return module.Literal(' %s ' % node.literal) if flt else node
    dfsMap(f, rules)

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
    dfsMap(f, rules)

def remove_aliases(rules, module):
    aliases = dict()
    for lhs, rhs in rules.items():
        if isinstance(rhs, module.Sequence) \
            and len(rhs._contents) == 1 \
            and isinstance(rhs._contents[0], module.Identifier):
            aliases[lhs] = rhs._contents[0].ident
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
    dfsMap(replacer, rules)

def apply_all(rules, module):
    transforms = [
        remove_dup_alternatives,
        pad_literals,
        concat_adj_literals,
        fix_quotes,
        simplify_lists,
        remove_aliases,
        name_parts
    ]
    for t in transforms:
        t(rules, module)
