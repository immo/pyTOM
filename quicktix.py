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

from Tix import *
from tktable import *

def add_balloon_button(dic, name, parent, text, command, balloonmsg,side=LEFT):
    dic[name] = Button(dic[parent],command=command,text=text)
    dic[name].pack(side=LEFT)    
    dic['balloon'].bind_widget(dic[name],balloonmsg=balloonmsg)

def min_win_size(window,width,height):
    window.update()
    w = max([width,window.winfo_width()])
    h = max([height,window.winfo_height()])
    window.wm_geometry("%ix%i"%(w,h))

def screencenter(window):
    window.update()
    x = window.winfo_screenwidth()/2 - window.winfo_width()/2
    y = window.winfo_screenheight()/2 - window.winfo_height()/2
    window.wm_geometry("+%i+%i"%(x,y))

def modalwait(window,parent=None):
    window.update()
    window.tkraise()
    window.grab_set()
    if parent:
        parent.wait_window(window)
    else:
        window.wait_window(window)
    window.grab_release()
