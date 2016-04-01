from __future__ import unicode_literals, absolute_import

from six import iteritems, callable


def merge(this, that):
    """
    Merge two dictionaries into a single one. It differs from dict.update in
    that it does not override values in the original dictionary. When a key is
    found in both dictionaries, a multi-value entry is created or extended.
    >>> merge({'one': 1}, {'one': 0})
    {'one': [1, 0]}
    >>> merge({'one': [0, 1]}, {'one': {'two': 2}})
    {'one': [0, 1, {'two': 2}]}
    >>> merge({'one': {'two': 2}}, {'one': 1})
    {'one': [{'two': 2}, 1]}
    >>> merge({'one': {'two': 2}}, {'one': {'three': 3}})
    {'one': {'three': 3, 'two': 2}}
    >>> merge({'one': {'two': 2}}, {'one': {'two': 3}})
    {'one': {'two': [2, 3]}}

    :param this: target dictionary
    :param that: dictionary to merge
    :return: merged dictionary
    :rtype: dict

    """
    if not isinstance(this, dict) or not isinstance(that, dict):
        return extend(listify(this), that)
    for key, value in iteritems(that):
        if key in this:
            this[key] = merge(this[key], value)
        else:
            this[key] = value
    return this


def extend(target, element):
    """
    Extend the given list with the given element. If element is a scalar, it is
    appended to target; if element is a list, target is extended with it.
    >>> extend([1, 2], 4)
    [1, 2, 4]
    >>> extend([1, 2], (1, 2,))
    [1, 2, 1, 2]
    >>> extend([1, 2], {1: 2, 3: 4})
    [1, 2, {1: 2, 3: 4}]
    >>> extend([1, 2], [0, 1])
    [1, 2, 0, 1]

    :param target:
    :type target: list
    :param element:
    :rtype: list

    """
    assert isinstance(target, list)
    if isinstance(element, (list, tuple,)):
        target.extend(element)
    else:
        target.append(element)
    return target


def listify(obj):
    """Returns a list with the given object. If the object is already a list, do
    nothing. If the object is a tuple, convert it to a list.
    >>> listify(4)
    [4]
    >>> listify((1, 2,))
    [1, 2]
    >>> listify([0, 1])
    [0, 1]

    :param obj: object to listify
    :rtype: list

    """
    if isinstance(obj, (list, tuple,)):
        return list(obj)
    return [obj]


def partition(name, ref=None, sep='__'):
    """
    Partition the given string into a nested dictionary using sep as a
    separator. If ref is provided, the leaf's value of the resulting structure
    is ref.
    >>> partition('a__nested__string')
    {'a': {'nested': {'string': None}}}
    >>> partition('a.nested.string', sep='.')
    {'a': {'nested': {'string': None}}}
    >>> partition('a__nested__string', sep='.')
    {'a__nested__string': None}
    >>> partition('a_string', sep='_', ref=42)
    {'a': {'string': 42}}

    :param name: string to partition
    :type name: basestring
    :param ref: value of the deepest leaf of the structure
    :param sep: separator used for partitioning.
    :type sep: basestring
    :return: a nested dictionary resulting from the partition of the input
             string.
    :rtype: dict
    """
    root, _, rel = name.partition(sep)
    if rel:
        return {root: partition(rel, ref, sep)}
    elif callable(ref):
        ref.__name__ = str(name)  # str() used for Python2 support
    return {name: ref}
