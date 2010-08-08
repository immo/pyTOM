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
from Tix import *
import code
import sys

class dummySelf(object):
    def __init__(self):
        pass

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
        def apply_entry(event=None,parent=self):
            parent.do_entry()
        def apply_line(event=None,parent=self):
            parent.do_line()
        def apply_par(event=None,parent=self):
            parent.do_paragraph()
        def apply_all(event=None,parent=self):
            parent.reset_interpreter()
            parent.do_code()            
        self.run_frame = Frame(self.window)
        self.run_frame.grid(row=1,column=0,sticky=E+W)
        self.run_entry = Entry(self.run_frame)
        self.run_entry.pack(side=LEFT,expand=1,fill=X)
        self.run_entry.bind("<Return>",apply_entry)
        self.run_line = Button(self.run_frame,text="←",command=apply_entry)
        self.run_line.pack(side=LEFT)
        self.run_code_line = Button(self.run_frame,text="↑",command=apply_line)
        self.run_code_line.pack(side=LEFT)
        self.run_selection = Button(self.run_frame,text="↑¶",command=apply_par)
        self.run_selection.pack(side=LEFT)        
        self.rerun_all = Button(self.run_frame,text="↺",command=apply_all)
        self.rerun_all.pack(side=LEFT)
        self.balloon = Balloon(self.window)
        self.balloon.bind_widget(self.run_line, balloonmsg="Run the line to the left"\
                                 " and append it to the code buffer above")
        self.balloon.bind_widget(self.run_code_line, balloonmsg="Run the current line"\
                                 " from the code buffer above (Ctrl+R)")
        self.window.bind("<Control-r>",apply_line)
        self.balloon.bind_widget(self.run_selection, balloonmsg="Run the selected lines"\
                                 " from the code buffer above (Ctrl+S)")
        self.window.bind("<Control-s>",apply_par)        
        self.balloon.bind_widget(self.rerun_all, balloonmsg="Clean up sandbox and run "\
                                 "all the code buffer above afterwards (Ctrl+Q)")
        self.window.bind("<Control-q>",apply_all)        
        self.interactive_output = ScrolledText(self.window,height=80)
        self.window.grid_rowconfigure(2,weight=0)
        self.interactive_output.grid(row=2,column=0,sticky=N+E+S+W)
        self.reset_interpreter()
        self.stdout = sys.stdout
        self.stderr = sys.stderr

    def do_entry(self):
        code = self.run_entry.get()
        self.run_entry.delete(0,END)
        self.code_window.subwidget("text").insert(END,"\n"+code+"\n")
        self.runsource(code)

    def do_line(self):
        code = self.code_window.subwidget("text").get("insert linestart",\
                                                      "insert lineend").strip()
        self.runsource(code)

    def do_paragraph(self):
        code = self.code_window.subwidget("text").get("sel.first linestart",\
                                                      "sel.last lineend")
        code = code.replace("\t"," "*8)
        starting_ws = ""
        for i in range(len(code)):
            if not code[i].isspace():
                break
            starting_ws += code[i]
        deindented_code = []
        for line in code.split("\n"):
            for i in range(len(line)):
                if i >= len(starting_ws) or (starting_ws[i] != line[i]):
                    deindented_code.append(line[i:])
                    starting_ws = starting_ws[:i]
                    break
        self.runcode("\n".join(deindented_code))

    def do_code(self):
        code = self.code_window.subwidget("text").get(1.0,END)
        code = code.replace("\t"," "*8)
        self.runcode(code)

    def reset_interpreter(self):
        self.interpreter = code.InteractiveInterpreter()
        self.interpreter.locals['__name__'] = '__main__'
        self.interpreter.locals['self'] = dummySelf()
        def write_local(s,parent=self):
            parent.write(s)
        self.interpreter.write = write_local
        self.clear_interactive_output()

    def write(self,s):
        self.interactive_output.subwidget("text").insert(END,s)

    def grab_output(self):
        sys.stdout = self
        sys.stderr = self

    def release_output(self):
        sys.stdout = self.stdout
        sys.stderr = self.stderr

    def runcode(self,code):
        self.clear_interactive_output()
        self.grab_output()
        self.interpreter.runcode(code)
        self.release_output()

    def runsource(self,code):
        self.clear_interactive_output()
        self.grab_output()
        self.interpreter.runsource(code)
        self.release_output()

    def clear_interactive_output(self):
        self.interactive_output.subwidget("text").delete(1.0,END)
        
    def mainloop(self):
        self.window.mainloop()
        


if __name__ == "__main__":
    print("*let Editor")
    root = SandboxInteraction()
    root.mainloop()
