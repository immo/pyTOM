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
from df_database import *
from os import path as os_path
from df_external import *
from df_volume_control import *

def save_global(out,name):
    try:
        out.write("DfGlobal()["+repr(name)+"] = "+repr(DfGlobal()[name])+"\n")
    except:
        pass

def send_global(out,name):
    try:
        out.write("try:\n   send_line("+repr(name)+", repr(DfGlobal()["+repr(name)+"]))\nexcept:\n   pass\n")
    except:
        pass

def save_state(path):
    """save the current machines state as executable python script in path"""
    out = open(path, "w")
    out.write("# drums-frontend state-restoring python script\n")
    out.write("print 'restoring saved state...'\n")

    global_saves = ["concept.list","last.sketch",\
                   "last.dbf_list","sketch.pool",\
                    "volume.presets"]

    for obj in global_saves:
        save_global(out,obj)

    global_objs = ["db.default.name","db.default.riff",\
                   "db.default.song",\
            "utils.g.domain","utils.g.codomain","utils.g.colormap","utils.g.vertexmap",\
            "utils.g.vertexpos","utils.g.behaviour","utils.lc.domain","utils.lc.codomains",\
            "utils.lc.colmaps","utils.lc.vtxmaps","utils.lc.behaviours","utils.lc.tags",\
            "utils.lc.vtxpos"]
    for obj in global_objs:
        save_global(out,obj)
        send_global(out,obj)
    try:
        out.write("send_line('sketch', repr(DfGlobal()['last.sketch']))\n")
    except:
        pass
    try:
        out.write("send_line('dbf_list', repr(DfGlobal()['last.dbf_list']))\n")
    except:
        pass    
    try:
        CompositionDatabase().store_database(out)
    except:
        pass
    out.write("print '  generating default rules...'\n")
    out.write("gen_default_rules()\n")
    out.write("print 'done.'\n")
    out.write("print 'Restoring instrument volume levels...'\n")
    out.write("set_instrument_volumes("+repr(get_instrument_volumes())+")\n")
    out.write("print 'Pre-Fetching favorite samples.'\n")
    out.write("prefetch_samples("+repr(DfGlobal()['play.count'])+","+DfGlobal()["id->name.repr"]+")\n")
    out.close()

def do_autosave():
    save_changed_external_data()
    if (DfGlobal()["autosave_path"] != "") and (DfGlobal()["autosave_path"]):
        if CompositionDatabase().isSuccessfulLoaded():
            print "Writing autosave to '"+DfGlobal()["autosave_path"] + "'"
            save_state(DfGlobal()["autosave_path"])
            print "...done."
        else: # do not overwrite the old autosave file
            #   in case it did not load correctly !!
            new_path = DfGlobal()["autosave_path"]
            sep_idx = new_path.rfind(os_path.sep)
            if sep_idx >= 0:
                directory = new_path[0:sep_idx+1]
                filename = new_path[sep_idx+1:]
            else:
                directory = ""
                filename = new_path
            token = 0
            while os_path.exists(directory+str(token)+"-"+filename):
                token += 1
            new_path= directory+str(token)+"-"+filename
            DfGlobal()["autosave_path"] = new_path
            print "Writing autosave to '"+new_path+"'"
            save_state(new_path)
            print "...done."
            CompositionDatabase().successfulLoaded()
