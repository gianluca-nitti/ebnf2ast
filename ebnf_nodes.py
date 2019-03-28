import sys, util

class RuleComponent:
    def set_name(self, val):
        self._name = val
    def get_name(self):
        return self._name
    def name_parts(self):
        pass
    def simplify(self):
        return self
    def dfs_visit(self, f):
        pass
    def dfsMap(self, f):
        pass
class Container(RuleComponent):
    def __init__(self, contents):
        self._contents = contents
    def name_parts(self):
        for part in self._contents:
            part.name_parts()
        used_names = set()
        kws = {} # sys.modules[self.__module__].keywords # TODO
        def name_part(part):
            name = util.unique_sanitized_name(part.get_preferred_name(), used_names, kws)
            part.set_name(name)
            return part
        self._contents = list(map(name_part, self._contents))
    def get_preferred_name(self):
        return '_'.join(map(lambda x: x.get_preferred_name(), self._contents))
    def dfs_visit(self, f):
        for i in range(len(self._contents)):
            self._contents[i].dfs_visit(f)
            f(self._contents[i])
    def dfsMap(self, f):
        for i in range(len(self._contents)):
            self._contents[i].dfsMap(f)
            self._contents[i] = f(self._contents[i])

class Alternative(Container):
    def __init__(self, alts):
        super().__init__(alts)
    def pp(self):
        return 'Alternative( ' + ', '.join(map(lambda x: x.pp(), self._contents)) + ' )'
class Sequence(Container):
    def __init__(self, parts):
        super().__init__(parts)
    def simplify(self):
        # if len(self._contents) == 1:
        #    return self._contents[0]
        return self
    def pp(self):
        return 'Sequence( ' + ', '.join(map(lambda x: x.pp(), self._contents)) + ' )'
class Optional(Container):
    def __init__(self, content):
        super().__init__([content])
    def get_preferred_name(self):
        return 'opt_%s' % self._contents[0].get_preferred_name()
    def pp(self):
        return 'Optional( ' + self._contents[0].pp() + ' )'
class List(Container):
    def __init__(self, content):
        super().__init__([content])
    def get_preferred_name(self):
        return 'list' # TODO
    def pp(self):
        return 'List( ' + self._contents[0].pp() + ' )'

class Identifier(RuleComponent):
    def __init__(self, ident):
        self.ident = ident
    def get_preferred_name(self):
        return self.ident
    def pp(self):
        return 'Identifier( ' + self.ident + ' )'
class Literal(RuleComponent):
    def __init__(self, literal):
        self.literal = literal
    def get_preferred_name(self):
        return self.literal.replace('\"', '').replace(' ', '') # TODO potentially dangerous!
    def pp(self):
        return 'Literal( ' + self.literal + ' )'
