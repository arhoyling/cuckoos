from __future__ import unicode_literals, absolute_import

from six import iteritems, callable
from inspect import isfunction
from functools import update_wrapper
from .flock import flock, get_context
from .utils import merge, partition


__all__ = ('NestedObjectType', 'Nest')


def excluded(name, ref):
    """Returns whether a given (name, ref,) tuple should be excluded from
    compiling.

    Here, if the name is private ('_' or '__' prefix) or if the given reference
    is not callable, the tuple should be excluded.
    >>> excluded('__method', lambda : True)
    True
    >>> excluded('attribute', 0)
    True
    >>> excluded('method', lambda : True)
    False

    :type name: basestring
    :param ref: value corresponding to the attribute name.
    :rtype: bool

    """
    return name[0] == '_' or not callable(ref)


def fledge(method):
    """Recontextualize a method outside of its nested namespace.
    In other words, use this if you want nested methods to be called within the
    context of their top-most composing class rather than their immediate
    namespace.

    For example, the context of object.nested.method is object.nested. 'fledge'
    will extract the method so that the context of object.nested.method becomes
    object.

    This can be very useful for users of the NestedObjectType as they only have
    a flat view of their class, and they will want to access top level
    attributes inside their nested functions.

    :param method: method to recontextualize
    :return: recontextualized method

    """
    def wrapped_method(self, *args, **kwargs):
        result = method(get_context(self), *args, **kwargs)
        # make sure we inherit any function properties
        update_wrapper(wrapped_method, method)
        return result

    update_wrapper(wrapped_method, method)
    return wrapped_method


def consolidated(schema):
    """
    Walk through the schema and merge list into dictionaries following a simple
    rule. If a member of the list is not a dictianary but a callable, we create
    a new dictionary {'__call__': value}. If a value is neither callable or
    a dictionary, we have a deeper problem so we fail.

    e.g.:
    ```
    schema = {
        'land': [
            <function Object.land at 0x7ff3ff119bf8>,
            {'realm': <function Object.land__realm at 0x7ff3ff119840>}
            {'realm':
                {'act': <function Object.land__realm__act at 0x7f21a16c3a60>}
            }
        ]
    }
    consolidated(schema)
    {
        'land': [
            {'__call__': <function Object.land at 0x7ff3ff119bf8>},
            {'realm':
                {
                    '__call__': <function Object.land__realm at 0x7ff3ff119840>,
                    'act': <function Object.land__realm__act at 0x7f21a16c3a60>
                }
            }
        ]
    }
    """
    if not isinstance(schema, dict):
        return schema

    consolidated_schema = {}
    for key, value in iteritems(schema):
        if isinstance(value, list):
            value_dict = {}
            for element in value:
                if callable(element):
                    element = {'__call__': element}
                value_dict = merge(value_dict, element)
            consolidated_schema[key] = consolidated(value_dict)
        else:
            consolidated_schema[key] = consolidated(value)
    return consolidated_schema


class NestedObjectType(type):
    """The nested object type looks up for method and creates nested methods if
    necessary. Method hierarchy is represented in code using the
    double underscore idiom.
        nested__method -> nested.method

    Arbitrary nesting should be possible.
    >>> from six import with_metaclass
    >>> class NestedClass(with_metaclass(NestedObjectType)):
    ...     def method(self):
    ...         return 0
    ...
    ...     def nested__method(self):
    ...         return 1
    ...
    >>> obj = NestedClass()
    >>> obj.method()
    0
    >>> obj.nested.method()
    1

    """
    # noinspection PyInitNewSignature,PyShadowingBuiltins
    def __new__(mcs, name, bases, namespace):
        schema = mcs.__compile_namespace(namespace)
        cls = super(NestedObjectType, mcs).__new__(mcs, name, bases, dict(schema))
        cls.__methods__ = tuple(namespace)
        return cls

    @classmethod
    def __compile_namespace(mcs, namespace):
        """
        Convert the given namespace into a flocked namespace, using '__' as a
        separator for nested structures. Private methods and attributes are
        kept untouched.

        :param namespace: original namespace as defined by the class.
        :type namespace: dict
        :rtype: dict

        """
        schema = {}
        for method_name, reference in iteritems(namespace):
            if excluded(method_name, reference):
                # If we keep our attribute as a dictionary it will be
                # misinterpreted during flocking, so we wrap it in an
                # unambiguous object.
                if isinstance(reference, dict):
                    reference = mcs.__wrap(reference)
                structure = {method_name: reference}
            else:
                if isfunction(reference):
                    reference = fledge(reference)
                structure = partition(method_name, reference)
            schema = merge(schema, structure)
        for key, value in iteritems(consolidated(schema)):
            if isinstance(value, (dict, )):
                schema[key] = flock(value)
            else:
                # Now we need to unwrap any dictionary attribute.
                if type(value).__name__ == '#!Wrapper':
                    value = value.content
                schema[key] = value
        return schema

    @staticmethod
    def __wrap(value):
        wrapper = type(str('#!Wrapper'), (object,), {})()
        wrapper.content = value
        return wrapper

Nest = NestedObjectType(str('Nest'), (object,), {})
