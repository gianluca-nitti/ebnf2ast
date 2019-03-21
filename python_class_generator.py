from itertools import chain

ind = 4*' '

class NodeType:
    def __init__(self, name, base = ''):
        self.name = name
        self._base = base
        self._parts = []
        self._identifiers = set()
        self._optionals = set()
        self._lists = set()
    def add_literal(self, literal):
        '''Note: the literal must already include quotes'''
        self._parts.append(literal.replace('\\', '\\\\').replace('\"', ' \" '))
    def add_identifier(self, identifier):
        c = 0
        while identifier in self._identifiers:
            c += 1
            identifier += '_%d' % c
        self._identifiers.add(identifier)
        self._parts.append(identifier)
    def add_optional(self, optional):
        # TODO: ensure no duplication, like identifiers
        self._optionals.add(optional)
        self._parts.append(optional)
    def add_list(self, lst):
        # TODO: ensure no duplication, like identifiers
        self._lists.add(lst)
        self._parts.append(lst)
    def __str__(self):
        def build_setter(x):
            return '%sdef set_%s(self, val):\n%sself._%s = val\n' % (ind, x, 2*ind, x)
        def initializer_builder(val):
            return lambda x: '%sself._%s = %s\n' % (2*ind, x, val)
        def build_renderer(part):
            if part in chain(self._identifiers, self._optionals):
                return 'self._' + part
            elif part in self._lists:
                return '\"\".join(map(str, self._%s))' % part
            else: # literals
                return part
        r = 'class %s(%s):\n' % (self.name, self._base)
        if len(self._parts) == 0:
            return r + ind + 'pass'
        if len(self._optionals) > 0 or len(self._lists) > 0:
            r += '%sdef __init__(self):\n' % ind
            r += ''.join(map(initializer_builder('\"\"'), self._optionals))
            r += ''.join(map(initializer_builder('[]'), self._lists))
        settable_parts = chain(self._identifiers, self._optionals, self._lists)
        r += ''.join(map(build_setter, settable_parts))
        r += ind + 'def __str__(self):\n' + 2*ind + 'return '
        r += ' + '.join(map(build_renderer, self._parts))
        # TODO keep track of which one are lists and print them accordingly
        return r
