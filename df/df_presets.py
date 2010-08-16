#
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
from df_data_channels import send_lines

def call_preset_fn(name,domain="default",parameters=()):
    g = DfGlobal()
    presetdomains = g["preset-functions"]
    if domain in presetdomains:
        funs = presetdomains[domain]
        if name in funs:
            fn = funs[name]
            try:
                fn(*parameters)
            except Exception,err:
                print "Error running preset", domain,":",name," for ", err

def add_preset_fn(fn,name,domain="default"):
    g = DfGlobal()
    presetdomains = g["preset-functions"]
    funs = presetdomains.setdefault(domain,{})
    funs[name] = fn
    send_preset_fn_names()
    
def send_preset_fn_names():
    g = DfGlobal()
    doms = g["preset-functions"]
    transfer = {}
    for f in doms:
        transfer_f = {}
        for k in doms[f]:
            transfer_f[k] = 0
        transfer[f] = transfer_f
    send_lines("set_global_key",repr(("preset-functions",transfer)))

def get_preset_fn_list(domain="default"):
    g = DfGlobal()
    presetdomains = g["preset-functions"]
    result = []
    print "dm-list:",domain
    print "presetdomains:",presetdomains
    if domain in presetdomains:
        result = presetdomains[domain].keys()[:]
        print "result:",result
        result.sort()

    return result
