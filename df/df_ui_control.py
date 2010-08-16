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
from Tix import *
import tkFileDialog
import Pmw
import sys
import os
import errno
import subprocess
import tkMessageBox
from pysqlite2 import dbapi2 as sqlite
from df_global import *
from ScrollableMultiSelectTree import *
from math import *
from biquad_calculations import *
from df_ui_new_technology import *
from df_database import *
from df_property_dialog import *


def start_song_i(i):
      """start_song_i(i)    start to play legacy song nr. i"""
      frontend_command("play_legacy(legacy_data["+str(i)+"],now()+5)")

def backend_command(command=""):
   """backend_command(command="")   send command to the backend"""
   out = DfGlobal()["UI_O"]
   for commands in command.split("\n"):
        out.write("CONSOLE:"+str(commands)+"\n")
   out.flush()

def frontend_command(command=""):
   """frontend_command(command="")   send commands to the frontend"""
   out = DfGlobal()["UI_O"]
   for commands in command.split("\n"):
       out.write("PYTHON:"+str(commands)+"\n")
   out.flush()

def volume_dialog(data_repr):
    g = DfGlobal()
    data = eval(data_repr)
    types = {}
    vars = []
    sorted_keys = data.keys()[:]
    sorted_keys.sort()
    for i in sorted_keys:
        types[i] = float
        def chg_volume(x,i=i):
            frontend_command("set_instrument_volumes({"+repr(i)+":"\
                             +repr(x)+"})")
        vars.append((i + " = ",i,"dbScale",chg_volume))
    results = property_dialog(vars,types,data)
    frontend_command("set_instrument_volumes("+repr(results)+")")
    

def initialize_ui_legacy_control(nb_page):
   """initialize_ui_legacy_control(nb_page)   create the contents of the legacy tab in the main window"""
   def load_legacy_data():
      frontend_command("legacy_data = test_load()")

   Button(nb_page,text="Load legacy data...",command=load_legacy_data).pack(side=TOP)
   
   def set_legacy_generators():
       frontend_command("set_legacy_generators()")
   Button(nb_page, text="Set legacy generators...", command=set_legacy_generators).pack(side=TOP)

   def stop_playback_btn():
      frontend_command("play_legacy([])")

   Button(nb_page,text="Stop legacy playback",command=stop_playback_btn).pack(side=TOP)

   for i in range(7):
      cmd = eval("lambda : start_song_i("+str(i)+")")
      Button(nb_page,text="Start legacy song "+str(i+1),command=cmd).pack(side=TOP)
   
   def set_new_generators():
       frontend_command("set_innovative_generators()")
   Button(nb_page, text="Set innovative generators...", command=set_new_generators).pack(side=TOP)

def initialize_ui_control(nb_page):
    volbuttons = Frame(nb_page)

    def volume_button():
        frontend_command("send_line('volume-dialog',repr(get_instrument_volumes()))")

    Button(volbuttons,text="Set instrument volumes...",command=volume_button).pack(side=LEFT)

    for r in ["A","B","C","D"]:
        def save_preset(name=r):
            frontend_command("save_volume_preset("+repr(name)+")")
        def load_preset(name=r):
            frontend_command("load_volume_preset("+repr(name)+")")
        Button(volbuttons,text="Save "+r,command=save_preset).pack(side=LEFT,padx=5)
        Button(volbuttons,text="Load "+r,command=load_preset).pack(side=LEFT)        

    add_data_channel_handler('volume-dialog',volume_dialog)
    
    btns = Frame(nb_page)
    Button(btns,text="Quick Change",\
           command=lambda:frontend_command("DfGlobal()['mind'].quick_change()")\
           ).pack(side=RIGHT)
    Button(btns,text="Medium Change",\
           command=lambda:frontend_command(\
           "DfGlobal()['mind'].quick_change(rest=4.0)")\
           ).pack(side=RIGHT)
    Button(btns,text="Slow Change",\
           command=lambda:frontend_command(\
           "DfGlobal()['mind'].quick_change(rest=8.0)")\
           ).pack(side=RIGHT)
    Button(btns,text="Clear Mind",\
           command=lambda:frontend_command(\
           "DfGlobal()['concept.list'] = []" +\
           "\nDfGlobal()['mind'].quick_change()")\
           ).pack(side=RIGHT)
    Button(btns,text="Skip Next Part",\
           command=lambda:frontend_command(\
           "DfGlobal()['concept.list'] = DfGlobal()['concept.list'][1:]")\
           ).pack(side=RIGHT)
    def sketch_button():
        data = DfGlobal()["sketch"].get(1.0, END)
        frontend_command("DfGlobal()['last.sketch'] = "+ repr(data))
        frontend_command("DfGlobal()['concept.list'] = processSketchList(DfGlobal()['last.sketch'])")
        frontend_command("DfGlobal()['mind'].switchJamMode(False)")
                            
    Button(btns,text="Make Sketch Concept List",\
           command=sketch_button
           ).pack(side=RIGHT)
        
    def lc_db_button():
        db = CompositionDatabase()
        try:
            data = eval(DfGlobal()["dbf_list"].get())
        except:
            data = []
        frontend_command("DfGlobal()['last.dbf_list'] = "+repr(DfGlobal()["dbf_list"].get()))
        frontend_command("DfGlobal()['concept.list'] = reduce(lambda x,y: x + y, [[]] + "\
                       + "[ processSketchList(CompositionDatabase().getComposition(id).getDrumCode()) for id in "\
                       + repr(data) + "])")
        frontend_command("DfGlobal()['mind'].switchJamMode(False)") 
        
    
    Button(btns,text="Make LC-DB Concept List",\
         command = lc_db_button).pack(side=RIGHT)

    volbuttons.pack(side=TOP,fill=X,padx=5)
    btns.pack(side=TOP,fill=X,padx=5,pady=5)
    sktchp = LabelFrame(nb_page,label="Sketch")
    sktch = sktchp.frame
    
    sketch = Text(sktch, width=80)
    sketch.config(bg="black",foreground='yellow',font='Courier 12',\
                  insertbackground="white")
    scroller = Scrollbar(sktch,command=sketch.yview)
    sketch.config(yscrollcommand=scroller.set)
    scroller.pack(side=RIGHT, fill=Y)
    sketch.pack(side=RIGHT,fill='both', expand = 1, padx = 5, pady = 5)
    DfGlobal()["sketch"] = sketch
    sktchp.pack(side=TOP,fill=BOTH,padx=5,pady=5,expand=1)
    
    def set_sketch(line):
        sk = DfGlobal()["sketch"]
        sk.delete(1.0, END)
        sk.insert(END, eval(line))
        
    add_data_channel_handler("sketch",set_sketch)
    
    dbfp = LabelFrame(nb_page,label="From local composition database")
    dbf = dbfp.frame
    dbf_list = Entry(dbf,width=80,foreground="red",bg="black",\
                     insertbackground="white")
    dbf_list.pack(side=LEFT,fill=X,expand=1)
    
    DfGlobal()["dbf_list"] = dbf_list
    
    dbfp.pack(side=TOP,fill=BOTH,expand=0)
    
    def set_dbf_list(line):
        sk = DfGlobal()["dbf_list"]
        sk.delete(0, END)
        sk.insert(END, eval(line))
        
    add_data_channel_handler("dbf_list",set_dbf_list)
    
    
    
def initialize_ui_view(nb_page):
    g = DfGlobal()
    g["canvas"] = Canvas(nb_page, bg="black", width=200, height=100)
    
    g["objects"] = {}
    g["canvas_w"] = 200.0
    g["canvas_h"]= 100.0
    def canvas_resize(event):
        new_height = min(event.height, event.width / 2.0)
        new_width = new_height * 2.0
        event.widget.scale(ALL, 0, 0, float(new_width)/g["canvas_w"], \
                           float(new_height)/g["canvas_h"])
        g["canvas_w"] = float(new_width)
        g["canvas_h"] = float(new_height)
        g["canvas_reconfigure"]()
        
    g["canvas"].bind("<Configure>",  canvas_resize)
    initialize_new_technology_ui()
    g["canvas"].pack(fill=BOTH, expand=YES)
    
    
    
    
