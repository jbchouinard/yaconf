from yamconfig.core import *

a = lambda: {"foo": 1, "bar": 2, "d": {1: 1, 2: 2}}

a1 = a()
b1 = {}
deep_merge(a1, b1)
assert a1 == a()

a2 = a()
b2 = {"foo": 2}
deep_merge(a2, b2)
assert a2["foo"] == 2

a3 = a()
b3 = {"d": {1: 11, 3: 33}}
deep_merge(a3, b3)
assert a3["d"][1] == 11
assert a3["d"][3] == 33


class AConfig(Config):
    z = Option("z", default=20, type=int)


class SomeConfig(Config):
    a = Option("a", type=AConfig)
    x = Option("x", default=1, type=int)
    y = Option("y", default="foo", type=str)


c = SomeConfig()
c.from_yaml(
    """
x: 10
y: bar
a:
    z: 25
"""
)
assert c.x == 10
assert c.y == "bar"
assert c.a.z == 25
c.validate()

c.set("a.z", 30)
assert c.a.z == 30
