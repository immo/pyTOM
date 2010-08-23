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
import sys,code,re,os
from dummyself import *
from messagebox import *
import tktable,quicktix
from scrolldummy import *

class SongEditor(object):
    regexps = [re.compile("\\s*taxa\\s*=.*")]
    colors = [{"foreground":"#CC0044","background":"#DDDDDD",\
               "font":"courier 12"}]
    regexps.append(re.compile("\\s*grammar\\s*=.*"))
    colors.append({"foreground":"#999999","background":"#000000",\
                   "font":"courier 12"})
    regexps.append(re.compile("\\s*length\\*?\\s*=.*"))
    colors.append({"foreground":"#FFFF00","background":"#000000",\
                   "font":"courier 12 bold"})
    regexps.append(re.compile("\\s*bpm\\s*=.*"))
    colors.append({"foreground":"#FFFF00","background":"#000000",\
                   "font":"courier 12 bold"})
    regexps.append(re.compile("\\s*rhythms\\s*=.*"))
    colors.append({"foreground":"#00FFFF","background":"#000000",\
                   "font":"courier 12 bold"})
    regexps.append(re.compile("\\s*initial\\s*=.*"))
    colors.append({"foreground":"#FF00FF","background":"#000000",\
                   "font":"courier 12 bold"})
    regexps.append(re.compile("\\s*things\\s*=.*"))
    colors.append({"foreground":"#FF3333","background":"#000000",\
                   "font":"courier 12 bold"})
    regexps.append(re.compile("\\:.*"))
    colors.append({"foreground":"#FFFFFF","background":"#333333",\
                   "font":"courier 12"})
    regexps.append(re.compile("\\s*postprocess\\s*=.*"))
    colors.append({"foreground":"cyan","background":"#330000",\
                   "font":"courier 12"})

    
    def __init__(self,parent=None,path=""):
        self.window = Toplevel(parent)
        self.name = os.path.basename(path)+' Song Editor'
        self.path = path
        self.saved_data = ""
        self.window.title(self.name)
        self.window.grid_columnconfigure(0,weight=1)
        self.window.grid_rowconfigure(0,weight=1)
        self.text = ScrolledText(self.window)
        self.text.grid(row=0,column=0,sticky=N+E+S+W)
        self.text.subwidget("text").configure(foreground="cyan",\
                                              background="#000000",\
                                              font="courier 12",\
                                              insertbackground="#FFFFFF")
        self.balloon = Balloon(self.window)
        self.tcontainer = Frame(self.window)
        self.tcontainer.grid(row=0,column=1,sticky=N+S+E+W)
        self.tvariable = ArrayVar(self.window)
        self.table = Table(self.tcontainer, rows=1,\
                           cols=1,titlerows=0,titlecols=0,roworigin=-1,\
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
        def scroll_table_up(x=None,s=self):
            s.table.yview_scroll(-1,"unit")
        def scroll_table_down(x=None,s=self):
            s.table.yview_scroll(1,"unit")
        self.table.bind("<Button-4>",scroll_table_up)
        self.table.bind("<Button-5>",scroll_table_down)

        self.time_container = Frame(self.window)
        self.time_container.grid(row=1,column=0,sticky=W)

        self.time = Entry(self.time_container,width=8)
        self.time.pack(side=RIGHT)
        self.time.insert(END,"0")

        self.tlabel = Label(self.time_container,text="@")
        self.tlabel.pack(side=RIGHT)

        for i in range(16):
            def set_time_to(x=None,s=self,txt=str(i)):
                s.time.delete(0, END)
                s.time.insert(END,txt)
            quicktix.add_balloon_button(self.__dict__, "btn_at"+str(i),\
                                        "time_container",str(i),\
                                        set_time_to,\
                                        "Set @ time entry to "+str(i))

        self.line_starts = Frame(self.window)
        self.line_starts.grid(row=2,column=0,columnspan=2,sticky=W)

        for txt in ["grammar=","length*=","bpm=","initial=","things=",\
                    "rhythms=","depth=","postprocess=",":","::",":::",\
                    "::::","taxa="]:
            txt2 = " "*(10-len(txt)) + txt
            txt2 = txt2.replace("="," = ")
            if txt.startswith(':'):
                txt2 = txt+" "
            def add_to_text(x=None,s=self,txt=txt2):
                line = int(s.text.subwidget("text").index("insert").split(".")[0])
                lastline = int(s.text.subwidget("text").index(END).split(".")[0])
                if line == lastline:
                    s.text.subwidget("text").insert("insert lineend","\n"+txt+"\n")
                else:
                    s.text.subwidget("text").insert("insert lineend","\n"+txt)
                s.text.subwidget("text").mark_set("insert","%i.%i"%(line+1,len(txt)))
                s.colorize_text_widget()
                s.text.subwidget("text").focus_set()
                
            quicktix.add_balloon_button(self.__dict__, "btn_txt"+txt,\
                                        "line_starts",txt,\
                                        add_to_text,\
                                        "Add "+txt+" line after insert line.")

        self.right_buttons = Frame(self.window)
        self.right_buttons.grid(row=1,column=1,sticky=E)

        def save_cmd(x=None,s=self):
            pass
        
        def upd_cmd(x=None,s=self):
            pass


        quicktix.add_balloon_button(self.__dict__,"btn_update","right_buttons",\
                                    "Update", upd_cmd,\
                                "Update the table and the text colorization.")
        quicktix.add_balloon_button(self.__dict__,"btn_save","right_buttons",\
                                    "Save", save_cmd,"Save the current file.",)
        

        self.colorize_text_widget()
        
        screencenter(self.window)

    def from_string(self,s):
        self.saved_data = s
        self.text.subwidget("text").delete("1.0",END)
        self.text.subwidget("text").insert(END,s)
        self.colorize_text_widget()

    def to_string(self):
        return self.text.subwidget("text").get("1.0",END)

    def colorize_text_widget(self):
        data = self.text.subwidget("text").get("1.0",END).split("\n")
        for i in range(len(self.regexps)):
            self.text.subwidget("text").tag_delete("colorize%i"%i)
            self.text.subwidget("text").tag_config("colorize%i"%i, **self.colors[i])
            self.text.subwidget("text").tag_lower("colorize%i"%i)

        for text,line in zip(data,range(1,len(data)+1)):
            for i in range(len(self.regexps)):
                if self.regexps[i].match(text):
                    self.text.subwidget("text").tag_add("colorize%i"%i,"%i.0"%line,\
                                                        "%i.0"%(line+1))
                    break

if __name__ == "__main__":
    root = Tk()
    root.wm_withdraw()
    x = SongEditor(root)
