fastypes = {}


def register(type):
    def handler(f):
        fastypes[type] = f
        return f

    return handler


from . import data_block, record, valueblock, symbol, untyped_pointer_block, code_id, user_id, list, immediates, \
    untyped_data_block, cmdblock, long_data_block, untyped_long_data_block
