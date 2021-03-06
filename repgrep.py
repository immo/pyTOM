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
import re

def grep(regexp,*arrays):
    exp = re.compile(regexp)
    for array in arrays:
        for k in array:
            x = str(k)
            if exp.search(x):
                print(x)

def grepi(regexp,*arrays):
    exp = re.compile(regexp.upper())
    for array in arrays:
        for k in array:
            x = str(k)
            if exp.search(x.upper()):
                print(x)
