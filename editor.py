#!/usr/bin/env python
# coding: utf-8
#
#   Copyright (C) 2010   C.D. Immanuel Albrecht
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

from __future__ import print_function
from sandbox import *
from lattices import *
from references import *
from Tix import *



class RhythmletEditor(object):
    def __init__(self, reference, pwindow=None):
        """ Create an RhythmletEditor associated with the reference object """
        self.reference = reference
        reference.____watch(self)
        self.window = Toplevel(pwindow)
        self.window.title('Rhythmlet Editor')
        self.window.bind('WM_DELETE_WINDOW', lambda : self.destroy())
        print("OK")

    def update(self,key,value):
        print("Update",key,"<-",value)

    def destroy(self):
        self.reference.____unwatch(self)
        self.__delattr__('reference')

if __name__ == "__main__":
    print("*let Editor")
    root = SandboxInteraction()
    root.mainloop()
