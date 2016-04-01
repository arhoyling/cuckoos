from __future__ import unicode_literals

import sys
from six import PY3
if PY3:
    from io import StringIO
else:
    from cStringIO import StringIO
try:
    from collections import OrderedDict
except ImportError:
    from ordereddict import OrderedDict

from toolbelt.collections import (
    merge, listify, extend, partition, pprint
)


class TestUtils:
    def test_listify(self):
        assert listify(4) == [4]
        assert listify((1, 2,)) == [1, 2]
        assert listify([0, 1]) == [0, 1]

    def test_merge(self):
        assert merge({'one': 1}, {'one': 0}) == {'one': [1, 0]}
        assert merge({'one': [0, 1]}, {'one': 2}) == {'one': [0, 1, 2]}
        assert merge({'one': [0, 1]}, {'one': {'two': 2}}) == {'one': [0, 1, {'two': 2}]}
        assert merge({'one': {'two': 2}}, {'one': 1}) == {'one': [{'two': 2}, 1]}
        assert merge({'one': {'two': 2}}, {'one': {'three': 3}}) == {'one': {'two': 2, 'three': 3}}
        assert merge({'one': {'two': 2}}, {'one': {'two': 3}}) == {'one': {'two': [2, 3]}}

    def test_extend(self):
        assert extend([1, 2], 4) == [1, 2, 4]
        assert extend([1, 2], (1, 2,)) == [1, 2, 1, 2]
        assert extend([1, 2], {1: 2, 3: 4}) == [1, 2,{1: 2, 3: 4}]
        assert extend([1, 2], [0, 1]) == [1, 2, 0, 1]

    def test_partition(self):
        assert partition('a__nested__string') == {'a': {'nested': {'string': None}}}
        assert partition('a.nested.string', sep='.') == {'a': {'nested': {'string': None}}}
        assert partition('a__nested__string', sep='.') == {'a__nested__string': None}
        assert partition('a_string', sep='_', ref=42) == {'a': {'string': 42}}
