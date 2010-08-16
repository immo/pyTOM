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
from df_xml_thing import *
from df_ui_waitwindow import *
import tkMessageBox, math



def property_dialog(vars,types=None,values=None,width=420,parent=None,\
                    title="Properties..."):
    """Create a dialog with the contents of vars, which is a sequence of
    pairs (Name,key[,opt[,fn]]) where name is the name of the field to be
    displayed.
    Types is a map that maps a key to a conversion function (e.g. float),
    and values is a map that maps each key to its values. (This will be changed
    on user input and returned afterwards)
    opt is an option string that can be set to 'dbScale' or 'Entry'.
    If opt is set to 'dbScale', fn can be a function that will be called
    every time the slider is moved.

    Options:
      (Name, key)                          ... Standard Entry
      (Name, key, 'Entry')                 ... Standard Entry
      (Name, key, 'dbScale')               ... Dezibel Scale slider
      (Name, key, 'dbScale', fn)           ... dbScale slider w/ fn called
                                               on update
      (Name, key, 'DropDown', list)            ... drop down list Entry
    """
    if values == None:
        values = {}
    if types == None:
        types = {}
    window = Toplevel(parent,width=width)
    window.title(title)
    scrolled_window = ScrolledWindow(window,scrollbar=Y)
    scrolled_window.pack(expand=1,fill=BOTH)
    frame = scrolled_window.window

    retrieve_variables = lambda: 0

    def end_window(evt=None,window=window):
        window.destroy()

    window.bind("<Escape>",end_window)
    window.bind("<Return>",end_window)
    window.bind("<KP_Enter>",end_window)    

    first_entry = None

    for v in vars:
        (Name, key) = (v[0],v[1])
        if len(v) >= 3:
            option = v[2]
        else:
            option = "Entry"
        if len(v) >= 4:
            updatefn = v[3]
        else:
            updatefn = None

        if option == "DropDown":
            print "DropDown-list:", updatefn
            if updatefn:
                droplist = updatefn
            else:
                option = "Entry"
            
        subframe = Frame(frame,width=width)
        subframe.pack(fill=X,expand=1)
        Label(subframe,text=Name,width=20,justify=RIGHT,anchor=NE)\
             .pack(side=LEFT,expand=0)                    
        if option == "Entry":
            var = StringVar()
            if key in values:
                var.set(str(values[key]))
            def retrieve_var(key=key,var=var,other=retrieve_variables):
                x = var.get()
                if key in types:
                    try:
                        values[key] = types[key](x)
                    except:
                        pass
                else:
                    values[key] = str(x)
                other()
            retrieve_variables = retrieve_var
            entry = Entry(subframe,textvariable=var)
            if not first_entry:
                first_entry = entry
                first_entry.selection_range(0,END)
            entry.pack(side=RIGHT,fill=X,expand=1)
            entry.bind("<Return>",end_window)
            entry.bind("<Escape>",end_window)
            entry.bind("<KP_Enter>",end_window)
        elif option == "dbScale":
            var = StringVar()
            if updatefn:
                update_dB = lambda x,fn=updatefn: fn(math.pow(10.0,\
                                                              float(x)/10.0))
            else:
                update_dB = None
            scale = Scale(subframe,from_=-45.0,to_=25.0,resolution=0.01,\
                          orient=HORIZONTAL,variable=var,tickinterval=15.0,\
                          command=update_dB)
            if key in values:
                dezibel = math.log10(values[key])*10.0
                scale.set(dezibel)
            def retrieve_var(key=key,var=var,other=retrieve_variables):
                x = math.pow(10.0,float(var.get())/10.0)
                if key in types:
                    try:
                        values[key] = types[key](x)
                    except:
                        pass
                else:
                    values[key] = x
                other()
            retrieve_variables = retrieve_var
            scale.pack(side=RIGHT,expand=1,fill=X)
            scale.bind("<Return>",end_window)
            scale.bind("<Escape>",end_window)
            scale.bind("<KP_Enter>",end_window)
            def set_to_zero(event,scale=scale):
                scale.set(0)
            scale.bind("<Button-3>",set_to_zero)
        elif option == "DropDown":
            var = StringVar()
            if key in values:
                var.set(str(values[key]))
            def retrieve_var(key=key,var=var,other=retrieve_variables):
                x = var.get()
                if key in types:
                    try:
                        values[key] = types[key](x)
                    except:
                        pass
                else:
                    values[key] = str(x)
                other()
            retrieve_variables = retrieve_var
            entry = ComboBox(subframe,dropdown=1,editable=1,variable=var)
            for optn in droplist:
                entry.insert(END,str(optn))
            if not first_entry:
                first_entry = entry
                first_entry.selection_range(0,END)
            entry.pack(side=RIGHT,fill=X,expand=1)
            entry.bind("<Return>",end_window)
            entry.bind("<Escape>",end_window)
            entry.bind("<KP_Enter>",end_window)
            
            


    (mousex,mousey) = window.winfo_pointerxy()

    window.update()

    height = window.winfo_height()
    if height > 600:
        height = 600
    
    geometry = str(width)+"x"+str(height)\
               +"+" + str(mousex-30)+"+"+str(mousey-30)
    window.wm_geometry(geometry)

    if first_entry:
        first_entry.focus_set()
    
    wait_window(window)
    retrieve_variables()
    return values

