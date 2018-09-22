#!/usr/bin/env python2

import struct
import sys
from engine.util import opcodes, comments

from engine.fasparser import Loader

# Some hardcoded offset in apple script binary
# root -> (<function index> -> (name, ..., literal, code))
ROOT_OFFSET = -1

# function object
NAME_OFFSET = 0
ARGS_OFFSET = 2
LITERAL_OFFSET = 5
CODE_OFFSET = 6


def main():
    path = sys.argv[1]
    f = Loader()
    f = f.load(path)

    root = f[ROOT_OFFSET]

    # assert code['kind'] == 'untypedPointerBlock'  # I think it doesn't matter
    def disassemble(function_offset):  # function number
        state = {'pos': 0, 'tab': 0}
        function = root[function_offset]
        if type(function) is not list:
            print "<not a function>"
            return
        if len(function) < 7:
            print "<maybe binding?>", function
            return
        literals = function[LITERAL_OFFSET + 1]
        name = function[NAME_OFFSET + 1]
        args = function[ARGS_OFFSET + 1]
        print 'Function name :', name
        print 'Function arguments: ',

        _args = []
        if isinstance(args, list) and len(args) >= 3 and isinstance(args[2], list):
            print args[2][1:]
            _args = args[2][1:]
        else:
            print '<empty or unknown>'
        code = bytearray(function[CODE_OFFSET + 1].value)

        def word():
            r = struct.unpack(">H", code[state['pos']:state['pos'] + 2])[0]
            state['pos'] += 2
            return r - 0x10000 if r & 0x8000 else r

        def literal(x):
            if x >= len(literals):
                return '[L%d]' % x
            return literals[x]

        def variable(x, local=False):
            if local and len(_args) > x:
                return '[var_%d (%r)]' % (x, _args[x])
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
                print variable(c & 0xf, True),
            elif op == 'PopVariableExtended':
                print variable(word(), True),
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
                print variable(c & 0xf, True),
            elif op == 'PushVariableExtended':
                print variable(word(), True)
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
            elif op == 'MakeRecord':
                pass
            elif op == 'ErrorHandler':
                print word(),
                state['tab'] += 1
            elif op == 'EndErrorHandler':
                state['tab'] -= 1
            elif op == 'StartsWith':
                pass
            elif op == 'EndsWith':
                pass
            elif op == 'PushParentVariable':
                print word(), variable(word()),
            elif op == 'PopParentVariable':
                print word(), variable(word()),
            else:
                print '<disassembler not implemented>',
            print

    for cur_function_offset in range(2, len(root)):
        print '=== data offset %d ===' % cur_function_offset
        disassemble(cur_function_offset)


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print 'Usage: python disassembler.py [apple script-compiled .scpt file]'
        exit()

    main()
