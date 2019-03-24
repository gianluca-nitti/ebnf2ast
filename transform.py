#def map_rhs(f, rules):
#    return {lhs: f(rhs) for lhs, rhs in rules.iteritems()}

def dfsMap(f, rules):
    for lhs in rules.keys():
        rules[lhs].dfsMap(f)
        rules[lhs] = f(rules[lhs])

def simplify(rules):
    dfsMap(lambda x: x.simplify(), rules)

def name_parts(rules):
    for rhs in rules.values():
        rhs.name_parts()

def apply_all(rules):
    transforms = [simplify, name_parts]
    for t in transforms:
        t(rules)
