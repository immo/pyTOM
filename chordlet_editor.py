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
import quicktix,os
import utils

def name_pitch(p):
    return {0:"C",1:"C#",2:"D",3:"D#",4:"E",5:"F",6:"F#",\
            7:"G",8:"G#",9:"A",10:"A#",11:"B"}[p%12]

class ChordletEditor(object):
    def __init__(self,parent=None):
        self.parent = parent

    def update_table(self):
        filterfn = lambda x:False
        try:
            code = "lambda x: "+self.fret_filter.get()
            fn = eval(code)
            filterfn = fn
        except:
            pass
            
        self.chordlet.style = self.stylevar.get().strip()        
        self.table.tag_delete("fingers")
        self.table.tag_delete("goodfret")
        self.table.tag_configure("goodfret",foreground="white",background="#333333")
        self.table.tag_raise("goodfret")
        self.table.tag_configure("goodfretfingers",foreground="#FF3333",background="#333333")
        self.table.tag_raise("goodfretfingers")
        self.table.tag_configure("fingers",foreground="red")
        self.table.tag_raise("fingers")
        for i in range(self.nfrets):
            for j in range(25):
                if filterfn(self.chordlet.g_tuning[self.nfrets-i-1]+j):
                    good = True
                    self.table.tag_cell("goodfret","%i,%i"%(i,j))
                else:
                    good = False
                
                if self.chordlet.frets[self.nfrets-i-1] == j:
                    self.tvariable.set("%i,%i"%(i,j),\
                                       name_pitch(self.chordlet.g_tuning\
                                                  [self.nfrets-i-1]+j))
                    if good:
                        self.table.tag_cell("goodfretfingers","%i,%i"%(i,j))                        
                    else:
                        self.table.tag_cell("fingers","%i,%i"%(i,j))
                else:
                    self.tvariable.set("%i,%i"%(i,j),"—")

        def str2(x):
            if x != None:
                return str(x)
            return "-"

        txt = "          ; " + " ".join(map(str2,self.chordlet.frets))
        txt += " "*(12+3*7+3-len(txt)) + self.chordlet.style
        txt += " "*(12+3*7+5-len(txt))
        txt += self.additional_stuff.get()
        
        self.copy_entry.delete(0,END)
        self.copy_entry.insert(END,txt)

    def edit_chordlet(self,input,name=None):
        self.window = Toplevel(self.parent)
        if name:
            self.window.title(name+" - Edit Chordlet")
        else:
            self.window.title("Edit Chordlet")

        self.tcontainer = Frame(self.window)
        self.tcontainer.grid(row=0,column=0,columnspan=4,sticky=N+S+E+W)
        self.tvariable = ArrayVar(self.window)
        for i in range(25):
            self.tvariable.set("-1,%i"%i,str(i))
        self.nfrets = len(input.frets)
        self.table = Table(self.tcontainer, rows=1+self.nfrets,\
                           cols=25,titlerows=0,titlecols=0,roworigin=-1,\
                           colorigin=0,selectmode='none',\
                           rowstretch='none',colstretch='all',\
                           variable=self.tvariable,drawmode='slow',\
                           state='disabled',colwidth=2,\
                           foreground="grey",background="black",\
                           borderwidth=0,highlightbackground="black")
        self.table.pack(side=LEFT,expand=1,fill='both')
        self.table.tag_configure("heading",background="black",\
                                 foreground="yellow")
        self.table.tag_configure("sel",background="black",\
                                 foreground="grey")
        for i in range(25):
            self.table.tag_cell("heading","-1,%i"%i)

        self.fret_filter = Entry(self.window)
        self.fret_filter.grid(row=3,column=0,columnspan=3,sticky=E+W+N)
        self.fret_filter.insert(END,"(x+4)%12 in [0,2,4,5,7,9,11]")

        self.additional_stuff = Entry(self.window)
        self.additional_stuff.grid(row=3,column=3,sticky=E+W)

        self.chordlet = input

        def left_click(x,s=self):
            row,col = map(lambda k:int(k),\
                          s.table.index("@%i,%i"%(x.x,x.y)).split(","))
            s.chordlet.frets[self.nfrets-row-1] = col
            s.chordlet.update_from_frets()
            s.update_table()

        def right_click(x,s=self):
            row,col = map(lambda k:int(k),\
                          s.table.index("@%i,%i"%(x.x,x.y)).split(","))
            s.chordlet.frets[self.nfrets-row-1] = None
            s.chordlet.update_from_frets()
            s.update_table()

        self.table.bind("<Button-1>",left_click)
        self.table.bind("<Button-3>",right_click)

        self.stylevar = StringVar()
        self.stylevar.set(" ")
        if self.chordlet.style:
            self.stylevar.set(self.chordlet.style)

        def do_update(x=None,s=self):
            s.update_table()

        clm = 0
        for n,v in [("palm mute","."),("legato","l"),\
                    ("normal"," "),("squeal","s")]:
            rbtn = Radiobutton(self.window,text=n,value=v,\
                               variable = self.stylevar,\
                               command = do_update)
            rbtn.grid(row=1,column=clm)
            clm += 1

        self.window.bind("<F5>",do_update)

        def done(x=None,s=self):
            s.window.destroy()

        self.copy_entry = Entry(self.window)
        self.copy_entry.grid(row=2,column=0,columnspan=3,sticky=E+W+N)

        def to_clipboard(x=None,s=self):
            data = s.copy_entry.get()+"\n"
            os.popen('xclip','wb').write(data)

        self.copy_btn = Button(self.window,text="→ clipboard",\
                               command=to_clipboard)

        self.copy_btn.grid(row=2,column=3,sticky=E+W)


        self.window.bind("<Return>",done)
        self.window.bind("<Escape>",done)
        self.window.bind("<KP_Enter>",done)        
            
        self.update_table()
        self.window.wait_window(self.window)
        self.chordlet.style = self.stylevar.get().strip()
        return self.chordlet


if __name__ == "__main__":
    root = Tk()
    root.withdraw()
    c = Chordlet("-2 4 4.")
    e = ChordletEditor(root)
    c = e.edit_chordlet(c)
    print("c=",c)
