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
from xml.etree import ElementTree as ET

def test_load():
   """test_load()    return split_legacy(load_legacy_xml("/home/immanuel/Documents/musik/trommeln_live.xml"))"""
   return split_legacy(load_legacy_xml("/home/immanuel/Documents/musik/trommeln_live.xml"))

def split_legacy(data, dt=4):
   """split_legacy(data, dt=4)   split legacy data structure at breaks without hits of length at least dt"""
   if len(data) == 0:
      return []
   parts = []
   data = map(lambda(t,d,s):(t-data[0][0],d,s),data)
   for j in range(len(data)-2,-1,-1):
      if data[j+1][0] - data[j][0] > dt:
         parts = parts + [ map(lambda(t,d,s):(t-data[j+1][0],d,s),data[j+1:]) ]
         data = data[:j+1]
   return parts + [data]

def preload_instruments():
   """obscure legacy code that i do not recognize :)"""
   g = DfGlobal()
   i = g["instruments"]
   counter = 0.0
   global_count = 0
   midi_names = {}
   midi_names[1] = 'cy20ride(bel)'
   midi_names[2] = 'cy15crash(ord)'
   midi_names[3] = 'cy15crash(bel)'
   midi_names[4] = 'cy15crash(grb)'
   midi_names[5] = 'cy15crash(rim)'
   midi_names[6] = 'cy15crash(top)'
   midi_names[7] = 'cy18crash(ord)'
   midi_names[8] = 'cy18crash(bel)'
   midi_names[9] = 'cy18crash(grb)'
   midi_names[10] = 'cy18crash(rim)'
   midi_names[11] = 'cy18crash(top)'
   midi_names[12] = 'cy19china(ord)'
   midi_names[13] = 'cy19china(grb)'
   midi_names[14] = 'cy19china(top)'
   midi_names[15] = 'tm14rock(ord,stxl)'
   midi_names[16] = 'tm14rock(ord,stxr)'
   midi_names[17] = 'tm14rock(rms,stxr)'
   midi_names[18] = 'hh13(grb)'
   midi_names[19] = 'tm10rock(ord,stxl)'
   midi_names[20] = 'tm10rock(ord,stxr)'
   midi_names[21] = 'tm10rock(rms,stxl)'
   midi_names[22] = 'tm10rock(rms,stxr)'
   midi_names[23] = 'kd20punch(a)'
   midi_names[24] = 'kd20punch(b)'
   midi_names[25] = 'tm12rock(ord,stxl)'
   midi_names[26] = 'tm12rock(ord,stxr)'
   midi_names[27] = 'tm12rock(rms,stxl)'
   midi_names[28] = 'tm12rock(rms,stxr)'
   midi_names[29] = 'hh13(ord,stxl)'
   midi_names[30] = 'hh13(ord,stxr)'
   midi_names[46] = 'hh13(ped)'
   midi_names[31] = 'sn14wrock(prs,stxl)'
   midi_names[32] = 'sn14wrock(prs,stxr)'
   midi_names[33] = 'cy20ride(ord)'
   midi_names[34] = 'cy20ride(grb)'
   midi_names[35] = 'cy20ride(rim)'
   midi_names[36] = 'sn14wrock(rms,stxl)'
   midi_names[37] = 'sn14wrock(rms,stxr)'
   midi_names[38] = 'sn14wrock(ord,stxl)'
   midi_names[39] = 'sn14wrock(ord,stxr)'
   midi_names[40] = 'cy8splash(ord)'
   midi_names[41] = 'cy8splash(bel)'
   midi_names[42] = 'cy8splash(grb)'
   midi_names[43] = 'hh13(stxl,top)'
   midi_names[44] = 'hh13(stxr,top)'
   midi_names[45] = 'sn14wrock(xtk)'
   midi_names[123] = 'synth(ful)'
   midi_names[124] = 'synth(ful)'
   for x in midi_names:
      global_count = global_count + i[x].preload_cache(time=now()+counter)
      print global_count
      counter = counter + 0.3
   return global_count

def load_legacy_xml(filename):
   """load_legacy_xml(filename)   load a legacy data xml file with name filename"""
   g = DfGlobal()
   midi_names = {}
   midi_names[1] = 'cy20ride(bel)'
   midi_names[2] = 'cy15crash(ord)'
   midi_names[3] = 'cy15crash(bel)'
   midi_names[4] = 'cy15crash(grb)'
   midi_names[5] = 'cy15crash(rim)'
   midi_names[6] = 'cy15crash(top)'
   midi_names[7] = 'cy18crash(ord)'
   midi_names[8] = 'cy18crash(bel)'
   midi_names[9] = 'cy18crash(grb)'
   midi_names[10] = 'cy18crash(rim)'
   midi_names[11] = 'cy18crash(top)'
   midi_names[12] = 'cy19china(ord)'
   midi_names[13] = 'cy19china(grb)'
   midi_names[14] = 'cy19china(top)'
   midi_names[15] = 'tm14rock(ord,stxl)'
   midi_names[16] = 'tm14rock(ord,stxr)'
   midi_names[17] = 'tm14rock(rms,stxr)'
   midi_names[18] = 'hh13(grb)'
   midi_names[19] = 'tm10rock(ord,stxl)'
   midi_names[20] = 'tm10rock(ord,stxr)'
   midi_names[21] = 'tm10rock(rms,stxl)'
   midi_names[22] = 'tm10rock(rms,stxr)'
   midi_names[23] = 'kd20punch(a)'
   midi_names[24] = 'kd20punch(b)'
   midi_names[25] = 'tm12rock(ord,stxl)'
   midi_names[26] = 'tm12rock(ord,stxr)'
   midi_names[27] = 'tm12rock(rms,stxl)'
   midi_names[28] = 'tm12rock(rms,stxr)'
   midi_names[29] = 'hh13(ord,stxl)'
   midi_names[30] = 'hh13(ord,stxr)'
   midi_names[46] = 'hh13(ped)'
   midi_names[31] = 'sn14wrock(prs,stxl)'
   midi_names[32] = 'sn14wrock(prs,stxr)'
   midi_names[33] = 'cy20ride(ord)'
   midi_names[34] = 'cy20ride(grb)'
   midi_names[35] = 'cy20ride(rim)'
   midi_names[36] = 'sn14wrock(rms,stxl)'
   midi_names[37] = 'sn14wrock(rms,stxr)'
   midi_names[38] = 'sn14wrock(ord,stxl)'
   midi_names[39] = 'sn14wrock(ord,stxr)'
   midi_names[40] = 'cy8splash(ord)'
   midi_names[41] = 'cy8splash(bel)'
   midi_names[42] = 'cy8splash(grb)'
   midi_names[43] = 'hh13(stxl,top)'
   midi_names[44] = 'hh13(stxr,top)'
   midi_names[45] = 'sn14wrock(xtk)'
   midi_names[123] = 'synth(ful)'
   midi_names[124] = 'synth(ful)'

   hits = []

   tree = ET.parse(filename)
   for x in tree.getroot():
      for evt in x.getchildren():
         time = float(evt.get("frame"))/44100.0
         drum = midi_names[int(evt.get("d1"))]
         strength = float(evt.get("d2")) / 127.0
         hits += [(time,drum, strength)]
   return hits

def play_legacy(list,delta=None,vol=1.0):
   """play_legacy(list,delta=None,vol=1.0)   plays legacy data list with offset delta and volume vol"""
   if delta==None:
      delta=now()
   g = DfGlobal()
   g["songstart"] = delta
   g["songdata"] = list


def play_legacy2(list,delta=None,vol=1.0):
   """play_legacy2(list,delta=None,vol=1.0)   puts legacy data list with offset delta and volume vol DIRECTLY (only for stress tests!)"""
   if delta==None:
      delta=now()
   gi = DfGlobal()["instruments"]
   for (t,d,s) in list:
      drum = gi[d]
      drum.hit(drum.energy(s),delta+t,vol=vol)
