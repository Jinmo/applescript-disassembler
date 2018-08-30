from . import register
from ..runtimeobjects import Binding, NIL

class Record(object):
    pass

@register(6)
def load(table, id, size):
    if size == 3:
        table.loader.stack.push(Binding(NIL, NIL, NIL))
        record = table.loader.stack[-1]
        table.registerObject(id, record)
        while size == 3:
            A = table.loader.read_s16()
            B = table.loader.read_s16()
            C = table.loader.read_s16()
            table.findObject(A)
            record.a = table.loader.stack.pop()
            table.findObject(B)
            record.b = table.loader.stack.pop()
            objC = table.findObject(C, False)
            if objC == False:
                index, ref, size = header = table.readFasHeader()
                if index != 6:
                    table.loadObjectBody(ref, index, size)
                    record.next = table.loader.stack.pop()
                    break
                if size != 3:
                    break
                record.next = Binding(NIL, NIL, NIL)
                record = record.next
            else:
                record.next = table.loader.stack.pop()
                break
        table.registerObject(id, record)
    elif size == 1:
        table.loader.stack.push(Binding(NIL, NIL, NIL))
    else:
        raise Exception('unknown fas record type: %d' % size)