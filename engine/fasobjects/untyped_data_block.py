from . import register
from ..runtimeobjects import String


@register(17)
def load_utd(table, id, size):
    table.loader.stack.push(
        String(table.loader.read(size))
    )
