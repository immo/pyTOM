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


def get_instrument_volumes():
    g = DfGlobal()
    ivol = {}
    for i in g["used.instruments"]:
        ivol[i] = g["instruments"][i].volume
    return ivol

def set_instrument_volumes(ivol):
    g = DfGlobal()
    for i in ivol:
        g["instruments"][i].volume = ivol[i]

def save_volume_preset(name):
    g = DfGlobal()
    g["volume.presets"][name] = get_instrument_volumes()

def load_volume_preset(name):
    g = DfGlobal()
    set_instrument_volumes(g["volume.presets"][name])

