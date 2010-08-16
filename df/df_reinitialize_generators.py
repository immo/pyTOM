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
from df_backend import *
from df_global import *
from df_interpreter import *
from df_ontology import *
from df_model import *
from df_live import *
from math import *
import random
from pysqlite2 import dbapi2 as sqlite

#
# This function will just re-enalbe the usage of the (legacy) generator structures
#

def set_legacy_generators():
   """activate legacy module for generating output"""
   g = DfGlobal()
   g["fill-output"] = default_fill_output
   g["cur_now"] = now('@') + g["cur_advance"]
   g["@now-callback"] = time_callback

# This function tries to reset all generator-stuff to the defaults,
# of course it is always possible to break the whole front-end and then
# this function will not work

def reinitialize_generators():
   """reset output generating structures and, if DfGlobal()["smp_feat"] exists, create DfGlobal()["instruments"] from it."""
   g = DfGlobal()
   ui = g["ui_out"]
   ui.write("CONSOLE: [o] ... initializing generators\n")
   ui.flush()
   g["cur_advance"] = 0.5 # generate output 0.5 seconds ahead
   g["fill-output"] = default_fill_output
   g["cur_now"] = now('@') + g["cur_advance"]
   g["@now-callback"] = time_callback
   g["songdata"] = []
   g["songstart"] = now()
   if (g.has("smp_feat")):
      initialize_instruments()
   else:
      g["instruments"] = {}


#
# This is most important to set it up according to the sample library you are using!
# (YOUR INDIVIDUAL WORK, DEPENDING ON YOUR SETUP)
#

def initialize_instruments():
   """initialize DfGlobal()["instruments"] variable with Instrument objects obtained from the "smp_feat" sample list"""
   g = DfGlobal()
   cur = g["in_db"].cursor()
   ui = g["ui_out"]
   ui.write("CONSOLE: [o] ... initializing instruments\n")
   ui.flush()

   try:
      cur.execute("SELECT * FROM instrument_names WHERE 1=2")
   except sqlite.OperationalError:
      g["regenerate_instruments"] = 1

   if g["regenerate_instruments"]:
      ui.write("CONSOLE: [o] ... re-generating instrument_names\n")
      ui.flush()

      g["regenerate_instruments"] = 0

      option_keys = filter(lambda x: (x != "off") and (x != "p50") and (x != "p75") and (len(x) == 3) and (x[0].isalpha())\
                           and (x != "pre") and (x != "ogg"), g["smp_keys"])\
                  + filter(lambda x: (x != "roll") and (x != "nsmr") and (len(x)==4) and ((x[3]=='l') or (x[3]=='r')),g["smp_keys"])\
                  + ["a","b"]
      def is_num(s):
         if len(s) == 0:
            return 0
         if (s[0].isdigit()):
            return 1
         return is_num(s[1:])
      def is_alpha_and_num(s):
         if len(s) <= 1:
            return 0
         if (s[0].isalpha()):
            return is_num(s[1:])
         return is_alpha_and_num(s[1:])
      instrument_keys = filter(lambda x: (len(x)>=4) and is_alpha_and_num(x[1:]) and (x[0].isalpha()), g["smp_keys"])\
                  + ["synth","bigkick"]
      option_keys.sort()
      instrument_keys.sort()
      def power_list(l):
         if l == []:
            return [[]]
         subl = power_list(l[1:])
         return map(lambda x: x + [l[0]], subl) + subl

      instruments = {}
      ui.write("CONSOLE: [o] ... found " +str(len(instrument_keys)) + " instruments and " + str(len(option_keys)) + " options.\n")
      ui.flush()

      loaded_instruments = []

      for iname in instrument_keys:
         ui.write("CONSOLE: [o] ... " + iname + "\n")
         ui.flush()
         ident = id()
         for onames in power_list(option_keys):
            if (len(onames) > 2):
               continue
            keys = [iname] + onames

            i = Instrument()


            i.add(keys)
            if len(i.sample_infos) > 0:
               name = iname + "("
               onames.sort()
               for oname in onames:
                  name += oname + ","
               name = name[0:len(name)-1]
               if (onames != []):
                  name += ")"

               loaded_instruments += [name]

               i.group_id = ident
               if iname.startswith("kd"):
                   i.kill_groups[ident] = 0.035
               elif iname.startswith("big"):
                   i.kill_groups[ident] = 0.04
               elif iname.startswith("syn"):
                   i.kill_groups[ident] = 0.04
                   i.hit = i.hit2
               elif iname.startswith("sn"):
                  i.kill_groups[ident] = -0.025
               elif iname.startswith("tm"):
                  i.kill_groups[ident] = -0.030
               elif "grb" in onames:
                  i.kill_groups[ident] = -0.1
               elif "hgrb" in onames:
                  i.kill_groups[ident] = -0.1
               elif "ped" in onames:
                  i.kill_groups[ident] = -0.05
               else:
                  i.kill_groups[ident] = -0.25

               i.matrix = "m"+iname;

               instruments[name] = i

      g["instruments"] = instruments

      ui.write("CONSOLE: [o] ... done.\n")
      ui.flush()

      cur.execute("DROP TABLE IF EXISTS instrument_names")
      cur.execute("CREATE TABLE instrument_names ( name TEXT )")
      for name in loaded_instruments:
         cur.execute("INSERT INTO instrument_names VALUES ('"+name+"')")
      g["in_db"].commit()
   else:
      ui.write("CONSOLE: [o] ... using cached instrument_names\n")
      ui.flush()
      instrument_names = cur.execute("SELECT * FROM instrument_names")
      g["instruments"] = {}
      instrument_ids = {}
      for vals in instrument_names:
         name = vals[0]
         n1 = name.split("(")
         n2 = ""
         if len(n1) > 1:
            n2 = n1[1].split(")")[0]
         opts = n2.split(",")
         iname = n1[0]
         regenname = iname
         if opts != ['']:
            regenname += '('
            for o in opts:
               regenname += o + ","
            regenname = regenname[0:len(regenname)-1] + ')'


         ui.write("CONSOLE: [o] ... " + regenname + "\n")
         ui.flush()

         i = Instrument()
         keys = [iname] + opts
         i.add(keys)

         if instrument_ids.has_key(iname):
            i.group_id = instrument_ids[iname]
         else:
            i.group_id = id()
            instrument_ids[iname] = i.group_id

         onames = opts
         ident = i.group_id

         if iname.startswith("kd"):
            i.kill_groups[ident] = 0.035
         elif iname.startswith("big"):
             i.kill_groups[ident] = 0.04
         elif iname.startswith("syn"):
            i.kill_groups[ident] = 0.04
            i.hit = i.hit2
         elif iname.startswith("sn"):
            i.kill_groups[ident] = -0.025
         elif iname.startswith("tm"):
            i.kill_groups[ident] = -0.030
         elif "grb" in onames:
            i.kill_groups[ident] = -0.1
         elif "hgrb" in onames:
            i.kill_groups[ident] = -0.1
         elif "ped" in onames:
            i.kill_groups[ident] = -0.05
         else:
            i.kill_groups[ident] = -0.25

         i.matrix = "m"+iname;

         g["instruments"][regenname] = i
   if "bigkick" in g["instruments"]:
      if "kd20punch" in g["instruments"]:
         g["instruments"]["kd20punch"].side_kick += [g["instruments"]["bigkick"]]
   if "bigkick(a)" in g["instruments"]:
      if "kd20punch(a)" in g["instruments"]:
         g["instruments"]["kd20punch(a)"].side_kick += [g["instruments"]["bigkick(a)"]]
   if "bigkick(b)" in g["instruments"]:
      if "kd20punch(b)" in g["instruments"]:
         g["instruments"]["kd20punch(b)"].side_kick += [g["instruments"]["bigkick(b)"]]
