from . import register
from .util import TInferiorRefList


@register(16)
def load_untypedPointerBlock(table, id, size):
    refs = TInferiorRefList(size, 0)
    refs.set_table(table)
    refs.readRefs()
    vector = refs.doLoad()
    table.registerObject(id, vector)
    table.loader.stack.push(vector)
