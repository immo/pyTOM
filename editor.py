#!/usr/bin/env python
#
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

class SandboxInteraction(object):
    def __init__(self,root=None):
        if root:
            self.window = Toplevel(root)
        else:
            self.window = Tk()
        self.window.title("Sandbox Interaction")
        self.window.grid_columnconfigure(0,weight=1)
        self.window.grid_rowconfigure(0,weight=1)        
        self.code_window = ScrolledText(self.window)
        self.code_window.grid(row=0,column=0,sticky=N+E+S+W)
        def return_callback(event):
            current_line = event.widget.get("insert linestart","insert")
            starting_ws = ""
            in_head = True
            for i in range(len(current_line)):
                if not current_line[i].isspace():
                    in_head = False
                    break
                starting_ws += current_line[i]
            ending_ws = ""                
            if in_head:
                current_line = event.widget.get("insert","insert lineend")
                for i in range(len(current_line)):
                    if not current_line[i].isspace():
                        break
                    ending_ws += current_line[i]                
            event.widget.insert(INSERT,ending_ws+"\n"+starting_ws)
            return "break"
        def tab_callback(event):
            event.widget.insert(INSERT,"    ")
            return "break"
        def backspace_callback(event):
            big_before = event.widget.get("insert-4c","insert")
            if big_before == "    ":
                event.widget.delete("insert-4c","insert")
            else:
                event.widget.delete("insert-1c","insert")
            return "break"
        self.code_window.subwidget("text").bind("<Return>",return_callback)
        self.code_window.subwidget("text").bind("<Tab>",tab_callback)
        self.code_window.subwidget("text").bind("<BackSpace>",backspace_callback)

    def mainloop(self):
        self.window.mainloop()
        


if __name__ == "__main__":
    print("*let Editor")
    root = SandboxInteraction()
    root.mainloop()
