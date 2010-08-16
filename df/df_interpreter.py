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

import code
import string
from df_global import *

class DfInterpreter(code.InteractiveInterpreter):
   """class that will act as input-stream for python code sent by the user interface"""
   vars = DfGlobal()
   cached = ""

   def __init__(self,globalvars,locals=None):
      vars = globalvars
      code.InteractiveInterpreter.__init__(self, locals)
      self.tracebacked = False
      self.oldshowtraceback = self.showtraceback
      def new_traceback(*args):
          self.tracebacked = True
          return self.oldshowtraceback(*args)
      self.showtraceback = new_traceback

   def write(self,data):
      send = "PYTHON:" + data.replace("\n","\nPYTHON':")+"\n"
      self.vars["ui_out"].write(send)
      self.vars["ui_out"].flush()

   def hasTracebacked(self):
       if self.tracebacked:
           self.tracebacked = False
           return True
       else:
           return False

