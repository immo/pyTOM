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
from Tix import *

def messagebox(*lines):
    """ ([parent_window], ... text-lines)
    prints a message box with parent_window as parent and
    text-lines as each line of text. If multiple lines are given,
    the first line will be used as messagebox caption """
    try:
        if "tk" in lines[0].__dict__:
            parent = lines[0]
            lines = lines[1:]
        else:
            parent = None
    except:
        parent = None
    if parent:
        window = Toplevel(parent)
    else:
        window = Toplevel()
    if len(lines) < 2:
        caption = "Notice!"
    else:
        caption = str(lines[0])
        lines = lines[1:]
    if not lines:
        lines = ["Nothing to say!"]
        
    row = 0
    for l in lines:
        lbl = Label(window,text=str(l))
        lbl.grid(row=row,column=0,sticky=W)
        row += 1
        
    def okay_action(x=None,w=window):
        w.destroy()

    btn = Button(window,text="Okay",command=okay_action)
    btn.grid(row=row,column=0,sticky=E+W+S)

    window.grid_columnconfigure(0,weight=1)
    window.grid_rowconfigure(row,weight=1)

    window.bind("<Return>",okay_action)
    window.bind("<KP_Enter>",okay_action)    
    window.bind("<Escape>",okay_action)

    w = window.winfo_width()
    h = window.winfo_height()
    if w < 120:
        w = 120
    if h < 80:
        h = 80
    window.wm_geometry("%ix%i"%(w,h))

    window.title(caption)
    screencenter(window)
    modalwait(window)

def inputbox(*lines):
    """ like messagebox, but lines ending with $ will be prompted for input,
    'text =$defaultval$' will set defaultval to the entry"""
    try:
        if "tk" in lines[0].__dict__:
            parent = lines[0]
            lines = lines[1:]
        else:
            parent = None
    except:
        parent = None
    if parent:
        window = Toplevel(parent)
    else:
        window = Toplevel()
    if len(lines) < 2:
        caption = "Notice!"
    else:
        caption = str(lines[0])
        lines = lines[1:]
    if not lines:
        lines = ["Nothing to say!"]

    entries = []

    first_entry = None
        
    row = 0
    for l in lines:
        l = str(l)
        if l.endswith("$"):
            l = l[:-1]
            if '$' in l:
                idx = l.rindex('$')
                defval = l[idx+1:]
                l = l[:idx]
            else:
                defval = ""
            lbl = Label(window,text=l)
            lbl.grid(row=row,column=0,sticky=E)
            var = StringVar()
            entry = Entry(window,textvariable=var)
            entry.grid(row=row,column=1,sticky=E+W)
            var.set(defval)
            entries.append(var)
            if not first_entry:
                first_entry = entry
            
        else:
            lbl = Label(window,text=l)
            lbl.grid(row=row,column=0,columnspan=2,sticky=W)
        row += 1

    cancelled = {}
        
    def okay_action(x=None,w=window):
        w.destroy()

    def cancel_action(x=None,w=window,c=cancelled):
        c["cancel"] = True
        w.destroy()

    btnbar = Frame(window)
    btnbar.grid(row=row,column=0,columnspan=2,sticky=E+W+S)

    btn = Button(btnbar,text="Okay",command=okay_action)
    btn.pack(side=LEFT)

    btn2 = Button(btnbar,text="Cancel",command=cancel_action)
    btn2.pack(side=LEFT)

    window.grid_columnconfigure(1,weight=1)
    window.grid_rowconfigure(row,weight=1)

    window.bind("<Return>",okay_action)
    window.bind("<KP_Enter>",okay_action)    
    window.bind("<Escape>",cancel_action)

    w = window.winfo_width()
    h = window.winfo_height()
    if w < 300:
        w = 300
    if h < 100:
        h = 100
    window.wm_geometry("%ix%i"%(w,h))

    if first_entry:
        first_entry.focus_set()

    window.title(caption)
    screencenter(window)
    modalwait(window)

    if cancelled:
        return None
    else:
        return [x.get() for x in entries]


def screencenter(window):
    window.update()
    x = window.winfo_screenwidth()/2 - window.winfo_width()/2
    y = window.winfo_screenheight()/2 - window.winfo_height()/2
    window.wm_geometry("+%i+%i"%(x,y))

def modalwait(window,parent=None):
    window.update()
    window.tkraise()
    window.grab_set()
    if parent:
        parent.wait_window(window)
    else:
        window.wait_window(window)
    window.grab_release()
