# this file contains tool code for rapid testing


import editor
from lattices import *
from references import *
from Tix import *
from messagebox import *
from repgrep import *

rhythm = ReferenceObject(Rhythmlet(1,2,3))
editor = reload(editor)
x = editor.RhythmletEditor(rhythm)

x.add_time_grid_dialog()





###

import editor
from lattices import *
from references import *
from Tix import *
from messagebox import *
from repgrep import *
from fractions import Fraction

rhythm = ReferenceObject(Rhythmlet(Fraction(1),Fraction(2),Fraction(3)))
editor = reload(editor)
x = editor.RhythmletEditor(rhythm)

x.add_time_grid_dialog()
