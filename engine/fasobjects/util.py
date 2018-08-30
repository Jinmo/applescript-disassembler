from ..runtimeobjects import Fixnum, NIL


class TInferiorRefList(object):
    """
    Original implementation uses inline vector on stack, but since it discards the stack after loading, I think it's not necessary to use stack on this implementation.
    """

    def __init__(self, size, offset):
        self.size = size
        self.offset = offset
        self.refs = [NIL] * size
        self.table = None

    def set_table(self, table):
        self.table = table

    def readRefs(self):
        for i in range(self.offset, self.size):
            self.refs[i] = Fixnum(self.table.loader.read_s16())

    def doLoad(self):
        r = [NIL] * self.size
        for i in range(self.offset, self.size):
            self.table.findObject(self.refs[i].value)
            r[i] = self.table.loader.stack.pop()
        return r
