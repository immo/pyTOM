
# this file contains tool code for rapid testing

import workspace
workspace = reload(workspace)
w = workspace.Workspace('/home/immanuel/Documents/drums/ext')
w.update_directory()

####


import rhythm_editor

rhythm_editor = reload(rhythm_editor)
x = rhythm_editor.RhythmEditor()

###

import editor
from lattices import *
from references import *
from Tix import *
from messagebox import *
from repgrep import *
from rhythmlet_editor import *

rhythm = ReferenceObject(Rhythmlet(1,2,3))
rhythmlet_editor = reload(rhythmlet_editor)
x = rhythmlet_editor.RhythmletEditor(rhythm)

x.add_time_grid_dialog()





###

import rhythmlet_editor as editor
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
###

import rhythmlet_editor as editor
from lattices import *
from references import *
from Tix import *
from messagebox import *
from repgrep import *
from fractions import Fraction

rhythm = ReferenceObject(Rhythmlet(Fraction(1),Fraction(2),Fraction(3)))
editor = reload(editor)
x = editor.RhythmletEditor(rhythm)
