# RWJigsaw
A python module for generating random walk puzzle for laser cutting

Usage example:

```
from RWJigsaw imort Jigsaw
j = Jigsaw(res=30, bordertype='circ')
j.initiate_pieces(10)
j.steps()
j.show()
j.complete()
j.export(filename='test.svg')
```
