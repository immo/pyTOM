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
import df.df_visual_concept_editor as vce


vce.initialize_char_setup()
vce.set_default_snippets()

class Workspace(object):
    thingtest = re.compile(r"[ \t]*<\?xml.*\?>.*<things/?>")
    grammartest = re.compile(r":.*\(.*\)")
    songtest = re.compile(".*:.*initial.*=.*")
    taxafinder = re.compile(r"[ \t]*taxa[ \t]*=[^\n]*")
    
    def __init__(self,path='./ext',parent_window=None):
        self.window = Toplevel(parent_window)
        self.window.grid_rowconfigure(0,weight=1)
        self.window.grid_columnconfigure(0,weight=1)
        self.window.title('Workspace'+' '+path)
        self.tcontainer = Frame(self.window)
        self.tcontainer.grid(sticky=N+S+E+W)
        self.tvariable = ArrayVar(self.window)
        for y,header in [(0,'Name'),(1,'Type'),\
                         (2,'Info')]:
            self.tvariable.set("-1,%i"%(y),header)
        self.table = Table(self.tcontainer, rows=1,\
                           cols=3,titlerows=1,titlecols=0,roworigin=-1,\
                           colorigin=0,selectmode='browse',\
                           rowstretch='none',colstretch='all',\
                           variable=self.tvariable,drawmode='slow',\
                           state='disabled',colwidth=20)
        self.table.pack(side=LEFT,expand=1,fill='both')
        def scroll_down(x=None,s=self):
            s.table.yview_scroll(1,"unit")
        def scroll_up(x=None,s=self):
            s.table.yview_scroll(-1,"unit")        
        self.window.bind("<Button-4>",scroll_up)
        self.window.bind("<Button-5>",scroll_down)                
        self.scrollbar = Scrollbar(self.tcontainer)
        self.scrollbar.pack(side=RIGHT,fill=Y)
        self.scroll_callback = ScrollDummy(self.table)
        self.scrollbar.config(command=self.scroll_callback.yview)
        self.table.config(yscrollcommand=self.scrollbar.set)
        self.filenbrs = []

        self.update_directory(path)
        
        self.table.focus_set()
        screencenter(self.window)
        

    def update_directory(self,new_path=None):
        if new_path:
            self.path = new_path
        self.filelist = {}
        self.fileinfo = {}
        new_files = [x for x in glob.glob( os.path.join(self.path,'*') )\
                     if not os.path.isdir(x)]
        new_files.sort()
        self.filenbrs = filter(lambda x: x in new_files,self.filenbrs) +\
                        filter(lambda x: not x in self.filenbrs,new_files)
        for x in self.filenbrs:
            ftype = 'unknown'
            with open(x) as f:
                data = f.read()
            if data:
                finfo = data.split('\n')[0]
            else:
                finfo = 'empty'
            if x.upper().endswith('.PY'):
                ftype = 'python'
            else:
                data_inline = data.replace('\n',' ')
                if self.thingtest.match(data_inline):
                    ftype = 'thing'
                    finfo = ""
                elif self.songtest.match(data_inline):
                    ftype = 'song'
                    taxamatch = self.taxafinder.search(data)
                    if taxamatch:
                        taxaline = data[taxamatch.start():taxamatch.end()]
                        rpart = taxaline.find('=')
                        try:
                            finfo = eval(taxaline[rpart+1:])
                            if type(finfo) == type(tuple()) or \
                               type(finfo) == type([]):
                                finfo = ", ".join([str(v) for v in finfo])
                            else:
                                finfo = str(finfo)
                        except:
                            finfo = taxaline[rpart+1:]
                    else:
                        finfo = ""
                elif self.grammartest.search(data):
                    ftype = 'grammar'
            self.filelist[x] = ftype
            self.fileinfo[x] = finfo
        self.table.config(rows=1+len(self.filenbrs))
        self.table.tag_delete("tag-unknown")
        self.table.tag_delete("tag-grammar")
        self.table.tag_delete("tag-song")
        self.table.tag_delete("tag-thing")
        self.table.tag_delete("tag-python")        
        self.table.tag_configure("tag-unknown",background="#880000",foreground="white")
        self.table.tag_configure("tag-python",background="green",foreground="black")  
        self.table.tag_configure("tag-grammar",background="#FF3300",\
                                 foreground="black")
        self.table.tag_configure("tag-thing",background="#00FF00",\
                                 foreground="black")
        self.table.tag_configure("tag-song",background="#00FFFF",foreground="black")
        for (x,i) in zip(self.filenbrs,range(len(self.filenbrs))):
            self.tvariable.set("%i,0"%i,os.path.basename(x))
            self.tvariable.set("%i,1"%i,self.filelist[x])
            self.tvariable.set("%i,2"%i,self.fileinfo[x])
            self.table.tag_cell("tag-"+self.filelist[x],"%i,0"%i,"%i,1"%i,"%i,2"%i)
