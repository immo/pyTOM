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

def CLEARHUD_FILTER(x):
    return x == 'CLEARHUD'

def CLEARHUD_INTERACTION_FILTER(x):
    return x == 'CLEARHUDINTERACTION'

def CLEARHUD_TIMER_FUN():
    send_line('headupdisplay', '""')

def CLEARHUD_INTERACTION():
    g = DfGlobal()
    g["hud.interaction"] = False
    g["hud.default_action"]()
    

def display_hud(text, timeout=3.0):
    """display text for `timeout` seconds"""
    send_line('headupdisplay', repr(str(text)))
    remove_timed_calls_filtered_by_name(CLEARHUD_FILTER)
    if timeout:
        add_timed_call(CLEARHUD_TIMER_FUN,timeout,'CLEARHUD')

def print_hud(text, timeout=3.0):
    """display text for `timeout` seconds and clear input behaviour"""
    CLEARHUD_INTERACTION()
    display_hud(text,timeout)

def clear_hud():
    """clear headup display"""
    remove_timed_calls_filtered_by_name(CLEARHUD_FILTER)
    CLEARHUD_TIMER_FUN()
    CLEARHUD_INTERACTION()

def init_hud_interaction_globals():
    g = DfGlobal()
    g["hud.default_action"] = lambda : 0.0
    g["hud.keylist"] = [["CONTROL_L"],["CONTROL_R"],["SPACE"],\
                        ["KP_ENTER","DELETE","INSERT"],\
                        ["KP_INSERT","RIGHT","END"]]
    g["hud.inputlist"] = [] # contains ([KEYS],actionfn,QUICKINFOTEXT)
    # Testing...
    #g["hud.interaction"] = True
    #g["hud.inputlist"] = [(["CONTROL_L"],lambda : 0.0,"PRESSED")]

def ask_hud(text, alternatives, timeout=10.0, default_action= lambda : 0.0 ):
    """Ask a question via hud, text is the question displayed,
    alternatives is a list of pairs (`name`,function)"""
    g = DfGlobal()
    display_hud(text,timeout)
    remove_timed_calls_filtered_by_name(CLEARHUD_INTERACTION_FILTER)
    g["hud.default_action"] = default_action
    if timeout:
        add_timed_call(CLEARHUD_INTERACTION,timeout,'CLEARHUDINTERACTION')
    g = DfGlobal()
    g["hud.interaction"] = True
    
    keys = g["hud.keylist"]
    alts = alternatives[0:len(keys)]
    g["hud.inputlist"] = [(keys[idx],alts[idx][1],alts[idx][0])\
                          for idx in range(min(len(keys),len(alts)))]
    

def hud_handle_keyboard_callback(key):
    """This is called when a key event arises and hud.interaction is set"""
    if key=="ESCAPE" or key=="F1":
        clear_hud()
    else:
        for item in DfGlobal()["hud.inputlist"]:
            if key in item[0]:
                add_root_call(item[1])
                display_hud(item[2],3.0)
                CLEARHUD_INTERACTION()


    
