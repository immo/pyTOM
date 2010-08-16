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

from df_global import *

class writeable(object):
    def __init__(self):
        self.s = ""
    def write(self,data):
        self.s += data

def prnt(*args):
    """ prints with a marker before each line """
    marker = DfGlobal()("prnt.marker","")
    format = writeable()
    for arg in args:
        print >> format, arg,
    print marker + format.s.replace("\n","\n"+marker)
    
