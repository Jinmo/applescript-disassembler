#!/usr/bin/env python2

from engine.definitions import opcodes, comments
from engine.fasparser import load_file

import sys
import struct


# Some hardcoded offset in apple script binary
# root -> (data -> (literal, code))
ROOT_OFFSET = -1
DATA_OFFSET = 2
LITERAL_OFFSET = 5
CODE_OFFSET = 6


def main():
    state = {'pos': 0, 'tab': 0}

    path = sys.argv[1]
    f = load_file(path)

    code = f['data'][ROOT_OFFSET]
    # assert code['kind'] == 'untypedPointerBlock'  # I think it doesn't matter
    data = code['data'][DATA_OFFSET]['data']
    literals = data[LITERAL_OFFSET]['data']
    code = bytearray(data[CODE_OFFSET])

    def word():
        r = struct.unpack(">H", code[state['pos']:state['pos'] + 2])[0]
        state['pos'] += 2
        return r - 0x10000 if r & 0x8000 else r

    def literal(x):
        if x >= len(literals):
            return '[L%d]' % x
        return literals[x]

    def variable(x):
        return '[var_%d]' % x

    while state['pos'] < len(code):
        print " " * state['tab'] * 4, '%05x' % state['pos'],
        c = code[state['pos']]
        state['pos'] += 1
        op = opcodes[c]
        print op,
        # print ops for each instruction
        if op == 'Jump':
            print hex(state['pos'] + word()),
        elif op == 'PushLiteral':
            print c & 0xf, '#', literal(c & 0xf),
        elif op == 'PushLiteralExtended':
            v = word()
            print v, '#', literal(v),
        elif op in ['Push0', 'Push1', 'Push2', 'Push3']:
            pass
        elif op == 'PushIt':
            pass
        elif op == 'PushGlobal':
            v = literal(c & 0xf)
            print v,
        elif op == 'PushGlobalExtended':
            v = literal(word())
            print v,
        elif op == 'PopGlobal':
            print literal(c & 0xf),
        elif op == 'PopGlobalExtended':
            print literal(word()),
        elif op == 'PopVariable':
            print variable(c & 0xf),
        elif op == 'PopVariableExtended':
            print variable(word()),
        elif op == 'Tell':
            print word(),
            state['tab'] += 1
        elif op == 'Subtract':
            pass
        elif op == 'Add':
            pass
        elif op == 'Equal':
            pass
        elif op == 'Concatenate':
            pass
        elif op == 'Remainder':
            pass
        elif op == 'Divide':
            pass
        elif op == 'Multiply':
            pass
        elif op == 'LessThanOrEqual':
            pass
        elif op == 'LessThan':
            pass
        elif op == 'GreaterThan':
            pass
        elif op == 'Contains':
            pass
        elif op == 'Exit':
            pass
        elif op == 'Power':
            pass
        elif op == 'Negate':
            pass
        elif op == 'PushUndefined':
            pass
        elif op == 'PushVariable':
            print variable(c & 0xf),
        elif op == 'PushVariableExtended':
            print variable(word())
        elif op in ['MakeObjectAlias', 'MakeComp']:
            t = c - 23
            print t, '# ' + comments.get(t, '<Unknown>')
        elif op == 'SetData':
            pass
        elif op == 'GetData':
            pass
        elif op == 'Dup':
            pass
        elif op in ('TestIf', 'And'):
            print hex(state['pos'] + word()),
        elif op == 'MessageSend':
            v = word()
            print v, '#', literal(v),
        elif op == 'StoreResult':
            pass
        elif op == 'PositionalMessageSend':
            v = word()
            print v, '#', literal(v),
        elif op == 'LinkRepeat':
            v = word() + state['pos']
            print hex(v)
        elif op == 'EndTell':
            state['tab'] -= 1
            pass
        elif op == 'RepeatInRange':
            print word(),
        elif op == 'Return':
            pass
        elif op == 'MakeVector':
            pass
        elif op == 'Coerce':
            pass
        elif op == 'PushMe':
            pass
        elif op == 'GreaterThanOrEqual':
            pass
        elif op == 'RepeatWhile':
            pass
        elif op == 'Pop':
            pass
        elif op == 'Quotient':
            pass
        elif op == 'DefineActor':
            print hex(word()),
        elif op == 'EndDefineActor':
            pass
        elif op == 'PushMinus1':
            pass
        else:
            print '<disassembler not implemented>',
        print


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print 'Usage: python disassembler.py [apple script-compiled .scpt file]'
        exit()

    main()
