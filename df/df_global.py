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

from bisect import *

class DfGlobal(object):
   """
global-namespace class that provides an associative array that is shared between all modules and namespaces
one can access global variables named by a string via DfGlobal()[name]"""
   data = {}

   def __init(self):
      pass

   def set(self,key,value):
      self.data[key] = value

   def get(self):
      return self.data

   def has(self, name):
      return name in self.data

   def __len__(self):
      return self.data.__len__()

   def __getitem__(self,key):
      return self.data.__getitem__(key)

   def __call__(self, key, default_value=None):
       return self.data.setdefault(key,default_value)

   def __setitem__(self,key,value):
      return self.data.__setitem__(key,value)

   def __delitem__(self,key):
      return self.data.__delitem__(key)

   def __iter__(self):
      return self.data.__iter__()

   def __contains__(self,item):
      return self.data.__contains__(item)

def add_root_call(callee):
    """ add callee to be called from root recursion depth position of the
    message handling queue"""
    DfGlobal()["root.call"].append(callee)

def run_root_call():
    g = DfGlobal()
    if g["loop-depth"] <= 1:
        if g["root.call"]:
            fn = g["root.call"].pop(0)
            fn()
            return True
    return False

def add_timed_call(callee, waitfor, name=None):
    """ add callee to be called from the root recursion depth position in
    `waitfor` seconds from now, name is an identifier/additional data
    field"""
    g = DfGlobal()
    infopair = (g["@now"]+float(waitfor)*g["output_rate"], callee, name)
    timer_list = g["timer.calls"]
    insort(timer_list, infopair)

def remove_timed_calls_filtered_by_name(filterfn):
    """ removes timed calls based on the filterfn-evaluation on its name"""
    g = DfGlobal()
    g["timer.calls"] = filter(lambda x: not filterfn(x[2]),\
                              g["timer.calls"])
    
