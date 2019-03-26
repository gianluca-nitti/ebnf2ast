import ebnf_nodes, util

ind = 4*' '
annotations_enabled = True
runtime_checks_enabled = True

_used_class_names = set()

class Alternative(ebnf_nodes.Alternative):
    def render(self, name):
        name = util.unique_name(name, _used_class_names)
        result = 'class %s:\n%spass\n' % (name, ind)
        for alt in self._contents:
            assert isinstance(alt, Sequence), 'An Alternative must only contain Sequences'
            result += alt.render('%s_%s' % (name, alt.get_name()), name)
        return result
class Sequence(ebnf_nodes.Sequence):
    def render(self, name, base=''):
        assert len(self._contents) > 0, 'Sequence must not be empty'
        name = util.unique_name(name, _used_class_names)
        classes = []
        constructor_lines = []
        methods = []
        str_result = []
        # TODO make everything settable via constructor
        for part in self._contents:
            assert not isinstance(part, Alternative), 'Alternative inside Sequence'
            assert not isinstance(part, Sequence), 'Nested Sequences'
            if hasattr(part, 'render_class'):
                classes.append(part.render_class(part.get_name()))
            if hasattr(part, 'render_initializer'):
                constructor_lines.append(part.render_initializer(part.get_name()))
            if hasattr(part, 'render_methods'):
                methods.append(part.render_methods(part.get_name()))
            str_result.append(part.render_str(part.get_name()))
        r = ''.join(classes)
        r += 'class %s%s:\n' % (name, '(%s)' % base if len(base) > 0 else '')
        if len(constructor_lines) > 0:
            r += '%sdef __init__(self):\n%s' % (ind, ''.join(constructor_lines))
        r += ''.join(methods)
        r += '%sdef __str__(self):\n%sreturn %s\n' % (ind, 2*ind, ' + '.join(str_result))
        return r
class Optional(ebnf_nodes.Optional):
    def render_class(self, name):
        c = self._contents[0]
        assert isinstance(c, Sequence) or isinstance(c, Alternative), 'Optional must contain Sequence or Alternative'
        return c.render(name)
    def render_initializer(self, name):
        return '%sself._%s = \'\'\n' % (2*ind, name)
    def render_methods(self, name):
        return '%sdef set_%s(self, val):\n%sself._%s = val\n' % (ind, name, 2*ind, name)
    def render_str(self, name):
        return 'str(self._%s)' % name
class List(ebnf_nodes.List):
    def render_class(self, name):
        c = self._contents[0]
        assert isinstance(c, Sequence) or isinstance(c, Alternative), 'List must contain Sequence or Alternative'
        return c.render(name)
    def render_initializer(self, name):
        return '%sself._%s = []\n' % (2*ind, name)
    def render_methods(self, name):
        return '%sdef set_%s_list(self, val):\n%sself._%s = val\n' % (ind, name, 2*ind, name)
    def render_str(self, name):
        return '\'\'.join(map(str, self._%s))' % name
class Identifier(ebnf_nodes.Identifier):
    def render_methods(self, name):
        # use self.ident for type annotation / checking
        return '%sdef set_%s(self, val):\n%sself._%s = val\n' % (ind, name, 2*ind, name)
    def render_str(self, name):
        return 'str(self._%s)' % name
class Literal(ebnf_nodes.Literal):
    def render_str(self, name):
        return self.literal.replace('\\', '\\\\').replace('\"', ' \" ')
