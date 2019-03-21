class Alternative:
    next_nt_index = 1
    def __init__(self, alts):
        self.alts = alts
    def populate_node_type(self, nt, node_builder):
        result = []
        for alt in self.alts:
            alt_nt = node_builder('alternative_%d' % Alternative.next_nt_index, nt.name)
            result.extend(alt.populate_node_type(alt_nt, node_builder))
            result.append(alt_nt)
            Alternative.next_nt_index += 1
        return result
    def pp(self):
        return 'Alternative( ' + ', '.join(map(lambda x: x.pp(), self.alts)) + ' )'
class Sequence:
    def __init__(self, parts):
        self.parts = parts
    def populate_node_type(self, nt, node_builder):
        additional = []
        for part in self.parts:
            additional.extend(part.populate_node_type(nt, node_builder))
        return additional # TODO replace loop with some sort of map & reduce
    def pp(self):
        return 'Sequence( ' + ', '.join(map(lambda x: x.pp(), self.parts)) + ' )'
class Optional:
    next_nt_index = 1
    def __init__(self, content):
        self.content = content
    def populate_node_type(self, nt, node_builder):
        opt_nt = node_builder('optional_%d' % Optional.next_nt_index)
        nt.add_optional(opt_nt.name)
        result = [opt_nt]
        result.extend(self.content.populate_node_type(opt_nt, node_builder))
        Optional.next_nt_index += 1
        return result
    def pp(self):
        return 'Optional( ' + self.content.pp() + ' )'
class List:
    next_nt_index = 1
    def __init__(self, content):
        self.content = content
    def populate_node_type(self, nt, node_builder):
        list_nt = node_builder('list_%d' % List.next_nt_index)
        nt.add_list(list_nt.name)
        result = [list_nt]
        result.extend(self.content.populate_node_type(list_nt, node_builder))
        List.next_nt_index += 1
        return result
    def pp(self):
        return 'List( ' + self.content.pp() + ' )'
class Identifier:
    def __init__(self, ident):
        self.ident = ident
    def populate_node_type(self, nt, node_builder):
        nt.add_identifier(self.ident)
        return []
    def pp(self):
        return 'Identifier( ' + self.ident + ' )'
class Literal:
    def __init__(self, literal):
        self.literal = literal
    def populate_node_type(self, nt, node_builder):
        nt.add_literal(self.literal)
        return []
    def pp(self):
        return 'Literal( ' + self.literal + ' )'
