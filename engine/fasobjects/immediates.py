import struct

from . import register
from ..runtimeobjects import *


@register(3)
def read_int(table, id, inlined):
    table.loader.stack.push(Fixnum(inlined))


@register(9)
def read_bool(table, id, inlined):
    table.loader.stack.push(bool(inlined))


@register(7)
def read_longint(table, id, inlined):
    if inlined != 4:
        raise Exception('Error -1702: LongInteger size error')
    table.loader.stack.push(table.loader.read_s32())


@register(8)
def read_float(table, id, inlined):
    if inlined != 8:
        raise Exception('Error -1702: Float size error')
    table.loader.stack.push(struct.unpack(
        ">d", table.loader.read_u64(False))[0])


@register(12)
def read_string(table, id, inlined):
    table.loader.stack.push(Object(UnicodeText(bytes(table.loader.read(
        table.loader.read_u16())), bytes(table.loader.read(table.loader.read_u16())))))
