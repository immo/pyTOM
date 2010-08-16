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

from df_global import *
from df_data_channels import *
from Tix import *
from df_limbs import *
from df_concept import *
import code

def nt_set_start_and_extent(name,  startandextent):
    """nt_set_start_and_extent(name,  startandextent)   
    sets the start and extent parameters for DfGlobal()[name] canvas-arc object
    """
    g = DfGlobal()
    args = startandextent.split(",")
    start = float(args[0])
    extent = float(args[1])
    g["canvas"].itemconfigure(g[name],  start=-start+90,  extent=-extent)
    DfGlobal()["Tk.root.update_idletasks"] ()

def nt_set_start(name, start,offset):
    g = DfGlobal()
    g["canvas"].itemconfigure(g[name], start=-float(start)+90+offset)
    DfGlobal()["Tk.root.update_idletasks"] ()    
    
def nt_riff_preview(info):
    g = DfGlobal()
    canvas = g["canvas"]
    if info == "clear":
        for i in g["riff.preview"]:
            canvas.delete(i)
        g["riff.preview"] = []
    else:
        l = info.split(',')
        if len(l) >= 5:
            w = g["canvas_w"]/2.0
            h = g["canvas_h"]
            
            g["riff.preview"].append(canvas.create_line(float(l[0])*w,\
                                  float(l[1])*h,float(l[2])*w,\
                                  float(l[3])*h,fill=l[4],width=2))
    
def show_limb_event(name, evt):
    """show_limb_event(name, evt)   
    process evt as event for showing the current state of limb name"""
    circle = DfGlobal()[name]
    canvas = DfGlobal()["canvas"]
    if evt == "hit":
        canvas.lift(circle)
        canvas.itemconfigure(circle, fill="#AAFFAA", outline="#BBAAFF")
        DfGlobal()["Tk.root.update_idletasks"] ()
    
    elif evt == "reset":
        canvas.lower(circle)
        canvas.itemconfigure(circle, fill="", outline="#222288")
        DfGlobal()["Tk.root.update_idletasks"] ()
    
    elif evt == "climax":
        canvas.lift(circle)
        canvas.itemconfigure(circle, fill="#FF3333", outline="#2222FF")
        DfGlobal()["Tk.root.update_idletasks"] ()

def set_potential_bar(name,evt):
    g = DfGlobal()
    canvas = g["canvas"]
    line = g[name]

    y = g["canvas_h"] / 100.0

    pos = float(evt)
    if pos < -0.1:
        pos = -0.1
    elif pos > 1.1:
        pos = 1.1

    coords = canvas.coords(line)
    ycoord = (60 + (pos*(-20.0)))*y

    canvas.coords(line,coords[0],ycoord,coords[2],ycoord)
    g["Tk.root.update_idletasks"] ()


def key_handler(evt):
    send_line("key",evt.keysym.upper())
    return "break"


def initialize_new_technology_ui():
    """initialize the new technology user interface"""
    g = DfGlobal()

    initialize_char_setup()
    g["concept.pool"] = {}
    g["gene.pool"] = {}
    g["DfInterpreter.console"] = code.InteractiveInterpreter()

    def set_gene_pool(x):
        g["gene.pool"] = eval(x)

    def set_concept_pool(x):
        g["concept.pool"] = eval(x)

    add_data_channel_handler("gene.pool",set_gene_pool)
    add_data_channel_handler("concept.pool",set_concept_pool)
    

    x = 200.0 / g["canvas_w"]
    y = 100.0 / g["canvas_h"]
    centerx = 100.0
    centery = 50.0


    g["speed-arc-bg"] = g["canvas"].create_arc(centerx + 5, centery - 15,\
                                            centerx + 40, centery - 5,\
                                            start=0, extent=180,\
                                            style=ARC, width=1,\
                                            outline="#444444")
    
    g["outer_arc"] = g["canvas"].create_arc(centerx - 20, centery - 20, \
                                            centerx + 20, centery + 20,\
                                            start=90, \
                                            extent=-200, outline="#22FF33",\
                                            style=ARC,  width=5)
    g["mid_arc"] = g["canvas"].create_arc(centerx - 18, centery - 18,\
                                          centerx + 18, centery + 18,\
                                          start=90,\
                                           extent=-100, outline="#FFFF33",\
                                           style=ARC,  width=5)
    g["inner_arc"] = g["canvas"].create_arc(centerx - 16, centery - 16,\
                                            centerx + 16, centery + 16,
                                            start=90,\
                                             extent=-300, outline="#FF3333",\
                                             style=ARC,  width=5)
    add_data_channel_handler("outer_arc", \
                             lambda l: nt_set_start_and_extent("outer_arc", l))
    add_data_channel_handler("mid_arc", \
                             lambda l: nt_set_start_and_extent("mid_arc", l))
    add_data_channel_handler("inner_arc", \
                             lambda l: nt_set_start_and_extent("inner_arc", l))
    add_data_channel_handler("left hand", \
                             lambda l: show_limb_event("left hand",l))
    add_data_channel_handler("right hand", \
                             lambda l: show_limb_event("right hand",l))
    add_data_channel_handler("left foot",   \
                             lambda l: show_limb_event("left foot",l))
    add_data_channel_handler("right foot", \
                             lambda l: show_limb_event("right foot",l))
    add_data_channel_handler("preview", nt_riff_preview)
    g["left hand"] = g["canvas"].create_oval(centerx,centery-10,centerx+10,\
                                             centery,outline="#222288",width=5)
    g["right hand"] = g["canvas"].create_oval(centerx-10,centery-10,centerx,\
                                              centery,outline="#222288",\
                                              width=5)
    g["left foot"] = g["canvas"].create_oval(centerx-2,centery,centerx+8,\
                                             centery+10,outline="#222288",\
                                             width=5)
    g["right foot"] = g["canvas"].create_oval(centerx-8,centery,centerx+2,\
                                              centery+10,outline="#222288",\
                                              width=5)
    g["riff.preview"] = []
    g["left hand.potential"] = g["canvas"].create_line(centerx-35,centery+10,centerx-31,centery+10,fill="white",width=5)
    g["right hand.potential"] = g["canvas"].create_line(centerx-30,centery+10,centerx-26,centery+10,fill="white",width=5)    
    g["left foot.potential"] = g["canvas"].create_line(centerx+31,centery+10,centerx+35,centery+10,fill="white",width=5)
    g["right foot.potential"] = g["canvas"].create_line(centerx+26,centery+10,centerx+30,centery+10,fill="white",width=5) 
    add_data_channel_handler("right foot.potential", \
                             lambda l: set_potential_bar("right foot.potential",l))
    add_data_channel_handler("left foot.potential", \
                             lambda l: set_potential_bar("left foot.potential",l))
    add_data_channel_handler("right hand.potential", \
                             lambda l: set_potential_bar("right hand.potential",l))
    add_data_channel_handler("left hand.potential", \
                             lambda l: set_potential_bar("left hand.potential",l))


    g["speed-arc"] = g["canvas"].create_arc(centerx + 5, centery - 15,\
                                            centerx + 40, centery - 5,\
                                            start=85, extent=10,\
                                            style=ARC, width=10,\
                                            outline="#00BBBB")

    g["speed-ctl-arc"] = g["canvas"].create_arc(centerx + 5, centery - 15,\
                                            centerx + 40, centery - 5,\
                                            start=-2.5, extent=2,\
                                            style=ARC, width=16,\
                                            outline="#FF0000")

    add_data_channel_handler("speed-arc", \
                             lambda l: nt_set_start("speed-arc", l, -5))

    add_data_channel_handler("speed-ctl-arc", \
                             lambda l: nt_set_start("speed-ctl-arc", l, -1))    



    font1 = "-*-courier-*-r-normal-*-*-240-100-100-*-*-*-*"
    font2 = "-*-courier-*-r-normal-*-*-180-100-100-*-*-*-*"
    font3 = "-*-courier-*-r-normal-*-*-140-100-100-*-*-*-*"
    font4 = "-*-courier-*-r-normal-*-*-120-100-100-*-*-*-*"
    #fonthud = "-*-fixed-*-r-*-*-90-*-*-*-*-*-*-*"
    fonthud = "-*-helvetica-*-r-bold-*-*-600-100-100-*-*-*-*"

    g["text1"] = g["canvas"].create_text(centerx,1,text="",anchor="n",fill="white",font=font1,width=200,justify="center")
    g["text2"] = g["canvas"].create_text(63,centery-25,text="",anchor="ne",fill="#00FF00",font=font2, width=60,justify="right")
    g["text3"] = g["canvas"].create_text(137,centery-25,text="",anchor="nw",fill="#FF2222",font=font2, width=60,justify="left")
    g["text4"] = g["canvas"].create_text(centerx-60,centery+25,text="",anchor="nw",fill="#77BBFF",font=font3,width=120,justify="left")
    g["text5"] = g["canvas"].create_text(40,centery+20,text="",anchor="ne",fill="#DDDDDD",font=font4,width=120,justify="right")
    g["text6"] = g["canvas"].create_text(160,centery+20,text="",anchor="nw",fill="#33FFFF",font=font4,width=120,justify="left")

    hud_outline = "#0066CC"
    hud_color = "#99FFFF"

    g["headupdisplay1"] = g["canvas"].create_text(centerx+5,5,text="", anchor="n",fill=hud_outline,width=200,justify="center",font=fonthud)
    g["headupdisplay2"] = g["canvas"].create_text(centerx-5,5,text="", anchor="n",fill=hud_outline,width=200,justify="center",font=fonthud)
    g["headupdisplay3"] = g["canvas"].create_text(centerx,5+5,text="", anchor="n",fill=hud_outline,width=200,justify="center",font=fonthud)
    g["headupdisplay4"] = g["canvas"].create_text(centerx,5-5,text="", anchor="n",fill=hud_outline,width=200,justify="center",font=fonthud)
    g["headupdisplay5"] = g["canvas"].create_text(centerx+5,5+5,text="", anchor="n",fill=hud_outline,width=200,justify="center",font=fonthud)
    g["headupdisplay6"] = g["canvas"].create_text(centerx-5,5+5,text="", anchor="n",fill=hud_outline,width=200,justify="center",font=fonthud)
    g["headupdisplay7"] = g["canvas"].create_text(centerx+5,5-5,text="", anchor="n",fill=hud_outline,width=200,justify="center",font=fonthud)
    g["headupdisplay8"] = g["canvas"].create_text(centerx-5,5-5,text="", anchor="n",fill=hud_outline,width=200,justify="center",font=fonthud)
    
    g["headupdisplay"] = g["canvas"].create_text(centerx,5,text="", anchor="n",fill=hud_color,width=200,justify="center",font=fonthud)


    g["text-mode"] = g["canvas"].create_text(199,99,text="JAM",anchor="se",fill="#333333",font=font4)
    g["text-next"] = g["canvas"].create_text(189,99,text="NEXT",anchor="se",fill="#333333",font=font4)
    g["text-keyboard"] = g["canvas"].create_text(179,99,text="",anchor="se",fill="#CCCCCC",font=font4)
    g["text-chord"] = g["canvas"].create_text(1,99,text="",anchor="sw",fill="#FFFFFF",font=font4)
    g["text-cmd"] = g["canvas"].create_text(119,99,text="",anchor="sw",fill="#CCCCCC",font=font4)    
    
    def canvas_resize():
        g["canvas"].itemconfigure(g["text1"], width = g["canvas_w"])
        g["canvas"].itemconfigure(g["text2"], width = g["canvas_w"]*0.3)
        g["canvas"].itemconfigure(g["text3"], width = g["canvas_w"]*0.3)
        g["canvas"].itemconfigure(g["text4"], width = g["canvas_w"]*0.6)
        g["canvas"].itemconfigure(g["text5"], width = g["canvas_w"]*0.185)
        g["canvas"].itemconfigure(g["text6"], width = g["canvas_w"]*0.185)
        g["canvas"].itemconfigure(g["headupdisplay"], width = g["canvas_w"])
        g["canvas"].itemconfigure(g["headupdisplay1"], width = g["canvas_w"])
        g["canvas"].itemconfigure(g["headupdisplay2"], width = g["canvas_w"])
        g["canvas"].itemconfigure(g["headupdisplay3"], width = g["canvas_w"])
        g["canvas"].itemconfigure(g["headupdisplay4"], width = g["canvas_w"])
        g["canvas"].itemconfigure(g["headupdisplay5"], width = g["canvas_w"])
        g["canvas"].itemconfigure(g["headupdisplay6"], width = g["canvas_w"])
        g["canvas"].itemconfigure(g["headupdisplay7"], width = g["canvas_w"])
        g["canvas"].itemconfigure(g["headupdisplay8"], width = g["canvas_w"])
        coords = g["canvas"].coords(g["headupdisplay"])
        coordx = coords[0]
        coordy = coords[1]
        g["canvas"].coords(g["headupdisplay1"],coordx+5,coordy)
        g["canvas"].coords(g["headupdisplay2"],coordx+5,coordy-5)
        g["canvas"].coords(g["headupdisplay3"],coordx+5,coordy+5)
        g["canvas"].coords(g["headupdisplay4"],coordx-5,coordy)
        g["canvas"].coords(g["headupdisplay5"],coordx-5,coordy+5)
        g["canvas"].coords(g["headupdisplay6"],coordx-5,coordy-5)
        g["canvas"].coords(g["headupdisplay7"],coordx,coordy+5)
        g["canvas"].coords(g["headupdisplay8"],coordx,coordy-5)

        
    g["canvas_reconfigure"] = canvas_resize

    text_elems = ["text"+str(i) for i in range(1,7)] + ["text-chord", "text-keyboard", "text-cmd"]
    for t in text_elems:
        add_data_channel_handler(t,lambda s,t=t:g["canvas"].itemconfigure(g[t],text=eval(s)))

    def headupupdate(txt):
        t = eval(txt)
        canvas = g["canvas"]
        canvas.itemconfigure(g["headupdisplay1"],text=t)
        g["Tk.root.update_idletasks"] ()
        canvas.itemconfigure(g["headupdisplay2"],text=t)
        g["Tk.root.update_idletasks"] ()
        canvas.itemconfigure(g["headupdisplay3"],text=t)
        g["Tk.root.update_idletasks"] ()
        canvas.itemconfigure(g["headupdisplay4"],text=t)
        g["Tk.root.update_idletasks"] ()
        canvas.itemconfigure(g["headupdisplay5"],text=t)
        g["Tk.root.update_idletasks"] ()        
        canvas.itemconfigure(g["headupdisplay6"],text=t)
        g["Tk.root.update_idletasks"] ()        
        canvas.itemconfigure(g["headupdisplay7"],text=t)
        g["Tk.root.update_idletasks"] ()        
        canvas.itemconfigure(g["headupdisplay8"],text=t)
        g["Tk.root.update_idletasks"] ()        
        canvas.itemconfigure(g["headupdisplay"],text=t)
        g["Tk.root.update_idletasks"] ()

    add_data_channel_handler("headupdisplay", headupupdate)

    def switch_text(l):
        if l == "JAM":
            g["canvas"].itemconfigure(g["text-mode"],fill="#FFFF00")
        else:
            g["canvas"].itemconfigure(g["text-mode"],fill="#333333")

    add_data_channel_handler("text-mode", switch_text)

    def next_text(l):
        if l == "NEXT":
            g["canvas"].itemconfigure(g["text-next"],fill="#FFFF00")
        else:
            g["canvas"].itemconfigure(g["text-next"],fill="#333333")

    add_data_channel_handler("text-next", next_text)


            

    g["canvas"].bind("<Key>", key_handler)
