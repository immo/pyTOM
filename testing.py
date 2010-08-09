# this file contains tool code for rapid testing

import editor
from lattices import *
from references import *
from Tix import *

rhythm = ReferenceObject(Rhythmlet(1,2,3))
editor = reload(editor)
x = editor.RhythmletEditor(rhythm)
