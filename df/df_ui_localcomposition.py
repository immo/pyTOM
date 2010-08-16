4# coding: utf-8
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
from df_codimugraph import *
import tkMessageBox
from math import *
from df_ui_codimugraphhom import *
from df_localcomposition import *
from df_global import *
from df_ui_control import *
from PIL import Image, ImageTk
from df_edit_tools import *
from df_ui_waitwindow import *
import copy
import re

class LocalCompositionEditor(PartialLocalComposition):
    """class that assists in assigning colored directed multi-graph hom.s
    to get certain local composition behaviours
    """
    def __init__(self,domain,vertexPos=None,codomains=None,vertexMaps=None,\
                 colorMaps=None, behaviours=None, tags=None):
        """initialize the local composition editor
        domain     is a CoDiMuGraph that is the common domain of all arrows
        vertexPos  is an associative array giving override-positions for
                   the vertices of the domain (for display purposes)
        codomains  is an associative array of CoDiMuGraphs that contains 
                   all arrows codomains
        vertexMaps is an associative array that contains all vertex maps
        colorMaps  is an associative array that contains all color maps
        behaviours is an associative array that contains all graph behaviours
        tags       is an associative array that contains tags associated with
                   the composition
        """
        
        self.last_action = "(created)"
        self.entityName = "unnamed"
        arrows = {}
        self.update_callback = None
            
        PartialLocalComposition.__init__(self,domain,vertexPos,codomains,vertexMaps,\
                 colorMaps, behaviours, tags, arrows)
                
        for key in self.codomains:
            if key in self.colorMaps:
                cmap = self.colorMaps[key]
            else:
                cmap = None
            if key in self.vertexMaps:
                vmap = self.vertexMaps[key]
            else:
                vmap = None                
            arrows[key] = CoDiMuGraphHomEditor(domain,self.codomains[key],cmap,vmap,self.vertexPos)
            chg_callback = lambda key=key: self.updateGlobalVariables(key)
            arrows[key].set_change_callback(chg_callback)
            if key in self.behaviours:
                arrows[key].behaviour = self.behaviours[key]
            
        self.sorted_arrows = self.arrows.keys()
        self.sorted_arrows.sort()

        self.last_state = self.getStateTuple()
        
        self.check()
        
        
    def __repr__(self):
        return "LocalCompositionEditor(" + repr(self.domain) + "," \
                    + repr(self.vertexPos) + "," + repr(self.codomains) + ","\
                    + repr(self.vertexMaps) + "," + repr(self.colorMaps) +","\
                    + repr(self.behaviours) + "," + repr(self.tags) + ")"
                    
    def repr_as_composition(self):
        return "PartialLocalComposition("  + repr(self.domain) + ","\
                    + repr(self.vertexPos) + "," + repr(self.codomains) + ","\
                    + repr(self.vertexMaps) + "," + repr(self.colorMaps) +","\
                    + repr(self.behaviours) + "," + repr(self.tags) + ")"    
    
    def __hash__(self):
        return hash(repr(self))
    
    def edit(self, parent, add_title=None):
        """pop up editor for the CoDiMuGraphHom as child window of parent"""
        self.edit_again = 1
        while self.edit_again:
            self.edit_again = 0
            window = Toplevel(parent)
            self.window = window
            title = "Local composition editor tool"
            if add_title != None:
                title = add_title + " - " + title
                self.entityName = add_title
            window.title(title)
            self.add_title = add_title
            lframe = Frame(window)
            rsframe = Frame(window)
            toolsframe = Frame(window)
            aframep = LabelFrame(lframe,label="Arrows")
            aframe = aframep.frame
            tframep = LabelFrame(lframe,label="Tags")
            tframe = tframep.frame
            rframep = LabelFrame(rsframe,label="Report")
            rframe = rframep.frame
            dframep = LabelFrame(rsframe,label="Domain")
            dframe = dframep.frame

            prvframep = LabelFrame(toolsframe,label="Preview")

            prvframe = prvframep.frame

            self.behaviour_labels = {}

            sorted_arrows = self.arrows.keys()
            sorted_arrows.sort()

            shortcuts = ["<Control-F"+str(i)+">" for i in range(1,13)] + \
                        ["<Control-"+str(i)+">" for i in range(1,10)] + ["<Control-0>"]
            shortcut_names = ["(C-F"+str(i)+")" for i in range(1,13)] + \
                        ["(C-"+str(i)+")" for i in range(1,10)] + ["(C-0)"]
            counter = 0
            for key in sorted_arrows:
                arframe = Frame(aframe)
                Label(arframe,text=str(key) + "\t--> " + repr(self.arrows[key].codomain),\
                      anchor="w").pack(side=LEFT,fill=X,expand=1)
                fn_helper = lambda key=key:self.edit_hom(key)
                edlabel = "Edit"
                if counter < len(shortcuts):
                    edlabel += " " + shortcut_names[counter]
                    window.bind(shortcuts[counter],lambda x,key=key:self.edit_hom(key))
                btn = Button(arframe,text=edlabel,command=fn_helper)
                btn.pack(side=RIGHT)
                arframe.pack(side=TOP,fill=X,expand=1)                
                arframe = Frame(aframe)            
                behaviour = ""
                if key in self.behaviours:
                    behaviour = self.behaviours[key]
                self.behaviour_labels[key] = Label(arframe,text="\t"+behaviour,anchor="w")
                self.behaviour_labels[key].pack(side=TOP,fill=X,expand=1)
                arframe.pack(side=TOP,fill=X,expand=1)
                counter += 1

            Button(rframe,text="Refresh (F5)",\
                   command=lambda:self.readcheck()).pack(side=TOP) 
            window.bind("<F5>",lambda x:self.readcheck())            
            self.report = Text(rframe,width=60,height=25)
            self.report.pack(side=TOP,fill=BOTH,expand=1)        

            Button(tframe,text="(edit)",\
                   command=lambda:self.tag_editor()).pack(side=TOP,expand=0,anchor="ne")
            self.tag_entry = Text(tframe,width=50,height=5)
            self.tag_entry.pack(side=TOP,fill=BOTH,expand=1)

            self.domain_entry = Text(dframe,width=50,height=5)
            self.domain_entry.pack(side=TOP,fill=BOTH,expand=1)

            prv1frame = Frame(prvframe)

            Button(prv1frame,text="Play (C-y)",command=lambda: self.play_command())\
                                        .pack(side=LEFT,fill=X)
            Button(prv1frame,text="Stop (C-x)",command=lambda: self.stop_command())\
                                        .pack(side=LEFT,fill=X)
            window.bind("<Control-y>",lambda x:self.play_command())
            window.bind("<Control-x>",lambda x:self.stop_command())
            prv1frame.pack(side=TOP)



            Button(prvframe,text="LilyPond (F6)",command= lambda:self.lilypond())\
                                           .pack(side=TOP,fill=X,expand=0)
            Button(prvframe,text="LilyPond Code (F8)",command= lambda:self.lilycode())\
                                           .pack(side=TOP,fill=X,expand=0)
            window.bind("<F6>",lambda x:self.lilypond())
            window.bind("<F8>",lambda x:self.lilycode())        

            prvframep.pack(side=TOP,fill=X)

            dtframep = LabelFrame(toolsframe,label="Domain tools")
            dtframe = dtframep.frame
            Button(dtframe,text="Add thin compatible colored arrows",\
                   command=lambda: self.addThinCompatibleArrows()).pack(side=TOP,\
                                                                        fill=X,\
                                                                        expand = 0)
            Button(dtframe,text="Delete incompatible colored arrows",\
                   command=lambda: self.deleteIncompatibleArrows()).pack(side=TOP,\
                                                                        fill=X,\
                                                                        expand = 0)        

            dtframep.pack(side=TOP,fill=X)

            mtframep = LabelFrame(toolsframe,label="Mapping tools")
            mtframe = mtframep.frame

            Button(mtframe,text="Fill blanks with universal colors",\
                   command=lambda: self.fillUniversalColors()).pack(side=TOP,\
                                                                    fill=X,\
                                                                    expand=0)
            Button(mtframe,text="Fill blanks with wildcard vertices",\
                   command=lambda: self.fillWildcardVertices()).pack(side=TOP,\
                                                                     fill=X,\
                                                                     expand=0)

            Button(mtframe,text="Permutate vertex map",\
                   command=lambda: self.permutateVertexMap()).pack(side=TOP,\
                                                                    fill=X,\
                                                                    expand=0)

            mtframep.pack(side=TOP,fill=X)

            Button(toolsframe,text="Revert state/undo",\
                   command=lambda: self.undoDialog()).pack(side=BOTTOM,\
                                                           expand=0,\
                                                           anchor="se")

            aframep.pack(side=TOP,fill=BOTH,expand=1)
            
            tframep.pack(side=TOP,fill=BOTH,expand=1)
            lframe.pack(side=LEFT,fill=BOTH,expand=1)
            dframep.pack(side=TOP,fill=BOTH,expand=1)
            rframep.pack(side=TOP,fill=BOTH,expand=1)
            rsframe.pack(side=LEFT,fill=BOTH,expand=1)
            toolsframe.pack(side=LEFT,anchor="n",expand=0,fill=BOTH)

            self.write()
            self.update_report()

            window.protocol("WM_DELETE_WINDOW",lambda :self.do_destroy())
            window.bind("<Alt-Escape>",lambda x:self.do_destroy())

            wait_window(window)

    def tag_editor(self):
        self.readcheck()
        
        window = Toplevel(self.window)
        window.title('Tags - ' + self.entityName)

        keys = self.tags.keys()
        keys.sort()

        all_entries = []

        for k in keys:
            line = Frame(window)
            kentry = Entry(line,width=15)
            kentry.pack(side=LEFT)
            Label(line,text=": ").pack(side=LEFT)
            ventry = Entry(line,width=20)
            ventry.pack(side=LEFT,fill=X,expand=1)            
            line.pack(side=TOP,fill=X,expand=1)
            all_entries.append( (kentry,ventry) )
            kentry.delete(0,END)
            kentry.insert(END, repr(k))
            ventry.delete(0,END)
            ventry.insert(END, repr(self.tags[k]))

        for count in range(5):
            line = Frame(window)
            kentry = Entry(line,width=15)
            kentry.pack(side=LEFT)
            Label(line,text=": ").pack(side=LEFT)
            ventry = Entry(line,width=20)
            ventry.pack(side=LEFT,fill=X,expand=1)            
            line.pack(side=TOP,fill=X,expand=1)
            all_entries.append( (kentry,ventry) )

        new_tags = {}

        def do_destroy():
            for (kentry,ventry) in all_entries:
                k = kentry.get()
                v = ventry.get()
                if len(k):
                    try:
                        kvalue = eval(k)
                    except:
                        kvalue = str(k)
                    try:
                        vvalue = eval(v)
                    except:
                        vvalue = str(v)
                    new_tags[kvalue] = vvalue
                
            window.destroy()

        window.protocol("WM_DELETE_WINDOW", lambda: do_destroy())
        window.bind("<Escape>",lambda x:do_destroy())

        wait_window(window)

        self.tag_entry.delete(1.0,END)
        self.tag_entry.insert(END,repr(new_tags))
        self.readcheck()
        
        

    def permutateVertexMap(self):
        self.readcheck()

        self.write()
        self.last_action = "Permutate vertex map"
        self.readcheck()
        

    def fillUniversalColors(self):
        self.readcheck()
        for key in self.arrows:
            arrow = self.arrows[key]
            if arrow.windows_open:
                arrow.readcheck()
            changed = 0
            uni_color = arrow.codomain.getUniversalColors()
            if uni_color:
                universalcolor = uni_color[0]
                for clr in self.domain.color_set:
                    if not clr in arrow.colorMap:
                        arrow.colorMap[clr] = universalcolor
                        changed += 1
                    
            if changed:
                arrow.on_change()
                try:
                    arrow.write()
                except:
                    pass
                self.colorMaps[key] = arrow.colorMap
            
        self.write()
        self.last_action = "Fill blanks with universal colors"
        self.readcheck()

        self.on_change()

    def fillWildcardVertices(self):
        self.readcheck()
        for key in self.arrows:
            arrow = self.arrows[key]
            if arrow.windows_open:
                arrow.readcheck()
            changed = 0
            wildcard_verts = arrow.codomain.getWildcardVertices()
            if wildcard_verts:
                wildcard = wildcard_verts[0]
                for vtx in range(self.domain.vertices):
                    if not vtx in arrow.vertexMap:
                        arrow.vertexMap[vtx] = wildcard
                        changed += 1
                    
            if changed:
                arrow.on_change()
                try:
                    arrow.write()
                except:
                    pass
                self.vertexMaps[key] = arrow.vertexMap
        
        self.write()
        self.last_action = "Fill blanks with wildcard vertices"
        self.readcheck()

        self.on_change()

    def addThinCompatibleArrows(self):
        self.readcheck()
        new_domain = addColoredArrows(self.domain, self.arrows)
        self.domain = new_domain
        
        for key in self.arrows:
            self.arrows[key].domain = self.domain
            
        self.write()
        self.last_action = "Add thin compatible colored arrows"
        self.readcheck()

        self.on_change()

    def deleteIncompatibleArrows(self):
        self.readcheck()
        new_domain = delColoredArrows(self.domain, self.arrows)
        self.domain = new_domain

        for key in self.arrows:
            self.arrows[key].domain = self.domain
                
        self.write()
        self.last_action = "Delete incompatible colored arrows"
        self.readcheck()

        self.on_change()
        
    def readcheck(self):
        self.read()
        self.update_report()
        
    def do_destroy(self):
        self.read()
        for key in self.arrows:
            self.updateGlobalVariables(key)
        self.window.destroy()
    
    def update_report(self):
        self.check()
        try:
            self.report.delete(1.0,END)
            self.report.insert(END, self.report_text)
        except:
            pass
        
    def stop_command(self):
        self.readcheck()
        frontend_command("DfGlobal()['concept.list'] = []\n"+\
                         "DfGlobal()['mind'].switchJamMode(False)\n"+\
                         "DfGlobal()['mind'].quick_change()")

    def play_command(self):
        self.readcheck()
        frontend_command("DfGlobal()['concept.list'] = processSketchList("+\
                         repr(self.getDrumCode())+")\n"+\
                         "DfGlobal()['mind'].switchJamMode(False)\n"+\
                         "DfGlobal()['mind'].quick_change()")

    def lilycode(self):
        for l in self.arrows:
            arrow = self.arrows[l]
            if arrow.codomain.default_graph_name == "guitar_graph":
                lilyCode = gtr2LY(arrow.getBehaviour())
                tl = Toplevel(self.window)
                txt = Text(tl,width=80,height=24)
                txt.insert(END, lilyCode)
                txt.pack()
                tl.bind("<Escape>",lambda x:tl.destroy())
                tl.title("LilyPond-Code  --  "+self.window.title())
    
                

    def lilypond(self):
        for l in self.arrows:
            arrow = self.arrows[l]
            if arrow.codomain.default_graph_name == "guitar_graph":
                lilyCode = gtr2LY(arrow.getBehaviour())                
                pngName = compileWithLilyPond(lilyCode)
                try:
                    im = Image.open(pngName)
                    photo = ImageTk.PhotoImage(im)
                    tl = Toplevel(self.window)
                    lbl = Label(tl,image=photo)
                    lbl.image = photo
                    lbl.pack()
                    tl.bind("<Escape>",lambda x:tl.destroy())
                    tl.title("LilyPond  --  "+self.window.title())
                except IOError:
                    pass
                    
    
    
    def read(self):
        changed = 0
        try:
            dom = eval(self.domain_entry.get(1.0,END))
            if dom != self.domain:
                changed = 1
                self.domain = dom
                for key in self.arrows:
                    self.arrows[key].domain = dom
        except:
            pass
        try:
            tags = eval(self.tag_entry.get(1.0,END))
            if tags != self.tags:
                changed = 1
                self.tags = tags
        except:
            pass
        if changed:
            self.on_change()
    
    def on_change(self):
        new_state_tuple = self.getStateTuple()
        if new_state_tuple != self.last_state:
            description = self.entityName + " .: " + self.last_action \
                          + " :. " + \
                          datetime.datetime.now().strftime("%Y-%m-%d %H.%M:%S")
            self.last_state = new_state_tuple
            
            CompositionDatabase().addUndoInformation(AssociatedData\
                                                     (new_state_tuple,\
                                                      description))
            
            self.last_action = "(edit)"
        if self.update_callback:
            try:
                self.update_callback()
            except:
                pass
    
    def write(self):
        try:
            self.domain_entry.delete(1.0,END)
            self.domain_entry.insert(END, repr(self.domain))
        except:
            pass
        try:
            self.tag_entry.delete(1.0,END)
            self.tag_entry.insert(END,repr(self.tags))
        except:
            pass
    
    def updateGlobalVariables(self, key):
        """self.arrows[key] -> self.vertexMap , ... """
        self.vertexMaps[key] = self.arrows[key].vertexMap
        self.colorMaps[key] = self.arrows[key].colorMap
        self.behaviours[key] = self.arrows[key].behaviour
        if self.arrows[key].vertexPos != self.vertexPos:
            self.vertexPos = self.arrows[key].vertexPos
            for k in self.arrows:
                self.arrows[k].vertexPos = self.vertexPos
        try:
            self.behaviour_labels[key].configure(text="\t"+self.arrows[key].behaviour)
            self.behaviour_labels.update()
        except:
            pass
        
    def edit_hom(self, key):
        self.readcheck()
        add_t = ""
        add_t += "[" + str(key) + "]"
        if self.add_title != None:
            add_t += " " + self.add_title         
        self.arrows[key].callback = lambda self=self: self.on_change()
        self.arrows[key].edit(self.window,add_t)

        self.last_action = "[" + str(key) + "]"
        if self.arrows[key].behaviour:
            self.last_action += "   " + str(self.arrows[key].behaviour)
        
        
        self.updateGlobalVariables(key)
        self.update_report()

        self.on_change()
        
    def undoDialog(self):
        self.readcheck()

        dlg = Toplevel(self.window)
        if self.add_title:
            dlg.title("Revert state/undo - " + self.add_title)
        else:
            dlg.title("Revert state/undo")

        frmp = LabelFrame(dlg,label="Regexp filtered states")
        frm = frmp.frame

        regvar = StringVar()

        efrm = Frame(frm)

        entry = Entry(efrm, textvariable=regvar, width=110)
        entry.pack(side=LEFT,fill=X,expand=1)
        

        efrm.pack(side=TOP,fill=X,expand=0)

        lfrm = Frame(frm)
        lfrm2 = Frame(lfrm)
        lbox = Listbox(lfrm2, exportselection=0, height=50)
        lbox.pack(side=TOP,expand=1,fill=BOTH)
        lfrm2.pack(side=LEFT,expand=1,fill=BOTH)
        sbar = Scrollbar(lfrm)
        sbar.pack(side=RIGHT,expand=0,fill=Y)
        sbar.config(command=lbox.yview)    
        lbox.config(yscrollcommand=sbar.set)
        sbar2 = Scrollbar(lfrm2,orient=HORIZONTAL)
        sbar2.pack(side=BOTTOM,expand=0,fill=X,anchor="sw")
        sbar2.config(command=lbox.xview)
        lbox.config(xscrollcommand=sbar2.set)

        undo_nbrs = {'':[]}

        def filter_btn(evt=None):
            lbox.delete(0, END)
            undo_list = CompositionDatabase().getUndoList()
            undo_names = map(lambda x: x.secondary, undo_list)
            rstr = regvar.get()
            undo_zipped = zip(undo_names,xrange(0,len(undo_names)))
            if len(rstr):
                regexp = re.compile(regvar.get(), re.IGNORECASE)
                undo_zipped = filter(lambda x: regexp.search(x[0]), undo_zipped)
                undo_names = map(lambda x: x[0], undo_zipped)
                undo_nbrs[''] = map(lambda x:x[1], undo_zipped)
            else:
                undo_nbrs[''] = range(0,len(undo_names))

            undo_nbrs[''].reverse()
            undo_names.reverse()
                
            lbox.insert(END, *undo_names)
            

        Button(efrm,text="Filter",command=filter_btn).pack(side=RIGHT,expand=0)
        dlg.bind("<Return>",filter_btn)

        filter_btn()

        lfrm.pack(side=TOP,expand=1,fill=BOTH)        
        frmp.pack(fill=BOTH,expand=1,side=TOP)

        btns = Frame(dlg)

        def do_choose():
            items = map(int, lbox.curselection())

            if len(items):
                self.readcheck()
                
                itm = undo_nbrs[''][items[0]]

                state = CompositionDatabase().getUndoItem(itm).primary

                self.setTupleState(state)

                try:
                    self.write()
                except:
                    pass

                self.last_state = state
                
                self.edit_again = 1
                try:
                    self.window.destroy()
                except:
                    pass

        Button(btns,text="OK", command=do_choose).pack(side=RIGHT)

        Button(btns,text="Cancel",\
               command=lambda: dlg.destroy()).pack(side=RIGHT)


        
        btns.pack(fill=X,expand=0,side=BOTTOM,anchor="se")

        wait_window(dlg)
        

    def getStateTuple(self):
        arrow_data = {}
        for key in self.arrows:
            arrow = self.arrows[key]
            arrow_data[key] = (repr(arrow.codomain), repr(arrow.colorMap),\
                               repr(arrow.vertexMap))
            
        return (repr(self.domain), arrow_data, repr(self.behaviours), \
                repr(self.tags), repr(self.vertexPos))

    def setTupleState(self, t):
        domain = eval(t[0])
        arrow_data = t[1]
        behaviours = eval(t[2])
        tags = eval(t[3])
        vertexPos = eval(t[4])
        arrows = {}
        vertexMaps = {}
        colorMaps = {}

        for key in arrow_data:
            codomain = eval(arrow_data[key][0])
            cmap = eval(arrow_data[key][1])
            vmap = eval(arrow_data[key][2])
            
            arrows[key] = CoDiMuGraphHomEditor(domain,codomain,cmap,vmap,vertexPos)
            chg_callback = lambda key=key: self.updateGlobalVariables(key)
            arrows[key].set_change_callback(chg_callback)

            if key in behaviours:
                arrows[key].behaviour = behaviours[key]

            vertexMaps[key] = vmap
            colorMaps[key] = cmap

        self.last_action = "(revert state/undo)"

        self.domain = domain
        self.arrows = arrows
        self.behaviours = behaviours
        self.tags = tags
        self.vertexPos = vertexPos
        self.colorMaps = colorMaps
        self.vertexMaps = vertexMaps
        
        self.sorted_arrows = self.arrows.keys()
        self.sorted_arrows.sort()
        
        


    
