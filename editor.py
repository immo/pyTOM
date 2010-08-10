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
                           state='disabled',colwidth=20)
        self.table.pack(side=LEFT,expand=1,fill='both')
        self.scrollbar = Scrollbar(self.tcontainer)
        self.scrollbar.pack(side=RIGHT,fill=Y)
        self.scroll_callback = ScrollDummy(self.table)
        self.scrollbar.config(command=self.scroll_callback.yview)
        self.table.config(yscrollcommand=self.scrollbar.set)
        def left_button(event,parent=self):
            row,col = parent.table.index("@%i,%i"%(event.x,event.y)).split(',')
            row = int(row)
            col = int(col)
            if (row >= 0) and (col > 0):
                key = {1:'left_hand',2:'feet',3:'right_hand'}[col]
                current = self.reference.at_h(self.reference.times[row],key)
                if current > 0:
                    current -= 1
                self.reference.__dict__[key][row] = \
                                    self.reference.i_priorities[key][current]
                self.reference.____changed(key)
        def db_left_button(event,parent=self):
            row,col = parent.table.index("@%i,%i"%(event.x,event.y)).split(',')
            row = int(row)
            col = int(col)
            if (row >= 0) and (col > 0):
                key = {1:'left_hand',2:'feet',3:'right_hand'}[col]
                current = 0
                self.reference.__dict__[key][row] = \
                                    self.reference.i_priorities[key][current]
                self.reference.____changed(key)                
        def right_button(event,parent=self):
            row,col = parent.table.index("@%i,%i"%(event.x,event.y)).split(',')
            row = int(row)
            col = int(col)
            if (row >= 0) and (col > 0):
                key = {1:'left_hand',2:'feet',3:'right_hand'}[col]
                current = self.reference.at_h(self.reference.times[row],key)
                if current < len(self.reference.i_priorities[key])-1:
                    current += 1
                self.reference.__dict__[key][row] = \
                                    self.reference.i_priorities[key][current]
                self.reference.____changed(key)
        def db_right_button(event,parent=self):
            row,col = parent.table.index("@%i,%i"%(event.x,event.y)).split(',')
            row = int(row)
            col = int(col)
            if (row >= 0) and (col > 0):
                key = {1:'left_hand',2:'feet',3:'right_hand'}[col]
                current = len(self.reference.i_priorities[key])-1
                self.reference.__dict__[key][row] = \
                                    self.reference.i_priorities[key][current]
                self.reference.____changed(key)
                
        self.table.bind("<Button-1>",left_button)
        self.table.bind("<Double-Button-1>",db_left_button)        
        self.table.bind("<Button-4>",left_button)        
        self.table.bind("<Button-3>",right_button)
        self.table.bind("<Double-Button-3>",db_right_button)        
        self.table.bind("<Button-5>",right_button)
        self.balloon = Balloon(self.window)        
        self.buttons = Frame(self.window)
        self.buttons.grid(row=1,column=0,sticky=E)
        self.add_btn = Button(self.buttons,text="Add time grid")
        self.add_btn.pack(side=LEFT)
        self.balloon.bind_widget(self.add_btn,\
                                 balloonmsg="Add evenly spaced time sampling points"\
                                            " to the rhythmlet. t_i = t_0 + i·d")
        self.del_btn = Button(self.buttons,text="Delete row")
        self.del_btn.pack(side=LEFT)
        self.balloon.bind_widget(self.del_btn,\
                                 balloonmsg="Delete the selected row's time"\
                                    " sampling point and hit data. (Delete)")

    def add_time_grid_dialog(self):
        dialog = Toplevel(self.window)
        dialog.title("Time Grid Parameters")
        dialog_vars = {'cancel':False,'t0':StringVar(),'t1':StringVar(),\
                       'd':StringVar(),'i':StringVar()}
        dialog.grid_columnconfigure(1,weight=1)
        infolabel = Label(dialog,text="t_0 ≤ t_0 + i·d ≤ t_1")
        infolabel.grid(row=0,column=0,columnspan=2)
        labelt0 = Label(dialog,text="t_0 =")
        labelt0.grid(row=1,column=0,sticky=E)
        t0 = Entry(dialog,textvariable=dialog_vars['t0'])
        t0.grid(row=1,column=1,sticky=E+W)
        labelt1 = Label(dialog,text="t_1 =")
        labelt1.grid(row=2,column=0,sticky=E)
        t1 = Entry(dialog,textvariable=dialog_vars['t1'])
        t1.grid(row=2,column=1,sticky=E+W)
        labeld = Label(dialog,text="d =")
        labeld.grid(row=3,column=0,sticky=E)
        d = Entry(dialog,textvariable=dialog_vars['d'])
        d.grid(row=3,column=1,sticky=E+W)
        labeli = Label(dialog,text="i =")
        labeli.grid(row=4,column=0,sticky=E)
        i = Entry(dialog,textvariable=dialog_vars['i'])
        i.grid(row=4,column=1,sticky=E+W)
        
        def cancel_action(x=None,v=dialog_vars,d=dialog):
            v['cancel'] = True
            d.destroy()
        def okay_action(x=None,d=dialog):
            d.destroy()

        btnframe = Frame(dialog)
        btnframe.grid(row=5,column=0,columnspan=2,sticky=E)

        cancel = Button(btnframe,text="Cancel",command=cancel_action)
        cancel.pack(side=LEFT)

        okay = Button(btnframe,text="OK",command=okay_action)
        okay.pack(side=LEFT)
        dialog.bind("<Return>",okay_action)
        dialog.bind("<Escape>",cancel_action)
        
        self.window.wait_window(dialog)

        if not dialog_vars.pop('cancel'):
            print("t0=",t0)
            for dlg_key in dialog_vars:
                print("var=",dialog_vars[dlg_key].get())
                locals()[dlg_key] = dialog_vars[dlg_key].get()
                print("dlg_key=",locals()[dlg_key])
            print("t0=",t0)

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
