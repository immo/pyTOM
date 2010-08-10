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
    btn.grid(row=row,column=0,sticky=E+W)

    window.grid_columnconfigure(0,weight=1)
    window.grid_rowconfigure(row,weight=1)

    window.bind("<Return>",okay_action)
    window.bind("<Escape>",okay_action)

    window.title(caption)

    window.tkraise()
    window.grab_set()
    x = window.winfo_screenwidth()/2 - window.winfo_width()/2
    y = window.winfo_screenheight()/2 - window.winfo_height()/2
    window.wm_geometry("+%i+%i"%(x,y))
    if parent:
        parent.wait_window(window)
    else:
        window.wait_window(window)
    window.grab_release()
