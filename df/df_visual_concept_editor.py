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
from df_global import *
from df_limbs import *
from df_xml_thing import *
import tkMessageBox
from df_snippets import *
from df_property_dialog import *

def apply_thing(thing, concept, tzero=0.0, g=DfGlobal()):
    try:
        if thing['type'] == 'snippet':
            g['snippets.'+thing['limb']][thing['name']]['apply'](thing,\
                                                                 concept,\
                                                                 tzero)
        elif thing['type'] == 'set-instrument':
            concept.add_change_instruments(thing['t']+tzero,thing['limb'],\
                                           thing['instrument'])
    except Exception,err:
        print "Problem applying thing: "
        print thing
        print "===="
        print " Error: ",err
        
def apply_things(things, concept, tzero=0.0, g=DfGlobal()):
    priorities = g['snippets.priorities']
    sorted = copy_things(things)
    def snippet_cmp(x,y):
        if x['type'] == y['type']:
            if x['type'] == 'snippet':
                c = cmp(priorities[x['name']],priorities[y['name']])
                if c == 0:
                    return cmp(x['t'],y['t'])
                else:
                    return c
            else:
                return cmp(x['t'],y['t'])
        else:
            if x['type'] == 'snippet':
                c = cmp(priorities[x['name']],0)
                if c == 0:
                    return cmp(x['t'],y['t'])
                else:
                    return c
            elif y['type'] == 'snippet':
                c = cmp(0,priorities[y['name']])
                if c == 0:
                    return cmp(x['t'],y['t'])
                else:
                    return c
        return cmp(x['t'],y['t'])                           
    sorted.sort(snippet_cmp)
    for thing in sorted:
        apply_thing(thing, concept, tzero, g)


def create_visual_editor(parent=None,name="GraConEd",things=None, length=16.0,\
                         width=2048,g=DfGlobal()):
    """Create an graphical editor window as child of parent"""
    window = Toplevel(parent)
    window.title(name)
    heights = [160,160,80,80]
    names = ["right hand","left hand","right foot","left foot"]
    
    if things == None:
        things = []
        
    dic = {}
    dic['name'] = name
    dic['window'] = window
    dic['width'] = width
    dic['length'] = length
    dic['things'] = things

    dic['ignore-changes'] = False

    elements = {}
    for name in names:
        elements[name] = []
    dic['elements'] = elements

    dic['x'] = 0
    dic['y'] = 0
    
        
    canvas = Canvas(window, width=600, height=sum(heights),\
                    scrollregion=(0,0,width,sum(heights)),bg="black")

    dic['canvas'] = canvas
    
    canvas_bg = canvas.create_rectangle(0,0,width,sum(heights),fill="#000000")
    dic['canvas_bg'] = canvas_bg
    
    accumulator = 0
    for h in heights[:-1]:
        accumulator += h
        canvas.create_line(0,accumulator,width,accumulator,fill="#555555")

    for beat in range(int(length)):
        x = float(beat)*float(width)/float(length)
        canvas.create_line(x,0,x,sum(heights),fill="#555588")
        canvas.create_text(x+2,50,fill="#555588",text=str(beat),anchor=NW)

    right_menus = {}
    y_margins = {}
    y_mins = {}
    dic['y_margins'] = y_margins
    dic['y_minmargins'] = y_mins
    left_menus = {}

    for i in range(len(names)):
        y_margins[names[i]] = sum(heights[0:i+1])
        y_mins[names[i]] = sum(heights[0:i])
    

    for thing in things:
        if thing['type'] == 'snippet':
            limb = thing['limb']
            name = thing['name']
            g['snippets.'+limb][name]['restore'](dic, thing)
        elif thing['type'] == 'set-instrument':
            chg = thing['instrument']
            limb = thing['limb']
            thing['y-min'] = dic['y_minmargins'][limb]
            thing['y-max'] = dic['y_margins'][limb]-21
            x = thing['t']*float(dic['width'])/float(dic['length'])
            thing['x'] = x
            thing['*self'] = thing
            y = thing['y']
            if y < thing['y-min']:
                y = thing['y-min']
            elif y > thing['y-max']:
                y = thing['y-max']
            thing['y'] = y
            new_thing = thing
            new_thing['*box'] = canvas.create_rectangle(x,\
                                                        y,\
                                                        x+150,\
                                                        y+20,\
                                                        fill="#331111",\
                                                        outline="red")
                    
            new_thing['*text'] = canvas.create_text(x+2,\
                                                    y+2,\
                                                    fill="red",\
                                                    text=chg,\
                                                    anchor=NW)
            def dragMotion(event,thing=new_thing,dic=dic,\
                                   canvas=canvas):
                x = canvas.xview()[0]*float(dic['width'])+event.x\
                    -thing['delta-x']
                y = event.y\
                    -thing['delta-y']
                if y < thing['y-min']:
                    y = thing['y-min']
                elif y > thing['y-max']:
                    y = thing['y-max']
                thing['x'] = x
                thing['y'] = y
                thing['t'] = float(x)*float(dic['length'])\
                             /float(dic['width'])
                canvas.coords(thing['*box'],x,y,x+150,y+20)
                canvas.coords(thing['*text'],x+2,y+2)

            def setDelta(event,thing=new_thing,dic=dic):
                thing['delta-x'] = canvas.xview()[0]*\
                                   float(dic['width'])+event.x\
                                   -thing['x']
                thing['delta-y'] = event.y\
                                   -thing['y']

            def removeThing(thing=new_thing,dic=dic):
                dic['things'].remove(thing)
                canvas.delete(thing['*box'])
                canvas.delete(thing['*text'])

            def propertyDialog(thing=new_thing,dic=dic):
                property_dialog([("t = ","t")],values=thing,\
                                 types={'t':float},parent=window,
                                 title=thing['instrument']+"@"+thing['limb'])
                thing['x'] = int(thing['t']*float(dic['width'])\
                                 /float(dic['length']))
                canvas.coords(thing['*box'],thing['x'],thing['y'],\
                              thing['x']+150,thing['y']+20)
                canvas.coords(thing['*text'],thing['x']+2,thing['y']+2)    

            new_thing['*menu'] = Menu(window,tearoff=0)
            new_thing['*menu'].add_command(label="Properties",\
                                           command=propertyDialog)

            new_thing['*menu'].add_command(label="Remove",\
                                          command=removeThing)
            new_thing['*menu'].add_separator()            
            new_thing['*menu'].add_command(label=chg)

            def rightClick(event,thing=new_thing,dic=dic):
                thing['*menu'].post(event.x_root,event.y_root)

            def leftDouble(event,thing=new_thing,dic=dic):
                propertyDialog(thing,dic)

            canvas.tag_bind(new_thing['*box'],"<Button-1>",setDelta)
            canvas.tag_bind(new_thing['*box'],"<B1-Motion>",dragMotion)
            canvas.tag_bind(new_thing['*box'],"<Button-3>",rightClick)
            canvas.tag_bind(new_thing['*box'],"<Double-Button-1>",leftDouble)
            canvas.tag_bind(new_thing['*text'],"<Button-1>",setDelta)
            canvas.tag_bind(new_thing['*text'],"<B1-Motion>",\
                            dragMotion)
            canvas.tag_bind(new_thing['*text'],"<Button-3>",rightClick)
            canvas.tag_bind(new_thing['*text'],"<Double-Button-1>",leftDouble)
                    

    fn = lambda t: names[0]
    for i in range(len(names)):
        canvas.create_text(3,3+sum(heights[0:i]),text=names[i],fill="#777777",\
                           anchor=NW)
        fn = lambda t,f=fn,acc=sum(heights[0:i]),n=names[i]:\
             f(t) if t < acc else n

        snippets = g['snippets.'+names[i]]

        menu = Menu(window,tearoff=0)
        sortsnippets = snippets.keys()[:]
        sortsnippets.sort()
        for sn in sortsnippets:
            def createSnippet(snippet=snippets[sn], dic=dic, limb=names[i]):
                
                new_thing = snippet['create'](dic,dic['t'],limb,snippet)
                dic['things'].append(new_thing)
                
            menu.add_command(label=sn, command=createSnippet)

        menu.add_separator()
        def pasteSnippet(dic=dic,limb=names[i]):
            if DfGlobal()["copied-snippet"]:
                try:
                    thing = copy_dic_thing(DfGlobal()["copied-snippet"])
                    thing['t'] = dic['t']
                    thing['y'] = dic['y']
                    thing['limb'] = limb
                    name = thing['name']
                    g['snippets.'+limb][name]['restore'](dic, thing)
                    dic['things'].append(thing)
                except Exception, err:
                    print "Error pasting snippet to ", limb, ": ",thing
                    print "Reason:", err
                    
        menu.add_command(label="paste...",command=pasteSnippet)
        menu.add_command(label="cancel")
        left_menus[names[i]] = menu
        
        
        groups = g['groups.' + names[i]]

        menu = Menu(window,tearoff=0)
        groups_sorted = groups.keys()[:]
        groups_sorted.sort()
        for gr in groups_sorted:
            gmenu = Menu(menu,tearoff=0)
            for gi in groups[gr]:
                def action(limb=names[i],chg=gi,dic=dic,window=window,\
                           canvas=canvas):
                    if dic['y']+21 >= dic['y_margins'][limb]:
                        dic['y'] = dic['y_margins'][limb]-21
                    new_thing = {}
                    new_thing['limb'] = limb
                    new_thing['type'] = 'set-instrument'
                    new_thing['instrument'] = chg
                    new_thing['x'] = dic['x']
                    new_thing['y'] = dic['y']
                    new_thing['y-min'] = dic['y_minmargins'][limb]
                    new_thing['y-max'] = dic['y_margins'][limb]-21
                    new_thing['t'] = float(dic['x'])*float(dic['length'])\
                                     /float(dic['width'])
                    new_thing['*self'] = new_thing
                    new_thing['*box'] = canvas.create_rectangle(dic['x'],\
                                                               dic['y'],\
                                                               dic['x']+150,\
                                                               dic['y']+20,\
                                                               fill="#331111",\
                                                               outline="red")
                    
                    new_thing['*text'] = canvas.create_text(dic['x']+2,\
                                                           dic['y']+2,\
                                                           fill="red",\
                                                           text=chg,\
                                                           anchor=NW)
                    def dragMotion(event,thing=new_thing,dic=dic,\
                                   canvas=canvas):
                        x = canvas.xview()[0]*float(dic['width'])+event.x\
                            -thing['delta-x']
                        y = event.y\
                            -thing['delta-y']
                        if y < thing['y-min']:
                            y = thing['y-min']
                        elif y > thing['y-max']:
                            y = thing['y-max']
                        thing['x'] = x
                        thing['y'] = y
                        thing['t'] = float(x)*float(dic['length'])\
                                     /float(dic['width'])
                        canvas.coords(thing['*box'],x,y,x+150,y+20)
                        canvas.coords(thing['*text'],x+2,y+2)

                    def setDelta(event,thing=new_thing,dic=dic):
                        thing['delta-x'] = canvas.xview()[0]*\
                                           float(dic['width'])+event.x\
                                           -thing['x']
                        thing['delta-y'] = event.y\
                                           -thing['y']

                    def removeThing(thing=new_thing,dic=dic):
                        dic['things'].remove(thing)
                        canvas.delete(thing['*box'])
                        canvas.delete(thing['*text'])

                    def propertyDialog(thing=new_thing,dic=dic):
                        property_dialog([("t = ","t")],values=thing,\
                                         types={'t':float},parent=window,
                                        title=thing['instrument']+"@"+thing['limb'])
                        thing['x'] = int(thing['t']*float(dic['width'])\
                                         /float(dic['length']))
                        canvas.coords(thing['*box'],thing['x'],thing['y'],\
                                      thing['x']+150,thing['y']+20)
                        canvas.coords(thing['*text'],thing['x']+2,thing['y']+2)    

                        
                    new_thing['*menu'] = Menu(window,tearoff=0)
                    new_thing['*menu'].add_command(label="Properties",\
                                                   command=propertyDialog)
                    new_thing['*menu'].add_separator()
                    new_thing['*menu'].add_command(label="Remove",\
                                                  command=removeThing)


                    def rightClick(event,thing=new_thing,dic=dic):
                        new_thing['*menu'].post(event.x_root,event.y_root)

                    def leftDouble(event,thing=new_thing,dic=dic):
                        propertyDialog(thing,dic)
                        

                    canvas.tag_bind(new_thing['*box'],"<Button-1>",setDelta)
                    canvas.tag_bind(new_thing['*box'],"<B1-Motion>",dragMotion)
                    canvas.tag_bind(new_thing['*box'],"<Button-3>",rightClick)
                    canvas.tag_bind(new_thing['*box'],"<Double-Button-1>",leftDouble)
                    canvas.tag_bind(new_thing['*text'],"<Button-1>",setDelta)
                    canvas.tag_bind(new_thing['*text'],"<B1-Motion>",\
                                    dragMotion)
                    canvas.tag_bind(new_thing['*text'],"<Button-3>",rightClick)
                    canvas.tag_bind(new_thing['*text'],"<Double-Button-1>",leftDouble)                    
                    
                    
                    dic['things'].append(new_thing)
                    
                    
                gmenu.add_command(label=gi, command=action)
            menu.add_cascade(label=gr,menu=gmenu)
            
        menu.add_separator()
        menu.add_command(label="cancel")

        def revoke_changes(evt=None,dic=dic):
            if tkMessageBox.askyesno(dic['name'],"Dismiss all changes?"):
                dic['ignore-changes'] = True
                dic['window'].destroy()
        
        menu.add_command(label="revoke changes!",command=revoke_changes)
            
        right_menus[names[i]] = menu
        

    dic['y2name'] = fn

    dic['right_menus'] = right_menus
    dic['left_menus'] = left_menus
    
    def onRightClick(event,dic=dic):
        dic['x'] = event.x+int(canvas.xview()[0]*float(dic['width']))
        dic['y'] = event.y
        dic['right_menus'][dic['y2name'](event.y)].\
                                      post(event.x_root, event.y_root)

    def onLeftClick(event,dic=dic):
        dic['x'] = event.x+int(canvas.xview()[0]*float(dic['width']))
        dic['y'] = event.y
        dic['t'] = float(dic['x'])/float(dic['width'])*float(dic['length'])
        dic['left_menus'][dic['y2name'](event.y)].\
                                      post(event.x_root, event.y_root)

    # better we swap left and right, cannot get used to left-click....
    canvas.tag_bind(canvas_bg,"<Button-1>",onRightClick)
    canvas.tag_bind(canvas_bg,"<Button-3>",onLeftClick)    
       
    canvas.pack(side=TOP,fill=BOTH,expand=1)
    scroller = Scrollbar(window, orient=HORIZONTAL)
    scroller.pack(side=BOTTOM,fill=X,expand=0)    
    scroller.config(command=canvas.xview)
    canvas.configure(xscrollcommand=scroller.set)

    return dic
    

if __name__ == '__main__':
    initialize_char_setup()
    set_default_snippets()
    global ed
    things = [{'y': 55, 'y-max': 59, 'delta-x': 105.0, 'delta-y': 12, 'instrument': 'hh13(ord,stxr)', 't': 3.015625, 'y-min': 0, 'limb': 'right hand', 'x': 0.0, 'type': 'set-instrument'}, {'y': 23, 'y-max': 59, 'delta-x': 80.0, 'delta-y': 11, 'instrument': 'cy15crash(ord)', 't': 1.71875, 'y-min': 0, 'limb': 'right hand', 'x': 123.0, 'type': 'set-instrument', }, {'name': 'hits', 'y-max': 139, 'y': 139, 'old-y': 162, 't': 2.0078125, 'y-min': 80, 'limb': 'left hand', 'x': 257, 'type': 'snippet', 'old-x': 321,'span':63.0/64.0,'scale':1.0,'repeat':1.0}]
    #property_dialog([("t","t =")])
    ed = create_visual_editor(things=things)
    doc = things_to_xml(things)

