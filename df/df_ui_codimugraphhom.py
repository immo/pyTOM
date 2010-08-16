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
from df_codimugraph import *
import tkMessageBox
from math import *
from tooltip import *
from df_global import *
from df_guitar_graph import *
from PIL import Image, ImageTk
from df_ui_waitwindow import *

class CoDiMuGraphHomEditor(PartialCoDiMuGraphHom):
    """class that assists in assigning colored directed multi-graph hom.s
    to get certain local composition behaviours
    """
    def __init__(self, domain, codomain, colorMap=None, vertexMap=None, vertexPos=None, override_initialization=None):
        PartialCoDiMuGraphHom.__init__(self,domain,codomain,colorMap,vertexMap,vertexPos, override_initialization)
        self.callback = None
        self.behaviour = ""
        self.cmap_entries = {}
        self.vmap_entries = {}
        self.vmap_annotations = {}
        self.windows_open = 0

    
    def __repr__(self):
        return "CoDiMuGraphHomEditor("+repr(self.domain)+","+\
                              repr(self.codomain)+","+repr(self.colorMap)+","+\
                              repr(self.vertexMap)+","+repr(self.vertexPos)+")"

    def __hash__(self):
        return hash(repr(self))
    
    def edit(self, parent, add_title=None):
        """pop up editor for the CoDiMuGraphHom as child window of parent"""
        window = Toplevel(parent)
        self.windows_open += 1
        self.window = window
        self.last_entry_value = ''
        self.last_color_value = ''
        title = "Graph homomorphism editor tool"
        if add_title != None:
            title = add_title + " - " + title
        window.title(title)
        mapframe = Frame(window)
        crframep = LabelFrame(mapframe,label="Color map")
        crframe = crframep.frame
        color_counter = 0
        clframe = Frame(crframe)
        self.cmap_entries = {}
        srt_colors = [i for i in self.domain.color_set]
        srt_colors.sort()
        for color in srt_colors:
            if color_counter >= 3:
                color_counter = 0
                clframe.pack(side=TOP,fill=X,expand=1)
                clframe = Frame(crframe)
            cframe = Frame(clframe)
            Label(cframe,text=repr(color),justify=LEFT,anchor="w").pack(side=TOP,fill=X,expand=1)
            entry = Entry(cframe,width=10)
            entry.pack(side=TOP,fill=X,expand=1)
            fn_helper = lambda x, entry=entry: self.color_helper(entry)
            entry.bind("<Button-3>",fn_helper)

            fn_quick = lambda x, entry=entry: self.color_quick(entry)
            entry.bind("<Button-2>",fn_quick)
            entry.bind("<Control-Button-3>",fn_quick)
            
            self.cmap_entries[color] = entry
            
            cframe.pack(side=LEFT,fill=X,expand=1)
            color_counter += 1
        
        clframe.pack(side=TOP,fill=X,expand=1)
        
        self.colorImages = [c for c in self.codomain.color_set]
        self.colorImages.sort()
        
        vxframep = LabelFrame(mapframe,label="Vertex map")
        vxframe = vxframep.frame
        
        vlframe = Frame(vxframe)
        self.vmap_entries = {}
        self.vmap_annotations = {}        
        vtx_counter = 0
        for vtx in range(self.domain.vertices):
            if vtx_counter >= 16:
                vtx_counter = 0
                vlframe.pack(side=TOP,fill=X,expand=1)
                vlframe = Frame(vxframe)
            vframe = Frame(vlframe)
            Label(vframe,text=str(vtx),justify=LEFT,anchor="w").pack(side=TOP,fill=X,expand=1)
            entry = Entry(vframe,width=5)
            entry.pack(side=TOP,fill=X,expand=1)
            self.vmap_entries[vtx] = entry
            fn_helper = lambda x, entry=entry, vtx=vtx: self.vertex_helper(entry,vtx)
            entry.bind("<Button-3>",fn_helper)

            fn_quick = lambda x, entry=entry: self.vertex_quick_helper(entry)
            entry.bind("<Button-2>",fn_quick)
            entry.bind("<Control-Button-3>",fn_quick)
            
            anlbl = Label(vframe,text="",justify=LEFT,anchor="w")
            anlbl.pack(side=TOP,fill=X,expand=1)
            self.vmap_annotations[vtx] = anlbl
            
            vframe.pack(side=LEFT,fill=X,expand=1)
            vtx_counter += 1
        
        vlframe.pack(side=TOP,fill=X,expand=1)
        
        vxframep.pack(side=LEFT,fill=BOTH,expand=1)
        crframep.pack(side=RIGHT,fill=BOTH, expand=1)        
        mapframe.pack(side=TOP,fill=X,expand=1)
        
        infoframe = Frame(window)
        
        checkframep = LabelFrame(infoframe,label="Report")
        checkframe = checkframep.frame
        bframe = Frame(checkframe)
        Button(bframe,text="Refresh (F5)",\
               command=lambda:self.readcheck()).pack(side=LEFT)
        Button(bframe,text="LilyPond-Code",\
               command=lambda:self.previewLilypondCode()).pack(side=RIGHT)
        Button(bframe,text="LilyPond (F6)",\
               command=lambda:self.previewLilypond()).pack(side=RIGHT)

        bframe.pack(side=TOP,fill=X,expand=0)
        
        self.report = Text(checkframe,width=50,height=25)
        self.report.pack(side=TOP,fill=Y,expand=1)

        
        window.bind("<F5>",lambda x:self.readcheck())
        window.bind("<F6>",lambda x:self.previewLilypond())        
        window.bind("<Escape>",lambda x:self.do_destroy())
        
        infographframep = LabelFrame(infoframe,label="Graph")
        infographframe = infographframep.frame
        
        self.canvas = Canvas(infographframe,width=600,height=600,bg="black")
        
        self.display_domain(600,600)
        
        self.canvas.pack(side=TOP)
        
        infographframep.pack(side=LEFT,fill=X,expand=1)        
        checkframep.pack(side=RIGHT,fill=Y,expand=1)
        infoframe.pack(side=TOP,fill=X,expand=1)
        
        self.write()
        self.check()
        self.read()
        
        
        window.protocol("WM_DELETE_WINDOW",lambda :self.do_destroy())

        if self.domain.vertices:
            self.vmap_entries[0].focus_set()
        
        wait_window(window)

        self.windows_open -= 1
    
    def position_vertices(self,w,h):
        n = self.domain.vertices
        self.vertexPositions = [(w/2 + sin(float(i)/float(n)*2.0*pi)*w/3,\
                                h/2 - cos(float(i)/float(n)*2.0*pi)*h/3)\
                                for i in range(n)]
        for vtx in self.vertexPos:
            if 0 <= vtx < n:
                self.vertexPositions[vtx] = self.vertexPos[vtx]

    def display_domain(self,w,h):
        n = self.domain.vertices
        self.position_vertices(w,h)
        vertexPositions = self.vertexPositions
        actualColors = {}
        usedRGBs = []
        needColors = []
        for color in self.domain.color_set:
            try:
                rgb = self.window.winfo_rgb(str(color))
                actualColors[color] = str(color)
                usedRGBs.append(rgb)       
            except:
                needColors.append(color)
        cheapList = ["#5D8AA8","#F0F8FF","#E32636","#F19CBB","#FFBF00",\
                     "#FF7E00","#9966CC","#FBCEB1","#00FFFF","#7FFFD4",\
                     "#4B5320","#3B444B","#7BA05B","#FF9966","#6D351A",\
                     "#007FFF"] #stolen from wikipedia...
        counter = 0
        for color in needColors:
            actualColors[color] = cheapList[counter%len(cheapList)]
            counter += 1
        self.canvas.delete(ALL)
        excenter = {}
        for (s,t,color) in self.domain.colored_common_domains:
            ex = 1
            if (s,t) in excenter:
                ex = excenter[(s,t)] + 1
            excenter[(s,t)] = ex
            count = len(self.domain.colored_common_domains[(s,t,color)])
            clr = actualColors[color]
            if s==t:
                arw = [vertexPositions[s][0],vertexPositions[s][1],\
                      vertexPositions[s][0]+20*ex,vertexPositions[s][1],\
                      vertexPositions[s][0]+20*ex,vertexPositions[s][1]+20*ex,\
                      vertexPositions[s][0],vertexPositions[s][1]+20*ex,
                    vertexPositions[s][0],vertexPositions[s][1]]
            else:
                arw = [vertexPositions[s][0],vertexPositions[s][1],\
                      0,0,vertexPositions[t][0],vertexPositions[t][1]]
                arw[2] = (arw[0] + arw[4])/2 + ((arw[5]-arw[1])*ex)/5
                arw[3] = (arw[1] + arw[5])/2 - ((arw[4]-arw[0])*ex)/5
            arw = tuple(arw)
            self.canvas.create_line(arw, arrow=LAST, smooth=1, joinstyle=ROUND, \
                fill=clr, width=count, activefill="white", tags="cl"+repr(color))
        for color in self.domain.color_set:
            entry = self.cmap_entries[color]
            fn_helper = lambda x, entry=entry: self.color_helper(entry)
            self.canvas.tag_bind("cl"+repr(color),"<Button-3>",fn_helper)
            
        for i in range(n):
            tag = "vtx" + str(i)
            entry = self.vmap_entries[i]
            fn_helper = lambda x, entry=entry, vtx=i: self.vertex_helper(entry,vtx)
            item = self.canvas.create_text(vertexPositions[i], fill="white",text=str(i),\
              activefill="red",tags=tag)
            self.canvas.tag_bind(tag,"<Button-3>",fn_helper)
            fn_helper = lambda x, vtx=i,mode=0,item=item: self.position_helper(vtx,mode,x,item)
            self.canvas.tag_bind(tag,"<ButtonPress-1>",fn_helper)
            fn_helper = lambda x, vtx=i,mode=1,item=item: self.position_helper(vtx,mode,x,item)
            self.canvas.tag_bind(tag,"<ButtonRelease-1>",fn_helper)            
    
    def position_helper(self, vtx, mode, event, item):
        if mode == 0:
            fn_helper = lambda x, vtx=vtx,mode=2,item=item: self.position_helper(vtx,mode,x,item)
            self.canvas.tag_bind("vtx"+str(vtx),"<Motion>",fn_helper)
        elif mode==1:
            self.canvas.tag_unbind("vtx"+str(vtx),"<Motion>")
            x = self.canvas.canvasx(event.x)
            if x < 0:
                x = 0
            elif x > 600:
                x = 600
            y = self.canvas.canvasy(event.y)
            if y < 0:
                y = 0
            elif y > 600:
                y = 600
            self.vertexPos[vtx] = (x,y)
            self.display_domain(600,600)
            
        elif mode==2:
            x = self.canvas.canvasx(event.x)
            if x < 0:
                x = 0
            elif x > 600:
                x = 600
            y = self.canvas.canvasy(event.y)
            if y < 0:
                y = 0
            elif y > 600:
                y = 600
            self.canvas.coords(item, (x,y))

    def color_quick(self, entry):
        entry.delete(0,END)
        entry.insert(0, self.last_color_value)
        self.readcheck()
    
    def color_helper(self, entry):
        (x,y) = self.window.winfo_pointerxy()
        dialog = Toplevel(self.window)
        counter = 0
        col = Frame(dialog)
        for c in self.colorImages:
            if counter >= 8:
                counter = 0
                col.pack(side=LEFT,anchor="ne",expand=1)
                col = Frame(dialog)
                
            def btn_cmd(value=c,dialog=dialog, entry=entry):
                dialog.destroy()
                entry.delete(0,END)
                entry.insert(0, repr(value))
                self.last_color_value = repr(value)
                
            Button(col,text=repr(c),command=btn_cmd).pack(side=TOP,fill=X,expand=1)
            counter += 1
        col.pack(side=LEFT,anchor="n",expand=1)
        DfGlobal()["root.window"].update()
        size = [dialog.winfo_width(), dialog.winfo_height()] # not working :(
        #new_geo = "+"+str(x-int(size[0])/2)+"+"+str(y-int(size[1])/2)
        new_geo = "+"+str(max(0,x-int(size[0])/2))+"+"+str(max(0,y-int(size[1])/2))
        dialog.wm_geometry(new_geo)
        wait_window(dialog)
        self.readcheck()

    def vertex_quick_helper(self, entry):
        entry.delete(0,END)
        entry.insert(0, self.last_entry_value)
        self.readcheck()
    
    def vertex_helper(self, entry, vertex):
        (x,y) = self.window.winfo_pointerxy()
        dialog = Toplevel(self.window)
        line = Frame(dialog)
        counter = 0
        perrow = 5
        if self.codomain.vertices > 65:
            perrow = int(sqrt(self.codomain.vertices/4))
        for vtx in range(self.codomain.vertices):
            if counter >= perrow:
                counter = 0
                line.pack(side=TOP)
                line = Frame(dialog)
                
            def btn_cmd(value=vtx,dialog=dialog,entry=entry):
                dialog.destroy()
                entry.delete(0,END)
                entry.insert(0, repr(value))
                self.last_entry_value = repr(value)
                
            fontcolor="black"
            if self.check_image(vertex,vtx) > 0:
                fontcolor="red"
            btn = Button(line,text=str(self.codomain.annotation(vtx))+" ("+str(vtx)+")",\
                command=btn_cmd,fg=fontcolor,width=12,justify=LEFT)
            btn.pack(side=LEFT)
            ToolTip(btn,delay=200,text=self.codomain.tooltip(vtx))
            counter += 1
            
        line.pack(side=TOP,anchor="w")
        DfGlobal()["root.window"].update()        
        size = [dialog.winfo_width(), dialog.winfo_height()] # not working :(
        new_geo = "+"+str(max(0,x-int(size[0])/2))+"+"+str(max(0,y-int(size[1])/2))
        dialog.wm_geometry(new_geo)
        wait_window(dialog)
        self.readcheck()
    
    def do_destroy(self):
        self.read()
        self.window.destroy()
    
    def readcheck(self):
        self.read()
        self.check()
        try:
            self.write()
        except:
            pass
    
    def check(self,update=1):
        """check & update report"""
        PartialCoDiMuGraphHom.check(self)
        if update:
            try:
                self.report.delete(1.0,END)
                self.report.insert(END, self.report_text)
            except: #on delete this sometimes doesnt work...
                pass
    
    def set_change_callback(self,fn):
        self.callback = fn
    
    def on_change(self):
        """called on change"""
        if self.callback != None:
            try:
                self.callback()
            except:
                pass
    
    def read(self):
        """read in all data from widget fields"""
        codomain_behaviours = [str(self.codomain.behaviourString(i)) for i \
                               in range(self.codomain.vertices)]
        codomain_annotations = [str(self.codomain.annotation(i)) for i\
                                in range(self.codomain.vertices)]
        v = {}
        for vtx in self.vmap_entries:
            entry_value = self.vmap_entries[vtx].get()
            if entry_value:
                try:
                    image = int(entry_value)
                    v[vtx] = image                
                except ValueError:
                    # not an int...
                    image_val = str( entry_value )
                    try:
                        v[vtx] = codomain_behaviours.index(image_val)
                    except ValueError:
                        try:
                            v[vtx] = codomain_annotations.index(image_val)
                        except ValueError:
                            try:
                                image_val = str( eval( entry_value) )
                                try:
                                    v[vtx] = codomain_behaviours.index(image_val)
                                except ValueError:
                                    try:
                                        v[vtx] = codomain_annotations.index(image_val)
                                    except ValueError:
                                        pass                                
                            except:
                                pass
                            
        c = {}
        for clr in self.cmap_entries:
            entry_value = self.cmap_entries[clr].get()
            if entry_value:
                try:
                    image = eval(entry_value)
                    c[clr] = image
                except: # use as string
                    c[clr] = self.cmap_entries[clr].get()
                    
        changed = 0
        if v != self.vertexMap:
            changed = 1
            self.vertexMap = v
        if c != self.colorMap:
            self.colorMap = c
            changed = 1
        if changed == 1:
            self.on_change()
        
        self.behaviour = ""
        for vtx in range(self.domain.vertices):
            if vtx in self.vertexMap:
                try:
                    image = int(self.vertexMap[vtx])
                    if self.codomain.vertices > image:
                        image = str(self.codomain.behaviourString(image))
                    else:
                        image = ""
                except:
                    image = ""
                self.behaviour += image

    def previewLilypondCode(self):
        try:
            self.readcheck()
        except:
            pass
        lilyCode = gtr2LY(self.behaviour)
        tl = Toplevel(self.window)
        txt = Text(tl,width=80,height=24)
        txt.insert(END, lilyCode)
        txt.pack()
        tl.bind("<Escape>",lambda x:tl.destroy())
        tl.title("LilyPond-Code  --  "+self.window.title())
        
        
        

    def previewLilypond(self):
        try:
            self.readcheck()
        except:
            pass
        lilyCode = gtr2LY(self.behaviour)
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
            pass # file not found...
        
        
        
    def write(self):
        """write all data to widget fields"""
        for vtx in self.vertexMap:
            if vtx in self.vmap_entries:
                entry = self.vmap_entries[vtx]
                entry.delete(0, END)
                entry.insert(0, repr(self.vertexMap[vtx]))
                try:
                    image = int(self.vertexMap[vtx])
                    if self.codomain.vertices > image:
                        image = str(self.codomain.annotation(image))
                    else:
                        image = ""
                except:
                    image = ""
                lbl = self.vmap_annotations[vtx]
                lbl.config(text=image)
        for vtx in self.vmap_annotations:
            if not vtx in self.vertexMap:
                lbl = self.vmap_annotations[vtx]
                lbl.config(text="")
        for color in self.colorMap:
            if color in self.cmap_entries:
                entry = self.cmap_entries[color]
                entry.delete(0, END)
                entry.insert(0, repr(self.colorMap[color]))
