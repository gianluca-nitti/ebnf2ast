ind = ' ' * 4
# q = '\'i'

class Identifier:
    def __init__(self, identifier):
        self._identifier = identifier
    def __str__(self):
        return 'self._' + self._identifier
class Literal:
    def __init__(self, literal):
        self._literal = literal
    def __str__(self):
        # return q + self._literal + q # quotes are already there!
        return self._literal

class NodeType:
    def __init__(self, name, base = ''):
        self._name = name
        self._base = base
        self._parts = []
    def add_literal(self, literal):
        self._parts.append(Literal(literal))
    def add_identifier(self, identifier):
        self._parts.append(Identifier(identifier))
    def __str__(self):
        r = 'class %s(%s):\n' % (self._name, self._base)
        r += '\n'.join([]) # TODO methods
        r += ind + 'def __str__(self):\n' + 2*ind + 'return '
        r += ' + '.join(map(str, self._parts))
        return r
