from . import register
from ..runtimeobjects import Pair, EmptyPair, NIL


@register(2)
def loadList(table, id, size):
    if size == 2:
        r = cur = Pair(NIL, EmptyPair())
        while True:
            a = table.loader.read_s16()
            b = table.loader.read_s16()
            table.findObject(a)
            cur.first = table.loader.stack.pop()
            if table.findObject(b, False):
                break
            _index, _ref, size = table.readFasHeader()
            if _index != 2:
                table.loadObjectBody(_ref, _index, size)
                cur.second = table.stack.pop()
            if size != 2:
                break
            cur.second = Pair(NIL, EmptyPair)
            cur = cur.second
            table.registerObject(_ref, cur)
        if size:
            raise Exception('Error -1702: size 0 expected')
        cur.second = EmptyPair()
    else:
        r = EmptyPair()

    table.loader.stack += [r]
