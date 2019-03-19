ind = ' ' * 4

class NodeType:
    def __init__(self, name, base = ''):
        self.name = name
        self._base = base
        self._parts = []
        self._identifiers = set()
    def add_literal(self, literal):
        '''Note: the literal must already include quotes'''
        self._parts.append(literal.replace('\\', '\\\\'))
    def add_identifier(self, identifier):
        c = 0
        while identifier in self._identifiers:
            c += 1
            identifier += '_%d' % c
        self._identifiers.add(identifier)
        self._parts.append('self._' + identifier)
    def __str__(self):
        r = 'class %s(%s):\n' % (self.name, self._base)
        if len(self._parts) == 0:
            return r + ind + 'pass'
        def identifier_setter(x):
            return '%sdef set_%s(self, val):\n%sself._%s = val\n' % (ind, x, 2*ind, x)
        r += ''.join(map(identifier_setter, self._identifiers))
        r += ind + 'def __str__(self):\n' + 2*ind + 'return '
        r += ' + '.join(map(str, self._parts))
        return r
