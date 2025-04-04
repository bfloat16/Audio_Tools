from lupa import LuaRuntime

lua = LuaRuntime(unpack_returned_tuples=True)

with open('0108.scb') as f:
    a = lua.execute(f.read())

print(a)