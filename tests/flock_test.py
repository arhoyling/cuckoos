from __future__ import unicode_literals

import six
from inspect import getmodule
from cuckoos.flock import flock, unflock, get_context

if six.PY2:
    import __builtin__ as builtins
else:
    import builtins as builtins


class TestPack:
    def func(self):
        return 1

    def test_flock_flat_attribute(self):
        assert flock({'one': 1}).one == 1

    def test_flock_flat_method(self):
        obj = flock({'one': self.func})
        assert six.callable(obj.one)
        assert isinstance(obj.one, type(self.func))
        assert obj.one() == 1

    def test_flock_nested_attributes(self):
        obj = flock({'one': {'two': {'three': 1, 'four': [1, {'five': 5}]}}})
        assert obj.one.two.three == 1
        assert obj.one.two.four == [1, {'five': 5}]

    def test_flock_nested_methods(self):
        obj = flock({'one': {'two': {'three': self.func}}})
        assert six.callable(obj.one.two.three)
        assert isinstance(obj.one.two.three, type(obj.one.two.three))
        assert obj.one.two.three() == 1

    def test_flock_nested_object(self):
        Class = type(str('Class'), (object,), {})
        obj = flock({'attr': Class()})
        assert isinstance(obj.attr, Class)

    def test_flock_unflock(self):
        definition = {'one': {'two': {'three': self.func}}}
        assert unflock(flock(definition)) == definition


class TestContext:
    def func(self):
        return 1

    def test_context_flocked_object(self):
        obj = flock({'one': {'two': lambda: 3, 'three': 4}})
        assert get_context(obj) == obj
        assert get_context(obj.one) == obj
        assert get_context(obj.one.two) == obj

    def test_context_function(self):
        assert get_context(lambda: 1) == getmodule(self)
        assert get_context(self.func) == self
        assert get_context(len) == builtins

    def test_context_random_object(self):
        flocker = TestContext()
        assert get_context(flocker) == flocker
        assert get_context('str') is None
        assert get_context(1) is None

    def test_context_collections(self):
        assert get_context([1, 2, 3, 4]) is None
        assert get_context((1, 2, 3,)) is None
        assert get_context({1: 2}) is None
