# coding: utf-8
#
#   drums-backend   a simple interactive audio sampler that plays vorbis samples
#   Copyright (C) 2009   C.D. Immanuel Albrecht
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
#  Here, we use Tkinter and Pmw (Python Mega Widgets) 1.3,
#  and tkinter-tree (see Tree.py for license & copyright information)
#

from Tix import *
from df_global import *


def wait_window(window):
    state = {}
    g = DfGlobal()
    def chg_state(event=None,state=state):
        state['done'] = True
    window.bind("<Destroy>",chg_state)
    g("wait.for.input",lambda: 0.0)
    while not state:
        window.update()
        g["wait.for.input"]()
