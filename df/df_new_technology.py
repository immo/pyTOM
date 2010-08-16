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
from df_backend import *
from df_data_channels import *
from df_live import *
from df_mind import *
from df_flesh import *
from df_concept import *
from df_gens import *
from df_keyboard import *

def set_innovative_generators():
    """This function will set the generator structures for the new output model"""
    g = DfGlobal()
    g["fill-output"] = g["mind"]
    g["cur_now"] = now('@') + g["cur_advance"]
    g["@now-callback"] = nt_time_callback 
    

def initialize_new_technology():
    """Do all initialization stuff needed for new output model"""
    initialize_gens()
    g = DfGlobal()
    g["viz_lag"] = g["cur_advance"] + float(g["@output_latency"])
    g["flesh"] = Flesh()
    g["last.sketch"] = ""
    g["last.dbf_list"] = ""    
    g["concept.pool"] = {}
    g["concept.list"] = []
    g["gene.pool"] = {}
    g["sketch.pool"] = {}
    g["mind"] = Mind()
    set_innovative_generators()
    initialize_keyboard()
