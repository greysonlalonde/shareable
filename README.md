shared-state
===========================
 Dynamic python object access & manipulation across threads/processes
---
 (This package is not close to being usable)
  
Example:
```python
from shared_state import SharedState

class Test:
    """test class"""
    def __init__(self, name):
        self.name = name
    
# in terminal 1
>>> s = Test("DB Cooper")
>>> ss = SharedState(s)
>>> print(ss["name"])
"DB Cooper"

# in terminal 2: 
>>> from shared_state import SharedState
>>> ss = SharedState()
>>> print(ss["name"])
"DB Cooper"
>>> ss["name"] = "new name"

# back in terminal 1:
>>> print(ss["name"])
"new name"
```
Gracefully handles keyboard or explicit exit:
```python
>>> s = SharedState()
>>> exit()
Destroyed shared resources
Killed all child processes
```
