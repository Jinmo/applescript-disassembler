from . import register

from .. import runtimeobjects
from ..util import getSizeByIndex
from .util import TInferiorRefList

@register(4)
@register(14)
def load(table, id, size):
    c = table.loader.read_u8()
    if size == 0 and c == 15:
        table.loader.stack.push(runtimeobjects.secondActor)
    else:
        if c == 15 and size + 1 <= getSizeByIndex(15):
            alloc = getSizeByIndex(15)
        else:
            alloc = size + 1
        refloader = TInferiorRefList(size + 1, 1)
        refloader.set_table(table)
        refloader.readRefs()
        res = refloader.doLoad()
        table.loader.stack.push(res)

    table.registerObject(id, table.loader.stack[-1])
