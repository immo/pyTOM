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
    names = ["taxa"]
    regexps = [re.compile("\\s*taxa\\s*=.*")]
    colors = [{"foreground":"#CC0044","background":"#DDDDDD",\
               "font":"courier 12"}]
    names.append("grammar")
    regexps.append(re.compile("\\s*grammar\\s*=.*"))
    colors.append({"foreground":"#999999","background":"#000000",\
                   "font":"courier 12"})
    names.append("length")    
    regexps.append(re.compile("\\s*length\\*?\\s*=.*"))
    colors.append({"foreground":"#FFFF00","background":"#000000",\
                   "font":"courier 12 bold"})
    names.append("bpm")    
    regexps.append(re.compile("\\s*bpm\\s*=.*"))
    colors.append({"foreground":"#FFFF00","background":"#000000",\
                   "font":"courier 12 bold"})
    names.append("rhythms")    
    regexps.append(re.compile("\\s*rhythms\\s*=.*"))
    colors.append({"foreground":"#00FFFF","background":"#000000",\
                   "font":"courier 12 bold"})
    names.append("initial")    
    regexps.append(re.compile("\\s*initial\\s*=.*"))
    colors.append({"foreground":"#FF00FF","background":"#000000",\
                   "font":"courier 12 bold"})
    names.append("things")    
    regexps.append(re.compile("\\s*things\\s*=.*"))
    colors.append({"foreground":"#FF3333","background":"#000000",\
                   "font":"courier 12 bold"})
    names.append(":")    
    regexps.append(re.compile("\\:.*"))
    colors.append({"foreground":"#FFFFFF","background":"#333333",\
                   "font":"courier 12"})
    names.append("postprocess")    
    regexps.append(re.compile("\\s*postprocess\\s*=.*"))
    colors.append({"foreground":"cyan","background":"#330000",\
                   "font":"courier 12"})
    names.append("depth")
    regexps.append(re.compile("\\s*depth\\s*=.*"))
    colors.append({"foreground":"cyan","background":"#000000",\
                   "font":"courier 12"})


    
    def __init__(self,parent=None,path="",workspace=None):
        self.window = Toplevel(parent)
        self.workspace = workspace
        self.name = os.path.basename(path)+' Song Editor'
        self.path = path
        self.saved_data = ""
        self.line_type = ""
        self.table_data = {}
        self.current_table_data = []
        self.table_scroll = {}
        self.table_colwidth = 36
        self.colon_depth = 0
        self.window.title(self.name)
        self.window.grid_columnconfigure(0,weight=1)
        self.window.grid_rowconfigure(0,weight=1)
        self.text = ScrolledText(self.window)
        self.text.grid(row=0,column=0,sticky=N+E+S+W)
        self.text.subwidget("text").configure(foreground="cyan",\
                                              background="#000000",\
                                              font="courier 12",\
                                              insertbackground="#FFFFFF",\
                                              undo=1,autoseparators=1)
        self.balloon = Balloon(self.window)
        self.tcontainer = Frame(self.window)
        self.tcontainer.grid(row=0,column=1,sticky=N+S+E+W)
        self.tvariable = ArrayVar(self.window)
        self.table = Table(self.tcontainer, rows=1,\
                           cols=1,titlerows=0,titlecols=0,roworigin=-1,\
                           colorigin=0,selectmode='browse',\
                           rowstretch='none',colstretch='all',\
                           variable=self.tvariable,drawmode='slow',\
                           state='disabled',colwidth=self.table_colwidth,\
                           font="courier 12",background="#222222",\
                           foreground="yellow",\
                           anchor=W)
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
        self.table.tag_configure("heading",background="#000000",\
                                 foreground="#FF00FF",font="courier 12 bold")
        self.table.tag_cell("heading","-1,0")

        self.time_container = Frame(self.window)
        self.time_container.grid(row=1,column=0,sticky=W)

        self.time_container2 = Frame(self.time_container)
        self.time_container2.pack(side=RIGHT)

        self.table_row = None

        for i in range(1,5):
            def set_offset_to(x=None,s=self,txt=str(i)):
                s.time_offset.delete(0,END)
                s.time_offset.insert(END,txt)
            quicktix.add_balloon_button(self.__dict__,"btn_off"+str(i),\
                                        "time_container2",str(i),\
                                        set_offset_to,\
                                        "Set += time offset entry to "+str(i))

                                        
        self.time_offset = Entry(self.time_container,width=4,justify=RIGHT)
        self.time_offset.pack(side=RIGHT)
        self.time_offset.insert(END,"4")
        
        self.tolabel = Label(self.time_container,text="+=")
        self.tolabel.pack(side=RIGHT)

        self.time = Entry(self.time_container,width=4,justify=RIGHT)
        self.time.pack(side=RIGHT)
        self.time.insert(END,"0")


        self.tlabel = Label(self.time_container,text="@")
        self.tlabel.pack(side=RIGHT)

        for i in range(16)[-1::-1]:
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

        def add_lot_of_text(x=None,s=self):
            txt = """  grammar = g_2010
  initial = 
      bpm = 
  length* = 
  rhythms = 
   things = """
            line = int(s.text.subwidget("text").index("insert").split(".")[0])
            lastline = int(s.text.subwidget("text").index(END).split(".")[0])
            if line == lastline:
                s.text.subwidget("text").insert("insert lineend","\n"+txt+"\n")
            else:
                s.text.subwidget("text").insert("insert lineend","\n"+txt)
            s.text.subwidget("text").mark_set("insert","%i.%i"%(line+1,len(txt)))
            s.colorize_text_widget()
            s.text.subwidget("text").focus_set()
                
        quicktix.add_balloon_button(self.__dict__, "btn_txtlot",\
                                        "line_starts","...",\
                                        add_lot_of_text,\
                                        "Add common stuff...")

            

        self.right_buttons = Frame(self.window)
        self.right_buttons.grid(row=1,column=1,sticky=E)

        def save_cmd(x=None,s=self):
            s.save_to()
        
        def upd_cmd(x=None,s=self):
            if s.workspace != None:
                s.workspace.update_directory()
            s.prepare_table_data()
            s.table_update()
            s.colorize_text_widget()

        def close_handler(x=None,s=self):
            if s.to_string() != s.saved_data:
                if yesnobox(self.name,"The song has been changed.",\
                            "","Do you want to save it now?"):
                    s.save_to()
            s.window.destroy()

        self.window.protocol("WM_DELETE_WINDOW",close_handler)
        self.window.bind("<Control-s>",save_cmd)

        def undo_cmd(x=None,s=self):
            s.text.subwidget("text").edit_undo()
            s.colorize_text_widget()
            s.table_update()

        def redo_cmd(x=None,s=self):
            s.text.subwidget("text").edit_redo()
            s.colorize_text_widget()
            s.table_update()

        quicktix.add_balloon_button(self.__dict__,"btn_undo","right_buttons",\
                                    "Undo", undo_cmd,\
                                    "Undo the last edit action.")

        quicktix.add_balloon_button(self.__dict__,"btn_redo","right_buttons",\
                                    "Redo", redo_cmd,\
                                    "Redo the last undone edit action.")



        quicktix.add_balloon_button(self.__dict__,"btn_update","right_buttons",\
                                    "Update", upd_cmd,\
                                "Update the table and the text colorization. (F5)")
        quicktix.add_balloon_button(self.__dict__,"btn_save","right_buttons",\
                                    "Save", save_cmd,"Save the current file.",)

        self.window.bind("<F5>",upd_cmd)

        self.b1_start_position = END

        def tbl_update(x=None,s=self):
            idx = s.text.subwidget("text").index("@%i,%i"%(x.x,x.y))
            s.text.subwidget("text").mark_set("insert",idx)
            ranges = s.text.subwidget("text").tag_ranges(SEL)
            if ranges:
                start = s.text.subwidget("text").index(ranges[0])
                end = s.text.subwidget("text").index(ranges[1])
                s.text.subwidget("text").tag_remove(SEL,start,end)
            s.text.subwidget("text").tag_add(SEL,idx,idx)
            s.b1_start_position = idx
            s.text.subwidget("text").focus_set()
            s.table_update()
            return "break"

        def tbl_drag(x=None,s=self):
            idx = s.text.subwidget("text").index("@%i,%i"%(x.x,x.y))
            s.text.subwidget("text").mark_set("insert",idx)
            ranges = s.text.subwidget("text").tag_ranges(SEL)

            if ranges:
                start = s.text.subwidget("text").index(ranges[0])
                end = s.text.subwidget("text").index(ranges[1])
                s.text.subwidget("text").tag_remove(SEL,start,end)
            s.text.subwidget("text").tag_add(SEL,s.b1_start_position,idx)
            s.text.subwidget("text").tag_add(SEL,idx,s.b1_start_position)           
            return "break"

        def tbl_select_dbl(x=None,s=self):
            s.select_current_fragment()
            return "break"

        def tbl_select_trp(x=None,s=self):
            s.select_current_values()
            return "break"

        self.text.subwidget("text").bind("<Button-1>",tbl_update)
        self.text.subwidget("text").bind("<Double-Button-1>",tbl_select_dbl)
        self.text.subwidget("text").bind("<Triple-Button-1>",tbl_select_trp)
        self.text.subwidget("text").bind("<B1-Motion>",tbl_drag)

        def refresh_table(x=None,s=self):
            s.table_update()

        for key in ["<Left>","<Right>","<Up>","<Down>","<Return>","<Prior>","<Next>"]:
            self.text.subwidget("text").bind(key,refresh_table)


        def refocus_text(x=None,s=self):
            s.table_row = int(s.table.index("@%i,%i"%(x.x,x.y)).split(",")[0])
            s.text.subwidget("text").focus_set()

        def insert_text(x=None,s=self):
            s.table_row = int(s.table.index("@%i,%i"%(x.x,x.y)).split(",")[0])
            s.table_text()

        def open_in_editor(x=None,s=self):
            s.table_row = int(s.table.index("@%i,%i"%(x.x,x.y)).split(",")[0])
            s.do_edit(s.table_row)

        self.table.bind("<Button-1>",refocus_text)
        self.table.bind("<Double-Button-1>",refocus_text)
        self.table.bind("<Triple-Button-1>",refocus_text)

        self.table.bind("<Double-Button-1>",insert_text)
        self.table.bind("<Triple-Button-1>",insert_text)
        self.table.bind("<Double-Button-3>",open_in_editor)

        self.prepare_table_data()


        self.colorize_text_widget()
        self.text.subwidget("text").focus_set()
        quicktix.min_win_size(self.window,700,680)
        screencenter(self.window)

    def table_text(self):
        if not self.line_type in self.table_data:
            return
        tbl = self.table_data[self.line_type]
        if 0 <= self.table_row < len(tbl):
            datum = tbl[self.table_row]
            line,column = map(lambda x:int(x),self.text.subwidget("text").index("insert").split("."))
            data = self.text.subwidget("text").get("%i.0"%line,"%i.end"%line)
            if self.line_type in ["rhythms","things"]:
                before = data[:column]
                after = data[column:]
                first_on_line = False
                following_stuff = False
                if "=" in before:
                    ttr = len(after)
                    if ";" in after:
                        ttr = after.index(";")
                    else:
                        if not before[before.index("=")+1:].strip():
                            first_on_line = True
                    insert = len(before) + ttr
                else:
                    first_on_line = True
                    if "=" in after:
                        ttr = after.index("=")
                        if len(after) > ttr+1:
                            if after[ttr+1].isspace():
                                ttr += 1
                    else:
                        ttr = len(after)
                    if after[ttr:].strip():
                        following_stuff = True
                    insert = len(before) + ttr+1
                try:
                    start_time = eval(self.time.get())
                except:
                    start_time = 0
                if not first_on_line:
                    txt = ";" + datum + "@" + str(start_time)
                elif first_on_line:
                    txt = datum + "@" + str(start_time)
                    if following_stuff:
                        txt += ";"
                self.text.subwidget("text").insert("%i.%i"%(line,insert),txt)
                self.text.subwidget("text").mark_set("insert","%i.%i"%(line,insert+len(txt)))
                try:
                    time_offset = eval(self.time_offset.get())
                except:
                    time_offset = 0
                self.time.delete(0,END)

                self.time.insert(END,str(start_time+time_offset))
            elif self.line_type.startswith("initial"):
                before = data[:column]
                after = data[column:]
                if "=" in before:
                    ttr = len(after)
                    if ")" in after:
                        ttr = after.index(")")+1
                    insert = len(before) + ttr
                else:
                    if "=" in after:
                        ttr = after.index("=")
                        if len(after) > ttr+1:
                            if after[ttr+1].isspace():
                                ttr += 1
                    else:
                        ttr = len(after)
                    insert = len(before) + ttr + 1
                txt = datum + "()"
                self.text.subwidget("text").insert("%i.%i"%(line,insert),txt)
                self.text.subwidget("text").mark_set("insert","%i.%i"%(line,insert+len(txt)-2))
                

            elif "=" in data:
                eqn = data.index("=")+1
                self.text.subwidget("text").delete("%i.%i"%(line,eqn),"%i.%i"%(line,len(data)))
                self.text.subwidget("text").insert("%i.%i"%(line,eqn)," "+datum)
        self.text.subwidget("text").focus_set()
            

    def prepare_table_data(self):
        data = {}
        data['bpm'] = "60,72,90,100,120,130,135,140,150,160,175,180,190,200,205,210,220,240,260".split(",")
        data['depth'] = "1,2,3,4,5,8,12,16".split(",")
        data['length'] = "1,2,3,4,6,8,12,15,16,18,20,21,24,32".split(",")
        if self.workspace != None:
            data['things'] = self.workspace.get_things()
            data['grammar'] = self.workspace.get_grammars()
            data['rhythms'] = self.workspace.get_rhythms()
        editor = self.text.subwidget("text").get("1.0",END)
        part_names = filter(lambda x:x.startswith(":"), editor.split("\n"))
        for pn in part_names:
            idx = 0
            while idx < len(pn) and pn[idx] == ":":
                idx += 1
            taxon = "initial level "+str(idx+1)
            if not taxon in data:
                data[taxon] = []
            data[taxon].append(pn[idx:].strip())
            
        self.table_data = data

    def table_update(self):
        line = int(self.text.subwidget("text").index("insert").split(".")[0])
        data = self.text.subwidget("text").get("%i.0"%line,"%i.end"%line)
        new_type = None
        for n,r in zip(self.names,self.regexps):
            if r.match(data):
                new_type = n
                break

        allbefore = "\n"+self.text.subwidget("text").get("0.0","%i.end"%line)
        if "\n:" in allbefore:
            idx = allbefore.rindex("\n:") + 1
            old = idx
            while idx < len(allbefore) and allbefore[idx] == ":":
                idx += 1
            self.colon_depth = idx - old
        else:
            self.colon_depth = 0

        if new_type == "initial":
            new_type = "initial level "+str(self.colon_depth)


        self.table_scroll[self.line_type] = self.table.yview()[0]
        
        if new_type in self.table_data:
            new_data = self.table_data[new_type]
        else:
            new_data = []
        self.tvariable.set("-1,0",new_type)            
        for i in range(len(new_data)):
            display_text = new_data[i]
            if len(display_text) > self.table_colwidth:
                display_text = "..."+display_text[-self.table_colwidth+3:]
            self.tvariable.set("%i,0"%i,display_text)
        self.table.configure(rows=len(new_data)+1,\
                             colwidth=self.table_colwidth)
        self.current_table_data = new_data

        if new_type in self.table_scroll:
            self.table.yview_moveto(self.table_scroll[new_type])
        
        self.line_type = new_type
            


    def select_current_fragment(self):
        line,column = map(lambda x:int(x),self.text.subwidget("text").index("insert").split("."))
        
        data = self.text.subwidget("text").get("%i.0"%line,"%i.end"%line)
        ranges = self.text.subwidget("text").tag_ranges(SEL)
        if ranges:
            start = self.text.subwidget("text").index(ranges[0])
            end = self.text.subwidget("text").index(ranges[1])
            self.text.subwidget("text").tag_remove(SEL,start,end)
        before = data[:column]
        after = data[column:]
        if self.line_type in ["rhythms","things"]:
            ttr = len(after)
            if ";" in after:
                ttr = after.index(";")+1
            end = ttr + len(before)
            if ";" in before:
                start = before.rindex(";")+1
            elif "=" in before:
                start = before.index("=")+1
                if len(before) > start+1:
                    if before[start+1].isspace():
                        start += 1
            elif "=" in after:
                start = after.index("=")+1
                if len(after) > start +1:
                    if after[start+1].isspace():
                        start += 1
                start += len(before)
            else:
                start = 0
            self.text.subwidget("text").tag_add(SEL,"%i.%i"%(line,start),"%i.%i"%(line,end))
        elif self.line_type.startswith("initial"):
            ttr = len(after)
            if ")" in after:
                ttr = after.index(")")+1
            end = ttr + len(before)
            if ")" in before:
                start = before.rindex(")")+1
            elif "=" in before:
                start = before.index("=")+1
                if len(before) > start+1:
                    if before[start+1].isspace():
                        start += 1
            elif "=" in after:
                start = after.index("=")+1
                if len(after) > start +1:
                    if after[start+1].isspace():
                        start += 1
                start += len(before)
            else:
                start = 0
            self.text.subwidget("text").tag_add(SEL,"%i.%i"%(line,start),"%i.%i"%(line,end))
        elif not self.line_type == ":":
            self.select_current_values()

    
    def select_current_values(self):
        line = int(self.text.subwidget("text").index("insert").split(".")[0])
        data = self.text.subwidget("text").get("%i.0"%line,"%i.end"%line)

        ranges = self.text.subwidget("text").tag_ranges(SEL)
        if ranges:
            start = self.text.subwidget("text").index(ranges[0])
            end = self.text.subwidget("text").index(ranges[1])
            self.text.subwidget("text").tag_remove(SEL,start,end)


        if self.line_type == ":":
            idx = 0
            while (idx < len(data)) and data[idx] == ":":
                idx += 1
            self.text.subwidget("text").tag_add(SEL,"%i.%i"%(line,idx),"%i.end"%line)
            return


        if "=" in data:
            eqn = data.index("=")
            if len(data) > eqn+1:
                if data[eqn+1].isspace():
                    eqn += 1
            self.text.subwidget("text").tag_add(SEL,"%i.%i"%(line,eqn+1),"%i.end"%line)
        else:
            self.text.subwidget("text").tag_add(SEL,"%i.0"%line,"%i.end"%line)


    def from_string(self,s):
        self.text.subwidget("text").delete("1.0",END)
        if s.endswith("\n"):
            self.text.subwidget("text").insert(END,s[:-1])
            self.saved_data = s                        
        else:
            self.text.subwidget("text").insert(END,s)
            self.saved_data = s+"\n"

        self.colorize_text_widget()
        self.prepare_table_data()


    def to_string(self):
        return self.text.subwidget("text").get("1.0",END)

    def save_to(self):
        i = inputbox(self.name,"Path =$"+self.path+"$")
        if i:
            self.save(i[0])

    def save(self,new_path=None):
        if new_path:
            self.path = new_path
            
        s = self.to_string()
        with open(self.path,'w') as f:
            f.write(s)
            
        self.saved_data = s


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

    def do_edit(self,row):
        if 0 <= row < len(self.current_table_data) and\
               self.workspace != None:
            entry = self.current_table_data[row]
            if self.line_type in ["things","grammar"]:
                self.workspace.edit_file_by_end(entry)
            elif self.line_type == "rhythms":
                if "/" in entry:
                    self.workspace.edit_file_by_end(entry[:entry.index("/")])

if __name__ == "__main__":
    root = Tk()
    root.wm_withdraw()
    x = SongEditor(root)
