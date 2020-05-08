class GlobalScope(dict):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

class CallScope(dict):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

class Scopes:
    def __init__(self):
        self.scopes = []

    @property
    def global_scope(self):
        return self.scopes[0]

    def push(self, scope_class=None):
        if not self.scopes:
            assert scope_class is None
            scope_class = GlobalScope
        elif not scope_class:
            scope_class = dict

        self.scopes.append(scope_class())

    def pop(self):
        if not self.scopes[-1] is self.global_scope:
            self.scopes.pop()

    def _find_scope(self, key):
        for scope in reversed(self.scopes):
            if key in scope:
                return scope

            # stop chained lookup at Call
            if isinstance(scope, CallScope):
                break

        assert key in self.global_scope, 'Undefined?'
        return self.global_scope

    def define(self, key, value):
        # special setter where we define a new var in the current scope
        self.scopes[-1][key] = value

    def __setitem__(self, key, value):
        scope = self._find_scope(key)
        scope[key] = value

    def __getitem__(self, key):
        scope = self._find_scope(key)
        return scope[key]

    def __len__(self):
        return len(self.scopes)

def new_scope(scope_type=None):
    '''Call function with new scope, remove it after the function exits'''
    def decorator(func):
        def wrapper(*args, **kwargs):
            self = args[0]
            try:
                self.env.push(scope_type)
                return func(*args, **kwargs)
            finally:
                self.env.pop()
        return wrapper
    return decorator

