from . import register
from ..runtimeobjects import String


@register(19)
def load_long_utd(table, id, _):
    size = table.loader.read_u32()
    table.loader.stack.push(
        String(table.loader.read(size))
    )
