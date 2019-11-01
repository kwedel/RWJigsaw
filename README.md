# RWJigsaw
A python module for generating random walk puzzle for laser cutting
The exported svg needs a bit of cleanup

Usage example:

```python
from RWJigsaw imort Jigsaw
j = Jigsaw(res=30, bordertype='circ') # Initate jigsaw
j.initiate_pieces(10) # Create 10 pieces
j.steps(grow_prop=0.2) # Grow until convergence
j.show() # Show puzzle with matplotlib
j.count() # Show sizes of pieces
j.complete() # Fill remaining parts close to the border
j.export(filename='test.svg') # Export
```

Output example:

![alt text](https://github.com/kwedel/RWJigsaw/blob/master/example.svg)

Clean up and cut!
White parts are supposed to stick to the frame when cutting.
Beware that where four pieces meet a very small diamond shaped piece is formed. These are easily found be hiding the colored dots in your favorite svg editor (Inkscape).