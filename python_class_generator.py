ind = ' ' * 4

class NodeType:
    def __init__(self, name, base = ''):
        self.name = name
        self._base = base
        self._parts = []
        self._identifiers = set()
        self._optionals = set()
    def add_literal(self, literal):
        '''Note: the literal must already include quotes'''
        self._parts.append(literal.replace('\\', '\\\\').replace('\"', ' \" '))
    def add_identifier(self, identifier):
        c = 0
        while identifier in self._identifiers:
            c += 1
            identifier += '_%d' % c
        self._identifiers.add(identifier)
        self._parts.append('self._' + identifier)
    def add_optional(self, optional):
        # TODO: ensure no duplication, like identifiers
        self._optionals.add(optional)
        self._parts.append('self._' + optional)
    def __str__(self):
        r = 'class %s(%s):\n' % (self.name, self._base)
        if len(self._parts) == 0:
            return r + ind + 'pass'
        if len(self._optionals) > 0:
            r += '%sdef __init__(self):\n' % ind
            def optional_initializer(x):
                return '%sself._%s=\"\"\n' % (2*ind, x)
            r += ''.join(map(optional_initializer, self._optionals))
        def setter(x):
            return '%sdef set_%s(self, val):\n%sself._%s = val\n' % (ind, x, 2*ind, x)
        r += ''.join(map(setter, self._identifiers))
        r += ''.join(map(setter, self._optionals))
        r += ind + 'def __str__(self):\n' + 2*ind + 'return '
        r += ' + '.join(map(str, self._parts))
        return r
