#!/usr/bin/env python
# coding: utf-8
#
#   Copyright (C) 2010   C.D. Immanuel Albrecht
#                                              
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or   
#   (at your option) any later version.                                 
#                                                                       
#   This program is distributed in the hope that it will be useful,     
#   but WITHOUT ANY WARRANTY; without even the implied warranty of      
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the       
#   GNU General Public License for more details.                        
#                                                                       
#   You should have received a copy of the GNU General Public License   
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

from __future__ import print_function
from sandbox import *
from lattices import *
from references import *
from Tix import *
from tktable import *
from fractions import *
from repgrep import *
from messagebox import *
import workspace
import song_editor
import math
import chordlet_editor

if __name__ == "__main__":
    root = Tk()
    root.withdraw()
    print("Fret Editor")
    c = Chordlet("")
    e = chordlet_editor.ChordletEditor(root)
    e.edit_chordlet(c)
else:
    root = None

