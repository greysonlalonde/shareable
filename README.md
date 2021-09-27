shareable
===========================
 Dynamic python object access & manipulation across threads/processes
---
 (This package is not close to being usable, though the examples below will work)
  
Example:

```python
from shareable import Shareable


# make a test class:
class Test:
    def __init__(self, name, age):
        self.name = name
        self.age = age

# in terminal 1
>>> from shareable import Shareable
>>> test = Test('DB Cooper', 50)
>>> s = Shareable(t)
>>> s
{'name': 'DB Cooper', 'age', 50}

# in terminal 2: 
>>> from shareable import Shareable
>>> s = Shareable()
'Connection established'
>>> s['name']
'DB Cooper'
>> > s['name'] = 'new name'

# back in terminal 1:
'Connection established'
>>> s['name']
'new name'
>>> s
{'name': 'new name', 'age', 50}
```

Support for complex objects:
```python
>>> import pandas as pd
>>> import numpy as np
>>> df = pd.DataFrame(np.random.randint(0,100,size=(100, 4)), columns=list('ABCD'))
>>> s = Sharedable(df)
>>> s['info']()
<class 'pandas.core.frame.DataFrame'>
RangeIndex: 100 entries, 0 to 99
Data columns (total 4 columns):
 #   Column  Non-Null Count  Dtype
---  ------  --------------  -----
 0   A       100 non-null    int64
 1   B       100 non-null    int64
 2   C       100 non-null    int64
 3   D       100 non-null    int64
dtypes: int64(4)
memory usage: 3.2 KB

# terminal 2:
>>> s = Shareable()
'Connection established'
>>> s['columns']
Index(['A', 'B', 'C', 'D'], dtype='object')
```

Gracefully handles resources on keyboard or explicit exit:
```python
>>> s = Shareable()
>>> exit()
'Destroyed shared resources'
'Killed all child processes'
```
