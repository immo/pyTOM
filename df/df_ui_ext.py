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
#  Here, we use Tkinter and Pmw (Python Mega Widgets) 1.3,
#  and tkinter-tree (see Tree.py for license & copyright information)
#

from Tix import *
from df_external import *
from df_data_channels import *
from df_visual_concept_editor import *
from df_ui_waitwindow import *
import Pmw
import tkMessageBox
import df_snippets
from df_xml_thing import *

def initialize_ext_control(nb_page):
    g = DfGlobal()
    frame = Frame(nb_page)
    frame.pack(fill=BOTH,expand=1)
    bframep = LabelFrame(frame,label="Actions...")
    bframep.pack(side=TOP,fill=X)
    bframe = bframep.frame

    lframe = Frame(frame)
    lframe.pack(side=BOTTOM,fill=BOTH,expand=1)

    songsframe = LabelFrame(lframe,label="Songs")
    songsframe.pack(side=LEFT,fill=BOTH,expand=1)
    songsframe = songsframe.frame

    songslist = Pmw.ScrolledListBox(songsframe)
    songslist.pack(fill=BOTH,expand=1)

    grammarsframe = LabelFrame(lframe,label="Grammars")
    grammarsframe.pack(side=LEFT,fill=BOTH,expand=1)
    grammarsframe = grammarsframe.frame

    grammarslist = Pmw.ScrolledListBox(grammarsframe)
    grammarslist.pack(fill=BOTH,expand=1)
    
    scriptsframe = LabelFrame(lframe,label="Scripts")
    scriptsframe.pack(side=RIGHT,fill=BOTH,expand=1)
    scriptsframe = scriptsframe.frame

    scriptslist = Pmw.ScrolledListBox(scriptsframe)
    scriptslist.pack(fill=BOTH,expand=1)


    thingsframe = LabelFrame(lframe,label="Things")
    thingsframe.pack(side=RIGHT,fill=BOTH,expand=1)
    thingsframe = thingsframe.frame

    thingslist = Pmw.ScrolledListBox(thingsframe)
    thingslist.pack(fill=BOTH,expand=1)

    g["ext.ui.selected"] = None
    g["ext.ui.type"] = None

    def select_thing(ev=None):
        songslist._listbox.selection_clear(0,END)
        grammarslist._listbox.selection_clear(0,END)
        scriptslist._listbox.selection_clear(0,END)
        g["ext.ui.selected"] = thingslist._listbox.get(\
            thingslist._listbox.curselection())
        g["ext.ui.type"] = "thing"

    def select_song(ev=None):
        thingslist._listbox.selection_clear(0,END)
        grammarslist._listbox.selection_clear(0,END)
        scriptslist._listbox.selection_clear(0,END)        
        g["ext.ui.selected"] = songslist._listbox.get(\
            songslist._listbox.curselection())
        g["ext.ui.type"] = "song"

    def select_grammar(ev=None):
        thingslist._listbox.selection_clear(0,END)
        songslist._listbox.selection_clear(0,END)
        scriptslist._listbox.selection_clear(0,END)        
        g["ext.ui.selected"] = grammarslist._listbox.get(\
            grammarslist._listbox.curselection())
        g["ext.ui.type"] = "grammar"

    def select_script(ev=None):
        thingslist._listbox.selection_clear(0,END)
        songslist._listbox.selection_clear(0,END)
        grammarslist._listbox.selection_clear(0,END)        
        g["ext.ui.selected"] = scriptslist._listbox.get(\
            scriptslist._listbox.curselection())
        g["ext.ui.type"] = "script"        
        
    songslist._listbox.bind("<<ListboxSelect>>",select_song)
    songslist._listbox.configure(exportselection=0)

    thingslist._listbox.bind("<<ListboxSelect>>",select_thing)
    thingslist._listbox.configure(exportselection=0)

    grammarslist._listbox.bind("<<ListboxSelect>>",select_grammar)
    grammarslist._listbox.configure(exportselection=0)

    scriptslist._listbox.bind("<<ListboxSelect>>",select_script)
    scriptslist._listbox.configure(exportselection=0)

    

    def doUpdateLists():
        songslist._listbox.delete(0,END)
        songs = g('ext.songs',[])[:]
        songs.sort()
        for song in songs:
            songslist._listbox.insert(END,song)
            
        thingslist._listbox.delete(0,END)
        things = g('ext.things',[])[:]
        things.sort()
        for thing in things:
            thingslist._listbox.insert(END,thing)

        grammarslist._listbox.delete(0,END)
        grammars = g('ext.grammars',[])[:]
        grammars.sort()
        for grammar in grammars:
            grammarslist._listbox.insert(END,grammar)

        scriptslist._listbox.delete(0,END)
        scripts = g('ext.scripts',[])[:]
        scripts.sort()
        for script in scripts:
            scriptslist._listbox.insert(END,script)
            
        g["ext.ui.selected"] = None
        g["ext.ui.type"] = None
            

    def doReload():
        send_line("PYTHON",'reload_external_data()')

    button = Button(bframe,text="Reload from disk...",command=doReload)
    button.pack(side=RIGHT)

    def doEmacs():
        if g["ext.ui.selected"]:
            if g["ext.ui.selected"] in g["ext.files"]:
                os.system("emacs.sh "+g["ext.files"][g["ext.ui.selected"]])
            else:
                tkMessageBox.showinfo(title="emacs.sh",message="The selected object does not stem from an ext file, thus cannot be edited with emacs.")

    button = Button(bframe,text="emacs.sh",command=doEmacs)
    button.pack(side=LEFT)

    def doStart():
        if g["ext.ui.selected"]:
            if g["ext.ui.type"] == "script":
                send_line("PYTHON","CALL("+repr(g["ext.ui.selected"])+")")
            elif g["ext.ui.type"] == "song":
                send_line("PYTHON",\
                          "PLAYEXT("+repr(g["ext.ui.selected"])+")")
                send_line("PYTHON","DfGlobal()['mind'].quick_change()")

    
                

    button = Button(bframe,text="start!",command=doStart)
    button.pack(side=LEFT)

    def doEdit():
        if g["ext.ui.selected"]:
            if g["ext.ui.type"] == "thing":
                send_line("bounce_ext",g["ext.ui.selected"])                
        
    def doEditBounce(representation):
        if g["ext.ui.type"] == "thing":
            extname = g["ext.ui.selected"]
            xml_rep = eval(representation)
            things = xml_to_things(xml_rep)
            ed = create_visual_editor(g["root.window"],\
                                      g["ext.ui.selected"] +\
                                      u" — ThingsEditor",\
                                      things,\
                                      g["edit.length"],\
                                      int(g["edit.length"]*g["edit.factor"]))
            wait_window(ed['window'])
            if not ed['ignore-changes']:
                doc = things_to_xml(things)
                if doc != xml_rep:
                    send_line("PYTHON","DfGlobal()['ext']["+repr(extname)+\
                              "]="+repr(doc))
                    send_line("PYTHON","DfGlobal()['things']["+repr(extname)+\
                              "]=xml_to_things(DfGlobal()['ext']["+\
                              repr(extname)+"])")
                    send_line("PYTHON","DfGlobal()['ext.changed'].append("+\
                              repr(extname)+")")

    def doSetEditorParameters(evt=None):
        property_dialog([("length = ","edit.length"),("pix per beat =","edit.factor")],\
                        types={'edit.length':float,'edit.factor':float},values=g,\
                        parent=g["root.window"],title="Thing editor properties...")


    g["edit.length"] = 64.0
    g["edit.factor"] = 128.0

    add_data_channel_handler("bounce_ext",doEditBounce)

    button = Button(bframe,text="edit",command=doEdit)
    button.pack(side=LEFT)
    button.bind("<Button-3>",doSetEditorParameters)

    def reloadSnippets(evt=None):
        reload(df_snippets).set_default_snippets()
        send_line("PYTHON","reload(df_snippets).set_default_snippets()")

    button = Button(bframe,text="reload snippets",command=reloadSnippets)
    button.pack(side=RIGHT)


    def openXTerm(evt=None):
        cmd = "xterm -e 'cd "+os.path.join(os.path.dirname(g["autosave_path"]),\
                                           "ext")+ " && bash'&"
        os.system(cmd)

    button = Button(bframe,text="bash",command=openXTerm)
    button.pack(side=RIGHT)

    def reloadAndPlayNewBeats(evt=None):
        doReload()
        send_line("PYTHON","PLAYEXT('new_beats')")
        send_line("PYTHON","DfGlobal()['mind'].quick_change()")

    button = Button(bframe,text="reload & play new_beats",command=reloadAndPlayNewBeats)
    button.pack(side=RIGHT)
        
    


    g['update-ext-lists'] = doUpdateLists

    program =\
r"""def new_reload_data_hook(old_hook=
         DfGlobal()('reload-external-data-hook',lambda:0)):
        old_hook()
        send_global_key("ext.songs")
        send_global_key("ext.things")
        send_global_key("ext.grammars")
        send_global_key("ext.files")
        send_global_key("ext.scripts")
        send_exec("DfGlobal()['update-ext-lists']()")
DfGlobal()['reload-external-data-hook'] = new_reload_data_hook"""

    send_lines("PYTHONBOUNCE",repr(program))
    

