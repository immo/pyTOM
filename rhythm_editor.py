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
from rhythmlet_editor import *
from scrolldummy import *
import quicktix,os
import utils

class RhythmEditor(object):
    def __init__(self,parent=None,save_path=None):
        self.save_path = save_path
        self.last_save_string = "Rhythm Desk"
        self.window = Toplevel(parent)
        if save_path:
            self.window.title(os.path.basename(save_path)+" Rhythm Editor Desk")
        else:
            self.window.title("Rhythm Editor Desk")
        self.rhythmletstack = []
        self.window.grid_columnconfigure(0,weight=0)
        self.window.grid_columnconfigure(1,weight=1)        
        self.window.grid_rowconfigure(0,weight=1)        
        self.tcontainer = Frame(self.window)
        self.tcontainer.grid(row=0,column=0,sticky=N+S+E+W)
        self.tvariable = ArrayVar(self.window)
        self.tvariable.set("-1,0","Rhythmlets")
        self.table = Table(self.tcontainer, rows=1,\
                           cols=1,titlerows=1,titlecols=0,roworigin=-1,\
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
        self.balloon = Balloon(self.window)
        self.r_buttons = Frame(self.window)
        self.r_buttons.grid(row=1,column=0,sticky=W)
        self.next_name = "A"
        self.second_op = -1
        self.canvas_op = -1

        def choose_second_op(event,s=self):
            row,col = s.table.index("@%i,%i"%(event.x,event.y)).split(",")
            row = int(row)
            s.second_op = row
            s.hilight_second_op()

        def calculate_meet(event,s=self):
            row,col = s.table.index("@%i,%i"%(event.x,event.y)).split(",")
            row = int(row)            
            if (0 <= s.second_op < len(s.rhythmletstack)) \
               and (0 <= row < len(s.rhythmletstack)):
                left = s.rhythmletstack[s.second_op]
                right = s.rhythmletstack[row]
                new_name = left[0]+" "*(max(utils.count_recurrences(left[0]," "))+1)\
                           + "&" + " "*(max(utils.count_recurrences(right[0]," "))+1)\
                           + right[0]
                idx = s.add_rhythmlet_var(new_name,left[1].____ref & right[1].____ref)
                s.second_op = idx
                s.hilight_second_op()

        def calculate_join(event,s=self):
            row,col = s.table.index("@%i,%i"%(event.x,event.y)).split(",")
            row = int(row)            
            if (0 <= s.second_op < len(s.rhythmletstack)) \
               and (0 <= row < len(s.rhythmletstack)):
                left = s.rhythmletstack[s.second_op]
                right = s.rhythmletstack[row]
                new_name = left[0]+" "*(max(utils.count_recurrences(left[0]," "))+1)\
                           + "|" + " "*(max(utils.count_recurrences(right[0]," "))+1)\
                           + right[0]
                idx = s.add_rhythmlet_var(new_name,left[1].____ref | right[1].____ref)
                s.second_op = idx
                s.hilight_second_op()

        def new_rhythmlet(x=None,s=self):
            row = s.add_rhythmlet_var(s.get_next_name(),Rhythmlet())
            s.rename_rhythmlet_var(row)

        def rename_rhythmlet(x=None,s=self):
            row,col = s.table.index("active").split(",")
            row = int(row)
            s.rename_rhythmlet_var(row)

        def mouse_rename_rhythmlet(event,s=self):
            row,col = s.table.index("@%i,%i"%(event.x,event.y)).split(",")
            row = int(row)
            s.rename_rhythmlet_var(row)
            
        def del_rhythmlet(x=None,s=self):
            row,col = s.table.index("active").split(",")
            row = int(row)
            s.del_rhythmlet_var(row)
                    
        quicktix.add_balloon_button(self.__dict__,'new_btn','r_buttons','New',\
                                    new_rhythmlet,'Create a new rhythmlet.')
        quicktix.add_balloon_button(self.__dict__,'ren_btn','r_buttons','Rename',\
                                    rename_rhythmlet,\
                                    'Rename the currently selected rhythmlet.')
        quicktix.add_balloon_button(self.__dict__,'del_btn','r_buttons','Delete',\
                                    del_rhythmlet,\
                                    'Deletes the currently selected rhythmlet. (Del)')
        
        
        def edit_rhythmlet(event,s=self):
            row,col = s.table.index("@%i,%i"%(event.x,event.y)).split(',')
            row = int(row)
            if row >= 0:
                RhythmletEditor(self.rhythmletstack[row][1],s.window,\
                                self.rhythmletstack[row][0]+" #"+str(row))

        def scroll_down(x=None,s=self):
            s.table.yview_scroll(1,"unit")
        def scroll_up(x=None,s=self):
            s.table.yview_scroll(-1,"unit")

        def pick_to_canvas(event,s=self):
            row,col = s.table.index("@%i,%i"%(event.x,event.y)).split(",")
            row = int(row)
            s.display_canvas(row)
            

        self.window.bind("<Button-4>",scroll_up)
        self.window.bind("<Button-5>",scroll_down)        

        self.table.bind("<Double-Button-1>",edit_rhythmlet)
        self.window.bind("<Delete>",del_rhythmlet)        
        self.table.bind("<Shift-Button-3>",mouse_rename_rhythmlet)
        self.table.bind("<Button-3>",choose_second_op)
        self.table.bind("<Button-2>",pick_to_canvas)        
        self.table.bind("<Control-Button-1>",calculate_meet)
        self.table.bind("<Shift-Button-1>",calculate_join)                        
        self.fill_table()

        self.canvas = Canvas(self.window,width=300,height=300)
        self.canvas.grid(row=0,column=1,sticky=N+E+S+W)

        self.canvas_ids = []
        self.canvas_op = -1

        self.c_buttons = Frame(self.window)
        self.c_buttons.grid(row=1,column=1,sticky=W)

        def clear_canvas(x=None,s=self):
            s.canvas_ids = []
            s.update_canvas()

        def update_canvas(x=None,s=self):
            s.update_canvas()

        def to_canvas(x=None,s=self):
            row,col = s.table.index("active").split(",")
            row = int(row)
            s.display_canvas(row)

        def from_canvas(x=None,s=self):
            s.remove_canvas(s.canvas_op)

        quicktix.add_balloon_button(self.__dict__,"add_btn","c_buttons","← Add",\
                                    to_canvas,\
                                    "Add selected Rhythmlet to canvas.")
        quicktix.add_balloon_button(self.__dict__,"rmv_btn","c_buttons","Remove ↑",\
                                    from_canvas,\
                                    "Removes the selected canvas object from canvas."\
                                    " (Middle-Click)")
        quicktix.add_balloon_button(self.__dict__,"clr_btn","c_buttons","Clear",\
                                    clear_canvas,\
                                    "Clear all objects from canvas.")
        quicktix.add_balloon_button(self.__dict__,"upd_btn","c_buttons","Update",\
                                    update_canvas,\
                                    "Update shown relations on canvas.")

        def save_to_path(x=None,s=self):
            if s.save_path:
                path = str(s.save_path)
            else:
                path = ""
            i = inputbox("Rhytm Desk "+path,"Path = $"+path+"$")
            if i:
                s.save_to(i[0])

        quicktix.add_balloon_button(self.__dict__,"save_btn","c_buttons","Save",\
                                    save_to_path,\
                                    "Save the current rhythm desk.")
                

        def reconfigure(x=None,s=self):
            s.update_canvas()

        self.window.bind("<Configure>",reconfigure)

        def check_for_save(x=None,s=self):
            if s.to_string() != s.last_save_string:
                if s.save_path:
                    path = str(s.save_path)
                else:
                    path = ""
                if yesnobox("Rhythm Desk "+path,"Rhythm Desk has been changed.","",\
                            "Do you want to save now?"):
                    save_to_path(x,s)
            s.window.destroy()

        self.window.protocol("WM_DELETE_WINDOW",check_for_save)
        
        quicktix.min_win_size(self.window,600,400)
        quicktix.screencenter(self.window)

    def display_canvas(self,index):
        if not index in self.canvas_ids:
            self.canvas_ids.append(index)
        self.update_canvas()

    def remove_canvas(self,index):
        self.canvas_ids = [i for i in self.canvas_ids if not i == index]
        self.update_canvas()

    def update_canvas(self):
        self.canvas_ids = filter(lambda x: 0 <= x < len(self.rhythmletstack),\
                                 self.canvas_ids)
        
        if not self.canvas_ids:
            self.canvas.delete(ALL)
            return
        
        ideals = {}
        from_top = {}
        for i in self.canvas_ids:
            ideals[i] = filter(lambda x: \
                               self.rhythmletstack[x][1].____ref <\
                               self.rhythmletstack[i][1].____ref,\
                               self.canvas_ids)
            from_top[i] = 0

        refined = True
        while refined:
            refined = False
            for i in ideals:
                relative = from_top[i] + 1
                for j in ideals[i]:
                    if from_top[j] < relative:
                        from_top[j] = relative
                        refined = True
        descendants = {}
        for i in ideals:
            relative = from_top[i] + 1
            descendants[i] = filter(lambda x: from_top[x] == relative,\
                                    ideals[i])
        # dummy coordination
        line_width = {}
        line_order = {}
        for i in from_top:
            l = from_top[i]
            if l in line_width:
                line_width[l] += 1
                line_order[l].append(i)
            else:
                line_width[l] = 1
                line_order[l] = [i]

        x_vals = []
        y_vals = []
        coords = {}
        for l in line_order:
            w = line_width[l]
            count = 0
            for i in line_order[l]:
                coords[i] = (10*count - 5*(w-1),10*l)
                x_vals.append(coords[i][0])
                y_vals.append(coords[i][1])
                count += 1

        canvas_w = self.canvas.winfo_width()
        canvas_h = self.canvas.winfo_height()
        low_x = min(x_vals)
        low_y = min(y_vals)
        paint_width = float(max(x_vals)-low_x)
        paint_height = float(max(y_vals)-low_y)
        if paint_width == 0.0:
            paint_width = 1.0
        if paint_height == 0.0:
            paint_height = 1.0
        for i in coords:
            x,y = coords[i]
            x = canvas_w*0.1 + 0.8*canvas_w*float(x-low_x)/paint_width
            y = canvas_h*0.1 + 0.8*canvas_h*float(y-low_y)/paint_height
            coords[i] = (int(x),int(y))
            
        # restructurize canvas
        self.canvas.delete(ALL)
        for i in self.canvas_ids:
            for j in descendants[i]:
                self.canvas.create_line(coords[i][0],coords[i][1],\
                                        coords[j][0],coords[j][1])
        for i in self.canvas_ids:
            t = self.canvas.create_text(coords[i][0],coords[i][1],\
                                    text=self.rhythmletstack[i][0]+ " #"+str(i))
            b = self.canvas.create_rectangle(*self.canvas.bbox(t),fill="white")
            self.canvas.lift(t)
            def choose_canvas_second_op(x=None,s=self,nbr=i):
                s.canvas_op = nbr
            self.canvas.tag_bind(t,"<Button-1>",choose_canvas_second_op)
            self.canvas.tag_bind(b,"<Button-1>",choose_canvas_second_op)            
            

        self.canvas.configure(scrollregion=self.canvas.bbox(ALL))


    def get_next_name(self):
        x = self.next_name
        y = x[:-1]
        c = x[-1]
        if c == "Z":
            y += "*"
            c = "A"
        else:
            c = chr(ord(c)+1)
        self.next_name = y+c
        return x
        
    def fill_table(self):
        for i in range(len(self.rhythmletstack)):
            self.tvariable.set("%i,0"%i,self.rhythmletstack[i][0])
        self.table.config(rows=len(self.rhythmletstack)+1)

    def hilight_second_op(self):
        self.table.tag_delete("hilit")
        self.table.tag_configure("hilit",background="yellow")
        self.table.tag_cell("hilit","%i,0"%self.second_op)

    def add_rhythmlet_var(self,name,rhythmlet):
        index = len(self.rhythmletstack)
        self.rhythmletstack.append((name,ReferenceObject(rhythmlet),))
        self.fill_table()
        return index

    def del_rhythmlet_var(self,index):
        if not 0 <= index < len(self.rhythmletstack):
            return
        if self.second_op > index:
            self.second_op -= 1
        new_stack = self.rhythmletstack[:index] + self.rhythmletstack[index+1:]
        self.rhythmletstack = new_stack
        self.fill_table()
        self.hilight_second_op()        
        

    def rename_rhythmlet_var(self,index):
        if 0 <= index < len(self.rhythmletstack):
            current = self.rhythmletstack[index][0]
            answer = inputbox(self.window,"Rename Rythmlet",\
                              "Rename '"+current+"'",\
                              "to: $"+current+"$")
            if answer:
                self.rhythmletstack[index] = (answer[0],self.rhythmletstack[index][1])
                self.fill_table()

    def to_string(self):
        data = ["Rhythm Desk"]
        for name,ref in self.rhythmletstack:
            data.append("Named Rhythmlet")
            data.append(repr(name))
            data.append(repr(ref.times))
            data.append(repr(ref.i_priorities.keys()))
            for k in ref.i_priorities.keys():
                data.append(repr(ref.__dict__[k]))
        return "\n".join(data)

    def from_string(self,s):
        data = map(lambda x:str(x).strip(),s.split('\n')[1:]) #skip name id
        data = filter(lambda x:x,data) # kill empty lines!
        i = 0
        self.rhythmletstack = []
        self.last_save_string = s
        while i < len(data):
            if data[i] == "Named Rhythmlet":
                name = eval(data[i+1])
                ref_times =eval(data[i+2])
                priority_keys = eval(data[i+3])
                i += 3
                events = {}
                for k in priority_keys:
                    i += 1                    
                    events[k] = eval(data[i])
                rhythmlet = Rhythmlet(*ref_times)
                for k in events:
                    rhythmlet.__dict__[k] = events[k]
                self.rhythmletstack.append((name,ReferenceObject(rhythmlet),))             
            else:
                raise Exception("RhythmEditor: cannot recognize: ",data[i])
            i += 1
        self.fill_table()

    def save_to(self,new_path=None):
        if new_path:
            self.save_path = new_path
        if self.save_path:
            self.last_save_string = self.to_string()
            with open(self.save_path,'w') as f:
                f.write(self.last_save_string)
