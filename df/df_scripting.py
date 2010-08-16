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
from df_hud_interaction import *

def PLAYEXT(ext_name,nocounting=False):
    """ makes the current jam session play next the concepts defined
    by ext data"""
    g = DfGlobal()
    ext = g["ext"]
    if ext_name in ext:
        g["mind"].switchJamMode(True)
        g["mind"].jam_session.setup_from_ext(ext_name,nocounting)
    else:
        print "PLAYEXT: external data not found for >>",ext_name,"<<"



def choose_ext_song():
    g = DfGlobal()
    songs = g["ext.songs"]
    if songs:
        g["choose.ext.song.index"] = 0

        fundict = {}
        
        def cycle_left():
            index = g["choose.ext.song.index"]-1
            if index < 0:
                index += len(songs)
            g["choose.ext.song.index"] = index
            fundict['display_question']()


        def cycle_right():
            index = g["choose.ext.song.index"]+1
            if index >= len(songs):
                index -= len(songs)
            g["choose.ext.song.index"] = index
            fundict['display_question']()

        def do_play():
            PLAYEXT(songs[g["choose.ext.song.index"]])

        def do_nothing():
            pass

        def display_question():
            ask_hud("Play\n"+songs[g["choose.ext.song.index"]],\
                    [("",cycle_left),\
                     ("",cycle_right),\
                     ("play song",do_play),\
                     ("cancel",do_nothing)],\
                    0.0)
        fundict['display_question'] = display_question

        display_question()

        
