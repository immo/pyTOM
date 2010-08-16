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
from os import path, listdir
from df_data_channels import *
import re
import os
import shutil
from df_xml_thing import *

def pad_string(s,length=4,c='0'):
    if len(s) < length:
        return c*(length-len(s)) + s
    return s

def save_changed_external_data():
    """ saves those external data, that have been marked as changed. makes backups """
    g = DfGlobal()
    if not "ext" in g:
        return
    
    backupdir = g["ext.path"] + path.sep + "bak"
    if not path.exists(backupdir):
        os.mkdir(backupdir)

    files = g["ext.files"]
    ext = g["ext"]
        
    for name in g["ext.changed"]:
        idx = 1
        filename = backupdir + path.sep + name + "-" + pad_string(str(idx))
        while path.exists(filename):
            idx += 1
            filename = backupdir + path.sep + name + "-" + pad_string(str(idx))
        shutil.move(files[name],filename)
        f = open(files[name], "w")
        f.write(ext[name])
        f.close()
        
    g["ext.changed"] = []
    

def reload_external_data():
    """ reloads external data that is written in files in the ext subdirs of
    the setup and autosave directories """

    g = DfGlobal()

    save_changed_external_data()

    paths = [g["setup_path"], g["autosave_path"]]

    g["ext.path"] = path.dirname(g["autosave_path"]) + path.sep + "ext"

    files = {}


    for p in paths:
        d = path.dirname(p) + path.sep + "ext"
        try:
            filelist = filter( lambda x: path.isfile(x),\
                               map(lambda x: d + path.sep + x,\
                                   listdir(d)) )
            for f in filelist:
                files[path.basename(f)] = f
        except OSError:
            pass

    ext = {}

    ext_taxa = {}

    taxafinder = re.compile(r"[ \t]*taxa[ \t]*=[^\n]*")

    things = []

    things_dic = {}

    thingtest = re.compile(r"[ \t]*<\?xml.*\?>.*<things/?>")

    grammartest = re.compile(r":.*\(.*\)")

    grammars = []    

    songs = []

    scripts = []

    songtest = re.compile(".*:.*initial.*=.*")

    for k in files:
        ext[k] = open(files[k]).read()

    g['ext.files'] = files

    g['ext'] = ext

    try:
        data = g["ext"]['reload_autorun.py']
    except KeyError:
        pass
    else:
        try:
            g["python.bouncer.fn"](repr(data))
        except Exception, err:
            print "ERROR IN ext/reload_autorun.py while loading ext data:"
            print err
        ext = g['ext']

    for k in ext:
        if k.endswith('~') or k.endswith('#'):
            continue
        taxamatch = taxafinder.search(ext[k])
        if taxamatch and not k.upper().endswith('.PY'):
            taxaline = ext[k][taxamatch.start():taxamatch.end()]
            rightpart = taxaline.find("=")
            try:
                taxa = eval(taxaline[rightpart+1:])
            except:
                taxa = taxaline[rightpart+1:]
            ext_taxa[k] = taxa
        data_inline = ext[k].replace('\n',' ')
        if songtest.match(data_inline):
            songs.append(k)
        elif grammartest.search(ext[k])\
                 and not k.upper().endswith('.PY'):
            grammars.append(k)
        if thingtest.match(data_inline):
            things.append(k)
            try:
                things_dic[k] = xml_to_things(ext[k])
            except Exception,err:
                print "Error building things list: ",k
                print "   reason:  ",err
        if k.upper().endswith(".PY"):
            scripts.append(k)
        

    g['ext.scripts'] = scripts
    g['ext.taxa'] = ext_taxa
    g['ext.songs'] = songs
    g['ext.things'] = things
    g['ext.changed'] = []
    g['ext.grammars'] = grammars
    g['things'] = things_dic
    
    g('reload-external-data-hook',lambda :0)()

    
def CALL(extname,*parms):
    """ call a script from ext data via interpreter bounce.... """
    g = DfGlobal()
    g["asynchroneous_parameters_id"] += 1    
    parmid = g["asynchroneous_parameters_id"]
    g["asynchroneous_parameters"][parmid] = parms
    try:
        data = g["ext"][extname]
    except KeyError:
        print "Cannot call ext-script >>",extname,"<<: Data not found."
    else:
        parmsdata = "DfGlobal()['PARMS'] = DfGlobal()"+\
                    "['asynchroneous_parameters'].pop("+repr(parmid)+")\n"
        parmsdata += data
        send_line('ext-bounce',repr(parmsdata))
    
def CALLNOW(extname,*parms):
    """ call a script from ext right now (use inside try-catch)
    optional parameters are sent to DfGlobal()['PARMS']
    """
    g = DfGlobal()
    g['PARMS'] = parms    
    try:
        data = g["ext"][extname]
    except KeyError:
        print "Cannot `call-now` ext-script >>",extname,"<<: Data not found."
    else:
        g["python.bouncer.fn"](repr(data))

def CALLRET(extname,*parms):
    """ call a script from ext right now and use DfGlobal()['RET'] as return value """
    g = DfGlobal()
    g['RET'] = None
    CALLNOW(extname,*parms)
    return g['RET']

