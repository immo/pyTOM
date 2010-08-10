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
import math


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
                current = parent.reference.at_h(parent.reference.times[row],key)
                if current > 0:
                    current -= 1
                parent.reference.__dict__[key][row] = \
                                    parent.reference.i_priorities[key][current]
                parent.reference.____changed(key)
        def db_left_button(event,parent=self):
            row,col = parent.table.index("@%i,%i"%(event.x,event.y)).split(',')
            row = int(row)
            col = int(col)
            if (row >= 0) and (col > 0):
                key = {1:'left_hand',2:'feet',3:'right_hand'}[col]
                current = 0
                parent.reference.__dict__[key][row] = \
                                    parent.reference.i_priorities[key][current]
                parent.reference.____changed(key)                
        def right_button(event,parent=self):
            row,col = parent.table.index("@%i,%i"%(event.x,event.y)).split(',')
            row = int(row)
            col = int(col)
            if (row >= 0) and (col > 0):
                key = {1:'left_hand',2:'feet',3:'right_hand'}[col]
                current = parent.reference.at_h(parent.reference.times[row],key)
                if current < len(parent.reference.i_priorities[key])-1:
                    current += 1
                parent.reference.__dict__[key][row] = \
                                    parent.reference.i_priorities[key][current]
                parent.reference.____changed(key)
        def db_right_button(event,parent=self):
            row,col = parent.table.index("@%i,%i"%(event.x,event.y)).split(',')
            row = int(row)
            col = int(col)
            if (row >= 0) and (col > 0):
                key = {1:'left_hand',2:'feet',3:'right_hand'}[col]
                current = len(parent.reference.i_priorities[key])-1
                parent.reference.__dict__[key][row] = \
                                    parent.reference.i_priorities[key][current]
                parent.reference.____changed(key)

        self.copy_row = 0

        def copy_row_selector(event,parent=self):
            row,col = parent.table.index("@%i,%i"%(event.x,event.y)).split(',')
            row = int(row)
            if (row >= 0):
                parent.copy_row = row
        def copy_row_action(event,parent=self):
            row,col = parent.table.index("@%i,%i"%(event.x,event.y)).split(',')
            row = int(row)
            col = int(col)
            if (row >= 0) and (col > 0) \
               and (0 <= parent.copy_row <= len(parent.reference.times)):
                key = {1:'left_hand',2:'feet',3:'right_hand'}[col]
                parent.reference.__dict__[key][row] = \
                    parent.reference.__dict__[key][parent.copy_row]
                parent.reference.____changed(key)
        def copy_all_action(event,parent=self):
            row,col = parent.table.index("@%i,%i"%(event.x,event.y)).split(',')
            row = int(row)
            col = int(col)
            if (row >= 0) and (col > 0) \
               and (0 <= parent.copy_row <= len(parent.reference.times)):
                for key in ['left_hand','feet','right_hand']:
                    parent.reference.__dict__[key][row] = \
                         parent.reference.__dict__[key][parent.copy_row]
                    parent.reference.____changed(key)            
                
        self.table.bind("<Button-1>",left_button)
        self.table.bind("<Double-Button-1>",db_left_button)
        self.table.bind("<Control-Button-3>",copy_row_selector)
        self.table.bind("<Control-Double-Button-3>",copy_row_selector)        
        self.table.bind("<Control-Button-1>",copy_row_action)
        self.table.bind("<Control-Double-Button-1>",copy_all_action)
        self.table.bind("<Control-space>",copy_all_action)
        self.table.bind("<space>",copy_row_action)                        
        self.table.bind("<Button-4>",left_button)        
        self.table.bind("<Button-3>",right_button)
        self.table.bind("<Double-Button-3>",db_right_button)        
        self.table.bind("<Button-5>",right_button)

        priority_list = "1234567890poiuztrewqasdfghjklmnbvcx"
        for key,nbr in zip(priority_list,range(len(priority_list)))\
                       + [("y",priority_list.index("z"))]:
            def set_instrument_by_key(event,parent=self,n=nbr):
                row,col = parent.table.index("@%i,%i"%(event.x,event.y)).split(',')
                row = int(row)
                col = int(col)
                if (row >= 0) and (col > 0):
                    key = {1:'left_hand',2:'feet',3:'right_hand'}[col]
                    if n < len(parent.reference.i_priorities[key]):
                        choosen = parent.reference.i_priorities[key][n]
                    else:
                        choosen = None
                    parent.reference.__dict__[key][row] = choosen
                    parent.reference.____changed(key)
            self.table.bind(key,set_instrument_by_key)
        
        
        self.balloon = Balloon(self.window)        
        self.buttons = Frame(self.window)
        self.buttons.grid(row=1,column=0,sticky=E)
        def add_command(x=None,s=self):
            s.add_time_grid_dialog()
        def del_command(x=None,s=self):
            s.delete_selected_row()
        def clear_command(x=None,s=self):
            s.clear_empty_rows()
        def command_1(x=None,s=self):
            s.add_fraction_time_grid(Fraction(1,1))
        def command_2(x=None,s=self):
            s.add_fraction_time_grid(Fraction(1,2))
        def command_4(x=None,s=self):
            s.add_fraction_time_grid(Fraction(1,4))
        def command_2_3(x=None,s=self):
            s.add_fraction_time_grid(Fraction(2,3))
        def command_3(x=None,s=self):
            s.add_fraction_time_grid(Fraction(1,3))
        def command_6(x=None,s=self):
            s.add_fraction_time_grid(Fraction(1,6))
        self.btn_1 = Button(self.buttons,text="1/4",command=command_1)
        self.btn_1.pack(side=LEFT)
        self.balloon.bind_widget(self.btn_1,balloonmsg="Add regular time grid.")
        self.btn_2 = Button(self.buttons,text="1/8",command=command_2)
        self.btn_2.pack(side=LEFT)
        self.balloon.bind_widget(self.btn_2,balloonmsg="Add regular time grid.")
        self.btn_4 = Button(self.buttons,text="1/16",command=command_4)
        self.btn_4.pack(side=LEFT)
        self.balloon.bind_widget(self.btn_4,balloonmsg="Add regular time grid.")
        self.btn_2_3 = Button(self.buttons,text="1/4 3let",command=command_2_3)
        self.btn_2_3.pack(side=LEFT)
        self.balloon.bind_widget(self.btn_2_3,balloonmsg="Add regular time grid.")
        self.btn_3 = Button(self.buttons,text="1/8 3let",command=command_3)
        self.btn_3.pack(side=LEFT)
        self.balloon.bind_widget(self.btn_3,balloonmsg="Add regular time grid.")
        self.btn_6 = Button(self.buttons,text="1/16 3let",command=command_6)
        self.btn_6.pack(side=LEFT)
        self.balloon.bind_widget(self.btn_6,balloonmsg="Add regular time grid.")
        
        self.add_btn = Button(self.buttons,text="Add time grid",command=add_command)
        self.add_btn.pack(side=LEFT)
        self.balloon.bind_widget(self.add_btn,\
                                 balloonmsg="Add evenly spaced time sampling points"\
                                            " to the rhythmlet. t_i = t_0 + i·d")
        self.del_btn = Button(self.buttons,text="Delete row",command=del_command)
        self.del_btn.pack(side=LEFT)
        self.balloon.bind_widget(self.del_btn,\
                                 balloonmsg="Delete the selected row's time"\
                                    " sampling point and hit data. (Delete)")
        self.clr_btn = Button(self.buttons,text="De-Sparse",command=clear_command)
        self.clr_btn.pack(side=LEFT)
        self.balloon.bind_widget(self.clr_btn,\
                                    balloonmsg="Delete all rows that have no hits.")
        self.window.bind("<Delete>",del_command)
        self.table.focus_set()
        screencenter(self.window)

    def add_fraction_time_grid(self,d):
        if self.reference.times:
            t1 = (max(self.reference.times) // 1) + 1
            if t1 < 4:
                t1 = 4
        else:
            t1 = 4
        t0 = 0
        i = int(math.floor(float(t1-t0)/float(d)))
        time_grid = [t0 + k*d for k in range(i)]
        self.reference.add_to_time_grid(*time_grid)
        self.reference.sort()
        self.reference.____changed('times')


    def add_time_grid_dialog(self):
        dialog = Toplevel(self.window)
        dialog.title("Time Grid Parameters")
        dialog_vars = {'cancel':False,'t0':StringVar(),'t1':StringVar(),\
                       'd':StringVar(),'i':StringVar()}
        dialog.grid_columnconfigure(1,weight=1)
        infolabel = Label(dialog,text="t_0 ≤ t_0 + i·d < t_1")
        infolabel.grid(row=0,column=0,columnspan=2)
        labelt0 = Label(dialog,text="t_0 =")
        labelt0.grid(row=1,column=0,sticky=E)
        t0 = Entry(dialog,textvariable=dialog_vars['t0'])
        t0.grid(row=1,column=1,sticky=E+W)
        labelt1 = Label(dialog,text="t_1 =")
        labelt1.grid(row=2,column=0,sticky=E)
        t1 = Entry(dialog,textvariable=dialog_vars['t1'])
        t1.grid(row=2,column=1,sticky=E+W)
        labeld = Label(dialog,text="¼d =")
        labeld.grid(row=3,column=0,sticky=E)
        d = Entry(dialog,textvariable=dialog_vars['d'])
        d.grid(row=3,column=1,sticky=E+W)
        labeli = Label(dialog,text="i_max + 1 =")
        labeli.grid(row=4,column=0,sticky=E)
        i = Entry(dialog,textvariable=dialog_vars['i'])
        i.grid(row=4,column=1,sticky=E+W)

        dialog_vars['d'].set('1/4')
        dialog_vars['t0'].set('0')
        dialog_vars['t1'].set('4')
        
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

        t0.focus_set()

        screencenter(dialog)
        modalwait(dialog)

        if not dialog_vars.pop('cancel'):
            for dlg_key in dialog_vars:
                dialog_vars[dlg_key] = dialog_vars[dlg_key].get().strip()
            try:
                t0 = dialog_vars['t0']
                if t0:
                    t0 = Fraction(t0)
                else:
                    t0 = 0
                t1 = dialog_vars['t1']
                if t1:
                    t1 = Fraction(t1)
                else:
                    t1 = 4
                d = Fraction(dialog_vars['d'])*4
                
                i = dialog_vars['i']
                if t1:
                    i = int(math.floor(float(t1-t0)/float(d)))
                else:
                    if i:
                        i = int(i)
                    else:
                        i = 1
                time_grid = [t0 + k*d for k in range(i)]
                self.reference.add_to_time_grid(*time_grid)
                self.reference.sort()
                self.reference.____changed('times')
            except Exception, err:
                messagebox(self.window, "Time Grid: Error", err)
                
    def delete_selected_row(self):
        try:
            selected = self.table.index('active')
        except:
            return
        row = int(selected.split(',')[0])
        if 0 <= row < len(self.reference.times):
            self.reference.del_times(self.reference.times[row])
            self.reference.____changed('times')

    def clear_empty_rows(self):
        self.reference.compactify_times()
        self.reference.____changed('times')        

    def fill_tvariable(self):
        def str2(x):
            if x:
                return str(x)
            return ""
        for x in range(len(self.reference.times)):
            time = self.reference.times[x]
            if not (time % 1 == 0):
                timecode = str((time // 1) + 1) + "  " + str((time % 1)/4)
            else:
                timecode = str(time+1) + " beat"
            self.tvariable.set("%i,0"%x,timecode)
            self.tvariable.set("%i,1"%x,str2(self.reference.left_hand[x]))
            self.tvariable.set("%i,2"%x,str2(self.reference.feet[x]))
            self.tvariable.set("%i,3"%x,str2(self.reference.right_hand[x]))
        if 'table' in self.__dict__:
            self.table.config(rows=len(self.reference.times)+1)

    def update(self,key,value):
        self.fill_tvariable()

    def destroy(self):
        self.window.destroy()
        self.reference.____unwatch(self)
        self.__delattr__('reference')
