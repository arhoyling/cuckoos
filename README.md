Cuckoos
=======

Cuckoos allows you to automatically bundle dictionaries into object. It also provides `NestedObjectType`, a new type which allows you to namespace your attributes.

Example Use
-----------
### Simple objectification

```python
from cuckoos.flock import flock

definition = {
    'triple': lambda _, x: 3 * x,
    'coeff': 4
}
obj = flock(definition)

assert obj.triple(2) == 6
assert obj.coeff == 4
```

### Nested objectification

```python
from cuckoos.flock import flock
from uuid import uuid4

definition = {
    'user': {
        'name': 'User',
        'email': 'user@example.com',
    },
    'auth': {
        'token': 'adcce3c0-00b2-11e6-8d22-5e5517507c66',
        'is_active': lambda _: True
    },
    'created_at': '2023-10-12T07:32:11'
}

obj = flock(definition)

assert obj.user.name == 'User'
assert obj.created_at == '2023-10-12T07:32:11'
assert obj.auth.is_active()
```

### Nest object

```python
import requests
from requests.compat import urljoin

from cuckoos.flock import flock
from cuckoos.nest import Nest

class Request(Nest):
    base_url = 'http://httpbin.org/'
        
    def __init__(self, uri):
        self.uri = uri
    
    def get(self, key):
        return requests.get(urljoin(self.base_url, self.uri), params={'id': key})
    
    # Uses __ as a special nesting delimiter
    def get__json(self, key):
        return self.get(key).json()
        
    def get__object(self, key):
        return flock(self.get.json(key))

req = Request('get')
key = '7fb64be0-f4d2-4acc-8fa8-b33eba90acd2'

assert req.base_url == 'http://httpbin.org/'
assert req.get(key).json()['args']['id'] == key
assert req.get.json(key)['args']['id'] == key
assert req.get.object(key).args.id == key
```

# TODO
* Create usage examples
* Extend docs
* Add tox (Should support 2.6, 2.7, 3.4, 3.5+)
* Configure travis
