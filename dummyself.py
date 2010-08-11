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

class dummySelf(object):
    def __init__(self,dict=None):
        if dict:
            self.__dict__ = dict.copy()
    def __repr__(self):
        if self.__dict__:
            keys = self.__dict__.keys()
            keys.sort()
            reps = [repr(k) for k in keys]
            maxlen = max([min(len(r),20) for r in reps])
            contents = []
            for k,r in zip(keys,reps):
                if len(r) < maxlen:
                    pad = " "*(maxlen-len(r))
                else:
                    pad = ""
                contents.append(r+": "+pad+repr(self.__dict__[k]))
            return "dummySelf({" + (",\\\n"+" "*19).join(contents)+"})"
        else:
            return "dummySelf()"
