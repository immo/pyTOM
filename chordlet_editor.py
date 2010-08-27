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
from scrolldummy import *
import quicktix,os
import utils

class ChordletEditor(object):
    def __init__(self,parent=None):
        self.parent = parent

    def update_table(self):
        pass

    def edit_chordlet(self,input,name=None):
        self.window = Toplevel(self.parent)
        if name:
            self.window.title(name+" - Edit Chordlet")
        else:
            self.window.title("Edit Chordlet")

        self.tcontainer = Frame(self.window)
        self.tcontainer.grid(row=0,column=0,sticky=N+S+E+W)
        self.tvariable = ArrayVar(self.window)
        for i in range(25):
            self.tvariable.set("-1,%i"%i,str(i))
        self.table = Table(self.tcontainer, rows=1+len(input.frets),\
                           cols=25,titlerows=1,titlecols=0,roworigin=-1,\
                           colorigin=0,selectmode='none',\
                           rowstretch='none',colstretch='all',\
                           variable=self.tvariable,drawmode='slow',\
                           state='disabled',colwidth=2,\
                           foreground="grey",background="black")
        self.table.pack(side=LEFT,expand=1,fill='both')

        self.chordlet = input
            
        self.update_table()
        self.window.wait_window(self.window)
        return self.chordlet


if __name__ == "__main__":
    root = Tk()
    root.withdraw()
    c = Chordlet("-2 4 4")
    e = ChordletEditor(root)
    c = e.edit_chordlet(c)
    print("c=",c)
