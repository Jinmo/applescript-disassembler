from . import register

@register(11)
def load(table, id, size):
	c = table.loader.read_u8()
	if c != 48:
		raise Exception('Error -1702: nope')
	a = table.loader.read_u16()
	_a = table.loader.read(a)
	b = table.loader.read_u16()
	_b = table.loader.read(b)
	if a >= 0x100 or b >= 0x100:
		raise Exception('Malformed file')
	with table.loader.context('UASUserIdentifierTable') as context:
		if b:
			key = _a
			value = _b
		else:
			key = _a
			value = _a
		table.loader.stack.push(value)
		if not hasattr(context, 'userIdentifiers'):
			context.userIdentifiers = {}
		context.userIdentifiers[_a if not b else _b] = _b