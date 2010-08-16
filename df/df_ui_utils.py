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

def edit_graph_hom():
    g = DfGlobal()
    try:
        domain = eval(g["utils.g.domain"].get())
    except:
        domain = MkGraph(1,"@red 00")
    try:
        codomain = eval(g["utils.g.codomain"].get())
    except:
        codomain = PotentialGraph()
    try:
        colormap = eval(g["utils.g.colormap"].get())
    except:
        colormap = {}
    try:
        vertexmap = eval(g["utils.g.vertexmap"].get())
    except:
        vertexmap = {}
    try:
        vertexpos = eval(g["utils.g.vertexpos"].get())
    except:
        vertexpos = {}
    ghom = CoDiMuGraphHomEditor(domain, codomain, colormap, vertexmap, vertexpos)
    ghom.edit(g["root.window"])
    g["utils.g.vertexmap"].delete(0,END)
    g["utils.g.vertexmap"].insert(0, repr(ghom.vertexMap))
    g["utils.g.colormap"].delete(0,END)
    g["utils.g.colormap"].insert(0, repr(ghom.colorMap))
    g["utils.g.behaviour"].delete(0,END)
    g["utils.g.behaviour"].insert(0, str(ghom.behaviour))    
    g["utils.g.vertexpos"].delete(0,END)
    g["utils.g.vertexpos"].insert(0, str(ghom.vertexPos))      
    frontend_command("DfGlobal()['utils.g.vertexmap'] = "+repr(repr(ghom.vertexMap)))
    frontend_command("DfGlobal()['utils.g.colormap'] = "+repr(str(ghom.colorMap)))
    frontend_command("DfGlobal()['utils.g.behaviour'] = "+repr(repr(ghom.behaviour)))
    frontend_command("DfGlobal()['utils.g.vertexpos'] = "+repr(repr(ghom.vertexPos)))
    frontend_command("DfGlobal()['utils.g.domain'] = "+repr(repr(domain)))
    frontend_command("DfGlobal()['utils.g.codomain'] = "+repr(repr(codomain)))    
    
def edit_local_composition():
    g = DfGlobal()
    try:
        domain = eval(g["utils.lc.domain"].get())
    except:
        domain = MkGraph(1,"@red 00")
    try: 
        codomains = eval(g["utils.lc.codomains"].get())
    except:
        codomains = None
    try:
        cmap = eval(g["utils.lc.colmaps"].get())
    except:
        cmap = None
    try:
        vpos = eval(g["utils.lc.vtxpos"].get())
    except:
        vpos = None
    try:
        vmap = eval(g["utils.lc.vtxmaps"].get())
    except:
        vmap = None        
    try:
        beh = eval(g["utils.lc.behaviours"].get())
    except:
        beh = None
    try:
        tags = eval(g["utils.lc.tags"].get())
    except:
        tags = None
    lceditor = LocalCompositionEditor(domain,vpos,codomains,vmap,cmap,beh,tags)
    lceditor.edit(g["root.window"])
    lst = ["utils.lc.domain","utils.lc.codomains","utils.lc.colmaps",\
           "utils.lc.vtxmaps","utils.lc.behaviours","utils.lc.tags",\
           "utils.lc.vtxpos"]
    for k in lst:
        g[k].delete(0,END)
    g["utils.lc.domain"].insert(0, repr(lceditor.domain))
    g["utils.lc.codomains"].insert(0, repr(lceditor.codomains)),
    g["utils.lc.colmaps"].insert(0,repr(lceditor.colorMaps))
    g["utils.lc.vtxmaps"].insert(0,repr(lceditor.vertexMaps))
    g["utils.lc.vtxpos"].insert(0,repr(lceditor.vertexPos))
    g["utils.lc.behaviours"].insert(0,str(lceditor.behaviours))
    g["utils.lc.tags"].insert(0, repr(lceditor.tags))
    for k in lst:
        frontend_command("DfGlobal()["+repr(k)+"] = "+repr(g[k].get()))

def initialize_ui_utils(nb_page):
    """initialize_ui_utils(nb_page)   create the contents of the utils tab in the main window"""
    g = DfGlobal()
    frame = Frame(nb_page)
    lframep = LabelFrame(frame,label="Graph-homomorphism helper tool")
    lframe = lframep.frame
    Label(lframe,text="Domain:",justify=LEFT,anchor="w").pack(side=TOP,fill=X,expand=1)
    g["utils.g.domain"] = Entry(lframe)
    g["utils.g.domain"].pack(side=TOP,fill=X,expand=1)
    Label(lframe,text="Co-Domain:",justify=LEFT,anchor="w").pack(side=TOP,fill=X,expand=1)
    g["utils.g.codomain"] = Entry(lframe)
    g["utils.g.codomain"].pack(side=TOP,fill=X,expand=1)
    Label(lframe,text="Color-map:",justify=LEFT,anchor="w").pack(side=TOP,fill=X,expand=1)
    g["utils.g.colormap"] = Entry(lframe)
    g["utils.g.colormap"].pack(side=TOP,fill=X,expand=1)
    Label(lframe,text="Vertex-map:",justify=LEFT,anchor="w").pack(side=TOP,fill=X,expand=1)
    g["utils.g.vertexmap"] = Entry(lframe)
    g["utils.g.vertexmap"].pack(side=TOP,fill=X,expand=1)
    Label(lframe,text="Vertex positions:",justify=LEFT,anchor="w").pack(side=TOP,fill=X,expand=1)
    g["utils.g.vertexpos"] = Entry(lframe)
    g["utils.g.vertexpos"].pack(side=TOP,fill=X,expand=1)
    Label(lframe,text="Behaviour:",justify=LEFT,anchor="w").pack(side=TOP,fill=X,expand=1)
    g["utils.g.behaviour"] = Entry(lframe)
    g["utils.g.behaviour"].pack(side=TOP,fill=X,expand=1)
    Button(lframe,text="Hom editor...",command=edit_graph_hom).pack\
          (side=TOP)
    lframep.pack(side=TOP,fill=X)
    
    lframep = LabelFrame(frame,label="Local composition editor tool")
    lframe = lframep.frame
    Label(lframe,text="Domain:",justify=LEFT,anchor="w").pack(side=TOP,fill=X,expand=1)
    g["utils.lc.domain"] = Entry(lframe)
    g["utils.lc.domain"].pack(side=TOP,fill=X,expand=1)
    Label(lframe,text="Vertex-Positions:",justify=LEFT,anchor="w").pack(side=TOP,fill=X,expand=1)
    g["utils.lc.vtxpos"] = Entry(lframe)
    g["utils.lc.vtxpos"].pack(side=TOP,fill=X,expand=1)     
    Label(lframe,text="Co-Domains:",justify=LEFT,anchor="w").pack(side=TOP,fill=X,expand=1)
    g["utils.lc.codomains"] = Entry(lframe)
    g["utils.lc.codomains"].pack(side=TOP,fill=X,expand=1)

    Label(lframe,text="Color-Maps:",justify=LEFT,anchor="w").pack(side=TOP,fill=X,expand=1)
    g["utils.lc.colmaps"] = Entry(lframe)
    g["utils.lc.colmaps"].pack(side=TOP,fill=X,expand=1)    
    Label(lframe,text="Vertex-Maps:",justify=LEFT,anchor="w").pack(side=TOP,fill=X,expand=1)
    g["utils.lc.vtxmaps"] = Entry(lframe)
    g["utils.lc.vtxmaps"].pack(side=TOP,fill=X,expand=1)        
    Label(lframe,text="Behaviours:",justify=LEFT,anchor="w").pack(side=TOP,fill=X,expand=1)
    g["utils.lc.behaviours"] = Entry(lframe)
    g["utils.lc.behaviours"].pack(side=TOP,fill=X,expand=1)            
    Label(lframe,text="Tags:",justify=LEFT,anchor="w").pack(side=TOP,fill=X,expand=1)
    g["utils.lc.tags"] = Entry(lframe)
    g["utils.lc.tags"].pack(side=TOP,fill=X,expand=1)                
    Button(lframe,text="Local composition editor...",command=edit_local_composition).pack\
          (side=TOP)
    lframep.pack(side=TOP,fill=X)
    frame.pack(side=TOP,fill=BOTH,expand=0)
    e_list = ["utils.g.domain","utils.g.codomain","utils.g.colormap","utils.g.vertexmap",\
              "utils.g.vertexpos","utils.g.behaviour","utils.lc.domain","utils.lc.codomains",\
            "utils.lc.colmaps","utils.lc.vtxmaps","utils.lc.behaviours","utils.lc.tags",\
            "utils.lc.vtxpos"]
    for entry in e_list:
        def fn_helper(r, entry=entry): 
            DfGlobal()[entry].delete(0,END)
            DfGlobal()[entry].insert(0, eval(r))
        add_data_channel_handler(entry, fn_helper)    
