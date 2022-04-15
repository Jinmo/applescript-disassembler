"""
Known type index:
0x01: Constant
0x02: List
0x03: Integer
0x05: Float
0x07: Integer
0x08: Application
0x0A: ClassIdentifier
0x0B: Constant
0x0C: LargeFloat
0x0D: RawData
0x0F: Actor
0x2E: EventIdentifier
0x6C: Comment
0x6E: Value
0xB1: UnicodeText
"""

import struct

value_types = {}


def value(cls):
    value_types[cls.type] = value
    return cls


class Value(object):
    def __repr__(self):
        return "<Value type=%d>" % self.type

    pass


class UnknownData(Value):
    def __init__(self, string):
        self.string = string

    def __repr__(self):
        return "<Value type=%d>" % self.type


@value
class Special(Value):
    # Some special constants with type 2
    type = 2
    KNOWN_CONSTANTS = {
        0x7A: 'True',
        0x79: 'False',
        0x00: 'nil'
    }

    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return "<Value type=special value=%s>" % \
            Special.KNOWN_CONSTANTS.get(
                self.value, 'unknown_0x%x' % self.value)

    def __eq__(self, other):
        return isinstance(other, Special) and other.value == value

    pass


NIL = Special(0)
TRUE = Special(0x7A)
FALSE = Special(0x79)


@value
class Fixnum(Value):
    type = 6

    def __init__(self, value):
        self.value = value
        # assert self.value < 2 ** 56 (or 24?) since it's stored in value * 8 + 6, in size_t format.

    def __repr__(self):
        return "<Value type=fixnum value=0x%x>" % self.value

    def __eq__(self, other):
        return isinstance(other, Fixnum) and other.value == self.value


@value
class Constant(Fixnum):
    type = 11

    def __repr__(self):
        return "<Value type=constant value=0x%x>" % self.value


@value
class Object(Value):
    type = 0

    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return "<Value type=object value=%r>" % self.value


@value
class String(Value):
    type = 0  # or 8?

    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return "<Value type=string value=%r>" % self.value


class Binding(Object):
    def __init__(self, a, b, c):
        self.a = a
        self.b = b
        self.next = None
        self.c = c

    def __repr__(self):
        return "<Binding a=%r b=%r c=%r next=%r>" % (
            self.a, self.b, self.c, self.next
        )


class EmptyBinding(Binding):
    def __init__(self):
        pass

    def __repr__(self):
        return "<Binding empty>"


@value
class EventIdentifier(Value):
    type = 46

    def __init__(self, a, b, c, d, e, f):
        self.identifier = a, b, c, d, e, f

    def __repr__(self):
        return "<Value type=event_identifier value=%r-%r-%r-%r-%r-%r>" % \
            tuple([struct.pack(">L", x) for x in self.identifier])


class Reference:
    def __init__(self, x):
        self.to = x

    def __repr__(self):
        return '<Reference to=%s>' % self.to


@value
class Pair(Value):
    type = 4

    def __init__(self, first, second):
        self.first, self.second = first, second

    def __repr__(self):
        return "<Value type=pair first=%r second=%r>" % \
            (self.first, self.second)


class EmptyPair(Pair):
    def __init__(self):
        pass

    def __repr__(self):
        return "<Value type=pair empty>"


class Statement:
    def __init__(self, type_info, bytecode_start, bytecode_end):
        self.type_info = type_info
        self.bytecode_start, self.bytecode_end = bytecode_start, bytecode_end
        self.children=None

    def __repr__(self):
        return "<Statement type_info=%r bytecode_start=%r bytecode_end=%r children=%r>" % \
            (self.type_info, self.bytecode_start, self.bytecode_end, self.children)

    def set_children(self, children):
        self.children=children


secondActor = Reference('secondActor')


class UnicodeText(Value):
    type = 0xB1

    def __init__(self, text, style=None):
        self.text = text
        self.style = style

    def __repr__(self):
        return "<UnicodeText text=%r style=%r>" % \
            (self.text, self.style)


def parse_value(type, *value):
    t = value_types.get(type)
    return t(*value)


kUASIndexClassIdentifier = 0x0A
kUASIndexClassIdentifier2 = 0x2F
kUASIndexEventIdentifier = 0x2E
kUASIndexSpecial = 0x0B
kUASIndexRawData = 0x0D


def get_flipper(t):
    if t == kUASIndexSpecial:
        return flip_kUASIndexSpecial
