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
import sys,code,re

class dummySelf(object):
    def __init__(self,dict=None):
        if dict:
            self.__dict__ = dict.copy()
    def __repr__(self):
        if self.__dict__:
            keys = self.__dict__.keys()
            keys.sort()
            reps = [repr(k) for k in keys]
            maxlen = max([min(len(r),20) for r in reps])
            contents = []
            for k,r in zip(keys,reps):
                if len(r) < maxlen:
                    pad = " "*(maxlen-len(r))
                else:
                    pad = ""
                contents.append(r+": "+pad+repr(self.__dict__[k]))
            return "sandbox.dummySelf({" + (",\\\n"+" "*19).join(contents)+"})"
        else:
            return "sandbox.dummySelf()"

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
        self.interactive_output = ScrolledText(self.window,height=160)
        self.window.grid_rowconfigure(2,weight=0)
        self.interactive_output.grid(row=2,column=0,sticky=N+E+S+W)
        self.stdout = sys.stdout
        self.stderr = sys.stderr
        self.error_line = re.compile(">., line [0-9]*")
        self.mark_error_offset = 0
        self.reset_interpreter()

    def do_entry(self):
        start_linecol = int(self.code_window\
                        .subwidget("text").index("end")\
                        .split(".")[0])
        self.mark_error_offset = start_linecol - 1  
        code = self.run_entry.get()
        self.run_entry.delete(0,END)
        self.code_window.subwidget("text").insert(END,"\n"+code+"\n")
        self.code_window.subwidget("text").yview_moveto(1.0)
        self.runsource(code)

    def do_line(self):
        start_linecol = int(self.code_window\
                        .subwidget("text").index("insert")\
                        .split(".")[0])
        self.mark_error_offset = start_linecol - 1
        code = self.code_window.subwidget("text").get("insert linestart",\
                                                      "insert lineend").strip()
        self.runsource(code)

    def do_paragraph(self):
        start_linecol = int(self.code_window\
                        .subwidget("text").index("sel.first linestart")\
                        .split(".")[0])
        self.mark_error_offset = start_linecol - 1
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
            add_empty_line = True
            for i in range(len(line)):
                if i >= len(starting_ws) or (starting_ws[i] != line[i]):
                    deindented_code.append(line[i:])
                    starting_ws = starting_ws[:i]
                    add_empty_line = False
                    break
            if add_empty_line:
                deindented_code.append("")
        self.runcode("\n".join(deindented_code))

    def do_code(self):
        self.mark_error_offset = 0
        code = self.code_window.subwidget("text").get(1.0,END)
        code = code.replace("\t"," "*8)
        self.runcode(code)

    def reset_interpreter(self):
        self.interpreter = code.InteractiveInterpreter()
        self.interpreter.locals['__name__'] = '__main__'
        self.interpreter.locals['self'] = dummySelf()
        self.interpreter.locals['sandself'] = self
        def write_local(s,parent=self):
            parent.write(s)
        self.interpreter.write = write_local
        self.runcode("import sandbox")        
        self.clear_interactive_output()

    def write(self,s):
        self.interactive_output.subwidget("text").insert(END,s)
        errline = self.error_line.search(s)
        if errline:
            start,end = errline.span()
            line = str( int(s[start+9:end]) + self.mark_error_offset )
            self.code_window.subwidget("text").mark_set("insert",line+".0")
            self.code_window.subwidget("text").tag_add("sel",line+".0",\
                                                       line+".end")
            self.code_window.subwidget("text").focus_set()
       
                            

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
        
