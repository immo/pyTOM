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
from df_ui_codimugraphhom import *
from df_ui_control import frontend_command as frontend_command
from df_ui_localcomposition import *
from df_database import *
from df_data_channels import *
from df_ui_waitwindow import *
import tkFileDialog
import copy
import re

def update_filter_lists():
    db = CompositionDatabase()
    g = DfGlobal()
    filters =  ['names','versions','songs','riffs']
    for k in filters:
        list = g["db."+k+".list"]
        list.delete(0,END)
        items = map(lambda x: repr(x), filter(lambda x: db.data[k][x],\
                                              db.data[k].keys()))
        items.sort()
        list.insert(END,*items)

def db_do_filter():
    g = DfGlobal()
    nf_list = map(lambda x: eval(g["db.names.list"].get(x)),\
                  g["db.names.list"].curselection())
    if g["db.names.invert"].get():
        names_filter = lambda x: not x in nf_list
    else:
        names_filter = lambda x: x in nf_list
        
    sg_list = map(lambda x: eval(g["db.songs.list"].get(x)),\
                  g["db.songs.list"].curselection())
    if g["db.songs.invert"].get():
        songs_filter = lambda x: not x in sg_list
    else:
        songs_filter = lambda x: x in sg_list
        
    rf_list = map(lambda x: eval(g["db.riffs.list"].get(x)),\
                  g["db.riffs.list"].curselection())
    if g["db.riffs.invert"].get():
        riffs_filter = lambda x: not x in rf_list
    else:
        riffs_filter = lambda x: x in rf_list
        
    vr_list = map(lambda x: eval(g["db.versions.list"].get(x)),\
                  g["db.versions.list"].curselection())
    if g["db.versions.invert"].get():
        versions_filter = lambda x: not x in vr_list
    else:
        versions_filter = lambda x: x in vr_list        
        
    show_deleted = g["db.show.deleted"].get()
    results = filter_results(names_filter,versions_filter,songs_filter,\
                             riffs_filter,show_deleted)
    # results is a list with of (text, id) pairs
    # filter regexp's
    try:
        expression = g["db.results.regexp"].get()
    except KeyError:
        pass # too early for filtering regexps
    else:
        if expression:
            try:
                pat = re.compile(expression)
                filter_fn = lambda x: pat.match(x[0])!=None
            except:
                filter_fn = lambda x: True
            results = filter(filter_fn, results)
    
    list = g["db.results.list"] 
    g["db.results.list.ids"] = results
    list.delete(0, END)
    resulting_items = map(lambda x: x[0], results)
    if len(resulting_items)>0:
        list.insert(END, *resulting_items)
        
def change_keys_dlg(id):
    g = DfGlobal()
    db = CompositionDatabase()
    root = g["root.window"]
    win = Toplevel(root)
    win.title("Edit storage keys for composition "+str(id))
    
    name, version, song, riff, tags, created,\
          modified, deleted = db.getIdKeys(id)
    
    frame = LabelFrame(win,label="Name")
    n = StringVar()
    e = Entry(frame.frame,width=100,textvariable=n)
    e.pack(side=TOP,fill=X,expand=1)
    frame.pack(side=TOP,fill=X,expand=1)
    
    
    frame = LabelFrame(win,label="Song")
    s = StringVar()
    e = Entry(frame.frame,width=100,textvariable=s)
    e.pack(side=TOP,fill=X,expand=1)
    frame.pack(side=TOP,fill=X,expand=1)    
    
    frame = LabelFrame(win,label="Riff")
    r = StringVar()
    e = Entry(frame.frame,width=100,textvariable=r)
    e.pack(side=TOP,fill=X,expand=1)
    frame.pack(side=TOP,fill=X,expand=1)        
    
    frame = LabelFrame(win,label="Version")
    v = StringVar()
    e = Entry(frame.frame,width=100,textvariable=v)
    e.pack(side=TOP,fill=X,expand=1)
    frame.pack(side=TOP,fill=X,expand=1)
    
    frame = LabelFrame(win,label="Tags")
    t = StringVar()
    e = Entry(frame.frame,width=100,textvariable=t)
    e.pack(side=TOP,fill=X,expand=1)
    frame.pack(side=TOP,fill=X,expand=1)            
    
    win.bind("<Escape>",lambda x: win.destroy())
    win.bind("<Return>",lambda x: win.destroy())    
    
    n.set( str(name))
    v.set(repr(version))
    s.set( str(song))
    r.set( str(riff))
    t.set(repr(tags))
    DfGlobal()["root.window"].update()
    x = win.winfo_screenwidth()/2
    y = win.winfo_screenwidth()/2    
    size = [win.winfo_width(), win.winfo_height()] # not working :(
        #new_geo = "+"+str(x-int(size[0])/2)+"+"+str(y-int(size[1])/2)
    new_geo = "+"+str(max(0,x-int(size[0])/2))+"+"+str(max(0,y-int(size[1])/2))
    win.wm_geometry(new_geo)
    wait_window(win)
    
    name = n.get()
    version = eval(v.get())
    song = s.get()
    riff = r.get()
    tags = eval(t.get())
    
    modified = datetime.datetime.now().strftime("%Y-%m-%d %H.%M:%S")
    db.delCurrentKeys(id)
    db.addIdKeys(id,name, version, song, riff, tags, created, modified, deleted)
    db.setTags(id,tags)
    
    
def update_item_nr(id):
    db = CompositionDatabase()
    composition = db.getComposition(id)
    db.setComposition(id, composition) # send copy to backend
    db.setModified(id, datetime.datetime.now().strftime("%Y-%m-%d %H.%M:%S"))
    # set modification date
    #print "Updated ",id

def initialize_ui_database(nb_page):
    """initialize_ui_database(nb_page)   create the contents of the utils tab in the main window"""
    def updateDB():
        update_filter_lists()
        db_do_filter()
    CompositionDatabase().setSendChanges()
    CompositionDatabase().globals["PartialLocalComposition"] \
                                                = LocalCompositionEditor
        
    db_ui_install_callbacks()
    g = DfGlobal()
    tframe = Frame(nb_page)
    fframep = LabelFrame(nb_page,label="Filter")
    fframe = fframep.frame
    cframep = LabelFrame(tframe,\
               label="Name / Song / Riff / Version / Last Modified / Id / Tags")
    cframe = cframep.frame
    btnframep = LabelFrame(tframe,label="Actions")
    btnframe = btnframep.frame

    Button(btnframe,text="Filter (C-f)",command=db_do_filter)\
                                 .pack(side=TOP,expand=0,anchor="n",fill=X)
    Frame(btnframe,height=5).pack(side=TOP,fill=X)

    def edit_sel():
        db = CompositionDatabase()
        list = g["db.results.list"]
        sel = list.curselection()
        idlist = g["db.results.list.ids"]
        for k in sel:
            id = idlist[int(k)][1]
            lcedit = db.getComposition(id)
            fn_helper = lambda id=id: update_item_nr(id)
            lcedit.update_callback = fn_helper
            lcedit.edit(g["root.window"],add_title=idlist[int(k)][0])
            db.setComposition(id, lcedit)
            db.setModified(id, datetime.datetime.now()\
                           .strftime("%Y-%m-%d %H.%M:%S"))
            
            
    Button(btnframe,text="Edit... (C-e)",command=edit_sel)\
                                  .pack(side=TOP,expand=0,anchor="n",fill=X)
    
    def edit_as_string():
        db = CompositionDatabase()
        list = g["db.results.list"]
        sel = list.curselection()
        idlist = g["db.results.list.ids"]
        for k in sel:
            id = idlist[int(k)][1]
            lcedit = db.getComposition(id)
            fn_helper = lambda id=id: update_item_nr(id)
            win = Toplevel(g["root.window"])
            win.title("Edit composition " + str(id) + " - " + idlist[int(k)][0])
            txt = Text(win, width=80,height=24)
            txt.insert(END, repr(lcedit))
            txt.pack()
            text = {"":"   !!ERROR    "}
            
            def del_win():
                text[""] = txt.get(1.0,END)
                win.destroy()
                
            win.protocol("WM_DELETE_WINDOW",del_win)
            wait_window(win)

            lcedit = eval(text[""])

            db.setComposition(id, lcedit)
            db.setModified(id, datetime.datetime.now()\
                           .strftime("%Y-%m-%d %H.%M:%S"))        
    
    Button(btnframe,text="Edit as string",command=edit_as_string)\
                               .pack(side=TOP,expand=0,anchor="n",fill=X)    
    
    def play_command():
        db = CompositionDatabase()
        list = g["db.results.list"]
        sel = list.curselection()
        idlist = g["db.results.list.ids"]
        for k in sel:
            id = idlist[int(k)][1]
            lcedit = db.getComposition(id)
            lcedit.play_command()
    
    Button(btnframe,text="Preview (C-y)",command=play_command)\
                                  .pack(side=TOP,expand=0,anchor="n",fill=X)    
    
    def stop_command():
        frontend_command("DfGlobal()['concept.list'] = []\n"+\
                         "DfGlobal()['mind'].switchJamMode(False)\n"+\
                         "DfGlobal()['mind'].quick_change()")
    
    Button(btnframe,text="Stop (C-x)",command=stop_command)\
                               .pack(side=TOP,expand=0,anchor="n",fill=X)    
    g["root.window"].bind("<Control-y>",lambda x:play_command())
    g["root.window"].bind("<Control-e>",lambda x:edit_sel())
    g["root.window"].bind("<Control-f>",lambda x:db_do_filter())    
    g["root.window"].bind("<Control-x>",lambda x:stop_command())    
    Frame(btnframe,height=5).pack(side=TOP,fill=X)

    def rename_duplicates():
        db = CompositionDatabase()
        list = g["db.results.list"]
        sel = list.curselection()
        idlist = g["db.results.list.ids"]
        name_list = {}
        for k in sel:
            id = idlist[int(k)][1]
            keys = (db.getIdKeys(id))
            riff = keys[3].strip()
            name_list.setdefault(riff,[]).append(id)
        for name in name_list.keys()[:]:
            ids = name_list[name]
            if len(ids) > 1:
                idx = name.rfind(".")
                if idx >= 0:
                    lpart = name[0:idx]+"."
                else:
                    lpart = name+"."
                rpart = 1
                
                for rename_id in ids[1:]:
                    while lpart+str(rpart) in name_list:
                        rpart += 1
                    name_list[lpart+str(rpart)] = [rename_id]

                    keys = (db.getIdKeys(id))
                    db.delCurrentKeys(rename_id)
                    db.addIdKeys(rename_id, keys[0], keys[1], keys[2], \
                                 lpart+str(rpart), keys[4], keys[5], keys[6],\
                                 keys[7])
                        
                

    Button(btnframe,text="Rename ambigous riffs", command=rename_duplicates)\
                                 .pack(side=TOP,expand=0,anchor="n",fill=X)
    
    Frame(btnframe,height=5).pack(side=TOP,fill=X)
    
    
    def mk_new():
        id = CompositionDatabase().createNewLocalComposition()
        change_keys_dlg(id)
        update_filter_lists()
    
    Button(btnframe,text="New... (C-n)",command=mk_new)\
                                 .pack(side=TOP,expand=0,anchor="n",fill=X)    
    g["root.window"].bind("<Control-n>",lambda x:mk_new())    
    
    def rename_sel():
        list = g["db.results.list"]
        sel = list.curselection()
        idlist = g["db.results.list.ids"]
        for k in sel:
            id = idlist[int(k)][1]
            change_keys_dlg(id)    
        update_filter_lists()            
            
    Button(btnframe,text="Rename...",command=rename_sel).\
           pack(side=TOP,expand=0,anchor="n",fill=X)
        
    def copy_sel():
        db = CompositionDatabase()        
        list = g["db.results.list"]
        sel = list.curselection()
        idlist = g["db.results.list.ids"]
        for k in sel:
            id = idlist[int(k)][1]
            name, version, song, riff, tags, created,\
                  modified, deleted = db.getIdKeys(id)
            tags = copy.copy(tags)
            name = copy.copy(name)
            version = copy.copy(version)
            riff = copy.copy(riff)
            
            if 'copy' in tags:
                tags['copy'] += 1
            else:
                tags['copy'] = 1
            id2 = db.createNewLocalComposition(name,version,song,riff,tags)
            db.setComposition(id2,eval( repr( db.getComposition(id) ) ) )
            change_keys_dlg(id2)
        update_filter_lists()
        
    Button(btnframe,text="Copy... (C-k)",command=copy_sel)\
                                  .pack(side=TOP,expand=0,anchor="n",fill=X)    
    g["root.window"].bind("<Control-k>",lambda x:copy_sel())

    def special_copy():
        res_list = g["db.results.list"]
        selctd = res_list.curselection()
        idlist = g["db.results.list.ids"]
        cpyids = [idlist[int(k)][1] for k in selctd]

        
        sel_window = Toplevel(g["root.window"])
        sel_window.title("Special copy...")
        
        seltor = Frame(sel_window)
        seltor.pack(side=TOP,fill=BOTH)

        pattern = LabelFrame(sel_window,label="Special copy action...")        
        
        regframe = Frame(seltor)
        reg_entry = Entry(regframe)
        reg_entry.pack(side=LEFT,fill=X,expand=1)

        listframe = Frame(seltor)

        sel_list = Listbox(listframe,exportselection=1,selectmode=SINGLE,\
                           width=100,height=20)
        sel_list.pack(side=LEFT,anchor="e",expand=1,fill=BOTH)
        sbar = Scrollbar(listframe)
        sbar.pack(side=RIGHT,anchor="w",expand=0,fill=Y)
        sbar.config(command=sel_list.yview)
        sel_list.config(yscrollcommand=sbar.set)

        seldata = {0: [], 1: {}, 2: None}

        def upd_list():
            sel_list.delete(0,END)
            items = map(lambda x: x[0], seldata[0])
            sel_list.insert(END,*items)

        def upd_selection(evt):
            sel = sel_list.curselection()
            
            if sel:
                seldata[2] = seldata[0][int(sel[0])][1]
            else:
                seldata[2] = None
            if seldata[2]:
                db = CompositionDatabase()
                c = db.getComposition(seldata[2])
                # delete widgets: pack_forget(), destroy(), =None
                for cod in seldata[1]:
                    (frm,lbl,overwrite,keepundefined,ovrwrt,\
                     kpundef) = seldata[1][cod]
                    frm.pack_forget()
                    lbl.pack_forget()
                    ovrwrt.pack_forget()
                    kpundef.pack_forget()
                    ovrwrt.destroy()
                    kpundef.destroy()
                    lbl.destroy()
                    frm.destroy()
                    
                seldata[1].clear()
                
                for cod in c.codomains:
                    frm = Frame(pattern)
                    try:
                        info = " : " + str(c.behaviours[cod])
                    except KeyError:
                        info = " : ?"
                        
                    overwrite = IntVar()
                    keepundefined = IntVar()
                    kpundef = Checkbutton(frm,text="keep undefined",\
                                          variable=keepundefined)
                    kpundef.pack(side=LEFT)
                    ovrwrt = Checkbutton(frm,text="overwrite",\
                                         variable=overwrite)
                    ovrwrt.pack(side=LEFT)
                    
                    lbl = Label(frm,text=str(cod)+info,justify=LEFT, anchor=W)
                    lbl.pack(side=LEFT,expand=1,fill=X)

                    frm.pack(side=TOP,expand=1,fill=X)
                    seldata[1][cod] = (frm,lbl,overwrite,keepundefined,ovrwrt,\
                                       kpundef)

        sel_list.bind("<<ListboxSelect>>",upd_selection)

        def reg_filter():
            db = CompositionDatabase()
            reg_string = reg_entry.get()
            if reg_string:
                try:
                    pat = re.compile(reg_string)
                    filter_fn = lambda x: pat.match(x[0])!=None
                except:
                    filter_fn = lambda x: True
            else:
                filter_fn = lambda x: True
            id_list = db.getNonDeletedList()
            id_texts = [" / ".join([str(x) for x in db.getIdKeysAlt(id)]) \
                        for id in id_list]
            zipped = zip(id_texts,id_list)
            zipped.sort()
            seldata[0] = filter(filter_fn, zipped)
            upd_list()


        reg_btn = Button(regframe,text="Filter", command=reg_filter)
        reg_btn.pack(side=RIGHT)
        sel_window.bind("<Return>",lambda x:reg_filter())
        regframe.pack(side=TOP,fill=X,expand=1)
        listframe.pack(side=TOP,fill=BOTH,expand=1)

        pattern.pack(side=TOP,fill=X)

        

        def do_it(createCopy=True):
            if not seldata[2]:
                sel_window.destroy()
                return
            if not createCopy:
                a =tkMessageBox.askquestion(title="Warning!",message=\
                                            "This will overwrite compositions"+\
                                         " and is currently not undo-able." +\
                                         " Continue?")
                if not (a == tkMessageBox.YES):
                    return
            stencil_id = seldata[2]
            db = CompositionDatabase()
            stencil = db.getComposition(stencil_id)
            for id in cpyids:
                name, version, song, riff, tags, created,\
                      modified, deleted = db.getIdKeys(id)
                tags = copy.copy(tags)
                name = copy.copy(name)
                version = copy.copy(version)
                riff = copy.copy(riff)

                if 'copy' in tags:
                    tags['copy'] += 1
                else:
                    tags['copy'] = 1

                if createCopy:
                    id2 = db.createNewLocalComposition(name,version,song,\
                                                       riff,tags)
                    composition = eval( repr( db.getComposition(id) ) )
                else:
                    id2 = id
                    composition = db.getComposition(id)
                
                for cod in seldata[1]:
                    packed = (seldata[1][cod])
                    overwrite = packed[2].get()
                    keepundefined = packed[3].get()
                    if overwrite and cod in composition.vertexMaps:
                        if keepundefined:
                            vm = composition.vertexMaps[cod]
                            for vtx in stencil.vertexMaps[cod]:
                                val = stencil.vertexMaps[cod][vtx]
                                if val:
                                    vm[vtx] = val
                            composition.arrows[cod].vertexMap = vm
                            composition.behaviours[cod] = \
                                       composition.arrows[cod].getBehaviour()
                        else:
                            composition.vertexMaps[cod] =stencil.vertexMaps[cod]
                            composition.behaviours[cod] =stencil.behaviours[cod]
                    
                db.setComposition(id2, eval(repr( composition )) )
                
            sel_window.destroy()

        bfrm = Frame(sel_window)

        Button(bfrm,text="Perform copy action...", command=do_it, width=50)\
                                        .pack(side=RIGHT,anchor="nw")

        Button(bfrm,text="Perform overwrite action...",\
               command=lambda:do_it(False))\
                                        .pack(side=LEFT,anchor="ne")

        bfrm.pack(side=BOTTOM,fill=X,expand=0)
        
        reg_filter()
        wait_window(sel_window)

    Button(btnframe,text="Special copy...",command=special_copy)\
                                  .pack(side=TOP,expand=0,anchor="n",fill=X)
        
    def delete_sel():
        db = CompositionDatabase()
        list = g["db.results.list"]
        sel = list.curselection()
        idlist = g["db.results.list.ids"]
        for k in sel:
            id = idlist[int(k)][1]
            name, version, song, riff, tags, created,\
                  modified, deleted = db.getIdKeys(id)
            db.delCurrentKeys(id)
            deleted = datetime.datetime.now().strftime("%Y-%m-%d %H.%M:%S")
            db.addIdKeys(id,name, version, song, riff, tags, created,\
                         modified, deleted)
        update_filter_lists()
        
        
    Button(btnframe,text="Delete (C-Del)",command=delete_sel)\
                                 .pack(side=TOP,expand=0,anchor="n",fill=X)    
    g["root.window"].bind("<Control-Delete>",lambda x:delete_sel())    
    
    Frame(btnframe,height=5).pack(side=TOP,fill=X)
    
    def save_state2():
        path = tkFileDialog.asksaveasfilename(\
                                      title="Save restore script to file...")
        if path:
            frontend_command("save_state("+repr(path)+")")

    Button(btnframe,text="Save as... (C-S-s)",command=save_state2)\
                               .pack(side=TOP,expand=0,anchor="n",fill=X)    
    g["root.window"].bind("<Control-Shift-S>",lambda x:save_state2())    

    
    g["db.show.deleted"] = IntVar()
    Checkbutton(fframe,text="include deleted compositions",\
                variable=g["db.show.deleted"]).pack(side=BOTTOM,anchor="w")

    g["db.results.regexp"] = Entry(cframe)
    g["db.results.regexp"].pack(side=TOP,anchor="ne",expand=0,fill=X)
    
    g["db.results.list"] = Listbox(cframe,exportselection=0,selectmode=EXTENDED)
    g["db.results.list"].pack(side=LEFT,anchor="w",expand=1,fill=BOTH)
    sbar = Scrollbar(cframe)
    sbar.pack(side=RIGHT,anchor="w",expand=0,fill=Y)
    sbar.config(command=g["db.results.list"].yview)
    g["db.results.list"].config(yscrollcommand=sbar.set)
    
    headings = {'names': "Name",\
            'versions': "Version",\
            'songs' : "Song",\
            'riffs' : "Riff"}
            
    hds = ['names','songs','riffs','versions']
    
    for k in hds:
        kframe = LabelFrame(fframe,label=headings[k])
        qframe = Frame(kframe)
        listbox = Listbox(qframe,selectmode=MULTIPLE,exportselection=0)
        g["db."+k+".list"] = listbox
        listbox.pack(side=LEFT,anchor="w",expand=1,fill=BOTH)
        sbar = Scrollbar(qframe)
        sbar.pack(side=LEFT,anchor="w",expand=0,fill=Y)
        sbar.config(command=listbox.yview)
        listbox.config(yscrollcommand=sbar.set)
        g["db."+k+".invert"] = IntVar()
        qframe.pack(side=TOP,fill=BOTH,expand=1)
        Checkbutton(kframe,text="invert selection",\
                    variable=g["db."+k+".invert"])\
                      .pack(side=BOTTOM,anchor="w",fill=X,expand=0)
        g["db."+k+".invert"].set(1)
        
        kframe.pack(side=LEFT,expand=1,fill=BOTH)
    
    fframep.pack(side=TOP,fill=BOTH,expand=1)
    cframep.pack(side=LEFT,fill=BOTH,expand=1)
    btnframep.pack(side=LEFT,fill=Y,expand=0,anchor="n")
    tframe.pack(side=TOP,fill=BOTH,expand=1)

    updateDB()
    g["updateDB"] = updateDB
    
def db_ui_install_callbacks():
    """install the ui-frontend-part-callbacks for the database"""
    def ex(x):
        exec(x)

    add_data_channel_handler("exec.db",ex)
