from . import register
from .util import TInferiorRefList
from ..runtimeobjects import Statement


@register(13)
def cmd_block(table, id, size):
    t = table.loader.read_u8()
    type_info, bytecode_start, bytecode_end = [table.loader.read_u16() for i in range(3)]

    refloader = TInferiorRefList(size + 3, 3)
    refloader.set_table(table)
    refloader.readRefs()
    statement = Statement(type_info, bytecode_start, bytecode_end)
    table.registerObject(id, statement)
    res = refloader.doLoad()
    statement.set_children(res)
    table.loader.stack.push(statement)
