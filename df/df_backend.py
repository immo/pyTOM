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
from pysqlite2 import dbapi2 as sqlite
from df_ontology import *
from df_limbs import *
from df_keyboard import *
from df_external import *
from df_userids import *
import math

def nbr(time):
   """nbr(time)   return the frame number of a time given in secs"""
   vars = DfGlobal()
   return int(vars["output_rate"] * time)

def cache(id):
    """cache(id)    send a cache request for sample number id"""

    out = DfGlobal()["out"]
    
    cmd = "!cache " + str(id) + "\n"
    out.write(cmd)
    out.flush()

def play(id, t=None, vol=1.0, group=-1, matrix="1", nosid=False):
   """play(id, t=None, vol=1.0, group=-1, matrix="1")   send a play command of sample number id and retrieve stream id"""
   vars = DfGlobal()
   vars["@sid"] = None
   out = vars["out"]

   if t==None:
      t = now() + 0.1

   uid = get_user_id()

   cmd = "!play " + str(id) + " " + str(nbr(t)) + " " + str(vol) + " " + str(group) + " " + str(matrix) + " " + str(uid) + "\n"
   #print cmd
   out.write(cmd)
   out.flush()

   try:
       vars["play.count"][id] += 1
   except KeyError:
       vars["play.count"][id] = 1

   # throughput of this version about 48*60 samples per minute (e.g. 4x16th @ 180BPM)
   # obviously, this is not enough for grindcore, so we have a shortcut (usually group ids suffice)

   if nosid:
       return uid
   else:
       while (1):
         if (vars["main_input_loop"]() < 0):
            break
         if vars["@sid"] != None:
            break

       id = vars["@sid"]
       if not id == None:
         id = int(id)
       return id


def id():
   """id()   get a fresh id"""
   vars = DfGlobal()
   vars["@id"] = None
   out = vars["out"]

   cmd = ".id\n"
   out.write(cmd)
   out.flush()

   #sleep_amount = vars["sleep_amount"]

   #vars["sleep_amount"] = 0.001 * sleep_amount

   while (1):
      if (vars["main_input_loop"]() < 0):
         break
      if vars["@id"] != None:
         break

   #vars["sleep_amount"] = sleep_amount

   id = vars["@id"]
   if not id == None:
      id = int(id)
   return id


def vol(id,vol,type='',group=0,t=None,bound=-1):
   """vol(id,vol,type='',group=0,t=None,bound=-1)
   several volume controls, apply command at time t
   if group = 1 -> id is group id, i.e. use VOL
   type=''  for setting volume,
   type='*' for multiplying volume
   type='<' for setting upper limits
   type='>' for setting lower limits"""
   vars = DfGlobal()
   if t == None:
      t = now()
   if group:
      cmd = "!VOL"
   else:
      cmd = "!vol"
   cmd += type + " " + str(id) + " " + str(vol) + " " + str(nbr(t))
   if group:
      cmd += " " + str(bound)
   cmd += "\n"

   out = vars["out"]
   out.write(cmd)
   out.flush()

def kill(id,group=0,t=None,bound=-1):
   """kill(id,group=0,t=None,bound=-1)   lap-kill streams (less popping)"""
   vars = DfGlobal()
   if t == None:
      t = now()
   if group:
      cmd = "!KILL"
   else:
      cmd = "!kill"
   cmd +=  " " + str(id) + " " + str(nbr(t))

   if group:
      cmd += " " + str(bound)

   cmd += "\n"
   #print cmd
   out = vars["out"]
   out.write(cmd)
   out.flush()

def ukill(id,group=0,t=None,bound=-1):
   """kill(id,group=0,t=None,bound=-1)   lap-kill streams (less popping)"""
   if bound < 0:
       kill(id,group,t,bound)
   else:
       vars = DfGlobal()
       if t == None:
          t = now()
       if group:
          cmd = "!UKILL"
       else:
          cmd = "!ukill"
       cmd +=  " " + str(id) + " " + str(nbr(t))

       if group:
          cmd += " " + str(bound)

       cmd += "\n"
       #print cmd
       out = vars["out"]
       out.write(cmd)
       out.flush()

def krll(id,group=0,t=None,bound=-1):
   """krll(id,group=0,t=None,bound=-1)   brutally-kill streams (popping!!)"""
   vars = DfGlobal()
   if t == None:
      t = now()
   if group:
      cmd = "!KRLL"
   else:
      cmd = "!krll"
   cmd += " " + str(id) + " " + str(nbr(t))


   if group:
      cmd += " " + str(bound)

   cmd += "\n"

   out = vars["out"]
   out.write(cmd)
   out.flush()

def now(position='cur_'):
   """now(position='cur_')  return the current time of the cursor named by position (e.g. the variable DfGlobal()[position+"now"])"""
   vars = DfGlobal()
   if position!='@':
      return vars[position+"now"]
   return vars["@now"]/vars["output_rate"]


# Internal stuff for setup etc.

def initialize_measures():
   """get a feature list from data contained in sample_info table of DfGlobal()["in_db"] and store in DfGlobal()["smp"] and DfGlobal()["smp_"+*] variables"""
   vars = DfGlobal()
   in_db = vars["in_db"]
   cur = in_db.cursor()
   cur.execute("CREATE TABLE IF NOT EXISTS sample_info ( filename TEXT, rate INTEGER, frames INTEGER, channels INTEGER, peak REAL, energy REAL ) ")
   cur.execute("SELECT filename, rate, frames, channels, peak, energy FROM sample_info")
   sample_info = {}
   sample_info_keyvals = {}
   sample_info_keysupp = {}
   smp = vars["smp"]
   length_vs_id = []
   energy_vs_id = []
   score_vs_id = []
   id_names = {}
   name_ids = {}

   for val in cur:
      info = {'rate': int(val[1]), 'frames': int(val[2]), 'channels': int(val[3]),\
              'peak': float(val[4]), 'energy': float(val[5])}
      info['length'] = float(info['frames'])/float(info['rate'])
      info['pre-roll'] = 0.0 #pre-roll is in seconds and says at which time of the sample file the actual hit takes place
      if val[0] in smp:
         info['id'] = smp[val[0]]
         length_vs_id.append( (info['length'], info['id'], val[0]) )
         energy_vs_id.append( (info['energy'], info['id'], val[0]) )
         score_vs_id.append( (info['length']*info['energy'], info['id'], val[0]) )
         id_names[info['id']] = val[0]
         name_ids[val[0]] = info['id']

      k = make_keys(val[0])

      if "p50" in k:
         info['pre-roll'] = 0.050
      if "p75" in k:
         info['pre-roll'] = 0.075
      if "p45" in k:
         info['pre-roll'] = 0.045

      sample_info[val[0]] = info
      sample_info_keyvals[val[0]] = k
      sample_info_keysupp = join_keys(sample_info_keysupp,k)
   vars["smp_info"] = sample_info
   vars["smp_info_vals"] = sample_info_keyvals
   vars["smp_info_keys"] = sample_info_keysupp
   ui = vars["ui_out"]
   #ui.write("CONSOLE: [o] calculating sample key value dependencies for known samples\n")
   #ui.flush()
   #vars["smp_info_deps"] = get_atomic_depends(sample_info_keyvals, sample_info_keysupp)
   ui.write("CONSOLE: [o] creating sample key feature info list for known samples\n")
   ui.flush()
   vars["smp_info_feat"] = make_feature_list(sample_info_keyvals, sample_info_keysupp, sample_info)
   ui.write("CONSOLE: [o] creating sample key feature info list for loaded samples\n")
   ui.flush()
   vars["smp_feat"] = make_feature_list(vars["smp_vals"], vars["smp_keys"], sample_info)

   length_vs_id.sort()
   energy_vs_id.sort()
   score_vs_id.sort()
   vars["t,id"] = length_vs_id
   vars["E,id"] = energy_vs_id
   vars["x,id"] = score_vs_id
   vars["id->name"] = id_names
   vars["id->name.repr"] = repr(id_names)
   vars["name->id"] = name_ids

   vars["play.count"] = {}

def prefetch_samples(playcount, id2names):
    """prefetch_samples(playcount, id2names)    prefetch the most important samples"""
    if not playcount:
        return
    
    name2ids = DfGlobal()["name->id"]
    
    quantiles = playcount.values()[:]
    quantiles.sort()
    p75quant = quantiles[int( math.floor(0.75*len(quantiles)))]
    clip = int(math.floor(p75quant *0.15))
    print "Play count 75-percentile = ",p75quant
    print "Prefetching samples with play count >= ",clip," ..."
    cnt = 0
    for i in playcount:
        if playcount[i] >= clip:
            try:
                cache(name2ids[ id2names[i] ])
                cnt += 1
            except KeyError:
                pass
    print "Prefetched ",cnt,"/",len(playcount)," samples."
    

def initialize_sample_list():
   """initialize the list with sample file id's used by the backend from DfGlobal()["out_db"] database table cached_samples."""
   vars = DfGlobal()
   cur = vars["out_db"].cursor()
   cur.execute("SELECT filename, file_id FROM cached_samples")
   filestruct={}
   keyvals = {}
   keysupp = {}
   ui = vars["ui_out"]
   ui.write("FLUSHSMP!\n")
   for val in cur:
      filestruct[val[0]] = int(val[1])
      k = make_keys(val[0])
      keyvals[val[0]] = k
      keysupp = join_keys(keysupp,k)
      ui.write("SMP:"+val[0]+"\n")
   ui.flush()
   vars["smp"] = filestruct
   vars["smp_vals"] = keyvals
   vars["smp_keys"] = keysupp
   #ui.write("CONSOLE: [o] calculating sample key value dependencies for loaded samples\n")
   #ui.flush()
   #vars["smp_deps"] = get_atomic_depends(keyvals, keysupp)

def initialize_backend():
   """initialize all stuff needed to drive the backend and generate music output"""
   vars = DfGlobal()
   out = vars["ui_out"]
   vars["@now"] = float(0)
   vars.set("in_db",sqlite.connect(vars["@input_db"]))
   vars.set("out_db",sqlite.connect(vars["@output_db"]))
   out.write("INDB:"+vars["@input_db"]+"\n")
   out.write("OUTDB:"+vars["@output_db"]+"\n")
   cur = vars["out_db"].cursor()
   cur.execute("SELECT name,value FROM configuration")
   for val in cur:
      value = val[1]
      if val[0] == "output_rate":
         value = float(value)
         out.write("SAMPLE-RATE:"+str(value)+"\n")
         out.flush()
      vars[val[0]] = value
      out.write("CONSOLE: (*) "+val[0]+" = "+str(val[1])+"\n")
   out.flush()
   initialize_sample_list()
   out = vars["out"]
   itime = int(vars["output_rate"])/25
   out.write("ointerval "+str(itime)+"\n")
   initialize_measures()
   ui = vars["ui_out"]
   ui.write("CONSOLE: [o] initializing generators & instruments\n")
   ui.flush()
   vars["reinitialize_generators"]()
   ui = vars["ui_out"]
   ui.write("CONSOLE: [o] done.\n")
   ui.flush()
   initialize_limbs()
   ui.write("CONSOLE: (.) try to run setup from "+ DfGlobal()["setup_path"] +"\n")
   ui.write("BOUNCE:"+ DfGlobal()["setup_path"] +"\n")
   ui.flush()
   ui.write("CONSOLE: (.) try to restore autosaved state from "+ DfGlobal()["autosave_path"] +"\n")
   ui.write("BOUNCE:"+ DfGlobal()["autosave_path"] +"\n")
   ui.flush()
   reload_external_data()

