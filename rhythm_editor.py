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
import quicktix
import utils

class RhythmEditor(object):
    def __init__(self,parent=None):
        self.window = Toplevel(parent)
        self.window.title("Rhythm Editor Desk")
        self.rhythmletstack = []
        self.window.grid_columnconfigure(0,weight=0)
        self.window.grid_columnconfigure(1,weight=1)        
        self.window.grid_rowconfigure(0,weight=1)        
        self.tcontainer = Frame(self.window)
        self.tcontainer.grid(row=0,column=0,sticky=N+S+E+W)
        self.tvariable = ArrayVar(self.window)
        self.tvariable.set("-1,0","Rhythmlets")
        self.table = Table(self.tcontainer, rows=1,\
                           cols=1,titlerows=1,titlecols=0,roworigin=-1,\
                           colorigin=0,selectmode='browse',\
                           rowstretch='none',colstretch='all',\
                           variable=self.tvariable,drawmode='slow',\
                           state='disabled',colwidth=30)
        self.table.pack(side=LEFT,expand=1,fill='both')
        self.scrollbar = Scrollbar(self.tcontainer)
        self.scrollbar.pack(side=LEFT,fill=Y)
        self.scroll_callback = ScrollDummy(self.table)
        self.scrollbar.config(command=self.scroll_callback.yview)
        self.table.config(yscrollcommand=self.scrollbar.set)
        self.balloon = Balloon(self.window)
        self.r_buttons = Frame(self.window)
        self.r_buttons.grid(row=1,column=0,sticky=W)
        self.next_name = "A"
        self.second_op = -1

        def choose_second_op(event,s=self):
            row,col = s.table.index("@%i,%i"%(event.x,event.y)).split(",")
            row = int(row)
            s.second_op = row
            s.hilight_second_op()

        def new_rhythmlet(x=None,s=self):
            row = s.add_rhythmlet_var(s.get_next_name(),Rhythmlet())
            s.rename_rhythmlet_var(row)

        def rename_rhythmlet(x=None,s=self):
            row,col = s.table.index("active").split(",")
            row = int(row)
            s.rename_rhythmlet_var(row)

        def mouse_rename_rhythmlet(event,s=self):
            row,col = s.table.index("@%i,%i"%(event.x,event.y)).split(",")
            row = int(row)
            s.rename_rhythmlet_var(row)
            
        def del_rhythmlet(x=None,s=self):
            row,col = s.table.index("active").split(",")
            row = int(row)
            s.del_rhythmlet_var(row)
                    
        quicktix.add_balloon_button(self.__dict__,'new_btn','r_buttons','New',\
                                    new_rhythmlet,'Create a new rhythmlet.')
        quicktix.add_balloon_button(self.__dict__,'ren_btn','r_buttons','Rename',\
                                    rename_rhythmlet,\
                                    'Rename the currently selected rhythmlet.')
        quicktix.add_balloon_button(self.__dict__,'del_btn','r_buttons','Delete',\
                                    del_rhythmlet,\
                                    'Deletes the currently selected rhythmlet. (Del)')
        
        
        def edit_rhythmlet(event,s=self):
            row,col = s.table.index("@%i,%i"%(event.x,event.y)).split(',')
            row = int(row)
            if row >= 0:
                RhythmletEditor(self.rhythmletstack[row][1],s.window)

        self.table.bind("<Double-Button-1>",edit_rhythmlet)
        self.table.bind("<Delete>",del_rhythmlet)        
        self.table.bind("<Shift-Double-Button-1>",mouse_rename_rhythmlet)
        self.table.bind("<Button-3>",choose_second_op)        
        self.fill_table()

        self.canvas = Canvas(self.window,width=300,height=300)
        self.canvas.grid(row=0,column=1,sticky=N+E+S+W)
        
        quicktix.min_win_size(self.window,600,400)
        quicktix.screencenter(self.window)

    def get_next_name(self):
        x = self.next_name
        y = x[:-1]
        c = x[-1]
        if c == "Z":
            y += "*"
            c = "A"
        else:
            c = chr(ord(c)+1)
        self.next_name = y+c
        return x
        
    def fill_table(self):
        for i in range(len(self.rhythmletstack)):
            self.tvariable.set("%i,0"%i,self.rhythmletstack[i][0])
        self.table.config(rows=len(self.rhythmletstack)+1)

    def hilight_second_op(self):
        self.table.tag_delete("hilit")
        self.table.tag_configure("hilit",background="yellow")
        self.table.tag_cell("hilit","%i,0"%self.second_op)

    def add_rhythmlet_var(self,name,rhythmlet):
        index = len(self.rhythmletstack)
        self.rhythmletstack.append((name,ReferenceObject(rhythmlet),))
        self.fill_table()
        return index

    def del_rhythmlet_var(self,index):
        if not 0 <= index < len(self.rhythmletstack):
            return
        if self.second_op > index:
            self.second_op -= 1
        new_stack = self.rhythmletstack[:index] + self.rhythmletstack[index+1:]
        self.rhythmletstack = new_stack
        self.fill_table()
        self.hilight_second_op()        
        

    def rename_rhythmlet_var(self,index):
        if 0 <= index < len(self.rhythmletstack):
            current = self.rhythmletstack[index][0]
            answer = inputbox(self.window,"Rename Rythmlet",\
                              "Rename '"+current+"'",\
                              "to: $"+current+"$")
            if answer:
                self.rhythmletstack[index] = (answer[0],self.rhythmletstack[index][1])
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
