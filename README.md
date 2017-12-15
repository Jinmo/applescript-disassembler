# AppleScript disassembler

Run-only applescript reversing. This is disassembler for that.

## What is it all about?

To write disassembler I reversed vm routine, file format (fas, uas) in applescript binary.

### Usage

```shell
python2 disassembler.py <scpt file>
```

- disassembler.py uses fasparser.py to parse format and extract literal table & code and disassemble it.
- fasparser.py parses compiled scpt file. If it's compiled without -x (run only mode), it would have error on cmdBlock parsing, for now.

** WARNING: ** It may have some unimplemented parts. Please make an issue for that if you liked it!
