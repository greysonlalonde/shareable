shared-state
===========================
 Dynamic python object access & manipulation across threads/processes
---
 (This package is not close to being usable)
  
Example:
```python
from shared_state import SharedState

# make a test class:
class Test:
    def __init__(self, name, age):
        self.name = name
        self.age = age
    
# in terminal 1
>>> s = Test("DB Cooper", 50)
>>> ss = SharedState(s)
>>> ss
{'name': 'DB Cooper', 'age', 50}

# in terminal 2: 
>>> from shared_state import SharedState
>>> ss = SharedState()
>>> print(ss["name"])
"DB Cooper"
>>> ss["name"] = "new name"

# back in terminal 1:
>>> print(ss["name"])
"new name"
>> ss 
{'name': 'new name', 'age', 50}
```
Gracefully handles resources on keyboard or explicit exit:
```python
>>> ss = SharedState()
>>> exit()
Destroyed shared resources
Killed all child processes
```
