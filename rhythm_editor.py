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
from lattices import *
from references import *
from Tix import *
from tktable import *
from fractions import *
from messagebox import *
from rhythmlet_editor import *
from scrolldummy import *

class RhythmEditor(object):
    def __init__(self,parent=None):
        self.window = Toplevel(parent)
        self.rhythmletstack = []
        self.window.grid_columnconfigure(0,weight=1)
        self.window.grid_rowconfigure(0,weight=1)        
        self.tcontainer = Frame(self.window)
        self.tcontainer.grid(sticky=N+S+E+W)
        self.tvariable = ArrayVar(self.window)
        self.tvariable.set("-1,0","Rhythmlets")
        self.table = Table(self.tcontainer, rows=1,\
                           cols=1,titlerows=1,titlecols=0,roworigin=-1,\
                           colorigin=0,selectmode='browse',\
                           rowstretch='none',colstretch='all',\
                           variable=self.tvariable,drawmode='slow',\
                           state='disabled',colwidth=20)
        self.table.pack(side=LEFT,expand=1,fill='both')
        self.scrollbar = Scrollbar(self.tcontainer)
        self.scrollbar.pack(side=LEFT,fill=Y)
        self.scroll_callback = ScrollDummy(self.table)
        self.scrollbar.config(command=self.scroll_callback.yview)
        self.table.config(yscrollcommand=self.scrollbar.set)
        
        def edit_rhythmlet(event,s=self):
            row,col = s.table.index("@%i,%i"%(event.x,event.y)).split(',')
            row = int(row)
            if row >= 0:
                RhythmletEditor(self.rhythmletstack[row][1],s.window)

        self.table.bind("<Double-Button-1>",edit_rhythmlet)
        self.fill_table()
        screencenter(self.window)
        
        
    def fill_table(self):
        for i in range(len(self.rhythmletstack)):
            self.tvariable.set("%i,0"%i,self.rhythmletstack[i][0])
        self.table.config(rows=len(self.rhythmletstack)+1)

    def add_rhythmlet_var(self,name,rhythmlet):
        self.rhythmletstack.append((name,ReferenceObject(rhythmlet),))
        self.fill_table()

    def to_string(self):
        data = []
        for name,ref in self.rhythmletstack:
            data.append("Named Rhythmlet")
            data.append(repr(name))
            data.append(repr(ref.times))
            data.append(repr(ref.i_priorities.keys()))
            for k in ref.i_priorities.keys():
                data.append(repr(ref.__dict__[k]))
        return "\n".join(data)
