from . import register
from ..runtimeobjects import Object, Constant, EventIdentifier


@register(10)
def load_codeIdentifier(table, id, size):
    c = table.loader.read_u8()
    _ = lambda value, expected: Exception(
        'Error -1702: Invalid size on codeId: expected %s, value: %s' % (expected, value))

    if c == 11:
        # The engine internalize the constant when reading
        # But I don't do this.
        if size != 8:
            raise _(size, 8)
        a = table.loader.read_u64()
        table.loader.stack.push(Object(Constant(a)))

    elif c in (10, 47):
        # Class identifier?
        if size != 4:
            raise _(size, 4)
        a = table.loader.read_u32()
        table.loader.stack.push(Object(Constant(a)))

    elif c == 46:
        if size != 24:
            raise _(size, 24)
        a, b, c, d, e, f = [table.loader.read_u32() for i in range(6)]
        table.loader.stack.push(Object(EventIdentifier(a, b, c, d, f, e)))  # yeah, not typo. abcdfe, not abcdef.
