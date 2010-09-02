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

from df_xml_thing import *
from Tix import *
from df_global import *
from df_limbs import *
from df_xml_thing import *
import tkMessageBox
from math import floor, cos, pi, log
from df_property_dialog import *
from df_presets import get_preset_fn_list, call_preset_fn
from df_functions import *
from bisect import insort

# snippet interface
# =================
#
# 'apply': function that takes the thing and the concept & tzero as parameter
#          and modifies the concept accordingly
# 'property': function that will pop up the thing's properties dialog
# 'set-delta': function that will be called when the left button is pressed
# 'drag': function that will move the thing's canvas stuff to the new x,y
#         and update accordingly
# 'scale': function that will apply the thing's scale changes (mouse)
# 'span': function that will apply the thing's span
# 'create': function that will create a new thing
# 'restore': restore the canvas objects for a thing


#
#
# helper functions
#

def bind_canvas_objects_to_snippet(dic, canvas, co, snippet, thing, props):
    def button3(event, thing=thing, dic=dic):
        thing['*menu'].post(event.x_root,event.y_root)
    def button1(event, thing=thing):
        snippet['set-delta'](event, thing)
    def b1_motion(event, thing=thing,dic=dic):
        if event.state & 1: #shift
            snippet['span'](event,dic, thing)
        elif event.state & 4: #control
            snippet['scale'](event,dic, thing)
        else:
            snippet['drag'](event,dic, thing)
        snippet['set-delta'](event, thing)
    def b1_double(event, thing=thing,dic=dic):
        props()
        

    for obj in co:
        canvas.tag_bind(obj,"<Button-3>",button3)
        canvas.tag_bind(obj,"<Button-1>",button1)
        canvas.tag_bind(obj,"<B1-Motion>",b1_motion)
        canvas.tag_bind(obj,"<Double-Button-1>",b1_double)

def copy_thing_to_global(thing):
    DfGlobal()["copied-snippet"] = copy_dic_thing(thing)


#
# This file contains all the snippets...
#
#

def set_default_snippets(g=DfGlobal()):
    """Creates the default named snippets database within g"""

    snippets = {}

    snip_list = [get_drop_changes_snippet(),\
                 get_hit_snippet(),\
                 get_alternate_hit_snippet(),\
                 get_cut_out_snippet(),\
                 get_strength_snippet(),\
                 get_multiply_strength_snippet(),\
                 get_emphasize_snippet(),\
                 get_set_last_hit_reduction_snippet(),\
                 get_constant_bpm_snippet(),\
                 get_relative_bpm_snippet(),\
                 get_preset_snippet(),\
                 get_hit_star_snippet(),\
                 get_alternate_hit_star_snippet(),\
                 get_restore_instrument_snippet(),\
                 get_warp_snippet(),\
                 get_punch_snippet()]

    print "...registering snippets: ",

    priorities = {}

    for snippet in snip_list:
        snippets[snippet['name']] = snippet
        priority = snippet['priority']
        priorities[snippet['name']] = priority
        print snippet['name'],"(",priority,")\t",

    print "."

    g['snippets.left hand'] = snippets
    g['snippets.right hand'] = snippets
    g['snippets.left foot'] = snippets
    g['snippets.right foot'] = snippets
    g['snippets.priorities'] = priorities



#
#
#  #####   #####    ####   #####         ##### ##  ##  ####  ##   ##  ##### ######  #####
#  ##  ##  ##  ##  ##  ##  ##  ##       ##     ##  ## ##  ## ###  ## ##     ##     ##
#  ##  ##  ####    ##  ##  ####    ###  ##     ###### ###### ## # ## ## ### ####    #####
#  ##  ##  ##  ##  ##  ##  ##           ##     ##  ## ##  ## ##  ### ##  ## ##          ##
#  #####   ##  ##   ####   ##            ##### ##  ## ##  ## ##   ##  ##### ######  #####
#  
#


def get_drop_changes_snippet():
    """returns a drop-changes snippet"""
    snippet = {}

    def apply(thing,concept,tzero,snippet=snippet):
        t_start = tzero + thing['t']
        t_end = tzero + thing['t'] + thing['span']
        limb = thing['limb']
        for t in concept.change_instruments:
            if t_start <= t <= t_end:
                l = concept.change_instruments[t]
                if limb in l:
                    l.pop(limb)
        concept.prepare_change_instruments()


    def update_span(dic,thing):
        w = int(thing['span']/float(dic['length'])*float(dic['width']))
        if w < 50:
            w = 50
        canvas = dic['canvas']
        for obj in thing['*objects']:
            coords = canvas.coords(obj)
            if len(coords)==4:
                coords[2] = coords[0] + w
                canvas.coords(obj,*coords)

    def property(dic,thing,snippet=snippet):
        values = {'span':thing['span'],\
                  't':thing['t']}

        property_dialog([("t = ","t"),\
                         ("span = ","span")],\
                        values=values,\
                        parent=dic['window'])
        
        if values['span'] != str(thing['span']):
            try:
                new_span = float(values['span'])
            except:
                pass
            else:
                thing['span'] = new_span
                update_span(dic,thing)

        if values['t'] != str(thing['t']):
            try:
                new_t = float(values['t'])
            except:
                pass
            else:
                thing['t'] = new_t
                x = float(dic['width'])*new_t/float(dic['length'])
                delta_x = x-thing['x']
                thing['x'] = x
                canvas = dic['canvas']
                for obj in thing['*objects']:
                    xys = canvas.coords(obj)
                    for i in range(len(xys)):
                        if not i%2:
                            xys[i] += delta_x
                    canvas.coords(obj,*xys)
        
        

    def set_delta(event, thing,snippet=snippet):
        thing['old-x'] = event.x
        thing['old-y'] = event.y

       

    def drag(event,dic,thing,snippet=snippet):
        delta_x = event.x - thing['old-x']
        delta_y = event.y - thing['old-y']
        x = thing['x']+delta_x
        y = thing['y']+delta_y
        if y < thing['y-min']:
            y = thing['y-min']
        elif y > thing['y-max']:
            y = thing['y-max']
        delta_x = x-thing['x']
        delta_y = y-thing['y']
        t = float(x)*float(dic['length'])/float(dic['width'])
        dic_extend(thing,{'x':x,'y':y,'t':t})
        canvas = dic['canvas']
        for obj in thing['*objects']:
            xys = canvas.coords(obj)
            for i in range(len(xys)):
                if i%2:
                    xys[i] += delta_y
                else:
                    xys[i] += delta_x
            canvas.coords(obj,*xys)

        

    def span(event,dic,thing,snippet=snippet):
        delta_x = event.x - thing['old-x']
        delta_t = float(delta_x)/float(dic['width'])*float(dic['length'])
        thing['span'] += delta_t        
        update_span(dic,thing)

    def restore(dic,thing,snippet=snippet):
        limb = thing['limb']
        t = thing['t']
        x = int(float(t)*float(dic['width'])/float(dic['length']))
        thing['x'] = x
        y = thing['y']
        
        y_min = dic['y_minmargins'][limb]
        y_max = dic['y_margins'][limb]
        
        thing['y-min'] = y_min
        thing['y-max'] = y_max-21

        canvas = dic['canvas']
        

        w = int(thing['span']/float(dic['length'])*float(dic['width']))
        if w < 50:
            w = 50

        box = canvas.create_rectangle(x,y,x+w,y+20,fill="#880000",outline="#553333")
        text = canvas.create_text(x+2,y+2,text=snippet['name'],fill="#330000",\
                                  anchor=NW)
        
        objects = [box, text]

        thing['*objects'] = objects

        menu = Menu(dic['window'],tearoff=0)

        def properties(thing=thing,dic=dic,snippet=snippet):
            snippet['property'](dic,thing)

        def removeThing(thing=thing,dic=dic):
            canvas = dic['canvas']
            for o in thing['*objects']:
                canvas.delete(o)
            for m in thing['*marks']:
                canvas.delete(m)
            dic['things'].remove(thing)

        menu.add_command(label="Copy",\
                         command=lambda t=thing:copy_thing_to_global(t))
        menu.add_command(label="Properties",command=properties)
        menu.add_command(label="Remove",command=removeThing)
        menu.add_separator()
        menu.add_command(label=snippet['name'])
        
        thing['*menu'] = menu
        
        bind_canvas_objects_to_snippet(dic,canvas,objects,snippet,thing,\
                                       properties)

        thing['*marks'] = []

        


    def create(dic,t,limb,snippet=snippet):
        x = dic['x']
        y = dic['y']
        
        thing = {'type':'snippet',\
                 'name':snippet['name'],\
                 'limb':limb,\
                 'span':snippet['initial-length'],\
                 't':t,\
                 'x':x,\
                 'y':y}

        restore(dic,thing)

        return thing

    dic_extend(snippet,{'apply':apply,\
               'property':property,\
               'set-delta':set_delta,\
               'drag':drag,\
               'scale':span,\
               'span':span,\
               'create':create,\
               'restore':restore,\
               'length':1.0,\
               'priority':-1,\
               'initial-length':1.0,\
               'name':'drop-changes'})

    return snippet





#
#
#   ####   ##  ##  ######        ####   ##  ##  ######
#  ##  ##  ##  ##    ##         ##  ##  ##  ##    ##
#  ##      ##  ##    ##    ###  ##  ##  ##  ##    ##
#  ##  ##  ##  ##    ##         ##  ##  ##  ##    ##
#   ####    ####     ##          ####    ####     ##
#  
#


def get_cut_out_snippet():
    """returns a cuts-out-hits snippet"""
    snippet = {}

    def apply(thing,concept,tzero,snippet=snippet):
        t_start = tzero + thing['t']
        t_end = tzero + thing['t'] + thing['span']
        limb = thing['limb']
        old_potential = concept.potential_funs[limb]
        barrier1 = floor(old_potential(t_start))
        barrier2 = floor(old_potential(t_end))
        
        def new_potential(x,fn=old_potential,y1=barrier1,\
                        y2=barrier2):
            y = fn(x)
            if y < y1:
                return y
            if y < y2:
                return y1
            return y - (y2-y1)
        concept.potential_funs[limb] = new_potential


    def update_span(dic,thing):
        w = int(thing['span']/float(dic['length'])*float(dic['width']))
        if w < 50:
            w = 50
        canvas = dic['canvas']
        for obj in thing['*objects']:
            coords = canvas.coords(obj)
            if len(coords)==4:
                coords[2] = coords[0] + w
                canvas.coords(obj,*coords)

    def property(dic,thing,snippet=snippet):
        values = {'span':thing['span'],\
                  't':thing['t']}

        property_dialog([("t = ","t"),\
                         ("span = ","span")],\
                        values=values,\
                        parent=dic['window'])
        
        if values['span'] != str(thing['span']):
            try:
                new_span = float(values['span'])
            except:
                pass
            else:
                thing['span'] = new_span
                update_span(dic,thing)

        if values['t'] != str(thing['t']):
            try:
                new_t = float(values['t'])
            except:
                pass
            else:
                thing['t'] = new_t
                x = float(dic['width'])*new_t/float(dic['length'])
                delta_x = x-thing['x']
                thing['x'] = x
                canvas = dic['canvas']
                for obj in thing['*objects']:
                    xys = canvas.coords(obj)
                    for i in range(len(xys)):
                        if not i%2:
                            xys[i] += delta_x
                    canvas.coords(obj,*xys)
        
        

    def set_delta(event, thing,snippet=snippet):
        thing['old-x'] = event.x
        thing['old-y'] = event.y

       

    def drag(event,dic,thing,snippet=snippet):
        delta_x = event.x - thing['old-x']
        delta_y = event.y - thing['old-y']
        x = thing['x']+delta_x
        y = thing['y']+delta_y
        if y < thing['y-min']:
            y = thing['y-min']
        elif y > thing['y-max']:
            y = thing['y-max']
        delta_x = x-thing['x']
        delta_y = y-thing['y']
        t = float(x)*float(dic['length'])/float(dic['width'])
        dic_extend(thing,{'x':x,'y':y,'t':t})
        canvas = dic['canvas']
        for obj in thing['*objects']:
            xys = canvas.coords(obj)
            for i in range(len(xys)):
                if i%2:
                    xys[i] += delta_y
                else:
                    xys[i] += delta_x
            canvas.coords(obj,*xys)

        

    def span(event,dic,thing,snippet=snippet):
        delta_x = event.x - thing['old-x']
        delta_t = float(delta_x)/float(dic['width'])*float(dic['length'])
        thing['span'] += delta_t        
        update_span(dic,thing)

    def restore(dic,thing,snippet=snippet):
        limb = thing['limb']
        t = thing['t']
        x = int(float(t)*float(dic['width'])/float(dic['length']))
        thing['x'] = x
        y = thing['y']
        
        y_min = dic['y_minmargins'][limb]
        y_max = dic['y_margins'][limb]
        
        thing['y-min'] = y_min
        thing['y-max'] = y_max-21

        canvas = dic['canvas']
        

        w = int(thing['span']/float(dic['length'])*float(dic['width']))
        if w < 50:
            w = 50

        box = canvas.create_rectangle(x,y,x+w,y+20,fill="#00AA00",outline="#335533")
        text = canvas.create_text(x+2,y+2,text=snippet['name'],fill="#335533",\
                                  anchor=NW)
        
        objects = [box, text]

        thing['*objects'] = objects

        menu = Menu(dic['window'],tearoff=0)

        def properties(thing=thing,dic=dic,snippet=snippet):
            snippet['property'](dic,thing)

        def removeThing(thing=thing,dic=dic):
            canvas = dic['canvas']
            for o in thing['*objects']:
                canvas.delete(o)
            for m in thing['*marks']:
                canvas.delete(m)
            dic['things'].remove(thing)

        menu.add_command(label="Copy",\
                         command=lambda t=thing:copy_thing_to_global(t))
        menu.add_command(label="Properties",command=properties)
        menu.add_command(label="Remove",command=removeThing)
        menu.add_separator()
        menu.add_command(label=snippet['name'])
        
        thing['*menu'] = menu
        
        bind_canvas_objects_to_snippet(dic,canvas,objects,snippet,thing,\
                                       properties)

        thing['*marks'] = []

        


    def create(dic,t,limb,snippet=snippet):
        x = dic['x']
        y = dic['y']
        
        thing = {'type':'snippet',\
                 'name':snippet['name'],\
                 'limb':limb,\
                 'span':snippet['initial-length'],\
                 't':t,\
                 'x':x,\
                 'y':y}

        restore(dic,thing)

        return thing

    dic_extend(snippet,{'apply':apply,\
               'property':property,\
               'set-delta':set_delta,\
               'drag':drag,\
               'scale':span,\
               'span':span,\
               'create':create,\
               'restore':restore,\
               'length':1.0,\
               'priority':-1,\
               'initial-length':1.0,\
               'name':'cut-out'})

    return snippet





#
#
#  ##  ##  ##  ######   #####
#  ##  ##  ##    ##    ##    
#  ######  ##    ##     #####
#  ##  ##  ##    ##         ##   
#  ##  ##  ##    ##     #####
#  
#

def get_hit_snippet():
    """returns a simple one-hit-after-another snippet"""
    snippet = {}

    def apply(thing,concept,tzero,snippet=snippet):
        limb = thing['limb']
        old_potential = concept.potential_funs[limb]
        start = tzero + thing['t']
        count = int(thing['span']/float(thing['scale']*snippet['length']))
        if count > 0:
            length = float(count)*snippet['length']*thing['scale']
        else:
            length = thing['scale']/64.0
        end = start+length
        hit_potential = lambda x,t0=start,alpha=float(count)/length: (x-t0)*alpha+1.0
        new_potential = lambda x,f=old_potential,t0=start-thing['scale']/64.0,\
                        t1=end,f2=hit_potential:\
                        f(x) if x < t0 else f(x)+f2(x) if x < t1 else f(x)+f2(end)
        concept.potential_funs[limb] = new_potential

    def make_marks(dic,thing,snippet=snippet):
        canvas = dic['canvas']
        for old_marks in thing['*marks']:
            canvas.delete(old_marks)
        marks = []
        for i in range(int(thing['span']/(snippet['length']*thing['scale']))+1):
            x = (float(i)*thing['scale']+thing['t'])*float(dic['width'])\
                /float(dic['length'])
            line = canvas.create_line(x,thing['y-min'],x,thing['y-max']+20,\
                                      fill="#888833")
            canvas.tag_lower(line)
            marks.append(line)


        thing['*marks'] = marks
        canvas.tag_lower(dic['canvas_bg'])

    def update_span(dic,thing):
        w = int(thing['span']/float(dic['length'])*float(dic['width']))
        if w < 50:
            w = 50
        canvas = dic['canvas']
        for obj in thing['*objects']:
            coords = canvas.coords(obj)
            if len(coords)==4:
                coords[2] = coords[0] + w
                canvas.coords(obj,*coords)
        make_marks(dic,thing)

   

    def property(dic,thing,snippet=snippet):
        repeat_str = str(thing['repeat'])
        values = {'span':str(thing['span']),\
                  't':str(thing['t']),
                  'repeat':repeat_str,\
                  'scale':str(thing['scale'])}
        property_dialog([("t = ","t"),\
                         ("span = ","span"),\
                         ("scale = ","scale"),\
                         ("repeat = ","repeat")],\
                        values=values,parent=dic['window'])
        if values['span'] != str(thing['span']):
            try:
                new_span = float(values['span'])
            except:
                pass
            else:
                thing['span'] = new_span
                thing['repeat'] = thing['span']\
                                  /(float(snippet['length'])*thing['scale'])
                update_span(dic,thing)
        if values['scale'] != str(thing['scale']):
            try:
                new_scale = float(values['scale'])
            except:
                pass
            else:
                thing['scale'] = new_scale
                thing['repeat'] = thing['span']\
                                  /(float(snippet['length'])*thing['scale'])
                update_span(dic,thing)
        if values['repeat'] != repeat_str:
            try:
                new_repeat = float(values['repeat'])
            except:
                pass
            else:
                thing['repeat'] = new_repeat
                thing['span'] = float(thing['scale'])*float(snippet['length'])\
                                *thing['repeat']
                update_span(dic,thing)
        if values['t'] != str(thing['t']):
            try:
                new_t = float(values['t'])
            except:
                pass
            else:
                thing['t'] = new_t
                x = float(dic['width'])*new_t/float(dic['length'])
                delta_x = x-thing['x']
                thing['x'] = x
                canvas = dic['canvas']
                for obj in thing['*objects']:
                    xys = canvas.coords(obj)
                    for i in range(len(xys)):
                        if not i%2:
                            xys[i] += delta_x
                    canvas.coords(obj,*xys)
                make_marks(dic,thing)
        

    def set_delta(event, thing,snippet=snippet):
        thing['old-x'] = event.x
        thing['old-y'] = event.y

       

    def drag(event,dic,thing,snippet=snippet):
        delta_x = event.x - thing['old-x']
        delta_y = event.y - thing['old-y']
        x = thing['x']+delta_x
        y = thing['y']+delta_y
        if y < thing['y-min']:
            y = thing['y-min']
        elif y > thing['y-max']:
            y = thing['y-max']
        delta_x = x-thing['x']
        delta_y = y-thing['y']
        t = float(x)*float(dic['length'])/float(dic['width'])
        dic_extend(thing,{'x':x,'y':y,'t':t})
        canvas = dic['canvas']
        for obj in thing['*objects']:
            xys = canvas.coords(obj)
            for i in range(len(xys)):
                if i%2:
                    xys[i] += delta_y
                else:
                    xys[i] += delta_x
            canvas.coords(obj,*xys)
        make_marks(dic,thing)


    def scale(event,dic,thing,snippet=snippet):
        delta_x = event.x - thing['old-x']
        delta_t = float(delta_x)/float(dic['width'])*float(dic['length'])
        thing['span'] += delta_t
        thing['scale'] = thing['span']/(snippet['length']*thing['repeat'])
        update_span(dic,thing)
        

    def span(event,dic,thing,snippet=snippet):
        delta_x = event.x - thing['old-x']
        delta_t = float(delta_x)/float(dic['width'])*float(dic['length'])
        thing['span'] += delta_t        
        thing['repeat'] = thing['span']/(snippet['length']*thing['scale'])
        update_span(dic,thing)

    def restore(dic,thing,snippet=snippet):
        limb = thing['limb']
        t = thing['t']
        x = int(float(t)*float(dic['width'])/float(dic['length']))
        thing['x'] = x
        y = thing['y']
        
        y_min = dic['y_minmargins'][limb]
        y_max = dic['y_margins'][limb]
        
        thing['y-min'] = y_min
        thing['y-max'] = y_max-21

        canvas = dic['canvas']
        

        w = int(thing['span']/float(dic['length'])*float(dic['width']))
        if w < 50:
            w = 50

        box = canvas.create_rectangle(x,y,x+w,y+20,fill="#335533",outline="green")
        text = canvas.create_text(x+2,y+2,text=snippet['name'],fill="green",\
                                  anchor=NW)
        
        objects = [box, text]

        thing['*objects'] = objects

        menu = Menu(dic['window'],tearoff=0)

        def properties(thing=thing,dic=dic,snippet=snippet):
            snippet['property'](dic,thing)

        def removeThing(thing=thing,dic=dic):
            canvas = dic['canvas']
            for o in thing['*objects']:
                canvas.delete(o)
            for m in thing['*marks']:
                canvas.delete(m)
            dic['things'].remove(thing)

        menu.add_command(label="Copy",\
                         command=lambda t=thing:copy_thing_to_global(t))
        menu.add_command(label="Properties",command=properties)
        menu.add_command(label="Remove",command=removeThing)
        menu.add_separator()
        menu.add_command(label=snippet['name'])
        
        thing['*menu'] = menu
        
        bind_canvas_objects_to_snippet(dic,canvas,objects,snippet,thing,\
                                       properties)

        thing['*marks'] = []
        make_marks(dic,thing)
        


    def create(dic,t,limb,snippet=snippet):
        x = dic['x']
        y = dic['y']
        
        thing = {'type':'snippet',\
                 'name':snippet['name'],\
                 'limb':limb,\
                 'scale':1.0,\
                 'repeat':snippet['initial-length']/snippet['length'],\
                 'span':snippet['initial-length'],\
                 't':t,\
                 'x':x,\
                 'y':y}

        restore(dic,thing)

        return thing

    dic_extend(snippet,{'apply':apply,\
               'property':property,\
               'set-delta':set_delta,\
               'drag':drag,\
               'scale':scale,\
               'span':span,\
               'create':create,\
               'restore':restore,\
               'priority':0,\
               'length':1.0,\
               'initial-length':62.0/63.0,\
               'name':'hits*'})

    return snippet

#
#
#   ####   ##      ######        ##  ##  ##  ######   #####
#  ##  ##  ##        ##          ##  ##  ##    ##    ##    
#  ######  ##        ##    ####  ######  ##    ##     #####
#  ##  ##  ##        ##          ##  ##  ##    ##         ##   
#  ##  ##  ######    ##          ##  ##  ##    ##     #####
#  
#

def even_hits(x):
    if x % 2.0 <= 1.0:
        return floor(x/2.0)+ x%2.0
    else:
        return floor(x/2.0) + 1.0

def odd_hits(x):
    if x % 2.0 >= 1.0:
        return floor(x/2.0)+ x%2.0 - 1.0
    else:
        return floor(x/2.0)

def get_alternate_hit_snippet():
    """returns a modified version of the hit snippet."""
    snippet = get_hit_snippet()
    snippet['name'] = "alt-hits*"

    def apply(thing,concept,tzero,snippet=snippet):
        limb = thing['limb']
        old_potential = concept.potential_funs[limb]
        start = tzero + thing['t']
        count = int(thing['span']/float(thing['scale']*snippet['length']))
        if count > 0:
            length = float(count)*snippet['length']*thing['scale']
        else:
            length = thing['scale']/64.0
        end = start+length
        hit_potential = lambda x,t0=start,alpha=float(count)/length:\
                        even_hits((x-t0)*alpha+1.0)
        new_potential = lambda x,f=old_potential,t0=start-thing['scale']/64.0,\
                        t1=end,f2=hit_potential:\
                        f(x)       if x < t0 else \
                        f(x)+f2(x) if x < t1 else f(x)+f2(end)
        concept.potential_funs[limb] = new_potential
        
        dual_limb = DfGlobal()["dual.limbs"][limb]
        old_potential = concept.potential_funs[dual_limb]
        hit_potential = lambda x,t0=start,alpha=float(count)/length:\
                        odd_hits((x-t0)*alpha+1.0)
        new_potential = lambda x,f=old_potential,t0=start-thing['scale']/64.0,\
                        t1=end,f2=hit_potential:\
                        f(x)       if x < t0 else \
                        f(x)+f2(x) if x < t1 else f(x)+f2(end)
        concept.potential_funs[dual_limb] = new_potential
    
    snippet['apply'] = apply
  
    return snippet


#
#
#    #####  ######  #####   ######  ##   ##   #####   ######  ##  ##
#   ##        ##    ##  ##  ##      ###  ##  ##         ##    ##  ##
#    #####    ##    #####   ####    ## # ##  ##  ##     ##    ######
#        ##   ##    ##  ##  ##      ##  ###  ##   ##    ##    ##  ##
#    #####    ##    ##  ##  ######  ##   ##   #####     ##    ##  ##
#  
#

def get_strength_snippet():
    """returns a simple hit-strength-setting snippet"""
    snippet = {}

    def apply(thing,concept,tzero,snippet=snippet):
        limb = thing['limb']        
        start = tzero + thing['t']
        end = start + thing['span']
        old_strength = concept.strength_funs[limb]
        def wave(t,d=(thing['gap']-thing['bar'])/2.0,\
                 bar=thing['bar'],f=2.0*pi/thing['scale']):
            return (cos(f*t)-1.0)*d + bar
            
        def new_strength(t,t0=start,t1=end,\
                         t00=start-1.0/64.0,t11=end+1.0/64.0,\
                         fn=old_strength,\
                         fn2=wave):
            if t < t00:
                return fn(t)
            elif t > t11:
                return fn(t)
            elif t < t0:
                c = (t-t00)*64.0
                return fn(t)*(1.0-c) + fn2(t)*c
            elif t > t1:
                c = (t-t1)*64.0
                return fn(t)*c + fn2(t)*(1.0-c)
            else:
                return fn2(t)
        concept.strength_funs[limb] = new_strength

    def make_marks(dic,thing,snippet=snippet):
        canvas = dic['canvas']
        for old_marks in thing['*marks']:
            canvas.delete(old_marks)
        marks = []
        for i in range(int(thing['span']/(snippet['length']*thing['scale']))+1):
            x = (float(i)*thing['scale']+thing['t'])*float(dic['width'])\
                /float(dic['length'])
            line = canvas.create_line(x,thing['y-min'],x,thing['y-max']+20,\
                                      fill="#0000CC")
            canvas.tag_lower(line)
            marks.append(line)

        gap_x = (0.5*thing['scale']+thing['t'])*float(dic['width'])\
                /float(dic['length']) 

        bar_x = thing['t']*float(dic['width'])/float(dic['length']) 

        bar_text = canvas.create_text(bar_x,thing['y']-30,fill="yellow",\
                                      anchor=N,text= "%.2f"%thing['bar'])

        gap_text = canvas.create_text(gap_x,thing['y']-15,fill="yellow",\
                                      anchor=N,text= "%.2f"%thing['gap'])

        marks.append(bar_text)
        marks.append(gap_text)
        
        thing['*marks'] = marks
        canvas.tag_lower(dic['canvas_bg'])

    def update_span(dic,thing):
        w = int(thing['span']/float(dic['length'])*float(dic['width']))
        if w < 50:
            w = 50
        canvas = dic['canvas']
        for obj in thing['*objects']:
            coords = canvas.coords(obj)
            if len(coords)==4:
                coords[2] = coords[0] + w
                canvas.coords(obj,*coords)
        make_marks(dic,thing)

   

    def property(dic,thing,snippet=snippet):
        repeat_str = str(thing['repeat'])
        values = {'span':str(thing['span']),\
                  't':str(thing['t']),
                  'repeat':repeat_str,\
                  'scale':str(thing['scale']),\
                  'bar':str(thing['bar']),\
                  'gap':str(thing['gap'])}
        property_dialog([("t = ","t"),\
                         ("span = ","span"),\
                         ("scale = ","scale"),\
                         ("repeat = ","repeat"),\
                         ("bar strength = ","bar"),\
                         ("gap strength = ","gap")],\
                        values=values,parent=dic['window'])
        try:
            thing['bar'] = float(values['bar'])
        except:
            pass
        try:
            thing['gap'] = float(values['gap'])
        except:
            pass
        if values['span'] != str(thing['span']):
            try:
                new_span = float(values['span'])
            except:
                pass
            else:
                thing['span'] = new_span
                thing['repeat'] = thing['span']\
                                  /(float(snippet['length'])*thing['scale'])
                update_span(dic,thing)
        if values['scale'] != str(thing['scale']):
            try:
                new_scale = float(values['scale'])
            except:
                pass
            else:
                thing['scale'] = new_scale
                thing['repeat'] = thing['span']\
                                  /(float(snippet['length'])*thing['scale'])
                update_span(dic,thing)
        if values['repeat'] != repeat_str:
            try:
                new_repeat = float(values['repeat'])
            except:
                pass
            else:
                thing['repeat'] = new_repeat
                thing['span'] = float(thing['scale'])*float(snippet['length'])\
                                *thing['repeat']
                update_span(dic,thing)
        if values['t'] != str(thing['t']):
            try:
                new_t = float(values['t'])
            except:
                pass
            else:
                thing['t'] = new_t
                x = float(dic['width'])*new_t/float(dic['length'])
                delta_x = x-thing['x']
                thing['x'] = x
                canvas = dic['canvas']
                for obj in thing['*objects']:
                    xys = canvas.coords(obj)
                    for i in range(len(xys)):
                        if not i%2:
                            xys[i] += delta_x
                    canvas.coords(obj,*xys)
        make_marks(dic,thing)
        

    def set_delta(event, thing,snippet=snippet):
        thing['old-x'] = event.x
        thing['old-y'] = event.y
        thing['old-bar'] = thing['bar']
        thing['old-gap'] = thing['gap']

       

    def drag(event,dic,thing,snippet=snippet):
        delta_x = event.x - thing['old-x']
        delta_y = event.y - thing['old-y']
        x = thing['x']+delta_x
        y = thing['y']+delta_y
        if y < thing['y-min']:
            y = thing['y-min']
        elif y > thing['y-max']:
            y = thing['y-max']
        delta_x = x-thing['x']
        delta_y = y-thing['y']
        t = float(x)*float(dic['length'])/float(dic['width'])
        dic_extend(thing,{'x':x,'y':y,'t':t})
        canvas = dic['canvas']
        for obj in thing['*objects']:
            xys = canvas.coords(obj)
            for i in range(len(xys)):
                if i%2:
                    xys[i] += delta_y
                else:
                    xys[i] += delta_x
            canvas.coords(obj,*xys)
        make_marks(dic,thing)


    def scale(event,dic,thing,snippet=snippet):
        delta_x = event.x - thing['old-x']
        delta_y = event.y - thing['old-y']
        delta_t = float(delta_x)/float(dic['width'])*float(dic['length'])
        thing['span'] += delta_t
        thing['gap'] = thing['old-gap'] - float(delta_y)/100.0
        thing['scale'] = thing['span']/(snippet['length']*thing['repeat'])
        update_span(dic,thing)
        

    def span(event,dic,thing,snippet=snippet):
        delta_x = event.x - thing['old-x']
        delta_y = event.y - thing['old-y']        
        delta_t = float(delta_x)/float(dic['width'])*float(dic['length'])
        thing['span'] += delta_t
        thing['bar'] = thing['old-bar'] - float(delta_y)/100.0        
        thing['repeat'] = thing['span']/(snippet['length']*thing['scale'])
        update_span(dic,thing)

    def restore(dic,thing,snippet=snippet):
        limb = thing['limb']
        t = thing['t']
        x = int(float(t)*float(dic['width'])/float(dic['length']))
        thing['x'] = x
        y = thing['y']
        
        y_min = dic['y_minmargins'][limb]
        y_max = dic['y_margins'][limb]
        
        thing['y-min'] = y_min
        thing['y-max'] = y_max-21

        canvas = dic['canvas']
        

        w = int(thing['span']/float(dic['length'])*float(dic['width']))
        if w < 50:
            w = 50

        box = canvas.create_rectangle(x,y,x+w,y+20,fill="#444400",outline="yellow")
        text = canvas.create_text(x+2,y+2,text=snippet['name'],fill="yellow",\
                                  anchor=NW)
        
        objects = [box, text]

        thing['*objects'] = objects

        menu = Menu(dic['window'],tearoff=0)

        def properties(thing=thing,dic=dic,snippet=snippet):
            snippet['property'](dic,thing)

        def removeThing(thing=thing,dic=dic):
            canvas = dic['canvas']
            for o in thing['*objects']:
                canvas.delete(o)
            for m in thing['*marks']:
                canvas.delete(m)
            dic['things'].remove(thing)

        menu.add_command(label="Copy",\
                         command=lambda t=thing:copy_thing_to_global(t))
        menu.add_command(label="Properties",command=properties)
        menu.add_command(label="Remove",command=removeThing)
        menu.add_separator()
        menu.add_command(label=snippet['name'])
        
        thing['*menu'] = menu
        
        bind_canvas_objects_to_snippet(dic,canvas,objects,snippet,thing,\
                                       properties)

        thing['*marks'] = []
        make_marks(dic,thing)
        


    def create(dic,t,limb,snippet=snippet):
        x = dic['x']
        y = dic['y']
        
        thing = {'type':'snippet',\
                 'name':snippet['name'],\
                 'limb':limb,\
                 'scale':1.0,\
                 'repeat':snippet['initial-length']/snippet['length'],\
                 'span':snippet['initial-length'],\
                 'bar':snippet['initial-bar'],\
                 'gap':snippet['initial-gap'],\
                 't':t,\
                 'x':x,\
                 'y':y}

        restore(dic,thing)

        return thing

    dic_extend(snippet,{'apply':apply,\
               'property':property,\
               'set-delta':set_delta,\
               'drag':drag,\
               'scale':scale,\
               'span':span,\
               'create':create,\
               'restore':restore,\
               'priority':0,\
               'length':1.0,\
               'initial-bar':0.9,\
               'initial-gap':0.7,\
               'initial-length':1.0,\
               'name':'strength'})

    return snippet

def get_multiply_strength_snippet():
    """returns a multiplicative hit-strength-setting snippet"""
    snippet = get_strength_snippet()
    snippet['name'] = 'multiply-strength'
    snippet['initial-bar'] = 1.1
    snippet['initial-gap'] = 0.5

    def apply(thing,concept,tzero,snippet=snippet):
        limb = thing['limb']        
        start = tzero + thing['t']
        end = start + thing['span']
        old_strength = concept.strength_funs[limb]
        def wave(t,d=(thing['gap']-thing['bar'])/2.0,\
                 bar=thing['bar'],f=2.0*pi/thing['scale']):
            return (cos(f*t)-1.0)*d + bar
            
        def new_strength(t,t0=start,t1=end,\
                         t00=start-1.0/64.0,t11=end+1.0/64.0,\
                         fn=old_strength,\
                         fn2=wave):
            if t < t00:
                return fn(t)
            elif t > t11:
                return fn(t)
            elif t < t0:
                c = (t-t00)*64.0
                return fn(t)*(1.0-c) + fn(t)*fn2(t)*c
            elif t > t1:
                c = (t-t1)*64.0
                return fn(t)*c + fn(t)*fn2(t)*(1.0-c)
            else:
                return fn(t)*fn2(t)
        concept.strength_funs[limb] = new_strength
    snippet['apply'] = apply
    snippet['priority'] = 1
    return snippet


#
#
# ######  ##  ##      #####    ##    ######  ######
# ##      ######     ##        ##        ##  ##    
# ####    ##  ##      #####    ##      ##    ####  
# ##      ##  ##          ##   ##     ##     ##    
# ######  ##  ## ##   #####    ##    ######  ######
#  
#

def get_emphasize_snippet():
    """returns a emphasize hit-strength-setting snippet"""
    snippet = {}

    def apply(thing,concept,tzero,snippet=snippet):
        limb = thing['limb']        
        start = tzero + thing['t']
        end = start + thing['span']
        old_strength = concept.strength_funs[limb]
        gap = thing['gap']
            
        def new_strength(t,t00=start,t11=end,\
                         t0=start+gap,t1=end-gap,\
                         fn=old_strength,gap=gap,\
                         lvl0=thing['level'],\
                         lvl1=thing['level1'],\
                         span=thing['span']-2.0*gap):
            if t < t00:
                return fn(t)
            elif t > t11:
                return fn(t)
            elif t < t0:
                c = (t-t00)/gap
                return fn(t)*(1.0-c) + fn(t)*lvl0*c
            elif t > t1:
                c = (t-t1)/gap
                return fn(t)*c + fn(t)*lvl1*(1.0-c)
            else:
                c = (t-t0)/span
                return fn(t)*(c*lvl1+(1.0-c)*lvl0)
        concept.strength_funs[limb] = new_strength

    def make_marks(dic,thing,snippet=snippet):
        canvas = dic['canvas']
        for old_marks in thing['*marks']:
            canvas.delete(old_marks)
        marks = []
        for i in [thing['gap'],thing['span']-thing['gap']]:
            x = (i+thing['t'])*float(dic['width']) / float(dic['length'])
            line = canvas.create_line(x,thing['y-min'],x,thing['y-max']+20,\
                                      fill="#0000CC")
            canvas.tag_lower(line)
            marks.append(line)

        level0_x = (thing['t']+thing['gap'])*float(dic['width'])\
                /float(dic['length'])

        level1_x = (thing['t']+thing['span']-thing['gap'])*float(dic['width'])\
                /float(dic['length'])

        gap_x = thing['t']*float(dic['width'])/float(dic['length']) 

        level0_text = canvas.create_text(level0_x,thing['y']-20,fill="yellow",\
                                      anchor=N,text= "%.2f"%thing['level'])

        level1_text = canvas.create_text(level1_x,thing['y']-20,fill="yellow",\
                                      anchor=N,text= "%.2f"%thing['level1'])

        gap_text = canvas.create_text(gap_x,thing['y']-15,fill="blue",\
                                      anchor=N,text= "%.2f"%thing['gap'])

        marks.append(level0_text)
        marks.append(level1_text)        
        marks.append(gap_text)
        
        thing['*marks'] = marks
        canvas.tag_lower(dic['canvas_bg'])

    def update_span(dic,thing):
        w = int(thing['span']/float(dic['length'])*float(dic['width']))
        if w < 50:
            w = 50
        canvas = dic['canvas']
        for obj in thing['*objects']:
            coords = canvas.coords(obj)
            if len(coords)==4:
                coords[2] = coords[0] + w
                canvas.coords(obj,*coords)
        make_marks(dic,thing)

   

    def property(dic,thing,snippet=snippet):
        repeat_str = str(thing['repeat'])
        values = {'span':str(thing['span']),\
                  't':str(thing['t']),
                  'repeat':repeat_str,\
                  'scale':str(thing['scale']),\
                  'level':str(thing['level']),\
                  'level1':str(thing['level1']),\
                  'gap':str(thing['gap'])}
        property_dialog([("t = ","t"),\
                         ("span = ","span"),\
                         ("gap length = ","gap"),\
                         ("start emphasize factor = ","level"),\
                         ("end emphasize factor = ","level1")],\
                        values=values,parent=dic['window'])
        try:
            thing['level'] = float(values['level'])
        except:
            pass
        try:
            thing['level1'] = float(values['level1'])
        except:
            pass        
        try:
            thing['gap'] = float(values['gap'])
        except:
            pass
        if values['span'] != str(thing['span']):
            try:
                new_span = float(values['span'])
            except:
                pass
            else:
                thing['span'] = new_span
                thing['repeat'] = thing['span']\
                                  /(float(snippet['length'])*thing['scale'])
                update_span(dic,thing)
        if values['scale'] != str(thing['scale']):
            try:
                new_scale = float(values['scale'])
            except:
                pass
            else:
                thing['scale'] = new_scale
                thing['repeat'] = thing['span']\
                                  /(float(snippet['length'])*thing['scale'])
                update_span(dic,thing)
        if values['repeat'] != repeat_str:
            try:
                new_repeat = float(values['repeat'])
            except:
                pass
            else:
                thing['repeat'] = new_repeat
                thing['span'] = float(thing['scale'])*float(snippet['length'])\
                                *thing['repeat']
                update_span(dic,thing)
        if values['t'] != str(thing['t']):
            try:
                new_t = float(values['t'])
            except:
                pass
            else:
                thing['t'] = new_t
                x = float(dic['width'])*new_t/float(dic['length'])
                delta_x = x-thing['x']
                thing['x'] = x
                canvas = dic['canvas']
                for obj in thing['*objects']:
                    xys = canvas.coords(obj)
                    for i in range(len(xys)):
                        if not i%2:
                            xys[i] += delta_x
                    canvas.coords(obj,*xys)
        make_marks(dic,thing)
        

    def set_delta(event, thing,snippet=snippet):
        thing['old-x'] = event.x
        thing['old-y'] = event.y
        thing['old-level'] = thing['level']
        thing['old-level1'] = thing['level1']
        thing['old-gap'] = thing['gap']

       

    def drag(event,dic,thing,snippet=snippet):
        delta_x = event.x - thing['old-x']
        delta_y = event.y - thing['old-y']
        x = thing['x']+delta_x
        y = thing['y']+delta_y
        if y < thing['y-min']:
            y = thing['y-min']
        elif y > thing['y-max']:
            y = thing['y-max']
        delta_x = x-thing['x']
        delta_y = y-thing['y']
        t = float(x)*float(dic['length'])/float(dic['width'])
        dic_extend(thing,{'x':x,'y':y,'t':t})
        canvas = dic['canvas']
        for obj in thing['*objects']:
            xys = canvas.coords(obj)
            for i in range(len(xys)):
                if i%2:
                    xys[i] += delta_y
                else:
                    xys[i] += delta_x
            canvas.coords(obj,*xys)
        make_marks(dic,thing)


    def scale(event,dic,thing,snippet=snippet):
        delta_x = event.x - thing['old-x']
        delta_y = event.y - thing['old-y']
        delta_t = float(delta_x)/float(dic['width'])*float(dic['length'])   
        thing['level1'] = thing['old-level1'] - float(delta_y)/100.0          
        thing['gap'] = thing['old-gap'] + delta_t
        thing['scale'] = thing['span']/(snippet['length']*thing['repeat'])
        update_span(dic,thing)
        

    def span(event,dic,thing,snippet=snippet):
        delta_x = event.x - thing['old-x']
        delta_y = event.y - thing['old-y']        
        delta_t = float(delta_x)/float(dic['width'])*float(dic['length'])
        thing['span'] += delta_t
        thing['level'] = thing['old-level'] - float(delta_y)/100.0        
        thing['repeat'] = thing['span']/(snippet['length']*thing['scale'])
        update_span(dic,thing)

    def restore(dic,thing,snippet=snippet):
        limb = thing['limb']
        t = thing['t']
        x = int(float(t)*float(dic['width'])/float(dic['length']))
        thing['x'] = x
        y = thing['y']
        
        y_min = dic['y_minmargins'][limb]
        y_max = dic['y_margins'][limb]
        
        thing['y-min'] = y_min
        thing['y-max'] = y_max-21

        canvas = dic['canvas']
        

        w = int(thing['span']/float(dic['length'])*float(dic['width']))
        if w < 50:
            w = 50

        box = canvas.create_rectangle(x,y,x+w,y+20,fill="#666600",outline="yellow")
        text = canvas.create_text(x+2,y+2,text=snippet['name'],fill="yellow",\
                                  anchor=NW)
        
        objects = [box, text]

        thing['*objects'] = objects

        menu = Menu(dic['window'],tearoff=0)

        def properties(thing=thing,dic=dic,snippet=snippet):
            snippet['property'](dic,thing)

        def removeThing(thing=thing,dic=dic):
            canvas = dic['canvas']
            for o in thing['*objects']:
                canvas.delete(o)
            for m in thing['*marks']:
                canvas.delete(m)
            dic['things'].remove(thing)

        menu.add_command(label="Copy",\
                         command=lambda t=thing:copy_thing_to_global(t))
        menu.add_command(label="Properties",command=properties)
        menu.add_command(label="Remove",command=removeThing)
        menu.add_separator()
        menu.add_command(label=snippet['name'])
        
        thing['*menu'] = menu
        
        bind_canvas_objects_to_snippet(dic,canvas,objects,snippet,thing,\
                                       properties)

        thing['*marks'] = []
        make_marks(dic,thing)
        


    def create(dic,t,limb,snippet=snippet):
        x = dic['x']
        y = dic['y']
        
        thing = {'type':'snippet',\
                 'name':snippet['name'],\
                 'limb':limb,\
                 'scale':1.0,\
                 'repeat':snippet['initial-length']/snippet['length'],\
                 'span':snippet['initial-length'],\
                 'level':snippet['initial-level'],\
                 'level1':snippet['initial-level1'],\
                 'gap':snippet['initial-gap'],\
                 't':t,\
                 'x':x,\
                 'y':y}

        restore(dic,thing)

        return thing

    dic_extend(snippet,{'apply':apply,\
               'property':property,\
               'set-delta':set_delta,\
               'drag':drag,\
               'scale':scale,\
               'span':span,\
               'create':create,\
               'restore':restore,\
               'priority':1,\
               'length':1.0,\
               'initial-level':1.7,\
               'initial-level1':1.0,\
               'initial-gap':1.0/64.0,\
               'initial-length':1.0,\
               'name':'emphasize'})

    return snippet
    

#
#  #####  ######  ######     #####  ###### #####
# ##      ##        ##       ##  ## ##     ##  ##
#  #####  ####      ##   ### #####  ####   ##  ##
#      ## ##        ##       ##  ## ##     ##  ##
#  #####  ######    ##       ##   # ###### #####  ###
#

def get_set_last_hit_reduction_snippet():
    """returns a snippet that sets the last hit time for strength reduction"""
    snippet = {}

    def apply(thing,concept,tzero,snippet=snippet):
        limb = thing['limb']
        start = thing['t'] + tzero
        def cmd(x, limb=limb, last=thing['last_hit']):
            DfGlobal()['limbs'][limb].last_stroke_red = x.tick_parameters['time_after']-last
        concept.add_timed_command(start,cmd)

    def make_marks(dic,thing,snippet=snippet):
        canvas = dic['canvas']
        for old_marks in thing['*marks']:
            canvas.delete(old_marks)
        
        x = (thing['t'])*float(dic['width'])/float(dic['length']) + 5

        marks = [canvas.create_text(x,thing['y']-15,text="%.2f"%thing['last_hit'],\
                                    fill="red",anchor=NW)]
        

        thing['*marks'] = marks
        canvas.tag_lower(dic['canvas_bg'])

    def update_span(dic,thing):
        w = int(thing['span']/float(dic['length'])*float(dic['width']))
        if w < 50:
            w = 50
        canvas = dic['canvas']
        for obj in thing['*objects']:
            coords = canvas.coords(obj)
            if len(coords)==4:
                coords[2] = coords[0] + w
                canvas.coords(obj,*coords)
        make_marks(dic,thing)

   

    def property(dic,thing,snippet=snippet):
        property_dialog([("t = ","t"),\
                         ("reduce like last hit was before (secs)  ","last_hit")],\
                        types={"t":float,"last_hit":float},\
                        values=thing,parent=dic['window'])
        update_span(dic,thing)
        

    def set_delta(event, thing,snippet=snippet):
        thing['old-x'] = event.x
        thing['old-y'] = event.y

       

    def drag(event,dic,thing,snippet=snippet):
        delta_x = event.x - thing['old-x']
        delta_y = event.y - thing['old-y']
        x = thing['x']+delta_x
        y = thing['y']+delta_y
        if y < thing['y-min']:
            y = thing['y-min']
        elif y > thing['y-max']:
            y = thing['y-max']
        delta_x = x-thing['x']
        delta_y = y-thing['y']
        t = float(x)*float(dic['length'])/float(dic['width'])
        dic_extend(thing,{'x':x,'y':y,'t':t})
        canvas = dic['canvas']
        for obj in thing['*objects']:
            xys = canvas.coords(obj)
            for i in range(len(xys)):
                if i%2:
                    xys[i] += delta_y
                else:
                    xys[i] += delta_x
            canvas.coords(obj,*xys)
        make_marks(dic,thing)


    def restore(dic,thing,snippet=snippet):
        limb = thing['limb']
        t = thing['t']
        x = int(float(t)*float(dic['width'])/float(dic['length']))
        thing['x'] = x
        y = thing['y']
        
        y_min = dic['y_minmargins'][limb]
        y_max = dic['y_margins'][limb]
        
        thing['y-min'] = y_min
        thing['y-max'] = y_max-21

        canvas = dic['canvas']
        

        w = int(thing['span']/float(dic['length'])*float(dic['width']))
        if w < 50:
            w = 50

        box = canvas.create_rectangle(x,y,x+w,y+20,fill="#335533",outline="green")
        text = canvas.create_text(x+2,y+2,text=snippet['name'],fill="green",\
                                  anchor=NW)
        
        objects = [box, text]

        thing['*objects'] = objects

        menu = Menu(dic['window'],tearoff=0)

        def properties(thing=thing,dic=dic,snippet=snippet):
            snippet['property'](dic,thing)

        def removeThing(thing=thing,dic=dic):
            canvas = dic['canvas']
            for o in thing['*objects']:
                canvas.delete(o)
            for m in thing['*marks']:
                canvas.delete(m)
            dic['things'].remove(thing)

        menu.add_command(label="Copy",\
                         command=lambda t=thing:copy_thing_to_global(t))
        menu.add_command(label="Properties",command=properties)
        menu.add_command(label="Remove",command=removeThing)
        menu.add_separator()
        menu.add_command(label=snippet['name'])
        
        thing['*menu'] = menu
        
        bind_canvas_objects_to_snippet(dic,canvas,objects,snippet,thing,\
                                       properties)

        thing['*marks'] = []
        make_marks(dic,thing)
        


    def create(dic,t,limb,snippet=snippet):
        x = dic['x']
        y = dic['y']
        
        thing = {'type':'snippet',\
                 'name':snippet['name'],\
                 'limb':limb,\
                 'scale':1.0,\
                 'repeat':snippet['initial-length']/snippet['length'],\
                 'span':snippet['initial-length'],\
                 'last_hit':snippet['initial-last_hit'],\
                 't':t,\
                 'x':x,\
                 'y':y}

        restore(dic,thing)

        return thing

    
    dic_extend(snippet,{'apply':apply,\
               'property':property,\
               'set-delta':set_delta,\
               'drag':drag,\
               'scale':drag,\
               'span':drag,\
               'create':create,\
               'restore':restore,\
               'priority':0,\
               'length':1.0,\
               'initial-length':62.0/63.0,\
               'initial-last_hit':4.0,\
               'name':'set-reduction'})
    
    return snippet


#
#
# #####   #####   ##  ##    #####   ######  ##
# ##  ##  ##  ##  ######    ##  ##  ##      ##
# #####   #####   ##  ## ## #####   ####    ##
# ##  ##  ##      ##  ##    ## ##   ##      ##
# #####   ##      ##  ##    ##  ##  ######  ###### ##
#  
#

def get_relative_bpm_snippet():
    """returns a relative-bpm-setting snippet"""
    snippet = {}

    def apply(thing,concept,tzero,snippet=snippet):
        start_time = tzero + thing['t']
        def set_bpm(x=None, start=thing['level'],\
                    end=thing['level1'],\
                    span=thing['span']):
            DfGlobal()["mind"].set_beatspersecond_relative_rate(start,end,span)
        concept.add_timed_command(start_time,set_bpm)

    def make_marks(dic,thing,snippet=snippet):
        canvas = dic['canvas']
        for old_marks in thing['*marks']:
            canvas.delete(old_marks)
        marks = []

        level0_x = (thing['t'])*float(dic['width'])\
                /float(dic['length'])

        level1_x = (thing['t']+thing['span'])*float(dic['width'])\
                /float(dic['length'])

        gap_x = thing['t']*float(dic['width'])/float(dic['length']) 

        level0_text = canvas.create_text(level0_x,thing['y']-20,fill="magenta",\
                                      anchor=NW,text= "%.1f"%(thing['level']*60.0))

        level1_text = canvas.create_text(level1_x,thing['y']-20,fill="magenta",\
                                      anchor=NE,text= "%.1f"%(thing['level1']*60.0))


        marks.append(level0_text)
        marks.append(level1_text)        

        
        thing['*marks'] = marks
        canvas.tag_lower(dic['canvas_bg'])

    def update_span(dic,thing):
        w = int(thing['span']/float(dic['length'])*float(dic['width']))
        if w < 50:
            w = 50
        canvas = dic['canvas']
        for obj in thing['*objects']:
            coords = canvas.coords(obj)
            if len(coords)==4:
                coords[2] = coords[0] + w
                canvas.coords(obj,*coords)
        make_marks(dic,thing)

   

    def property(dic,thing,snippet=snippet):
        repeat_str = str(thing['repeat'])
        values = {'span':str(thing['span']),\
                  't':str(thing['t']),
                  'repeat':repeat_str,\
                  'scale':str(thing['scale']),\
                  'level':str(thing['level']*60.0),\
                  'level1':str(thing['level1']*60.0),\
                  'gap':str(thing['gap'])}
        property_dialog([("t = ","t"),\
                         ("span = ","span"),\
                         ("start beats per minute = ","level"),\
                         ("end beats per minute = ","level1")],\
                        types={'level':lambda x: float(x)/60.0,\
                              'level1':lambda x: float(x)/60.0},\
                        values=values,parent=dic['window'])
        try:
            thing['level'] = float(values['level'])
        except:
            pass
        try:
            thing['level1'] = float(values['level1'])
        except:
            pass        
        try:
            thing['gap'] = float(values['gap'])
        except:
            pass
        if values['span'] != str(thing['span']):
            try:
                new_span = float(values['span'])
            except:
                pass
            else:
                thing['span'] = new_span
                thing['repeat'] = thing['span']\
                                  /(float(snippet['length'])*thing['scale'])
                update_span(dic,thing)
        if values['scale'] != str(thing['scale']):
            try:
                new_scale = float(values['scale'])
            except:
                pass
            else:
                thing['scale'] = new_scale
                thing['repeat'] = thing['span']\
                                  /(float(snippet['length'])*thing['scale'])
                update_span(dic,thing)
        if values['repeat'] != repeat_str:
            try:
                new_repeat = float(values['repeat'])
            except:
                pass
            else:
                thing['repeat'] = new_repeat
                thing['span'] = float(thing['scale'])*float(snippet['length'])\
                                *thing['repeat']
                update_span(dic,thing)
        if values['t'] != str(thing['t']):
            try:
                new_t = float(values['t'])
            except:
                pass
            else:
                thing['t'] = new_t
                x = float(dic['width'])*new_t/float(dic['length'])
                delta_x = x-thing['x']
                thing['x'] = x
                canvas = dic['canvas']
                for obj in thing['*objects']:
                    xys = canvas.coords(obj)
                    for i in range(len(xys)):
                        if not i%2:
                            xys[i] += delta_x
                    canvas.coords(obj,*xys)
        make_marks(dic,thing)
        

    def set_delta(event, thing,snippet=snippet):
        thing['old-x'] = event.x
        thing['old-y'] = event.y
        thing['old-level'] = thing['level']
        thing['old-level1'] = thing['level1']
        thing['old-gap'] = thing['gap']

       

    def drag(event,dic,thing,snippet=snippet):
        delta_x = event.x - thing['old-x']
        delta_y = event.y - thing['old-y']
        x = thing['x']+delta_x
        y = thing['y']+delta_y
        if y < thing['y-min']:
            y = thing['y-min']
        elif y > thing['y-max']:
            y = thing['y-max']
        delta_x = x-thing['x']
        delta_y = y-thing['y']
        t = float(x)*float(dic['length'])/float(dic['width'])
        dic_extend(thing,{'x':x,'y':y,'t':t})
        canvas = dic['canvas']
        for obj in thing['*objects']:
            xys = canvas.coords(obj)
            for i in range(len(xys)):
                if i%2:
                    xys[i] += delta_y
                else:
                    xys[i] += delta_x
            canvas.coords(obj,*xys)
        make_marks(dic,thing)


    def scale(event,dic,thing,snippet=snippet):
        delta_x = event.x - thing['old-x']
        delta_y = event.y - thing['old-y']
        delta_t = float(delta_x)/float(dic['width'])*float(dic['length'])   
        thing['level1'] = thing['old-level1'] - float(delta_y)/100.0          
        thing['gap'] = thing['old-gap'] + delta_t
        thing['scale'] = thing['span']/(snippet['length']*thing['repeat'])
        update_span(dic,thing)
        

    def span(event,dic,thing,snippet=snippet):
        delta_x = event.x - thing['old-x']
        delta_y = event.y - thing['old-y']        
        delta_t = float(delta_x)/float(dic['width'])*float(dic['length'])
        thing['span'] += delta_t
        thing['level'] = thing['old-level'] - float(delta_y)/100.0        
        thing['repeat'] = thing['span']/(snippet['length']*thing['scale'])
        update_span(dic,thing)

    def restore(dic,thing,snippet=snippet):
        limb = thing['limb']
        t = thing['t']
        x = int(float(t)*float(dic['width'])/float(dic['length']))
        thing['x'] = x
        y = thing['y']
        
        y_min = dic['y_minmargins'][limb]
        y_max = dic['y_margins'][limb]
        
        thing['y-min'] = y_min
        thing['y-max'] = y_max-21

        canvas = dic['canvas']
        

        w = int(thing['span']/float(dic['length'])*float(dic['width']))
        if w < 50:
            w = 50

        box = canvas.create_rectangle(x,y,x+w,y+20,fill="#CC00CC",outline="#FF00FF")
        text = canvas.create_text(x+2,y+2,text=snippet['name'],fill="#330033",\
                                  anchor=NW)
        
        objects = [box, text]

        thing['*objects'] = objects

        menu = Menu(dic['window'],tearoff=0)

        def properties(thing=thing,dic=dic,snippet=snippet):
            snippet['property'](dic,thing)

        def removeThing(thing=thing,dic=dic):
            canvas = dic['canvas']
            for o in thing['*objects']:
                canvas.delete(o)
            for m in thing['*marks']:
                canvas.delete(m)
            dic['things'].remove(thing)

        menu.add_command(label="Copy",\
                         command=lambda t=thing:copy_thing_to_global(t))
        menu.add_command(label="Properties",command=properties)
        menu.add_command(label="Remove",command=removeThing)
        menu.add_separator()
        menu.add_command(label=snippet['name'])
        
        thing['*menu'] = menu
        
        bind_canvas_objects_to_snippet(dic,canvas,objects,snippet,thing,\
                                       properties)

        thing['*marks'] = []
        make_marks(dic,thing)
        


    def create(dic,t,limb,snippet=snippet):
        x = dic['x']
        y = dic['y']
        
        thing = {'type':'snippet',\
                 'name':snippet['name'],\
                 'limb':limb,\
                 'scale':1.0,\
                 'repeat':snippet['initial-length']/snippet['length'],\
                 'span':snippet['initial-length'],\
                 'level':snippet['initial-level'],\
                 'level1':snippet['initial-level'],\
                 'gap':snippet['initial-gap'],\
                 't':t,\
                 'x':x,\
                 'y':y}

        restore(dic,thing)

        return thing

    dic_extend(snippet,{'apply':apply,\
               'property':property,\
               'set-delta':set_delta,\
               'drag':drag,\
               'scale':scale,\
               'span':span,\
               'create':create,\
               'restore':restore,\
               'priority':0,\
               'length':1.0,\
               'initial-level':2.0,\
               'initial-gap':1.0/64.0,\
               'initial-length':1.0,\
               'name':'relative-bpm'})

    return snippet

    
#
#
# #####   #####   ##  ##     ####    ####   ##  ##   ##### ######
# ##  ##  ##  ##  ######    ##  ##  ##  ##  ### ##  ##       ##
# #####   #####   ##  ## ## ##      ##  ##  ## ###   ####    ##
# ##  ##  ##      ##  ##    ##  ##  ##  ##  ##  ##      ##   ##
# #####   ##      ##  ##     ####    ####   ##  ##  #####    ##
#  
#

def get_constant_bpm_snippet():
    """returns a constant-bpm-setting snippet"""
    snippet = {}

    def apply(thing,concept,tzero,snippet=snippet):
        start_time = tzero + thing['t']
        def set_bpm(x=None, start=thing['level'],\
                    end=thing['level1'],\
                    span=thing['seconds']):
            DfGlobal()["mind"].set_beatspersecond_constant_rate(start,end,span)
        concept.add_timed_command(start_time,set_bpm)

    def make_marks(dic,thing,snippet=snippet):
        canvas = dic['canvas']
        for old_marks in thing['*marks']:
            canvas.delete(old_marks)
        marks = []

        level0_x = (thing['t'])*float(dic['width'])\
                /float(dic['length'])

        level1_x = (thing['t']+thing['span'])*float(dic['width'])\
                /float(dic['length'])

        seconds_x = level0_x

        level0_text = canvas.create_text(level0_x,thing['y']-15,fill="magenta",\
                                      anchor=NW,text= "%.1f"%(60.0*thing['level']))

        level1_text = canvas.create_text(level1_x,thing['y']-15,fill="magenta",\
                                      anchor=NE,text= "%.1f"%(60.0*thing['level1']))

        seconds_text = canvas.create_text(seconds_x,thing['y']-30,fill="green",\
                                      anchor=NW,text= "%.1f"%thing['seconds'])

        marks.append(level0_text)
        marks.append(level1_text)        
        marks.append(seconds_text)
        
        thing['*marks'] = marks
        canvas.tag_lower(dic['canvas_bg'])

    def update_span(dic,thing):
        w = int(thing['span']/float(dic['length'])*float(dic['width']))
        if w < 50:
            w = 50
        canvas = dic['canvas']
        for obj in thing['*objects']:
            coords = canvas.coords(obj)
            if len(coords)==4:
                coords[2] = coords[0] + w
                canvas.coords(obj,*coords)
        make_marks(dic,thing)

   

    def property(dic,thing,snippet=snippet):
        repeat_str = str(thing['repeat'])
        values = {'span':str(thing['span']),\
                  't':str(thing['t']),
                  'repeat':repeat_str,\
                  'scale':str(thing['scale']),\
                  'level':str(thing['level']*60.0),\
                  'level1':str(thing['level1']*60.0),\
                  'seconds':str(thing['seconds'])}
        property_dialog([("t = ","t"),\
                         ("duration of movement = ","seconds"),\
                         ("start beats per minute = ","level"),\
                         ("end beats per minute = ","level1")],\
                        values=values,\
                        types={'level':lambda x: float(x)/60.0,\
                              'level1':lambda x: float(x)/60.0},\
                              parent=dic['window'])
        try:
            thing['level'] = float(values['level'])
        except:
            pass
        try:
            thing['level1'] = float(values['level1'])
        except:
            pass        
        try:
            thing['seconds'] = float(values['seconds'])
        except:
            pass
        if values['span'] != str(thing['span']):
            try:
                new_span = float(values['span'])
            except:
                pass
            else:
                thing['span'] = new_span
                thing['repeat'] = thing['span']\
                                  /(float(snippet['length'])*thing['scale'])
                update_span(dic,thing)
        if values['scale'] != str(thing['scale']):
            try:
                new_scale = float(values['scale'])
            except:
                pass
            else:
                thing['scale'] = new_scale
                thing['repeat'] = thing['span']\
                                  /(float(snippet['length'])*thing['scale'])
                update_span(dic,thing)
        if values['repeat'] != repeat_str:
            try:
                new_repeat = float(values['repeat'])
            except:
                pass
            else:
                thing['repeat'] = new_repeat
                thing['span'] = float(thing['scale'])*float(snippet['length'])\
                                *thing['repeat']
                update_span(dic,thing)
        if values['t'] != str(thing['t']):
            try:
                new_t = float(values['t'])
            except:
                pass
            else:
                thing['t'] = new_t
                x = float(dic['width'])*new_t/float(dic['length'])
                delta_x = x-thing['x']
                thing['x'] = x
                canvas = dic['canvas']
                for obj in thing['*objects']:
                    xys = canvas.coords(obj)
                    for i in range(len(xys)):
                        if not i%2:
                            xys[i] += delta_x
                    canvas.coords(obj,*xys)
        make_marks(dic,thing)
        

    def set_delta(event, thing,snippet=snippet):
        thing['old-x'] = event.x
        thing['old-y'] = event.y
        thing['old-level'] = thing['level']
        thing['old-level1'] = thing['level1']
        thing['old-seconds'] = thing['seconds']

       

    def drag(event,dic,thing,snippet=snippet):
        delta_x = event.x - thing['old-x']
        delta_y = event.y - thing['old-y']
        x = thing['x']+delta_x
        y = thing['y']+delta_y
        if y < thing['y-min']:
            y = thing['y-min']
        elif y > thing['y-max']:
            y = thing['y-max']
        delta_x = x-thing['x']
        delta_y = y-thing['y']
        t = float(x)*float(dic['length'])/float(dic['width'])
        dic_extend(thing,{'x':x,'y':y,'t':t})
        canvas = dic['canvas']
        for obj in thing['*objects']:
            xys = canvas.coords(obj)
            for i in range(len(xys)):
                if i%2:
                    xys[i] += delta_y
                else:
                    xys[i] += delta_x
            canvas.coords(obj,*xys)
        make_marks(dic,thing)


    def scale(event,dic,thing,snippet=snippet):
        delta_x = event.x - thing['old-x']
        delta_y = event.y - thing['old-y']
        delta_t = float(delta_x)/float(dic['width'])*float(dic['length'])   
        thing['level1'] = thing['old-level1'] - float(delta_y)/100.0          
        thing['seconds'] = thing['old-seconds'] + delta_t
        thing['scale'] = thing['span']/(snippet['length']*thing['repeat'])
        update_span(dic,thing)
        

    def span(event,dic,thing,snippet=snippet):
        delta_x = event.x - thing['old-x']
        delta_y = event.y - thing['old-y']        
        delta_t = float(delta_x)/float(dic['width'])*float(dic['length'])
        thing['level'] = thing['old-level'] - float(delta_y)/100.0        
        thing['repeat'] = thing['span']/(snippet['length']*thing['scale'])
        update_span(dic,thing)

    def restore(dic,thing,snippet=snippet):
        limb = thing['limb']
        t = thing['t']
        x = int(float(t)*float(dic['width'])/float(dic['length']))
        thing['x'] = x
        y = thing['y']
        
        y_min = dic['y_minmargins'][limb]
        y_max = dic['y_margins'][limb]
        
        thing['y-min'] = y_min
        thing['y-max'] = y_max-21

        canvas = dic['canvas']
        

        w = int(thing['span']/float(dic['length'])*float(dic['width']))
        if w < 50:
            w = 50

        box = canvas.create_rectangle(x,y,x+w,y+20,fill="#440044",outline="magenta")
        text = canvas.create_text(x+2,y+2,text=snippet['name'],fill="#FF00FF",\
                                  anchor=NW)
        
        objects = [box, text]

        thing['*objects'] = objects

        menu = Menu(dic['window'],tearoff=0)

        def properties(thing=thing,dic=dic,snippet=snippet):
            snippet['property'](dic,thing)

        def removeThing(thing=thing,dic=dic):
            canvas = dic['canvas']
            for o in thing['*objects']:
                canvas.delete(o)
            for m in thing['*marks']:
                canvas.delete(m)
            dic['things'].remove(thing)

        menu.add_command(label="Copy",\
                         command=lambda t=thing:copy_thing_to_global(t))
        menu.add_command(label="Properties",command=properties)
        menu.add_command(label="Remove",command=removeThing)
        menu.add_separator()
        menu.add_command(label=snippet['name'])
        
        thing['*menu'] = menu
        
        bind_canvas_objects_to_snippet(dic,canvas,objects,snippet,thing,\
                                       properties)

        thing['*marks'] = []
        make_marks(dic,thing)
        


    def create(dic,t,limb,snippet=snippet):
        x = dic['x']
        y = dic['y']
        
        thing = {'type':'snippet',\
                 'name':snippet['name'],\
                 'limb':limb,\
                 'scale':1.0,\
                 'repeat':snippet['initial-length']/snippet['length'],\
                 'span':snippet['initial-length'],\
                 'level':snippet['initial-level'],\
                 'level1':snippet['initial-level'],\
                 'seconds':snippet['initial-seconds'],\
                 't':t,\
                 'x':x,\
                 'y':y}

        restore(dic,thing)

        return thing

    dic_extend(snippet,{'apply':apply,\
               'property':property,\
               'set-delta':set_delta,\
               'drag':drag,\
               'scale':scale,\
               'span':span,\
               'create':create,\
               'restore':restore,\
               'priority':0,\
               'length':1.0,\
               'initial-level':2.0,\
               'initial-seconds':20.0,\
               'initial-length':2.0,\
               'name':'absolute-bpm'})

    return snippet



#
#
# #####   ######   ######   #####   ######  ######
# ##  ##  ##   ##  ##      ##       ##        ##
# #####   ######   ####     ####    ####      ##
# ##      ##  ##   ##           ##  ##        ##
# ##      ##   ##  ######   #####   ######    ##
#
#


def get_preset_snippet():
    """returns a preset snippet"""
    snippet = {}

    def apply(thing,concept,tzero,snippet=snippet):
        start_time = tzero + thing['t']
        limb = thing['limb']
        fname = thing['preset']
        def call_snippet(x=None, limb=limb,\
                         fname=fname):
            call_preset_fn(fname,limb)
            
        concept.add_timed_command(start_time,call_snippet)
        

    def make_marks(dic,thing,snippet=snippet):
        canvas = dic['canvas']
        for old_marks in thing['*marks']:
            canvas.delete(old_marks)
        marks = []
        x = (thing['t'])*float(dic['width'])\
                /float(dic['length']) + 3
        y = thing['y']-2

        presettext = canvas.create_text(x,y,text=thing['preset'],fill="#00FFFF",\
                                  anchor=SW)
        
        marks.append(presettext)

        thing['*marks'] = marks
        canvas.tag_lower(dic['canvas_bg'])


    def update_span(dic,thing):
        w = int(thing['span']/float(dic['length'])*float(dic['width']))
        if w < 50:
            w = 50
        canvas = dic['canvas']
        for obj in thing['*objects']:
            coords = canvas.coords(obj)
            if len(coords)==4:
                coords[2] = coords[0] + w
                canvas.coords(obj,*coords)
        make_marks(dic,thing)

    def property(dic,thing,snippet=snippet):
        values = {'span':thing['span'],\
                  'preset':thing['preset'],\
                  't':thing['t']}

        print "props:",thing
        print "list:",get_preset_fn_list(thing['limb'])

        property_dialog([("t = ","t"),\
                         ("preset = ","preset",\
                          "DropDown",get_preset_fn_list(thing['limb']))],\
                        values=values,\
                        parent=dic['window'])
        
        thing['preset'] = values['preset']
        if values['t'] != str(thing['t']):
            try:
                new_t = float(values['t'])
            except:
                pass
            else:
                thing['t'] = new_t
                x = float(dic['width'])*new_t/float(dic['length'])
                delta_x = x-thing['x']
                thing['x'] = x
                canvas = dic['canvas']
                for obj in thing['*objects']:
                    xys = canvas.coords(obj)
                    for i in range(len(xys)):
                        if not i%2:
                            xys[i] += delta_x
                    canvas.coords(obj,*xys)
        make_marks(dic,thing)
        
        

    def set_delta(event, thing,snippet=snippet):
        thing['old-x'] = event.x
        thing['old-y'] = event.y

       

    def drag(event,dic,thing,snippet=snippet):
        delta_x = event.x - thing['old-x']
        delta_y = event.y - thing['old-y']
        x = thing['x']+delta_x
        y = thing['y']+delta_y
        if y < thing['y-min']:
            y = thing['y-min']
        elif y > thing['y-max']:
            y = thing['y-max']
        delta_x = x-thing['x']
        delta_y = y-thing['y']
        t = float(x)*float(dic['length'])/float(dic['width'])
        dic_extend(thing,{'x':x,'y':y,'t':t})
        canvas = dic['canvas']
        for obj in thing['*objects']:
            xys = canvas.coords(obj)
            for i in range(len(xys)):
                if i%2:
                    xys[i] += delta_y
                else:
                    xys[i] += delta_x
            canvas.coords(obj,*xys)
        make_marks(dic,thing)

        

    def span(event,dic,thing,snippet=snippet):
        delta_x = event.x - thing['old-x']
        delta_t = float(delta_x)/float(dic['width'])*float(dic['length'])
        thing['span'] += delta_t        
        update_span(dic,thing)

    def restore(dic,thing,snippet=snippet):
        limb = thing['limb']
        t = thing['t']
        x = int(float(t)*float(dic['width'])/float(dic['length']))
        thing['x'] = x
        y = thing['y']
        
        y_min = dic['y_minmargins'][limb]
        y_max = dic['y_margins'][limb]
        
        thing['y-min'] = y_min
        thing['y-max'] = y_max-21

        canvas = dic['canvas']
        

        w = int(thing['span']/float(dic['length'])*float(dic['width']))
        if w < 50:
            w = 50

        box = canvas.create_rectangle(x,y,x+w,y+20,fill="#00AADD",outline="#00FFFF")
        text = canvas.create_text(x+2,y+2,text=snippet['name'],fill="#00FFFF",\
                                  anchor=NW)
        
        objects = [box, text]

        thing['*objects'] = objects

        menu = Menu(dic['window'],tearoff=0)

        def properties(thing=thing,dic=dic,snippet=snippet):
            snippet['property'](dic,thing)

        def removeThing(thing=thing,dic=dic):
            canvas = dic['canvas']
            for o in thing['*objects']:
                canvas.delete(o)
            for m in thing['*marks']:
                canvas.delete(m)
            dic['things'].remove(thing)

        menu.add_command(label="Copy",\
                         command=lambda t=thing:copy_thing_to_global(t))
        menu.add_command(label="Properties",command=properties)
        menu.add_command(label="Remove",command=removeThing)
        menu.add_separator()
        menu.add_command(label=snippet['name'])
        
        thing['*menu'] = menu
        
        bind_canvas_objects_to_snippet(dic,canvas,objects,snippet,thing,\
                                       properties)

        thing['*marks'] = []
        make_marks(dic,thing)

        


    def create(dic,t,limb,snippet=snippet):
        x = dic['x']
        y = dic['y']
        
        thing = {'type':'snippet',\
                 'name':snippet['name'],\
                 'limb':limb,\
                 'span':snippet['initial-length'],\
                 'preset':snippet['initial-preset'],\
                 't':t,\
                 'x':x,\
                 'y':y}

        restore(dic,thing)

        return thing

    dic_extend(snippet,{'apply':apply,\
               'property':property,\
               'set-delta':set_delta,\
               'drag':drag,\
               'scale':span,\
               'span':span,\
               'create':create,\
               'restore':restore,\
               'length':1.0,\
               'priority':-1,\
               'initial-length':1.0,\
               'initial-preset':'default-s.r.',\
               'name':'preset'})

    return snippet
#
#                               ##
#  ##  ##  ##  ######   #####  ## #
#  ##  ##  ##    ##    ##       ##
#  ######  ##    ##     #####
#  ##  ##  ##    ##         ##   
#  ##  ##  ##    ##     #####
#  
#

def get_hit_star_snippet():
    """returns a modified version of the hit snippet."""
    snippet = get_hit_snippet()
    snippet['name'] = "hits"

    def apply(thing,concept,tzero,snippet=snippet):
        limb = thing['limb']
        old_potential = concept.potential_funs[limb]
        start = tzero + thing['t']
        count = int(thing['span']/float(thing['scale']*snippet['length']))
        if count > 0:
            length = float(count)*snippet['length']*thing['scale']
        else:
            length = thing['scale']/64.0
        end = start+length
        start0 = start - thing['scale']/64.0
        current_hits = get_hit_point_map(old_potential,start0,end).keys()
        current_hits.sort()
        hit_points = current_hits[1:]
        for pt in [start + float(i)*thing['scale'] for i in range(count+1)]:
            insort(hit_points,pt)
        hit_map = {start0:0.0}
        for i in range(len(hit_points)):
            hit_map[hit_points[i]] = float(i+1)
        hit_potential = get_linear_interpolation_fn(hit_map)
        new_potential = lambda x,f=old_potential,t0=start0,\
                        t1=end,f2=hit_potential,\
                        y0=floor(old_potential(start0)),\
                        y1=float(count+1):\
                        f(x) if x < t0 else y0+f2(x) if x < t1 else f(x)+y1
        concept.potential_funs[limb] = new_potential

    snippet['apply'] = apply
  
    return snippet


#
#                                                             ##
#   ####   ##      ######        ##  ##  ##  ######   #####  ## #
#  ##  ##  ##        ##          ##  ##  ##    ##    ##       ##
#  ######  ##        ##    ####  ######  ##    ##     #####
#  ##  ##  ##        ##          ##  ##  ##    ##         ##   
#  ##  ##  ######    ##          ##  ##  ##    ##     #####
#  
#

def get_alternate_hit_star_snippet():
    """returns a modified version of the hit snippet."""
    snippet = get_hit_snippet()
    snippet['name'] = "alt-hits"

    def apply(thing,concept,tzero,snippet=snippet):
        count_both = int(thing['span']/float(thing['scale']*snippet['length'])) 
        limb = thing['limb']
        old_potential = concept.potential_funs[limb]
        start = tzero + thing['t']
        count = count_both/2
        if count > 0:
            length = float(count_both)*snippet['length']*thing['scale']
        else:
            length = thing['scale']/64.0
        end = start+length
        start0 = start - thing['scale']/64.0
        current_hits = get_hit_point_map(old_potential,start0,end).keys()
        current_hits.sort()
        hit_points = current_hits[1:]
        for pt in [start + float(2*i)*thing['scale'] for i in range(count+1)]:
            insort(hit_points,pt)
        hit_map = {start0:0.0}
        for i in range(len(hit_points)):
            hit_map[hit_points[i]] = float(i+1)
        hit_potential = get_linear_interpolation_fn(hit_map)
        new_potential = lambda x,f=old_potential,t0=start0,\
                        t1=end,f2=hit_potential,\
                        y0=floor(old_potential(start0)),\
                        y1=float(count+1):\
                        f(x) if x < t0 else y0+f2(x) if x < t1 else f(x)+y1
        concept.potential_funs[limb] = new_potential

        limb = DfGlobal()["dual.limbs"][limb]

        if count_both > 0:
            count = (count_both-1)/2
            old_potential = concept.potential_funs[limb]
            current_hits = get_hit_point_map(old_potential,start0,end).keys()
            current_hits.sort()
            hit_points = current_hits[1:]
            for pt in [start + float(2*i+1)*thing['scale'] \
                       for i in range(count+1)]:
                insort(hit_points,pt)
            hit_map = {start0:0.0}
            for i in range(len(hit_points)):
                hit_map[hit_points[i]] = float(i+1)
            hit_potential = get_linear_interpolation_fn(hit_map)
            new_potential = lambda x,f=old_potential,t0=start0,\
                            t1=end,f2=hit_potential,\
                            y0=floor(old_potential(start0)),\
                            y1=float(count+1):\
                            f(x) if x < t0 else y0+f2(x) if x < t1 else f(x)+y1
            concept.potential_funs[limb] = new_potential
            
        
        
    
    snippet['apply'] = apply
  
    return snippet

# 
#  #####   ######   ####   ######   ####   #####   ######       ####
#  ##  ##  ##      ##        ##    ##  ##  ##  ##  ##            ##
#  #####   ####     ####     ##    ##  ##  #####   ####   ####   ##
#  ##  #   ##          ##    ##    ##  ##  ##  #   ##            ##
#  ##   #  ######   ####     ##     ####   ##   #  ######       ####  ##
#

def get_restore_instrument_snippet():
    """returns a restore-instrument snippet"""
    snippet = {}

    def apply(thing,concept,tzero,snippet=snippet):
        start_time = tzero + thing['t']
        end_time = tzero + thing['t'] + thing['span']
        if end_time > start_time:
            ext = concept.ext
            idnbr = ext.setdefault("restore-id",0) + 1
            ext["restore-id"] = idnbr
            def grab_instrument_name(concept,idnbr=idnbr,limb=thing['limb']):
                concept.ext[("restore-instrument",idnbr)] = DfGlobal()["limbs"][limb].current
            def restore_instrument_name(concept,idnbr=idnbr,limb=thing['limb']):
                DfGlobal()["limbs"][limb].current = concept.ext[("restore-instrument",idnbr)]
            concept.add_timed_command(start_time,grab_instrument_name)
            concept.add_timed_command(end_time,restore_instrument_name)

    def make_marks(dic,thing,snippet=snippet):
        pass
    
    def update_span(dic,thing):
        w = int(thing['span']/float(dic['length'])*float(dic['width']))
        if w < 50:
            w = 50
        canvas = dic['canvas']
        for obj in thing['*objects']:
            coords = canvas.coords(obj)
            if len(coords)==4:
                coords[2] = coords[0] + w
                canvas.coords(obj,*coords)
        make_marks(dic,thing)

    def property(dic,thing,snippet=snippet):
        values = {'span':thing['span'],\
                  't':thing['t']}

        property_dialog([("t = ","t"),\
                         ("span = ","span")],\
                        values=values,\
                        parent=dic['window'])
        
        if values['span'] != str(thing['span']):
            try:
                new_span = float(values['span'])
            except:
                pass
            else:
                thing['span'] = new_span
                update_span(dic,thing)

        if values['t'] != str(thing['t']):
            try:
                new_t = float(values['t'])
            except:
                pass
            else:
                thing['t'] = new_t
                x = float(dic['width'])*new_t/float(dic['length'])
                delta_x = x-thing['x']
                thing['x'] = x
                canvas = dic['canvas']
                for obj in thing['*objects']:
                    xys = canvas.coords(obj)
                    for i in range(len(xys)):
                        if not i%2:
                            xys[i] += delta_x
                    canvas.coords(obj,*xys)
        

    def set_delta(event, thing,snippet=snippet):
        thing['old-x'] = event.x
        thing['old-y'] = event.y

       

    def drag(event,dic,thing,snippet=snippet):
        delta_x = event.x - thing['old-x']
        delta_y = event.y - thing['old-y']
        x = thing['x']+delta_x
        y = thing['y']+delta_y
        if y < thing['y-min']:
            y = thing['y-min']
        elif y > thing['y-max']:
            y = thing['y-max']
        delta_x = x-thing['x']
        delta_y = y-thing['y']
        t = float(x)*float(dic['length'])/float(dic['width'])
        dic_extend(thing,{'x':x,'y':y,'t':t})
        canvas = dic['canvas']
        for obj in thing['*objects']:
            xys = canvas.coords(obj)
            for i in range(len(xys)):
                if i%2:
                    xys[i] += delta_y
                else:
                    xys[i] += delta_x
            canvas.coords(obj,*xys)
        make_marks(dic,thing)

    def span(event,dic,thing,snippet=snippet):
        delta_x = event.x - thing['old-x']
        delta_t = float(delta_x)/float(dic['width'])*float(dic['length'])
        thing['span'] += delta_t        
        update_span(dic,thing)


    def restore(dic,thing,snippet=snippet):
        limb = thing['limb']
        t = thing['t']
        x = int(float(t)*float(dic['width'])/float(dic['length']))
        thing['x'] = x
        y = thing['y']
        
        y_min = dic['y_minmargins'][limb]
        y_max = dic['y_margins'][limb]
        
        thing['y-min'] = y_min
        thing['y-max'] = y_max-21

        canvas = dic['canvas']
        

        w = int(thing['span']/float(dic['length'])*float(dic['width']))
        if w < 50:
            w = 50

        box = canvas.create_rectangle(x,y,x+w,y+20,fill="#DD0000",outline="#660000")
        text = canvas.create_text(x+2,y+2,text=snippet['name'],fill="#440000",\
                                  anchor=NW)
        
        objects = [box, text]

        thing['*objects'] = objects

        menu = Menu(dic['window'],tearoff=0)

        def properties(thing=thing,dic=dic,snippet=snippet):
            snippet['property'](dic,thing)

        def removeThing(thing=thing,dic=dic):
            canvas = dic['canvas']
            for o in thing['*objects']:
                canvas.delete(o)
            for m in thing['*marks']:
                canvas.delete(m)
            dic['things'].remove(thing)

        menu.add_command(label="Copy",\
                         command=lambda t=thing:copy_thing_to_global(t))
        menu.add_command(label="Properties",command=properties)
        menu.add_command(label="Remove",command=removeThing)
        menu.add_separator()
        menu.add_command(label=snippet['name'])
        
        thing['*menu'] = menu
        
        bind_canvas_objects_to_snippet(dic,canvas,objects,snippet,thing,\
                                       properties)

        thing['*marks'] = []
        make_marks(dic,thing)
        


    def create(dic,t,limb,snippet=snippet):
        x = dic['x']
        y = dic['y']
        
        thing = {'type':'snippet',\
                 'name':snippet['name'],\
                 'limb':limb,\
                 'scale':1.0,\
                 'repeat':snippet['initial-length']/snippet['length'],\
                 'span':snippet['initial-length'],\
                 't':t,\
                 'x':x,\
                 'y':y}

        restore(dic,thing)

        return thing

    dic_extend(snippet,{'apply':apply,\
               'property':property,\
               'set-delta':set_delta,\
               'drag':drag,\
               'scale':span,\
               'span':span,\
               'create':create,\
               'restore':restore,\
               'priority':0,\
               'length':1.0,\
               'initial-length':2.0,\
               'name':'restore-instrument'})

    return snippet




#
#
# ##       ##   ######   #######   #######
# ##       ##  ##    ##  ##    ##  ##    ##
# ##   #   ##  ##    ##  ##    ##  ##    ##
# ##  ###  ##  ########  ######    #######
# ## ## ## ##  ##    ##  ##   ##   ##
#  ###   ###   ##    ##  ##    ##  ##
#

def get_warp_snippet():
    """returns a warp snippet"""
    snippet = {}

    def apply(thing,concept,tzero,snippet=snippet):
        limb = thing['limb']        
        start = tzero + thing['t']
        end = start + thing['span']
        old_strength = concept.strength_funs[limb]
        old_potential = concept.potential_funs[limb]        
        midpoint = thing['gap']*thing['span'] + start
        curvature = thing['level']
        gaplen = thing['gap']*thing['span']
        halfspan = thing['span']*0.5
        def new_strength(t,t0=start,t1=midpoint,t2=end,\
                         c=curvature,tm=halfspan,\
                         fn = old_strength,glen=gaplen,\
                         glen2=thing['span']-gaplen):
            if t < t0:
                return fn(t)
            if t < t1:
                return fn(t0 + (((t-t0)/glen)**c)*tm)
            if t < t2:
                return fn(t1 - (((t1-t)/glen2)**c)*tm)
            return fn(t)

        def new_potential(t,t0=start,t1=midpoint,t2=end,\
                         c=curvature,tm=halfspan,\
                         fn = old_potential,glen=gaplen,\
                         glen2=thing['span']-gaplen):
            if t < t0:
                return fn(t)
            if t < t1:
                return fn(t0 + (((t-t0)/glen)**c)*tm)
            if t < t2:
                return fn(t1 - (((t1-t)/glen2)**c)*tm)
            return fn(t)

                
        concept.strength_funs[limb] = new_strength
        concept.potential_funs[limb] = new_potential

    def make_marks(dic,thing,snippet=snippet):
        canvas = dic['canvas']
        for old_marks in thing['*marks']:
            canvas.delete(old_marks)
        marks = []
        for i in [thing['gap']*thing['span']]:
            x = (i+thing['t'])*float(dic['width']) / float(dic['length'])
            line = canvas.create_line(x,thing['y-min'],x,thing['y-max']+20,\
                                      fill="#0000CC")
            canvas.tag_lower(line)
            marks.append(line)

        level0_x = (thing['t']+thing['gap']*thing['span'])*float(dic['width'])\
                /float(dic['length'])

        gap_x = thing['t']*float(dic['width'])/float(dic['length']) 

        level0_text = canvas.create_text(level0_x,thing['y']-20,fill="yellow",\
                                      anchor=N,text= "%.2f"%thing['level'])

        gap_text = canvas.create_text(gap_x,thing['y']-15,fill="blue",\
                                      anchor=N,text= "%.2f"%thing['gap'])

        marks.append(level0_text)
        marks.append(gap_text)
        
        thing['*marks'] = marks
        canvas.tag_lower(dic['canvas_bg'])

    def update_span(dic,thing):
        w = int(thing['span']/float(dic['length'])*float(dic['width']))
        if w < 50:
            w = 50
        canvas = dic['canvas']
        for obj in thing['*objects']:
            coords = canvas.coords(obj)
            if len(coords)==4:
                coords[2] = coords[0] + w
                canvas.coords(obj,*coords)
        make_marks(dic,thing)

   

    def property(dic,thing,snippet=snippet):
        repeat_str = str(thing['repeat'])
        values = {'span':str(thing['span']),\
                  't':str(thing['t']),
                  'repeat':repeat_str,\
                  'scale':str(thing['scale']),\
                  'level':str(thing['level']),\
                  'gap':str(thing['gap'])}
        property_dialog([("t = ","t"),\
                         ("span = ","span"),\
                         ("new-middle-position = ","gap"),\
                         ("curvature factor = ","level")],\
                        values=values,parent=dic['window'])
        try:
            thing['level'] = float(values['level'])
        except:
            pass
        try:
            thing['gap'] = float(values['gap'])
        except:
            pass
        if values['span'] != str(thing['span']):
            try:
                new_span = float(values['span'])
            except:
                pass
            else:
                thing['span'] = new_span
                thing['repeat'] = thing['span']\
                                  /(float(snippet['length'])*thing['scale'])
                update_span(dic,thing)
        if values['scale'] != str(thing['scale']):
            try:
                new_scale = float(values['scale'])
            except:
                pass
            else:
                thing['scale'] = new_scale
                thing['repeat'] = thing['span']\
                                  /(float(snippet['length'])*thing['scale'])
                update_span(dic,thing)
        if values['repeat'] != repeat_str:
            try:
                new_repeat = float(values['repeat'])
            except:
                pass
            else:
                thing['repeat'] = new_repeat
                thing['span'] = float(thing['scale'])*float(snippet['length'])\
                                *thing['repeat']
                update_span(dic,thing)
        if values['t'] != str(thing['t']):
            try:
                new_t = float(values['t'])
            except:
                pass
            else:
                thing['t'] = new_t
                x = float(dic['width'])*new_t/float(dic['length'])
                delta_x = x-thing['x']
                thing['x'] = x
                canvas = dic['canvas']
                for obj in thing['*objects']:
                    xys = canvas.coords(obj)
                    for i in range(len(xys)):
                        if not i%2:
                            xys[i] += delta_x
                    canvas.coords(obj,*xys)
        make_marks(dic,thing)
        

    def set_delta(event, thing,snippet=snippet):
        thing['old-x'] = event.x
        thing['old-y'] = event.y
        thing['old-level'] = thing['level']
        thing['old-gap'] = thing['gap']

       

    def drag(event,dic,thing,snippet=snippet):
        delta_x = event.x - thing['old-x']
        delta_y = event.y - thing['old-y']
        x = thing['x']+delta_x
        y = thing['y']+delta_y
        if y < thing['y-min']:
            y = thing['y-min']
        elif y > thing['y-max']:
            y = thing['y-max']
        delta_x = x-thing['x']
        delta_y = y-thing['y']
        t = float(x)*float(dic['length'])/float(dic['width'])
        dic_extend(thing,{'x':x,'y':y,'t':t})
        canvas = dic['canvas']
        for obj in thing['*objects']:
            xys = canvas.coords(obj)
            for i in range(len(xys)):
                if i%2:
                    xys[i] += delta_y
                else:
                    xys[i] += delta_x
            canvas.coords(obj,*xys)
        make_marks(dic,thing)


    def scale(event,dic,thing,snippet=snippet):
        delta_x = event.x - thing['old-x']
        delta_y = event.y - thing['old-y']
        delta_t = float(delta_x)/float(dic['width'])*float(dic['length'])   
        thing['gap'] = thing['old-gap'] + delta_t/thing['span']
        thing['scale'] = thing['span']/(snippet['length']*thing['repeat'])
        update_span(dic,thing)
        

    def span(event,dic,thing,snippet=snippet):
        delta_x = event.x - thing['old-x']
        delta_y = event.y - thing['old-y']        
        delta_t = float(delta_x)/float(dic['width'])*float(dic['length'])
        thing['span'] += delta_t
        thing['level'] = thing['old-level'] - float(delta_y)/100.0        
        thing['repeat'] = thing['span']/(snippet['length']*thing['scale'])
        update_span(dic,thing)

    def restore(dic,thing,snippet=snippet):
        limb = thing['limb']
        t = thing['t']
        x = int(float(t)*float(dic['width'])/float(dic['length']))
        thing['x'] = x
        y = thing['y']
        
        y_min = dic['y_minmargins'][limb]
        y_max = dic['y_margins'][limb]
        
        thing['y-min'] = y_min
        thing['y-max'] = y_max-21

        canvas = dic['canvas']
        

        w = int(thing['span']/float(dic['length'])*float(dic['width']))
        if w < 50:
            w = 50

        box = canvas.create_rectangle(x,y,x+w,y+20,fill="#666600",outline="yellow")
        text = canvas.create_text(x+2,y+2,text=snippet['name'],fill="yellow",\
                                  anchor=NW)
        
        objects = [box, text]

        thing['*objects'] = objects

        menu = Menu(dic['window'],tearoff=0)

        def properties(thing=thing,dic=dic,snippet=snippet):
            snippet['property'](dic,thing)

        def removeThing(thing=thing,dic=dic):
            canvas = dic['canvas']
            for o in thing['*objects']:
                canvas.delete(o)
            for m in thing['*marks']:
                canvas.delete(m)
            dic['things'].remove(thing)

        menu.add_command(label="Copy",\
                         command=lambda t=thing:copy_thing_to_global(t))
        menu.add_command(label="Properties",command=properties)
        menu.add_command(label="Remove",command=removeThing)
        menu.add_separator()
        menu.add_command(label=snippet['name'])
        
        thing['*menu'] = menu
        
        bind_canvas_objects_to_snippet(dic,canvas,objects,snippet,thing,\
                                       properties)

        thing['*marks'] = []
        make_marks(dic,thing)
        


    def create(dic,t,limb,snippet=snippet):
        x = dic['x']
        y = dic['y']
        
        thing = {'type':'snippet',\
                 'name':snippet['name'],\
                 'limb':limb,\
                 'scale':1.0,\
                 'repeat':snippet['initial-length']/snippet['length'],\
                 'span':snippet['initial-length'],\
                 'level':snippet['initial-level'],\
                 'gap':snippet['initial-gap'],\
                 't':t,\
                 'x':x,\
                 'y':y}

        restore(dic,thing)

        return thing

    dic_extend(snippet,{'apply':apply,\
               'property':property,\
               'set-delta':set_delta,\
               'drag':drag,\
               'scale':scale,\
               'span':span,\
               'create':create,\
               'restore':restore,\
               'priority':10,\
               'length':1.0,\
               'initial-level':1.7,\
               'initial-gap':0.6,\
               'initial-length':1.0,\
               'name':'warp'})

    return snippet


#
#
#   #######  ##  ## ##   ##  ##### ##  ##
#   ##    ## ##  ## ###  ## ##     ##  ##
#   ##    ## ##  ## ## # ## ##     ######
#   #######  ##  ## ##  ### ##     ##  ##
#   ##       ##  ## ##   ## ##     ##  ##
#   ##        ####  ##   ##  ##### ##  ##
#

def get_punch_snippet():
    """returns a punching snippet"""
    snippet = {}

    def apply(thing,concept,tzero,snippet=snippet):
        limb = thing['limb']        
        start = tzero + thing['t']
        end = start + thing['span']
        old_strength = concept.strength_funs[limb]
        old_potential = concept.potential_funs[limb]        
        gaplen = thing['gap']*thing['span']
        curvature = thing['level']
        gaplen = thing['gap']*thing['span']
        d = thing['span']-gaplen
        s = thing['span']
        alpha = -(curvature - 1.0)/(2.0*d)
        gamma = s / (-alpha*d*d + d)
        
        def new_strength(t,fn = old_strength,t0=start,\
                         t1=start+gaplen,\
                         t2=start+thing['span'],\
                         alpha=alpha,gamma=gamma):
            if t < t0:
                return fn(t)
            if t < t1:
                return fn(t0)
            if t < t2:
                x = t-t2
                return fn(t2 + gamma*(alpha*x*x+x))
            return fn(t)

        def new_potential(t,fn = old_potential,t0=start,\
                         t1=start+gaplen,\
                         t2=start+thing['span'],\
                         alpha=alpha,gamma=gamma):
            if t < t0:
                return fn(t)
            if t < t1:
                return fn(t0)
            if t < t2:
                x = t-t2
                return fn(t2 + gamma*(alpha*x*x+x))
            return fn(t)
               
        concept.strength_funs[limb] = new_strength
        concept.potential_funs[limb] = new_potential

    def make_marks(dic,thing,snippet=snippet):
        canvas = dic['canvas']
        for old_marks in thing['*marks']:
            canvas.delete(old_marks)
        marks = []
        for i in [thing['gap']*thing['span']]:
            x = (i+thing['t'])*float(dic['width']) / float(dic['length'])
            line = canvas.create_line(x,thing['y-min'],x,thing['y-max']+20,\
                                      fill="#0000CC")
            canvas.tag_lower(line)
            marks.append(line)

        level0_x = (thing['t']+thing['gap']*thing['span'])*float(dic['width'])\
                /float(dic['length'])

        gap_x = thing['t']*float(dic['width'])/float(dic['length']) 

        level0_text = canvas.create_text(level0_x,thing['y']-20,fill="yellow",\
                                      anchor=N,text= "%.2f"%thing['level'])

        gap_text = canvas.create_text(gap_x,thing['y']-15,fill="blue",\
                                      anchor=N,text= "%.2f"%thing['gap'])

        marks.append(level0_text)
        marks.append(gap_text)
        
        thing['*marks'] = marks
        canvas.tag_lower(dic['canvas_bg'])

    def update_span(dic,thing):
        w = int(thing['span']/float(dic['length'])*float(dic['width']))
        if w < 50:
            w = 50
        canvas = dic['canvas']
        for obj in thing['*objects']:
            coords = canvas.coords(obj)
            if len(coords)==4:
                coords[2] = coords[0] + w
                canvas.coords(obj,*coords)
        make_marks(dic,thing)

   

    def property(dic,thing,snippet=snippet):
        repeat_str = str(thing['repeat'])
        values = {'span':str(thing['span']),\
                  't':str(thing['t']),
                  'repeat':repeat_str,\
                  'scale':str(thing['scale']),\
                  'level':str(thing['level']),\
                  'gap':str(thing['gap'])}
        property_dialog([("t = ","t"),\
                         ("span = ","span"),\
                         ("new-middle-position = ","gap"),\
                         ("curvature factor = ","level")],\
                        values=values,parent=dic['window'])
        try:
            thing['level'] = float(values['level'])
        except:
            pass
        try:
            thing['gap'] = float(values['gap'])
        except:
            pass
        if values['span'] != str(thing['span']):
            try:
                new_span = float(values['span'])
            except:
                pass
            else:
                thing['span'] = new_span
                thing['repeat'] = thing['span']\
                                  /(float(snippet['length'])*thing['scale'])
                update_span(dic,thing)
        if values['scale'] != str(thing['scale']):
            try:
                new_scale = float(values['scale'])
            except:
                pass
            else:
                thing['scale'] = new_scale
                thing['repeat'] = thing['span']\
                                  /(float(snippet['length'])*thing['scale'])
                update_span(dic,thing)
        if values['repeat'] != repeat_str:
            try:
                new_repeat = float(values['repeat'])
            except:
                pass
            else:
                thing['repeat'] = new_repeat
                thing['span'] = float(thing['scale'])*float(snippet['length'])\
                                *thing['repeat']
                update_span(dic,thing)
        if values['t'] != str(thing['t']):
            try:
                new_t = float(values['t'])
            except:
                pass
            else:
                thing['t'] = new_t
                x = float(dic['width'])*new_t/float(dic['length'])
                delta_x = x-thing['x']
                thing['x'] = x
                canvas = dic['canvas']
                for obj in thing['*objects']:
                    xys = canvas.coords(obj)
                    for i in range(len(xys)):
                        if not i%2:
                            xys[i] += delta_x
                    canvas.coords(obj,*xys)
        make_marks(dic,thing)
        

    def set_delta(event, thing,snippet=snippet):
        thing['old-x'] = event.x
        thing['old-y'] = event.y
        thing['old-level'] = thing['level']
        thing['old-gap'] = thing['gap']

       

    def drag(event,dic,thing,snippet=snippet):
        delta_x = event.x - thing['old-x']
        delta_y = event.y - thing['old-y']
        x = thing['x']+delta_x
        y = thing['y']+delta_y
        if y < thing['y-min']:
            y = thing['y-min']
        elif y > thing['y-max']:
            y = thing['y-max']
        delta_x = x-thing['x']
        delta_y = y-thing['y']
        t = float(x)*float(dic['length'])/float(dic['width'])
        dic_extend(thing,{'x':x,'y':y,'t':t})
        canvas = dic['canvas']
        for obj in thing['*objects']:
            xys = canvas.coords(obj)
            for i in range(len(xys)):
                if i%2:
                    xys[i] += delta_y
                else:
                    xys[i] += delta_x
            canvas.coords(obj,*xys)
        make_marks(dic,thing)


    def scale(event,dic,thing,snippet=snippet):
        delta_x = event.x - thing['old-x']
        delta_y = event.y - thing['old-y']
        delta_t = float(delta_x)/float(dic['width'])*float(dic['length'])   
        thing['gap'] = thing['old-gap'] + delta_t/thing['span']
        thing['scale'] = thing['span']/(snippet['length']*thing['repeat'])
        update_span(dic,thing)
        

    def span(event,dic,thing,snippet=snippet):
        delta_x = event.x - thing['old-x']
        delta_y = event.y - thing['old-y']        
        delta_t = float(delta_x)/float(dic['width'])*float(dic['length'])
        thing['span'] += delta_t
        thing['level'] = thing['old-level'] - float(delta_y)/100.0        
        thing['repeat'] = thing['span']/(snippet['length']*thing['scale'])
        update_span(dic,thing)

    def restore(dic,thing,snippet=snippet):
        limb = thing['limb']
        t = thing['t']
        x = int(float(t)*float(dic['width'])/float(dic['length']))
        thing['x'] = x
        y = thing['y']
        
        y_min = dic['y_minmargins'][limb]
        y_max = dic['y_margins'][limb]
        
        thing['y-min'] = y_min
        thing['y-max'] = y_max-21

        canvas = dic['canvas']
        

        w = int(thing['span']/float(dic['length'])*float(dic['width']))
        if w < 50:
            w = 50

        box = canvas.create_rectangle(x,y,x+w,y+20,fill="#666600",outline="yellow")
        text = canvas.create_text(x+2,y+2,text=snippet['name'],fill="yellow",\
                                  anchor=NW)
        
        objects = [box, text]

        thing['*objects'] = objects

        menu = Menu(dic['window'],tearoff=0)

        def properties(thing=thing,dic=dic,snippet=snippet):
            snippet['property'](dic,thing)

        def removeThing(thing=thing,dic=dic):
            canvas = dic['canvas']
            for o in thing['*objects']:
                canvas.delete(o)
            for m in thing['*marks']:
                canvas.delete(m)
            dic['things'].remove(thing)

        menu.add_command(label="Copy",\
                         command=lambda t=thing:copy_thing_to_global(t))
        menu.add_command(label="Properties",command=properties)
        menu.add_command(label="Remove",command=removeThing)
        menu.add_separator()
        menu.add_command(label=snippet['name'])
        
        thing['*menu'] = menu
        
        bind_canvas_objects_to_snippet(dic,canvas,objects,snippet,thing,\
                                       properties)

        thing['*marks'] = []
        make_marks(dic,thing)
        


    def create(dic,t,limb,snippet=snippet):
        x = dic['x']
        y = dic['y']
        
        thing = {'type':'snippet',\
                 'name':snippet['name'],\
                 'limb':limb,\
                 'scale':1.0,\
                 'repeat':snippet['initial-length']/snippet['length'],\
                 'span':snippet['initial-length'],\
                 'level':snippet['initial-level'],\
                 'gap':snippet['initial-gap'],\
                 't':t,\
                 'x':x,\
                 'y':y}

        restore(dic,thing)

        return thing

    dic_extend(snippet,{'apply':apply,\
               'property':property,\
               'set-delta':set_delta,\
               'drag':drag,\
               'scale':scale,\
               'span':span,\
               'create':create,\
               'restore':restore,\
               'priority':10,\
               'length':1.0,\
               'initial-level':1.6,\
               'initial-gap':0.1,\
               'initial-length':1.0,\
               'name':'punch'})

    return snippet
    
