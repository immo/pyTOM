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

class ScrollDummy(object):
    def __init__(self,table):
        self.table = table

    def yview(self,*args):
        if args[0] == 'scroll':
            self.table.yview_scroll(*args[1:])
        if args[0] == 'moveto':
            self.table.yview_moveto(*args[1:])

class RhythmletEditor(object):
    def __init__(self, reference, pwindow=None):
        """ Create an RhythmletEditor associated with the reference object """
        reference.sort()
        self.reference = reference
        reference.____watch(self)
        self.window = Toplevel(pwindow)
        self.window.title('Rhythmlet Editor')
        self.window.protocol('WM_DELETE_WINDOW', lambda : self.destroy())
        self.window.grid_columnconfigure(0,weight=1)
        self.window.grid_rowconfigure(0,weight=1)
        self.tcontainer = Frame(self.window)
        self.tcontainer.grid(sticky=N+S+E+W)
        self.tvariable = ArrayVar(self.window)
        for y,header in [(0,'time'),(1,'left hand'),\
                         (3,'right hand'),(2,'feet')]:
            self.tvariable.set("-1,%i"%(y),header)
        self.fill_tvariable()
        self.table = Table(self.tcontainer, rows=len(reference.times)+1,\
                           cols=4,titlerows=1,titlecols=0,roworigin=-1,\
                           colorigin=0,selectmode='browse',\
                           rowstretch='none',colstretch='all',\
                           variable=self.tvariable,drawmode='slow',\
                           state='disabled')
        self.table.pack(side=LEFT,expand=1,fill='both')
        self.scrollbar = Scrollbar(self.tcontainer)
        self.scrollbar.pack(side=RIGHT,fill=Y,expand=1)
        self.scroll_callback = ScrollDummy(self.table)
        self.scrollbar.config(command=self.scroll_callback.yview)
        self.table.config(yscrollcommand=self.scrollbar.set)
        def left_button(event,parent=self):
            row,col = parent.table.index("@%i,%i"%(event.x,event.y)).split(',')
            row = int(row)
            col = int(col)
            if (row >= 0):
                if col == 1:
                    parent.reference.left_hand
        self.table.bind("<Button-1>",left_button)

    def fill_tvariable(self):
        def str2(x):
            if x:
                return str(x)
            return ""
        for x in range(len(self.reference.times)):
            self.tvariable.set("%i,0"%x,self.reference.times[x])
            self.tvariable.set("%i,1"%x,str2(self.reference.left_hand[x]))
            self.tvariable.set("%i,2"%x,str2(self.reference.feet[x]))
            self.tvariable.set("%i,3"%x,str2(self.reference.right_hand[x]))

    def update(self,key,value):
        self.fill_tvariable()

    def destroy(self):
        self.window.destroy()
        self.reference.____unwatch(self)
        self.__delattr__('reference')

if __name__ == "__main__":
    print("*let Editor")
    root = SandboxInteraction()
    root.mainloop()
