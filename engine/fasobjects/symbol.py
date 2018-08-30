from . import register
from ..runtimeobjects import NIL

class Symbol:
	def __init__(self, num):
		self.num = num
	def __repr__(self):
		return '<Symbol num=0x%x>' % self.num

@register(1)
def load_symbol(table, id, inlined):
	# TODO: symbol translated when not run only?
	if inlined:
		# Fun thing is, it pushes a 64bit immediate to stack, which leads to type confusion
		table.loader.stack.push(Symbol(table.loader.read_u64()))
	else:
		table.loader.stack.push(NIL)