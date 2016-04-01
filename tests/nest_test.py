from __future__ import unicode_literals

import pytest
from cuckoos import Nest


class Birds(Nest):
    attribute = {'zero': 0}

    def method(self):
        pass

    def top_level_method(self):
        pass

    def nested(self):
        pass

    def nested__method(self):
        pass

    def nested__deeper(self):
        pass

    def nested__deeper__method(self):
        pass

    def branch__method(self):
        pass

    def __private(self):
        pass


class TestNestedObjectType:
    def setup(self):
        self.object = Birds()

    def test_generated_namespace(self):
        assert hasattr(self.object, 'nested')
        assert hasattr(self.object.nested, '__call__')
        assert hasattr(self.object.nested, 'method')
        assert hasattr(self.object.nested, 'deeper')
        assert hasattr(self.object.nested.deeper, 'method')
        assert hasattr(self.object, 'branch')
        assert hasattr(self.object, '_Birds__private')
        assert hasattr(self.object, 'attribute')
        assert not hasattr(self.object, 'top')
        assert not hasattr(self.object, 'level')
        assert not hasattr(self.object, 'nested__method')
        assert not hasattr(self.object, 'nested__deeper__method')

    def test_valid_method_access(self):
        assert callable(self.object.method)
        assert callable(self.object.top_level_method)
        assert callable(self.object.nested)
        assert callable(self.object.nested.method)
        assert callable(self.object.nested.deeper)
        assert callable(self.object.nested.deeper.method)
        assert callable(self.object.branch.method)

    def test_invalid_method_access(self):
        with pytest.raises(AttributeError):
            self.object.branch__method()

        with pytest.raises(AttributeError):
            self.object.nested__deeper__method()

        with pytest.raises(AttributeError):
            self.object.branch__method()

        with pytest.raises(AttributeError):
            self.object.deeper.method()

    def test_namespace_dereferencing(self):
        service = self.object.nested
        assert service is self.object.nested
        assert callable(service)
        assert hasattr(service, 'method')
        assert callable(service.method)

        service = self.object.nested.deeper
        assert service is self.object.nested.deeper
        assert callable(service)
        assert hasattr(service, 'method')
        assert callable(service.method)

    def test_dictionary_attribute(self):
        assert self.object.attribute == {'zero': 0}
