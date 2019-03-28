#def map_rhs(f, rules):
#    return {lhs: f(rhs) for lhs, rhs in rules.iteritems()}

def dfs_visit(f, rules):
    for rule_rhs in rules.values():
        rule_rhs.dfs_visit(f)

def dfsMap(f, rules):
    for lhs in rules.keys():
        rules[lhs].dfsMap(f)
        rules[lhs] = f(rules[lhs])

def simplify(rules, module):
    dfsMap(lambda x: x.simplify(), rules)

def name_parts(rules, module):
    for rhs in rules.values():
        rhs.name_parts()

def fix_quotes(rules, module):
    def f(node):
        flt = isinstance(node, module.Identifier) and node.ident == 'double_quote'
        return module.Literal('\'"\'') if flt else node
    dfsMap(f, rules)

def apply_all(rules, module):
    transforms = [simplify, fix_quotes, name_parts]
    for t in transforms:
        t(rules, module)
