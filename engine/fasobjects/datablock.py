from engine.runtimeobjects import parse_value
from . import register


class Descriptor(object):
    def __init__(self, type, content):
        self.type = type
        self.content = content

    def __repr__(self):
        return "<Descriptor type=%r content=%r>" % (self.type, self.content)


@register(15)
def load(table, ref, inlined):
    stack = table.loader.stack
    t = ord(table.loader.read(1))
    if t == 8:
        table.loader.read(8)
        table.loader.read(4)
        table.loader.read(70)
        a = table.loader.read_u32()
        table.loader.read(4)
        # Read descriptor
        desc = Descriptor(table.loader.read(4),
                          table.loader.read(inlined - 94))
        # if desc.type == 'alis':
        # 	# Some alias process
        # 	pass
        stack.push(desc)
    else:
        stack.push(parse_value(t, table.loader.read(inlined)))
    table.registerObject(ref, stack[-1])
