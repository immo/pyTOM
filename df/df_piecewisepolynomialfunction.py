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

from df_polynom import *
from df_piecewise import *
import re

def string2polynom(s):
    """convert a string like '23(x-2)(x+3) + 12x**2 + 3*4' to a Polynom object"""
    if s == '':
        return Polynom()
    replace = {r'\)\(':')*(',r'\)x':')*x',r'x\(':'x*(', '1x':'1*x','2x':'2*x','3x':'3*x','4x':'4*x','5x':'5*x',\
                     '6x':'6*x','7x':'7*x','8x':'8*x','9x':'9*x','0x':'0*x','1\\(':'1*(','2\\(':'2*(','3\\(':'3*(',\
                     '4\\(':'4*(','5\\(':'5*(','6\\(':'6*(','7\\(':'7*(','8\\(':'8*(','9\\(':'9*(','0\\(':'0*(',\
                     r'\^':'**','xx':'x*x'}
    for k in replace:
        regex = re.compile(k)  #make up the string to be evaluated later....
        sneu = s
        s = ''
        while sneu != s:
            s = sneu
            sneu = regex.sub(replace[k],s)
            
    x = Polynom({1.0:1.0})
    return Polynom(eval(s))

def string2piecewisepolynom(s):
    """convert a string like "bound, P('2*x+3'), bound, P(...),..." to a piecewise polynomial function. Each polynomial has to be written as P(p) and p will be passed to string2polynom. "P(" will be replaced by "string2polynom(" and then the string is evaluated as parameters to PiecewiseFun"""
    regex = re.compile(r'P\(')
    return eval("PiecewiseFun("+regex.sub("string2polynom(",s)+")")
