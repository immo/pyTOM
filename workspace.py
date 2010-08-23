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
import sys,re,os,glob,subprocess
from Tix import *
from tktable import *
from scrolldummy import *
from messagebox import *
import df.df_visual_concept_editor as vce
import df.df_xml_thing as xt
import quicktix
import rhythm_editor
import song_editor

def call_editor(path):
    try:
        p = subprocess.Popen(['gnuclient','-batch','-eval','t'],\
                             stdout=subprocess.PIPE)
        out,error = p.communicate()
        if out.strip() == 't':
            subprocess.Popen(['gnuclient','-q',path])
        else:
            raise Exception('emacs not running')
    except:
        subprocess.Popen(['emacs',path])

vce.initialize_char_setup()
vce.set_default_snippets()

class SnippetEditor(object):
    def __init__(self,path,parent_window=None):
        self.path = path
        with open(path,'r') as f:
            self.data = f.read()
        self.things = xt.xml_to_things(self.data)
        self.name = "Snippet "+os.path.basename(path)
        self.dic = vce.create_visual_editor(parent_window,name=self.name,\
                                            things=self.things)
        self.window = self.dic['window']
        def close_handler(x=None,s=self):
            if xt.things_to_xml(s.things) != s.data:
                if yesnobox(self.name,"The snippet has been changed.",\
                            "","Do you want to save it now?"):
                    s.save_to()
            s.window.destroy()
        def save_handler(x=None,s=self):
            s.save_to()
        self.window.bind("<Control-s>",save_handler)
        self.window.protocol("WM_DELETE_WINDOW",close_handler)
        screencenter(self.window)

    def save_to(self):
        i = inputbox(self.name,"Path =$"+self.path+"$")
        if i:
            self.save(i[0])

    def save(self,new_path=None):
        if new_path:
            self.path = new_path
        self.data = xt.things_to_xml(self.things)
        with open(self.path,'w') as f:
            f.write(self.data)
        

class Workspace(object):
    snippettest = re.compile(r"[ \t]*<\?xml.*\?>.*<things/?>")
    grammartest = re.compile(r":.*\(.*\)")
    songtest = re.compile(".*:.*initial.*=.*")
    taxafinder = re.compile(r"[ \t]*taxa[ \t]*=[^\n]*")
    
    def __init__(self,path='./ext',parent_window=None):
        self.window = Toplevel(parent_window)
        self.window.grid_rowconfigure(0,weight=1)
        self.window.grid_columnconfigure(0,weight=1)
        self.name = 'Workspace'+' '+path
        self.path = path
        self.window.title(self.name)        
        self.balloon = Balloon(self.window)
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
        self.selected_file = -1

        self.update_directory(path)
        
        def open_in_editor(event,s=self):
            row = int(s.table.index("@%i,%i"%(event.x,event.y)).split(",")[0])
            if 0 <= row < len(s.filenbrs):
                call_editor(s.filenbrs[row])

        def edit_file(event,s=self):
            row = int(s.table.index("@%i,%i"%(event.x,event.y)).split(",")[0])
            if 0 <= row < len(s.filenbrs):
                s.edit_file(s.filenbrs[row])

        def select_file(event,s=self):
            row = int(s.table.index("@%i,%i"%(event.x,event.y)).split(",")[0])
            if 0 <= row < len(s.filenbrs):
                s.selected_file = row
                s.update_directory()
            
        self.table.bind("<Control-Double-Button-1>",open_in_editor)
        self.table.bind("<Double-Button-1>",edit_file)        
        self.table.bind("<Button-3>",select_file)

        def sort_by_name(x=None,s=self):
            s.update_directory()            
            s.filenbrs.sort()
            s.update_directory()

        def sort_by_type(x=None,s=self):
            s.update_directory()            
            sortlist = [(s.filelist[x],x) for x in s.filenbrs]
            sortlist.sort()
            s.filenbrs = map(lambda x:x[1], sortlist)
            s.update_directory()

        def just_update(x=None,s=self):
            s.update_directory()

        def copy_sel(x=None,s=self):
            row = int(s.table.index("active").split(",")[0])
            if 0 <= row < len(s.filenbrs):
                s.copy_file(s.filenbrs[row])

        self.r_buttons = Frame(self.window)
        self.r_buttons.grid(row=1,column=0,sticky=E+W)

        quicktix.add_balloon_button(self.__dict__,'by_name','r_buttons','By Name',\
                                    sort_by_name,'Sort all files by their name')
        quicktix.add_balloon_button(self.__dict__,'by_type','r_buttons','By Type',\
                                    sort_by_type,\
                                    'Sort all files by their type and then by their name')
        quicktix.add_balloon_button(self.__dict__,'j_upd','r_buttons','Update',\
                                    just_update,\
                                    'Update directory contents only. (New files will go last)')
        quicktix.add_balloon_button(self.__dict__,'t_cpy','r_buttons','Copy',\
                                    copy_sel,\
                                    'Creates a copy of the currently grey-selected file.')

        def add_song(x=None,s=self):
            s.choose_new_filename_and_copy_and_edit(os.path.join(s.path,'00_new-song'))            


        def add_snippet(x=None,s=self):
            s.choose_new_filename_and_copy_and_edit(os.path.join(s.path,'00_new-thing'))            

        def add_rhythms(x=None,s=self):
            s.choose_new_filename_and_copy_and_edit(os.path.join(s.path,'00_new-rhythms'))  

        def add_grammar(x=None,s=self):
            s.choose_new_filename_and_copy_and_edit(os.path.join(s.path,'00_new-song'))          

        def add_script(x=None,s=self):
            s.choose_new_filename_and_copy_and_edit(os.path.join(s.path,'00_new-script.py'))

        quicktix.add_balloon_button(self.__dict__,'add_song','r_buttons','+song',\
                                    add_song,\
                                    'Adds a new song from template.')
        quicktix.add_balloon_button(self.__dict__,'add_snpt','r_buttons','+snippet',\
                                    add_snippet,\
                                    'Adds a new snippet from template.')
        quicktix.add_balloon_button(self.__dict__,'add_rhthms','r_buttons','+rhythms',\
                                    add_rhythms,\
                                    'Adds a new rhythm desk from template.')
        quicktix.add_balloon_button(self.__dict__,'add_scr','r_buttons','+python',\
                                    add_script,\
                                    'Adds a new script from template.')
        quicktix.add_balloon_button(self.__dict__,'add_grm','r_buttons','+grammar',\
                                    add_grammar,\
                                    'Adds a new grammar from template.')
    
        
        self.table.focus_set()
        screencenter(self.window)

    def edit_file(self,path):
        if path in self.filelist:
            editor = self.filelist[path]
        else:
            editor = "unknown"
        if editor == 'snippet':
            SnippetEditor(path,self.window)
        elif editor == 'rhythms':
            ed = rhythm_editor.RhythmEditor(self.window,path)
            with open(path,'r') as f:
                ed.from_string(f.read())
        elif editor == "song":
            ed = song_editor.SongEditor(self.window,path)
            with open(path,'r') as f:
                ed.from_string(f.read())
        else:
            call_editor(path)

    def copy_file(self,path):
        i = inputbox(self.name,"Copy file "+path,"","Dest = $"+path+"-$")
        if i:
            dest = i[0]
            if os.path.exists(dest):
                if not yesnobox(self.name,"The file "+dest+" already exists.","",\
                                "Do you want to replace it with "+path+"?"):
                    return
            with open(path,'r') as fi:
                with open(dest,'w') as fo:
                    fo.write(fi.read())
            self.update_directory()

    def choose_new_filename_and_copy_and_edit(self,path):
        i = inputbox(self.name,"Path = $"+self.path+"$","Name =$")
        if i:
            dest = os.path.join(i[0],i[1])
            if not os.path.exists(dest):
                with open(path,'r') as fi:
                    with open(dest,'w') as fo:
                        fo.write(fi.read())
            self.update_directory()
            self.edit_file(dest)                
            

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
                if data.startswith('Rhythm Desk'):
                    ftype = "rhythms"
                    finfo = ""
                elif self.snippettest.match(data_inline):
                    ftype = 'snippet'
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
        self.table.tag_delete("tag-snippet")
        self.table.tag_delete("tag-python")
        self.table.tag_delete("tag-rhythms")        
        self.table.tag_delete("hilit")
        self.table.tag_configure('hilit',background="yellow")
        self.table.tag_configure("tag-unknown",background="#880000",foreground="white")
        self.table.tag_configure("tag-python",background="#008800",foreground="black")
        self.table.tag_configure("tag-rhythms",background="#008888",foreground="black")          
        self.table.tag_configure("tag-grammar",background="#FF3300",\
                                 foreground="black")
        self.table.tag_configure("tag-snippet",background="#00FF00",\
                                 foreground="black")
        self.table.tag_configure("tag-song",background="#00FFFF",foreground="black")
        for (x,i) in zip(self.filenbrs,range(len(self.filenbrs))):
            self.tvariable.set("%i,0"%i,os.path.basename(x))
            self.tvariable.set("%i,1"%i,self.filelist[x])
            self.tvariable.set("%i,2"%i,self.fileinfo[x])
            self.table.tag_cell("tag-"+self.filelist[x],"%i,0"%i,"%i,1"%i,"%i,2"%i)
        self.table.tag_cell("hilit","%i,0"%self.selected_file,"%i,1"%self.selected_file,\
                            "%i,2"%self.selected_file)
