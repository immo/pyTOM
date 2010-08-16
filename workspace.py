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
import sys,re,os,glob
from Tix import *
from tktable import *
from scrolldummy import *
from messagebox import *


class Workspace(object):
    thingtest = re.compile(r"[ \t]*<\?xml.*\?>.*<things/?>")
    grammartest = re.compile(r":.*\(.*\)")
    songtest = re.compile(".*:.*initial.*=.*")    
    
    def __init__(self,path='./ext',parent_window=None):
        self.window = Toplevel(parent_window)
        self.window.grid_rowconfigure(0,weight=1)
        self.window.grid_columnconfigure(0,weight=1)
        self.window.title('Workspace')
        self.tcontainer = Frame(self.window)
        self.tcontainer.grid(sticky=N+S+E+W)
        self.tvariable = ArrayVar(self.window)
        for y,header in [(0,'Name'),(1,'Type'),\
                         (2,'Path')]:
            self.tvariable.set("-1,%i"%(y),header)
        self.table = Table(self.tcontainer, rows=1,\
                           cols=3,titlerows=1,titlecols=0,roworigin=-1,\
                           colorigin=0,selectmode='browse',\
                           rowstretch='none',colstretch='all',\
                           variable=self.tvariable,drawmode='slow',\
                           state='disabled',colwidth=20)
        self.table.pack(side=LEFT,expand=1,fill='both')
        self.scrollbar = Scrollbar(self.tcontainer)
        self.scrollbar.pack(side=RIGHT,fill=Y)
        self.scroll_callback = ScrollDummy(self.table)
        self.scrollbar.config(command=self.scroll_callback.yview)
        self.table.config(yscrollcommand=self.scrollbar.set)

        self.update_directory(path)
        
        self.table.focus_set()
        screencenter(self.window)
        

    def update_directory(self,new_path=None):
        if new_path:
            self.path = new_path
        self.filelist = {}
        self.filenbrs = [x for x in glob.glob( os.path.join(self.path,'*') )\
                         if not os.path.isdir(x)]

        for x in self.filenbrs:
            ftype = 'unkown'
            if x.upper().endswith('.PY'):
                ftype = 'python'
            else:
                with open(x) as f:
                    data = f.read()
                data_inline = data.replace('\n',' ')
                if self.thingtest.match(data_inline):
                    ftype = 'thing'
                elif self.songtest.match(data_inline):
                    ftype = 'song'
                elif self.grammartest.search(data):
                    ftype = 'grammar'
            self.filelist[x] = ftype
        for (x,i) in zip(self.filenbrs,range(len(self.filenbrs))):
            self.tvariable.set("%i,2"%i,x)
        self.table.config(rows=1+len(self.filenbrs))
        
