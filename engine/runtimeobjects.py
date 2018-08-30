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
        return ("<Value type=special value=%s>" % Special.KNOWN_CONSTANTS.get(self.value, 'unknown_0x%x' % self.value))

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
        return "<Value type=event_identifier value=%08x-%08x-%08x-%08x-%08x-%08x>" % self.identifier


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
        return "<Value type=pair first=%r second=%r>" % (self.first, self.second)


class EmptyPair(Pair):
    def __init__(self):
        pass

    def __repr__(self):
        return "<Value type=pair empty>"


secondActor = Reference('secondActor')


def parse_value(type, value):
    t = value_types.get(type)
    return t(value)


kUASIndexClassIdentifier = 0x0A
kUASIndexClassIdentifier2 = 0x2F
kUASIndexEventIdentifier = 0x2E
kUASIndexSpecial = 0x0B
kUASIndexRawData = 0x0D


def get_flipper(t):
    if t == kUASIndexSpecial:
        return flip_kUASIndexSpecial
