from __future__ import unicode_literals, absolute_import

import six
from inspect import getmodule, ismethod
from types import FunctionType, BuiltinFunctionType

__all__ = ['flock', 'unflock', 'get_context']

collection_types = (dict, list, tuple,)


def flock(definition):
    """
    Turns a dictionary into an object. This supports nested structures. Each
    level will spawn a new object.
    >>> flock({'one': 1}).one
    1
    >>> flock({'one': {'two': 2}}).one.two
    2

    :param definition: definition of the object to flock.
    :type definition: dict
    :return : full-fledged object as defined by the original dictionary.
    :rtype: Namespace

    """
    assert isinstance(definition, dict)
    schema = {}
    for key, value in six.iteritems(definition):
        if isinstance(value, dict):
            schema[key] = flock(value)
        else:
            schema[key] = value
    return type(str('Flock'), (Context,), schema)()


def unflock(obj):
    """
    Turn an object into a dictionary. This supports nested structures.
    >>> obj = flock({'one': {'two': 2}})
    >>> unflock(obj)
    {'one': {'two': 2}}

    :param obj: object to unflock.
    :type obj: object
    :return: definition
    :rtype: dict

    """
    assert isinstance(obj, object)
    schema = {}
    for attr_name in (entity for entity in dir(obj) if '_' not in entity[:2]):
        attr = getattr(obj, attr_name)
        if isinstance(attr, Context):
            structure = {attr_name: unflock(attr)}
        else:
            structure = {attr_name: attr}
        schema.update(structure)
    return schema


if six.PY2:
    # noinspection PyUnresolvedReferences
    builtins = (int, long, float, basestring, bool,
                FunctionType, BuiltinFunctionType,
                list, tuple, dict)
else:
    builtins = (int, float, str, bool,
                FunctionType, BuiltinFunctionType,
                list, tuple, dict)


def get_context(entity):
    """Returns the operating context of the given object.

    If the object is a subclass of Context, returns the top most context (or
    containing instance) of the object.

    If the object is a builtin object, returns the operating module (if available).

    Otherwise, returns the object itself.

    >>> obj = flock({'one': {'two': lambda : 1}})
    >>> get_context(obj.one.two) == obj
    True

    :param entity: object which context we are trying to find.
    :return: context of the current object.

    """
    if isinstance(entity, builtins):
        return getmodule(entity)
    if ismethod(entity):
        return get_context(six.get_method_self(entity))

    return entity.__context__ if hasattr(entity, '__context__') else entity


class Context(object):
    """Base class for flocked object."""
    def __get__(self, instance, owner):
        """Overriding __get__ allows us to create a context attribute.
        __context__ will be the top most container of the current context."""
        context = instance.__context__ if hasattr(instance, '__context__') else instance
        setattr(self, '__context__', context)
        return self
