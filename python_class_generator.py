import keyword, ebnf_nodes, util

keywords = keyword.kwlist

ind = 4*' '
annotations_enabled = True
runtime_checks_enabled = True

_used_class_names = set()

header = '''
import typing

def _opt_to_str(x):
    return str(x) if x != None else \'\'\n
'''

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
        def_constructor_lines = []
        constructor_parts = []
        str_result = []
        for part in self._contents:
            assert not isinstance(part, Alternative), 'Alternative inside Sequence'
            assert not isinstance(part, Sequence), 'Nested Sequences'
            if hasattr(part, 'render_class'):
                classes.append(part.render_class(part.get_name()))
            if hasattr(part, 'render_def_initializer'):
                def_constructor_lines.append(part.render_def_initializer(part.get_name()))
            if hasattr(part, 'render_constructor_part'):
                constructor_parts.append(part.render_constructor_part(part.get_name()))
            str_result.append(part.render_str(part.get_name()))
        r = ''.join(classes)
        r += 'class %s%s:\n' % (name, '(%s)' % base if len(base) > 0 else '')
        if len(constructor_parts) > 0:
            constructor_parts.sort() # put optionals last. TODO might not be a good idea (different order from ebnf)
            # TODO add decorator to enforce type checks at runtime
            # TODO consider using kwargs (BUT, maybe not much of a good idea, you'd have to look at the code anyway)
            r += '%sdef __init__(self, %s):\n%s' % (ind, \
                ','.join(map(lambda x: x[1], constructor_parts)),
                ''.join(map(lambda x: x[2], constructor_parts)))
        r += '%sdef __str__(self):\n%sreturn %s\n' % (ind, 2*ind, ' + '.join(str_result))
        return r
class Optional(ebnf_nodes.Optional):
    def render_class(self, name):
        c = self._contents[0]
        assert isinstance(c, Sequence) or isinstance(c, Alternative), 'Optional must contain Sequence or Alternative'
        return '' \
            if isinstance(c, Sequence) and len(c._contents) == 1 and isinstance(c._contents[0], Identifier) \
            else c.render(name)
    def render_def_initializer(self, name):
        return '%sself.%s = \'\'\n' % (2*ind, name)
    def render_constructor_part(self, name):
        type_annot = 'typing.Optional[%s]' % name
        init_expr = '_%s' % name
        # Allow True/False to be used to enable/disable an optional literal without manually instantiating it
        if isinstance(self._contents[0], Sequence) \
            and len(self._contents[0]._contents) == 1 \
            and isinstance(self._contents[0]._contents[0], Literal):
                type_annot = 'typing.Union[%s, bool]' % type_annot
                init_expr = '%s() if %s == True else (None if %s == False else %s)' \
                    % (name, init_expr, init_expr, init_expr)
        # Allow content to be passed directly (no opt_ wrapper class) for optional identifiers
        elif isinstance(self._contents[0], Sequence) \
            and len(self._contents[0]._contents) == 1 \
            and isinstance(self._contents[0]._contents[0], Identifier):
                cont_type = self._contents[0]._contents[0].ident
                type_annot = 'typing.Optional[%s]' % cont_type
        return (1, '_%s: \'%s\' = None' % (name, type_annot), \
                '%sself.%s = %s\n' % (2*ind, name, init_expr))
    def render_str(self, name):
        return '_opt_to_str(self.%s)' % name
class List(ebnf_nodes.List):
    def render_class(self, name):
        c = self._contents[0]
        return c.render(name) \
            if isinstance(c, Sequence) or isinstance(c, Alternative) \
            else ''
    def _get_type(self):
        c = self._contents[0]
        return self.get_name() \
            if isinstance(c, Sequence) or isinstance(c, Alternative) \
            else c.ident
    def render_def_initializer(self, name):
        return '%sself.%s = []\n' % (2*ind, name)
    def render_constructor_part(self, name):
        return (1, '_%s: \'typing.Optional[typing.List[%s]]\' = None' % (name, self._get_type()), \
            '%sself.%s = _%s or []\n' % (2*ind, name, name))
    def render_str(self, name):
        return '\'%s\'.join(map(str, self.%s))' % (self._sep, name)
class Identifier(ebnf_nodes.Identifier):
    def render_constructor_part(self, name):
        return (0, '_%s: \'%s\'' % (name, self.ident), '%sself.%s = _%s\n' % (2*ind, name, name))
    def render_str(self, name):
        return 'str(self.%s)' % name
class Literal(ebnf_nodes.Literal):
    def render_str(self, name):
        return '\"%s\"' % self.literal.replace('\\', '\\\\').replace('\"', '\\\"')
