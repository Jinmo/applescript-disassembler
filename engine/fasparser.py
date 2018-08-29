import struct
import sys
from pprint import pprint

from engine.definitions import getSizeByIndex

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


def load_file(path):
    f = open(path, 'rb')
    magic = ''
    refMap = {}
    constIdTable = {}
    classIdTable = {}
    eventIdTable = {}
    userIdTable = {}
    # literals = []

    # magic
    c = f.read(4)
    assert c == 'Fasd'
    magic += c
    c = f.read(4)
    assert c == 'UAS '
    c = f.read(4)
    if c >= '1.10':
        c = f.read(4)
    assert '0.97' < c < '1.11'

    def findObject(refId, load=True):
        if refId < 0 or refId not in refMap:
            if load:
                refMap[refId] = readObject(refId)
            else:
                return None
        return refMap[refId]

    read1 = lambda: ord(f.read(1))
    read2 = lambda: hword(f.read(2))
    read4 = lambda: dword(f.read(4))
    read8 = lambda: qword(f.read(8))

    def _readRefList(size):
        r = [read2() for i in range(size)]
        R = []
        for refId in r:
            R.append(findObject(refId))
        # literals.append(R)
        return R

    def readValueBlock(id, size):
        c = read1()
        if size == 0 and c == 15:
            r = []
        else:
            if c == 15:
                alloc = getSizeByIndex(c)
            else:
                alloc = size + 1
            r = _readRefList(size)
        # literals.append(r)
        return r

    def readSymbol(size):
        if not size:
            r = '<symbol>'
        else:
            r = read8()
        # literals.append(r)
        return r

    def readUntypedPointerBlock(id, size):
        r = _readRefList(size)
        # literals.append(r)
        return r

    def readCodeId(size):
        c = read1()
        if c == 11:
            a = read4()
            b = read4()
            v = a | (b << 32)
            v = struct.pack(">Q", v & 0xffffffffffffffff)
            constIdTable[v] = v
        elif c in [10, 47]:
            a = read4()
            v = struct.pack(">L", a & 0xffffffff)
            classIdTable[a] = v
        elif c == 46:
            v = tuple([read4() for i in range(6)])
            key = v[0] | (v[1] << 32)
            v = tuple(struct.pack(">L", x & 0xffffffff) for x in v)
            eventIdTable[key] = v
        # literals.append(v)
        return v

    def readList(id, size):
        cur = r = {'next': None, 'value': None}
        if size == 2:
            while True:
                a = read2()
                b = read2()
                value = findObject(a)
                cur['value'] = value
                if b < 0 or findObject(b, False) is None:
                    index, realRef, _size = read_header()
                    if types[index] != 'list':
                        item = readObject(realRef, (index, realRef, _size))
                        cur['next'] = {'value': item, 'next': None}
                        break
                    else:
                        item = {'next': None}
                        refMap[realRef] = item
                        cur['next'] = item
                        cur = cur['next']
                    if _size != 2:
                        break
                else:
                    break
            if _size != 0:
                raise Exception('list size is not in 0, 2')
            rlist = []
            cur = r
            while cur['next']:
                rlist.append(cur['value'])
                cur = cur['next']
            refMap[id] = rlist
            return rlist
        else:
            if size != 0:
                raise Exception('list initial size is not in 0, 2')
            return []

    def readUntypedDataBlock(id, size):
        refMap[id] = f.read(size)
        # literals.append(refMap[id])
        return refMap[id]

    def readUserId(size):
        c = read1()
        assert c == 48
        a = read2()
        a_s = f.read(a)
        b = read2()
        b_s = f.read(b)
        if b == 0:
            v = a_s
        else:
            v = b_s
        assert size == a + b + 4
        userIdTable[v] = a_s
        # literals.append(a_s)
        return UserId(a_s)

    def readCmdBlock(id, size):
        x = read1()
        a = read2()
        b = read2()
        c = read2()
        data = _readRefList(size)
        return x, a, b, c, data

    def readDataBlock(id, size):
        c = read1()
        if c != 8:
            result = f.read(c)
        else:
            f.read(8)
            f.read(4)
            f.read(70)
            a = f.read(4)
            f.read(4)
            typeCode = f.read(4)
            if typeCode == 'alis':
                result = ('alis', a)
            else:
                if typeCode == 'targ':
                    result = 'ppc://'
                else:
                    exit()
            result = result, f.read(size - 94)
        refMap[id] = result
        # literals.append(result)
        return result

    def readRecord(id, size):
        assert size in (1, 3)
        if size == 3:
            records = []
            while size == 3:
                A = read2()
                B = read2()
                C = read2()
                objA = findObject(A)
                objB = findObject(B)
                objC = findObject(C, False)
                if objC is None:
                    index, ref, size = header = read_header()
                    if index != 6:
                        readObject(ref, reuse_header=header)
            refMap[id] = records
            return records
        else:
            return '<empty record>'

    def read_header():
        index = read1()
        realRef = read2()
        size = read2()
        obj = index, realRef, size
        # literals.append(obj)
        return obj

    def readObject(refIdExpected, reuse_header=None):
        if reuse_header:
            index, id, size = reuse_header
        else:
            index, id, size = read_header()
        # print id, refIdExpected
        assert id == refIdExpected
        obj = {}
        obj['kind'] = kind = types[index]
        if kind == 'valueBlock2':
            data = readValueBlock(id, size)
        elif kind == 'symbol':
            data = readSymbol(size)
        elif kind == 'untypedPointerBlock':
            data = readUntypedPointerBlock(id, size)
        elif kind == 'codeId':
            data = readCodeId(size)
        elif kind == 'list':
            data = readList(id, size)
        elif kind == 'untypedDataBlock':
            return readUntypedDataBlock(id, size)
        elif kind == 'int':
            return size
        elif kind == 'long':
            return read4()
        elif kind == 'float':
            data = struct.unpack(">d", f.read(8))[0]
        elif kind == 'userId':
            return readUserId(size)
        elif kind == 'dataBlock':
            data = readDataBlock(id, size)
        elif kind == 'cmdBlock':
            data = readCmdBlock(id, size)
        elif kind == 'record':
            data = readRecord(id, size)
        else:
            print kind, 'is not handled'
            exit()
        obj['data'] = data
        obj['id'] = id
        # literals.append(obj)
        return obj

    r = readObject(0)
    # pprint(# literals)
    # exit()
    return r


if __name__ == '__main__':
    # TODO: make below code work. it doesn't work in current because applescript-disassembler has no package for now
    # If run as script, it'll cause error in importing "engine.*".
    path = sys.argv[1]
    pprint(load_file(path))
