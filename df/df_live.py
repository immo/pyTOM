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
from df_ontology import *
from df_backend import *
from df_model import *
from df_data_channels import *

def default_fill_output(start,end):
   """default_fill_output(start,end)   called whenever a new part of output should be sent to the backend, from start to end"""
   g = DfGlobal()
   data = g["songdata"]
   offset = g["songstart"]
   ins = g["instruments"]
   while (data != []):
      (t,d,s) = data[0]
      t += offset
      if start <= t < end:
         data = data[1:]
         drum = ins[d]
         drum.hit(drum.energy(s),t)
      elif end <= t:
         break
      else:
         data = data[1:]
   g["songdata"] = data
   
def time_callback():
   """time_callback()   called whenever a new time event arises, handles legacy data output"""
   g = DfGlobal()
   if g["loop-depth"] < 2: # do not change the cursor if we get a time message within play, ...
      old_time = g["cur_now"]
      g["cur_now"] = now('@') + g["cur_advance"]
      g["fill-output"](old_time,g["cur_now"])

def nt_time_callback():
    """nt_time_callback()   called whenever a new time event arises, handles new technology output"""
    g = DfGlobal()
    send_lines_up_to(now('@') + g["cur_advance"])

    if g["loop-depth"]<=g["save-loop-depth"]: # do not change the cursor if we get a time message within play, ...
        old_time = g["cur_now"]
        g["cur_now"] = now('@')+g["cur_advance"]
        g["fill-output"].fill_output(old_time, g["cur_now"])
