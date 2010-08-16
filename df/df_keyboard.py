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
from df_external import *
from df_experimental import *
from df_hud_interaction import *
from df_scripting import *

def clear_keyboard_input_chord():
    DfGlobal()["current.chord"] = ""
    send_line("text-chord","''")
    

def handle_keyboard(n):

    if n == "ESCAPE" or n == "F1":
        clear_keyboard_input_chord()
        return
    
    g = DfGlobal()
    
    current = g["current.chord"]

    key = current + n

    if not (key in g["key.possible"]):
        return
    
    try:
        handler = g["key.bindings"][key]
    except KeyError:
        if len(filter(lambda x: x=='-', key)) >= 4:
            key = ""
        else:
            key += "-"            
        g["current.chord"] = key
        send_line("text-chord",repr(key))
        return

    try:
        info = repr(g["key.infos"][key])
    except KeyError:
        info = "''"
    
    g["current.chord"] = key
    send_line("text-cmd",info)
    handler()
    clear_keyboard_input_chord()
    return

def bind_keyboard(type=1):
    g = DfGlobal()
    g["key.bindings"] = g["key.bindings."+str(type)]
    g["key.infos"] = g["key.infos."+str(type)]
    g["key.possible"] = g["key.possible."+str(type)]        
    send_line("text-keyboard","'KEY"+str(type)+"'")

def possible_partial_key_chords(keys):
    p = {}
    for k in keys:
        s = k.split("-")
        x = ""
        for i in range(len(s)):
            if i:
                x += "-"
            x += s[i]
            p[x] = 1
    return p

def handle_keyboard_if_root(n=None):
    g = DfGlobal()
    if n == None:
        if g["loop-depth"]<=1:
            if g["keyboard-queue"]:
                x = g["keyboard-queue"]
                g["keyboard-queue"] = []
                for n in x:
                    handle_keyboard(n)
                return True
        return False
    else:
        if g["hud.interaction"]:
            hud_handle_keyboard_callback(n)
        else:
            g["keyboard-queue"].append(n)
            return handle_keyboard_if_root()
    
    

def initialize_keyboard():
    g = DfGlobal()
    mind = g["mind"]


#                           'A': lambda: mind.jam_session\
#                           .setup_info_and_plan_again\
#                           ({'desc':{'CARNAL':4.0,'START':0.5}}),\
#                           'S': lambda: mind.jam_session\
#                           .setup_info_and_plan_again\
#                           ({'desc':{'NPFO':4.0,'START':0.5}}),\

#                           'Z': lambda: mind.jam_session\
#                           .setup_from_ext('song_1'),\
#                           'X': lambda: mind.jam_session\
#                           .setup_from_ext('blaster_bastard_breed'),\
#                           'V': lambda: mind.jam_session\
#                           .setup_from_ext('gott_der_truemmer'),\

    def get_menu_fun(nbr):
        def menu_fn(fnname='menu_fn'+str(nbr)):
            fn = g(fnname,lambda : 0.0)
            fn()
        return menu_fn

    g["key.bindings.1"] = {'F12': lambda: mind.switchJamMode(),\
                           'F11': reload_external_data,\
                           'F10': g["gen_default_rules"],\
                           'RETURN-RETURN-RETURN': lambda: mind.quick_change(),\
                           'BACKSPACE': lambda: mind.jam_session\
                           .switch_wait_state(),\
                           'RETURN-BACKSPACE': lambda: mind.jam_session\
                           .switch_wait_state(),\
                           'RETURN-RETURN-BACKSPACE': lambda: mind.jam_session\
                           .switch_wait_state(),\
                           'P-P-P': lambda: mind.jam_session\
                           .plan_again(), \
                           'TAB': lambda: mind.jam_session\
                           .add_or_remove_count_in(),\
                           'T-T-T': lambda: mind.jam_session\
                           .setup_info_and_plan_again({}),\
                           'CONTROL_R': lambda: mind.set_target_timewarp\
                           (mind.c_target_timewarp * 1.01),\
                           'CONTROL_L': lambda: mind.set_target_timewarp\
                           (mind.c_target_timewarp / 1.01),\
                           'SPACE': lambda: mind.unwarp_faster(0.01),\
                           'KP_INSERT': choose_ext_song,\
                           'RIGHT': choose_ext_song,\
                           'END': choose_ext_song,\
                           'S': get_menu_fun(1),\
                           '8': get_menu_fun(2),\
                           'KP_SUBTRACT': get_menu_fun(3)\
                           }

#                        'A': 'CARNAL',\
#                        'S': 'NAZI PUNKS FUCK OFF',\
#                        'Z': 'ext/song_1',\
#                        'X': 'ext/blaster_bastard_breed',\
#                        'V': 'ext/gott_der_truemmer',\
 

    g["key.infos.1"] = {'F12': 'switch jam mode',\
                        'F11': 'reload external data',\
                        'F10': 'generate default database rules',\
                        'RETURN-RETURN-RETURN': 'quick change',\
                        'BACKSPACE': 'switch wait state',\
                        'RETURN-BACKSPACE': 'switch wait state',\
                        'RETURN-RETURN-BACKSPACE': 'switch wait state',\
                        'P-P-P': 'plan again',\
                        'TAB': 'switch count in',\
                        'T-T-T': 'reset info & plan again',\
                        'CONTROL_L': '<<<<<<',\
                        'CONTROL_R': '>>>>>>',\
                        'SPACE': '>>><<<',\
                        'KP_INSERT': 'choose ext song',\
                        'RIGHT': 'choose ext song',\
                        'END': 'choose ext song',\
                        'S': 'menu 1',\
                        '8': 'menu 2',\
                        'KP_SUBTRACT': 'menu 3'\
                        }

    g["key.possible.1"] = possible_partial_key_chords(g["key.bindings.1"])
    

    bind_keyboard()
    
    add_data_channel_handler("key",handle_keyboard_if_root)

    g["current.chord"] = ""

