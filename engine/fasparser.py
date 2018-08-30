import struct
import sys
from pprint import pprint

from engine.fasobjects import fastypes
from engine.runtimeobjects import *
from engine.util import getSizeByIndex


# magic!
class instancemethod:
    def method():
        pass


instancemethod = type(instancemethod.method)

types = {
    1: 'symbol',
    2: 'list',
    3: 'int',
    4: 'valueBlock',
    6: 'record',
    7: 'long',
    8: 'float',
    9: 'bool',
    10: 'codeId',
    11: 'userId',
    12: 'str',
    13: 'cmdBlock',
    14: 'valueBlock2',
    15: 'dataBlock',
    16: 'untypedPointerBlock',
    17: 'untypedDataBlock',
    18: 'longDataBlock',
    19: 'untypedLongDataBlock'
}


def hword(x):
    r = struct.unpack(">H", x)[0]
    if r > 0x8000:
        r -= 0x10000
    return r


def dword(x):
    r = struct.unpack(">L", x)[0]
    if r > 0x80000000:
        r -= 2 ** 32
    return r


def qword(x):
    r = struct.unpack(">Q", x)[0]
    if r > 0x8000000000000000:
        r -= 2 ** 64
    return r


class UserId(object):
    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return ':%s' % repr(self.name)[1:-1]


class TRefTable(object):
    # This is weird class extending TGCStack and overriding some pointer-related fields.
    # I think the interpreter has bug, but didn't investigate it yet.
    def __init__(self):
        # I think it does some kind of scope things:
        # it seems to make a linked-list-ed vector to gSwitchedGlobals->refTable (offset 0x3E8)
        self.allocate(32)
        # self.field_14 = -1 <-- what?

    def allocate(self, size):
        self.refTable += [(nil, 6)] * size


class FasLoadTable(TRefTable):
    def __init__(self, loader):
        super(TRefTable, self).__init__()
        self.depth = 0

        # Some static fields in binary. See help(Loader.context) for mechanism.
        # it's simply a keyed-storage with class name as key, like the binary did.
        with loader.context(self) as context:
            context.reuseHeader = False
            context.index = None
            context.realRef = None

            # TODO: how can I show these errors? It's errors with max 5 count
            context.refErrors = []

        self.loader = loader
        self.field_38 = False  # don't know what it is for now

        maybe_hashbang = loader.read(2)
        if maybe_hashbang == '#!':
            while True:
                c = loader.read(1)
                if c in ('\n', ''):
                    break
                loader = self.loader  # This line's ported from the binary. Beware of TOCTOU

        else:
            loader.seek(-2)

        # Fasd magic
        c = loader.read_u32(False)
        assert c == 'Fasd'
        self.magic_fasd = c

        # UAS magic
        c = loader.read_u32(False)
        assert c == 'UAS '
        self.magic_uas = c

        c = loader.read_u32(False)
        if c >= '1.10':
            c = self.loader.read_u32(False)
        if c <= '0.97':
            raise Exception('File version too low: %r' % c)
        if c >= '1.11':
            raise Exception('File version too high: %r' % c)
        if c <= '1.00':
            self.field_38 = True

        self.refTable = [(NIL, 2)] * 32

        self.version = c
        pass

    def loadObject(self, num):
        loader = self.loader
        with loader.context(self) as context:
            pos = loader.f.tell()
            if context.reuseHeader:
                context.reuseHeader = False
            else:
                context.index, context.ref, context.inlined = self.readFasHeader()

            self.depth += 1
            out = ' '.join(repr(x) for x in (hex(pos) + ' idx:%d' % context.index, context.ref, context.inlined))
            if context.ref == num:
                self.loadObjectBody(num, context.index, context.inlined)
            else:
                err = "%08x: AppleScript: Error while loading script, RefID doesn't match. Expected %d, found %d." % (
                    pos, num, context.ref)
                context.reuseHeader = True
                print >> sys.stdout, err
                context.refErrors.append(err)
                if len(context.refErrors) >= 6:
                    raise Exception("AppleScript: Too many RefID errors.")
                loader.stack.push(NIL)
            self.depth -= 1

    def readFasHeader(self):
        index = ord(self.loader.read(1))
        ref = self.loader.read_s16()
        inlined = self.loader.read_u16(True)
        return index, ref, inlined

    def loadObjectBody(self, ref, index, inlined):
        # loader.stack.reserve(20)
        stack = self.loader.stack

        t = fastypes.get(index)

        if t is None:
            raise Exception('Error -1702: unknown object type: %d!' % index)

        if index in (2, 7, 10, 11):
            ref = 0  # not used in binary

        prevlen = len(stack)
        t(self, ref, inlined)
        assert len(stack) == prevlen + 1, t.__module__  # little check

    def findObject(self, num, load=True):
        if not load:  # FindObjectNoLoad
            if num >= 0:
                exists, result = self.lookUpByRefId(num)
                if exists:
                    self.loader.stack.push(result)
                    return True
                else:
                    return False
            else:
                return False
        else:  # FindObject
            if num < 0:
                self.loadObject(num)
            else:
                exists, result = self.lookUpByRefId(num)
                if exists:
                    self.loader.stack.push(result)
                else:
                    self.loadObject(num)

    def lookUpByRefId(self, num):
        if num >= len(self.refTable):
            return False, None
        value, type = self.refTable[num]
        return type in (14, 30), value

    def registerObject(self, id, value):
        if id < 0:
            return
        if id >= len(self.refTable):
            self.refTable += [(NIL, NIL)] * (id - len(self.refTable) + 1)
        self.refTable[id] = (value, 30)


class Stack(list):
    def push(self, x):
        self.append(x)

    pass


class Context:
    def __init__(self):
        pass

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass


class Loader:
    """
    port of FasLoad, wraps TBasicInputStream.
    Original version of AppleScript uses global variable for it, and I use class for separating file contexts.
    """

    def __init__(self):
        """
        You can just call Loader() without any arguments.
        loader = Loader()
        loader.load(file)
        """
        self.stack = None
        self.bigEndian = None

        # Some internal stuffs
        self.__context = {}

        integer_reader = self.integer_reader
        self.read_u64, self.read_s64 = integer_reader(8, 'Q')
        self.read_u32, self.read_s32 = integer_reader(4, 'L')
        self.read_u16, self.read_s16 = integer_reader(2, 'H')
        self.read_u8, self.read_s8 = integer_reader(1, 'B')
        pass

    def integer_reader(self, size, format):
        mask = 1 << (size * 8 - 1)
        format = ">%s" % format

        def reader(unpack=True):
            data = self.read(size)
            if not self.bigEndian:
                data = data[::-1]
            if unpack:
                return struct.unpack(format, data)[0]
            else:
                return data

        def signed_reader():
            num = reader(True)
            if num & mask:
                return num - mask * 2
            else:
                return num

        return (reader, signed_reader)

    def load(self, path):
        self.f = f = open(path, 'rb')

        self.bigEndian = True
        self.stack = Stack()
        self.loadTable = FasLoadTable(self)

        self.loadTable.loadObject(0)
        return self.stack.pop()

    def read(self, size):
        return self.f.read(size)

    def seek(self, pos, set=1):
        return self.f.seek(pos, set)

    def context(self, key):
        if not isinstance(key, str):
            key = key.__class__.__name__
        if key not in self.__context:
            self.__context[key] = Context()
        return self.__context[key]


if __name__ == '__main__':
    # TODO: make below code work. it doesn't work in current because applescript-disassembler has no package for now
    # If run as script, it'll cause error in importing "engine.*".
    path = sys.argv[1]
    loader = Loader()
    pprint(loader.load(path))
