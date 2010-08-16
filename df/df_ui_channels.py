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
from Tix import *
import tkFileDialog
import Pmw
import sys
import os
import errno
import subprocess
import tkMessageBox
from pysqlite2 import dbapi2 as sqlite
from df_global import *
from ScrollableMultiSelectTree import *
from math import *
from biquad_calculations import *

def get_filter_list(filters):
   """get_filter_list(filters)   turn filters string into a list of filter values to be passed to the backend"""
   filters = filters.replace('\n',' ')
   f = [x.strip().split('(') for x in filters.split(')')]
   vals = []
   for filter in f:
      if len(filter)==2:
         type = filter[0]
         type = type.strip().lower()

         try:
            params = [float(x) for x in filter[1].split(",")]
            nbr = 3
            if type.endswith("pass"):
               nbr = 2
            if len(params) != nbr:
               print "Error in filter ",type,"(",filter[1],"): Should have ", nbr, "parameters!"
            elif type=="band":
               a,b = band_biquad(params[0],params[1],params[2],DfGlobal()["sample-rate"])
               vals += [(a,b)]
            elif type=="low":
               a,b = lowshelf_biquad(params[0],params[1],params[2],DfGlobal()["sample-rate"])
               vals += [(a,b)]
            elif type=="high":
               a,b = highshelf_biquad(params[0],params[1],params[2],DfGlobal()["sample-rate"])
               vals += [(a,b)]
            elif type=="bandpass":
               a,b = bandpass_biquad(params[0],params[1],DfGlobal()["sample-rate"])
               vals += [(a,b)]
            elif type=="lowpass":
               a,b = bandpass_biquad(params[0],params[1],DfGlobal()["sample-rate"])
               vals += [(a,b)]
            elif type=="highpass":
               a,b = bandpass_biquad(params[0],params[1],DfGlobal()["sample-rate"])
               vals += [(a,b)]
            else:
               print "Error in filter ",type,"(",filter[1],"): Unknown filter type"
         except ValueError, msg:
            print "Error in filter ",type,"(",filter[1],"): ", msg
      elif filter != ['']:
         print "Error in filter list: Parenthesis mismatch: ", filter
   return vals

def generate_command_dyn(channel,filters):
   """generate_command_dyn(channel,filters)   generate dynamic filter command for channel from filters"""
   filters = filters.replace('\n',' ')
   f = [x.strip().split('(') for x in filters.split(')')]
   cmd = ""
   for filter in f:
      if len(filter)==2:
         type = filter[0]
         type = type.strip().lower()

         params = filter[1]
         if type=="meter":
               cmd += "CONSOLE:ssetdynmeter " + str(channel)+ " "+params+"\n"
         elif type=="gain":
               cmd += "CONSOLE:ssetdyn " + str(channel) + " "+ params+ "\n"
         else:
               print "Error in filter list: Unknown type: ", type
      else:
         print "Error in filter list: Parenthesis mismatch: ", filter
   return cmd

def generate_command(type,channel,filters):
   """generate_command(type,channel,filters)   generate command for channel and filters, using "sset"+type command"""
   cmd = "sset"+type+" " + str(channel)
   for f in filters:
      a,b = f
      cmd += " ( "
      for x in a:
         cmd += str(x) + " "
      cmd += "| "
      for x in b:
         cmd += str(x) + " "
      cmd += ")"
   return cmd


def create_channel_panel(num,notebook,root):
   """create_channel_panel(num,notebook,root)   creates the panel window for channel num in notebook, creating shortcut in root"""
   global chan_page
   num += 1;
   pname = "#"+str(num)
   print "UI: #",str(num)
   page = notebook.insert(pname,'control')
   DfGlobal()["notebook"] = notebook
   if (num < 10):
      shortcut = "<Control-Key-"+str(num)+">"
   elif (num==10):
      shortcut = "<Control-Key-0>"
   if num <= 10:
      root.bind(shortcut,eval("lambda x: DfGlobal()[\"notebook\"].selectpage('"+pname+"')"))

   Label(page,text="Pre-dynamic filter equalizer settings:",justify=LEFT,anchor="w").pack(side=TOP)
   prefr = Frame(page)
   prefr.pack(fill=X,side=TOP)
   pre = Text(prefr,width=60,height=6)
   pre.pack(side=LEFT,fill=X,expand=True)
   pre_r = Frame(prefr)
   pre_r.pack(side=RIGHT)

   def help_callback():
            tkMessageBox.showinfo(message=\
"Enter the codes for the subsequent equalizer-filters, where\n\n\
band(freq, gain, width)\t... adjust gain to band around freq with bandwidth width\n\n\
low(freq, gain, slope)\t... adjust gain to low-shelf with cutoff freq and slope\n\n\
high(freq, gain, slope)\t... adjust gain to high-shelf with cutoff freq and slope\n\n\
bandpass(freq, width)\t... apply band-pass filter around freq with bandwidth with\n\n\
lowpass(freq, slope)\t... apply low-pass filter with cutoff freq and slope\n\n\
highpass(freq, slope)\t... apply high-pass filter with cutoff freq and slope\n\n")

   def apply_callback():
      filters = get_filter_list(pre.get(1.0,END))
      DfGlobal()[pname+".pre"] = pre.get(1.0,END)
      o = DfGlobal()["UI_O"]
      o.write("CONSOLE:"+generate_command("pre",num-1,filters)+"\n")
      o.flush()

   Button(pre_r,text="Help",command=help_callback).pack(side=TOP,fill=X)
   Button(pre_r,text="Set/Apply",command=apply_callback).pack(side=TOP,fill=X)

   Label(page,text="Dynamic filter settings:",justify=LEFT,anchor="w").pack(side=TOP,pady=10)
   dynfr = Frame(page)
   dynfr.pack(fill=X,side=TOP)
   dyn = Text(dynfr,width=60,height=6)
   dyn.pack(side=LEFT,fill=X,expand=True)
   dyn_r = Frame(dynfr)
   dyn_r.pack(side=RIGHT)

   def help_callback2():
      tkMessageBox.showinfo(message=\
"Enter the following setup codes:\n\n\
meter(AVG_BLOCK_SIZE METER_DECAY)\twhere AVG_BLOCK_SIZE is the size of the blocks that are\
 used to determine the current volume and METER_DECAY is the influence factor of the old meter value\n\n\
gain([METER_LEVEL GAIN ATTACK_FACTOR RELEASE_FACTOR](n times) METER_LEVEL GAIN )\t set the dynamic filter behaviour\n\n")
      pass

   def apply_callback3():
      filters = dyn.get(1.0,END)
      DfGlobal()[pname+".dyn"] = dyn.get(1.0,END)
      o = DfGlobal()["UI_O"]
      o.write(generate_command_dyn(num-1,filters))
      o.flush()

   Button(dyn_r,text="Help",command=help_callback2).pack(side=TOP,fill=X)
   Button(dyn_r,text="Set/Apply",command=apply_callback3).pack(side=TOP,fill=X)

   Label(page,text="Post-dynamic filter equalizer settings:",justify=LEFT,anchor="w").pack(side=TOP,pady=10)
   postfr = Frame(page)
   postfr.pack(fill=X,side=TOP)
   post = Text(postfr,width=60,height=6)
   post.pack(side=LEFT,fill=X,expand=True)
   post_r = Frame(postfr)
   post_r.pack(side=RIGHT)

   def apply_callback2():
      filters = get_filter_list(post.get(1.0,END))
      DfGlobal()[pname+".post"] = post.get(1.0,END)
      o = DfGlobal()["UI_O"]
      o.write("CONSOLE:"+generate_command("post",num-1,filters)+"\n")
      o.flush()

   Button(post_r,text="Help",command=help_callback).pack(side=TOP,fill=X)
   Button(post_r,text="Set/Apply",command=apply_callback2).pack(side=TOP,fill=X)


   Label(page,text="Master volume gain factor:",justify=LEFT,anchor="w").pack(side=TOP,pady=10)
   fr = Frame(page)
   fr.pack(fill=X,side=TOP)

   DfGlobal()[pname+".volume"] = StringVar()
   DfGlobal()[pname+".volume"].set("1.0")

   entry = Entry(fr,width=20,justify=RIGHT,textvariable=DfGlobal()[pname+".volume"])

   entry.pack(side=RIGHT)
   scale = Scale(fr,from_=-10.0,to=log(10.0),resolution=0.025,showvalue=0,orient=HORIZONTAL)
   scale.pack(side=LEFT,fill=X,expand=True)
   scale.set(log(1.0))
   DfGlobal()[pname+".volume.slider"] = log(1.0)


   def callback_fn(*args):
      value = DfGlobal()[pname+".volume"].get()
      o = DfGlobal()["UI_O"]
      print "SCALE CALLBACK"
      try:
         newval = float(value)
         cmd = "svol " + str(num-1) + " " + str(newval)
         o.write("CONSOLE:"+cmd+"\n")
         o.flush()

         if newval > 0:
            if DfGlobal()[pname+".volume.slider"] != log(newval):
               scale.set(log(newval))
         else:
            if DfGlobal()[pname+".volume.slider"] != log(-10.0):
               scale.set(-10.0)

      except ValueError:
         pass

   def scale_callback(event):
      newslider = float(scale.get())
      oldslider = float(DfGlobal()[pname+".volume.slider"])

      if (newslider != oldslider):
         DfGlobal()[pname+".volume.slider"] = newslider
         entry.delete(0,END)
         if newslider <= -10.0:
            entry.insert(0,str(0.0))
         else:
            entry.insert(0,str(exp(newslider)))
         callback_fn(0)

   DfGlobal()[pname+".volume"].trace("w",callback_fn)

   scale.config(command=scale_callback)

   Label(page,text="Input database:",justify=LEFT,anchor="w").pack(side=TOP,pady=10)
   fr = Frame(page)
   fr.pack(fill=X,side=TOP)

   def load_db():
      in_db = sqlite.connect(DfGlobal()["in_db_name"])
      cur = in_db.cursor()
      cur.execute("CREATE TABLE IF NOT EXISTS channel_"+str(num-1)+"_filter_settings ( name TEXT, value TEXT ) ")
      settings = cur.execute("SELECT * FROM channel_"+str(num-1)+"_filter_settings")
      for s in settings:
         if s[0] == "post":
            post.delete(1.0, END)
            post.insert(END, s[1])
         elif s[0] == "pre":
            pre.delete(1.0, END)
            pre.insert(END, s[1])
         elif s[0] == "dyn":
            dyn.delete(1.0, END)
            dyn.insert(END, s[1])
         elif s[0] == "master":
            DfGlobal()[pname+".volume"].set(s[1])
      apply_callback()
      apply_callback2()
      apply_callback3()

   def clear_db():
      in_db = sqlite.connect(DfGlobal()["in_db_name"])
      cur = in_db.cursor()
      cur.execute("DROP TABLE IF EXISTS channel_"+str(num-1)+"_filter_settings")
      in_db.commit()
      pass

   def save_db():
      in_db = sqlite.connect(DfGlobal()["in_db_name"])
      cur = in_db.cursor()
      cur.execute("DROP TABLE IF EXISTS channel_"+str(num-1)+"_filter_settings")
      cur.execute("CREATE TABLE IF NOT EXISTS channel_"+str(num-1)+"_filter_settings ( name TEXT, value TEXT ) ")
      cur.execute("INSERT INTO channel_"+str(num-1)+"_filter_settings VALUES (?,?)", ("post",post.get(1.0,END),))
      cur.execute("INSERT INTO channel_"+str(num-1)+"_filter_settings VALUES (?,?)", ("pre",pre.get(1.0,END),))
      cur.execute("INSERT INTO channel_"+str(num-1)+"_filter_settings VALUES (?,?)", ("dyn",dyn.get(1.0,END),))
      cur.execute("INSERT INTO channel_"+str(num-1)+"_filter_settings VALUES (?,?)", ("master",DfGlobal()[pname+".volume"].get()))
      in_db.commit()
      pass

   Button(fr,text="Load database settings (Reset current)",command=load_db).pack(side=TOP,fill=X)
   Button(fr,text="Clear database settings",command=clear_db).pack(side=TOP,fill=X)
   Button(fr,text="Save settings to database",command=save_db).pack(side=TOP,fill=X)

   load_db()


