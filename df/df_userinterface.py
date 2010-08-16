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
#  Here, we use Tkinter and Pmw (Python Mega Widgets) 1.3,
#  and tkinter-tree (see Tree.py for license & copyright information)
#

from Tix import *
import tkFileDialog
import Pmw
import sys
import os
import errno
import subprocess
import select
import tkMessageBox
from pysqlite2 import dbapi2 as sqlite
from ScrollableMultiSelectTree import *
from df_ui_channels import *
from df_ui_control import *
from df_data_channels import *
from df_ui_new_technology import *
from df_ui_utils import *
from df_ui_database import *
from my_readline import *
from df_ui_ext import *
from df_limbs import *
from df_visual_concept_editor import *
from df_ui_waitwindow import *

i = sys.stdin
o = sys.stdout
timer_delay = 0.5
in_db_name = ""
out_db_name = ""
backend_path = ""
sampler_time = ""

def raise_cmd(name):
   """raise_cmd(name)   place cursor in the appropriate edit control when entering the tab name"""
   global coninput, frontinput, do_raise
   if (do_raise == 0):
      return
   if name == 'backend-console':
      coninput.focus_set()
   elif name == 'python-shell':
      frontinput.focus_set()
   elif name == 'view':
      DfGlobal()["canvas"].focus_set()

def add_samples2(files):
   """add_samples2(files)   files contains a list of sample file paths that are added to the input-configuration database of the backend"""
   in_db = sqlite.connect(in_db_name)
   cur = in_db.cursor()
   cur.execute("CREATE TABLE IF NOT EXISTS load_samples ( filename TEXT ) ")
   for name in files:
      cur.execute("INSERT OR REPLACE INTO load_samples VALUES ('"+name+"')")
   in_db.commit()
   tkMessageBox.showinfo(message="Added "+str(len(files))+" files to the input-configuration database." + \
                        "\nPlease restart the drums-frontend to have the changes take effect.")

def add_samples(one_per_line):
   """add_samples2(files)   files contains a path to a list of sample file paths, one at each line, that are added to the input-configuration database of the backend"""
   in_db = sqlite.connect(in_db_name)
   cur = in_db.cursor()
   files = one_per_line.readlines()
   cur.execute("CREATE TABLE IF NOT EXISTS load_samples ( filename TEXT ) ")
   for name in files:
      name = name[0:len(name)-1]
      cur.execute("INSERT OR REPLACE INTO load_samples VALUES ('"+name+"')")
   in_db.commit()
   tkMessageBox.showinfo(message="Added "+str(len(files))+" files to the input-configuration database." + \
                        "\nPlease restart the drums-frontend to have the changes take effect.")


def add_samples_dir():
   """add samples to the backend input configuration db by choosing all samples from a directory"""
   name = tkFileDialog.askdirectory()
   if (len(name)>0):
      proc = subprocess.Popen("find "+name+" -name \"*.ogg\"",\
                           shell=True,stdout=subprocess.PIPE)
      add_samples(proc.stdout)

def get_contents(node):
        """get_contents(node)    return the contents of a directory tree node"""
        path=os.path.join(*node.full_id())
        for filename in os.listdir(path):
            full=os.path.join(path, filename)
            name=filename
            if os.path.isdir(full):
               if not filename.startswith("."):
                  node.widget.add_node(name=name, id=filename, flag=1,full_parent_id=node.full_id(),expanded=True)

def get_tree_oggs(path):
   """get_tree_oggs(path)   return a list of all OGG files in the directory path"""
   files = []
   for filename in os.listdir(path):
      full=os.path.join(path, filename)
      if not os.path.isdir(full):
         if filename.upper().endswith(".OGG"):
            files = files + [full]
   return files


def traverse_tree(node, inherited):
   """traverse_tree(node, inherited)   traverse a tree node"""
   path=os.path.join(*node.full_id())
   if node.selected == None:
      files = get_tree_oggs(path)
      for child in node.children():
         files = files + traverse_tree(child,0)
   elif node.selected or inherited:
      files = get_tree_oggs(path)
      for child in node.children():
         files = files + traverse_tree(child,1)
   else:
      files = []
      for child in node.children():
         files = files + traverse_tree(child,0)
   return files



def add_samples_hierarchy():
   """add samples from a directory hierarchy by choosing from a directory tree"""
   global root
   name = tkFileDialog.askdirectory(mustexist=1)
   if (len(name)>0):
      dlg = Toplevel(root)
      dlg.title("Select directories to add samples...")
      dlg.geometry("1000x700")
      l = Label(dlg,text="Thick=recursive add, grey=break recursion/no files from subdirectories",justify=LEFT)
      l.grid(row=0, column=0)
      t=MultiSelectTree(master=dlg,
           root_id=name,
           root_label=name,
           get_contents_callback=get_contents,
           width=500)
      t.grid(row=1, column=0, sticky='nsew')
      dlg.grid_rowconfigure(1, weight=1)
      dlg.grid_columnconfigure(0, weight=1)
      sb=Scrollbar(dlg)
      sb.grid(row=1, column=1, sticky='ns')
      t.configure(yscrollcommand=sb.set)
      sb.configure(command=t.yview)
      sb=Scrollbar(dlg, orient=HORIZONTAL)
      sb.grid(row=2, column=0, sticky='ew')
      t.configure(xscrollcommand=sb.set)
      sb.configure(command=t.xview)
      t.focus_set()
      t.root.expand()
      wait_window(dlg)
      files = traverse_tree(t.root,0)
      add_samples2(files)


def del_samples():
   """delete selected samples from the input configuration database"""
   global samplelist
   in_db = sqlite.connect(in_db_name)
   cur = in_db.cursor()
   files = samplelist.selection_get().split("\n")
   for name in files:
      cur.execute("DELETE FROM load_samples WHERE filename='"+name+"'")
   in_db.commit()
   tkMessageBox.showinfo(message="Removed "+str(len(files))+" files from the input-configuration database." + \
                        "\nPlease restart the drums-frontend to have the changes take effect.")


def add_samples_file():
   """add a samples from a list file to the sample input database"""
   file = tkFileDialog.askopenfile()
   if file != None:
      add_samples(file)

def refresh_status():
   """update status line"""
   global sampler_time, status_widget, master_meter, master_gain
   statusline = "v=" + master_meter +" g=" + master_gain + " t=" + sampler_time
   status_widget.configure(text=statusline)

def measure_file(file):
   """measure_file(file)  call the backend to measure the file and then write the results in the input configuration database"""
   global backend_path
   proc = subprocess.Popen(backend_path + " --measure '"+file+"'",\
                           shell=True,stdout=subprocess.PIPE)
   (out,err) = proc.communicate()
   rate = 0
   frames = 0
   channels = 0
   peak = 0.0
   energy = 0.0
   for line in out.split("\n"):
      if line.startswith("rate "):
         rate = int(line[5:])
      elif line.startswith("frames "):
         frames = int(line[7:])
      elif line.startswith("channels "):
         channels = int(line[9:])
      elif line.startswith("peak "):
         peak = float(line[5:])
      elif line.startswith("energy "):
         energy = float(line[7:])
   return "INSERT OR REPLACE INTO sample_info VALUES ('"+file+"', "+str(rate)+", "+ str(frames)+", "\
          +str(channels)+", " + str(peak) +", "+str(energy)+")"


def measure_new2(in_db):
   """measure_new2(in_db)  measure all samples in the input-db-sample list, for which no metrics are available yet."""
   global o
   cur = in_db.cursor()
   cur.execute("CREATE TABLE IF NOT EXISTS sample_info ( filename TEXT, rate INTEGER, frames INTEGER, channels INTEGER, peak REAL, energy REAL ) ")
   cur.execute("SELECT DISTINCT filename FROM load_samples")
   filenames = [val[0] for val in cur]
   cur.execute("SELECT DISTINCT filename FROM sample_info")
   measured = [val[0] for val in cur]
   todo = [file for file in filenames if not (file in measured)]
   for file in todo:
      cur.execute(measure_file(file))
   in_db.commit()
   o.write("MEASURED!\n")
   o.flush()

def measure_new():
   """trigger the measurement of all new samples in the input db"""
   in_db = sqlite.connect(in_db_name)
   measure_new2(in_db)

def clear_instrument_list():
   """delete the instrument list table in the input db"""
   in_db = sqlite.connect(in_db_name)
   in_db.cursor().execute("DROP TABLE IF EXISTS instrument_names")
   in_db.commit()
   tkMessageBox.showinfo(message="Removed instrument generation cache." + \
                        "\nNext time instruments will be generated from scratch.")

def regen_instrument_list():
   """rebuild instrument data structures"""
   global o
   o.write("REGENERATE-INSTRUMENTS!\n")
   o.flush()



def measure_all():
   """re-measure all samples in the input-db"""
   in_db = sqlite.connect(in_db_name)
   cur = in_db.cursor()
   cur.execute("DROP TABLE IF EXISTS sample_info")
   measure_new2(in_db)
        

def input_timer():
   """callback for checking the input data stream"""
   global root, console, coninput, i, o, notebook, frontconsole,\
          frontinput, samplelist, in_db_name, out_db_name, info,\
          sampler_time, master_meter, master_gain, line_start
   line = ""
   while (1):
      try:
         #line = i.readline()
         line = my_readline(i)
         if (len(line)==0):
            root.quit()
            return
         line = line_start + line
         if line.endswith('\n'):
             line_start = ""
             #print "~~~~~ ", repr(line)
             line = line[0:len(line)-1]
             if line == "UI-FINISH!":
                root.quit()
                return
             if line.startswith("CONSOLE:"):
                console.config(state=NORMAL)
                console.insert(END, line[8:]+"\n")
                console.see(END)
                console.config(state=DISABLED)
                console.update()
             elif line.startswith("BOUNCE:"):
                 send_line("PYTHON","execfile('"+line[7:]+"')")
             elif line.startswith("PYTHON:"):
                frontconsole.config(state=NORMAL)
                frontconsole.insert(END, line[7:])
                frontconsole.see(END)
                frontconsole.config(state=DISABLED)
                frontconsole.update()
             elif line.startswith("PYTHON':"):
                frontconsole.config(state=NORMAL)
                frontconsole.insert(END, line[8:]+"\n")
                frontconsole.see(END)
                frontconsole.config(state=DISABLED)
                frontconsole.update()
             elif line == "FLUSHSMP!":
                samplelist.delete(0,END)
             elif line.startswith("SMP:"):
                samplelist.insert(END, line[4:])
             elif line.startswith("INDB:"):
                in_db_name = line[5:]
                frame = Frame(info)
                DfGlobal()["in_db_name"] = in_db_name
                Label(frame,text="Input database: "+in_db_name).pack(side=LEFT,fill=X,expand=0)
                cmd = "sqliteman "+in_db_name
                Button(frame,text=cmd, command=\
                       lambda: subprocess.Popen(cmd,\
                               shell=True)).pack(side=RIGHT,fill=X,expand=0)
                frame.pack(side=TOP,fill=X,expand=0)
                in_db = sqlite.connect(in_db_name)
                cur = in_db.cursor()
                cur.execute("CREATE TABLE IF NOT EXISTS frontend (name TEXT, value TEXT)")
                cur.execute("SELECT value FROM frontend WHERE name='autosave_path'")
                default_autosave = "./frontend_autosave"
                for x in cur:
                    default_autosave = x[0]
                frame = Frame(info)
                autosave_label = Label(frame,text="Current autosave file: " + default_autosave)
                autosave_label.pack(side=LEFT,fill=X,expand=0)

                in_db.commit()
                DfGlobal()["autosave_path"] = default_autosave
                send_line("PYTHON","DfGlobal()['autosave_path'] = " + repr(default_autosave))
                def chg_autosave_path(autosave_label=autosave_label):
                    path = tkFileDialog.asksaveasfilename(title="Autosave to file...")
                    DfGlobal()["autosave_path"] = path
                    db = sqlite.connect(in_db_name)
                    cr = db.cursor()
                    cr.execute("DELETE FROM frontend WHERE name='autosave_path'")
                    cr.execute("INSERT INTO frontend VALUES ('autosave_path', '"+path+"')")
                    db.commit()
                    autosave_label.configure(text="Current autosave file: " + path)
                    send_line("PYTHON","DfGlobal()['autosave_path'] = " + repr(path))


                Button(frame,text="Select...",command=chg_autosave_path).pack(side=RIGHT,fill=X,expand=0)
                Button(frame,text="Commit",command=lambda:send_line("PYTHON",\
                        "save_state(DfGlobal()['autosave_path'])")).pack(side=RIGHT,fill=X,expand=0)

                frame.pack(side=TOP,fill=X,expand=0)

                cur.execute("SELECT value FROM frontend WHERE name='setup_path'")
                default_setup = "./frontend_local_setup"
                for x in cur:
                    default_setup = x[0]
                frame = Frame(info)
                setup_label = Label(frame,text="Current setup file: " + default_setup)
                setup_label.pack(side=LEFT,fill=X,expand=0)
                in_db.commit()
                DfGlobal()["setup_path"] = default_setup
                send_line("PYTHON","DfGlobal()['setup_path'] = " + repr(default_setup))
                def chg_setup_path(autosave_label=setup_label):
                    path = tkFileDialog.askopenfilename(title="Setup script path...")
                    DfGlobal()["setup_path"] = path
                    db = sqlite.connect(in_db_name)
                    cr = db.cursor()
                    cr.execute("DELETE FROM frontend WHERE name='setup_path'")
                    cr.execute("INSERT INTO frontend VALUES ('setup_path', '"+path+"')")
                    db.commit()
                    autosave_label.configure(text="Current setup file: " + path)
                    send_line("PYTHON","DfGlobal()['setup_path'] = " + repr(path))

                Button(frame,text="Select...",command=chg_setup_path).pack(side=RIGHT,fill=X,expand=0)
                Button(frame,text="Run again",command=lambda:send_line("PYTHON",\
                        "execfile(DfGlobal()['setup_path'])")).pack(side=RIGHT,fill=X,expand=0)

                frame.pack(side=TOP,fill=X,expand=0)

             elif line.startswith("CHANNUM:"):
                nbr = int(line[8:])
                for n in range(nbr):
                   create_channel_panel(n,notebook,root)
             elif line.startswith("OUTDB:"):
                out_db_name = line[6:]
                frame = Frame(info)
                Label(frame,text="Output database: "+out_db_name).pack(side=LEFT,fill=X,expand=0)
                cmd = "sqliteman "+out_db_name
                Button(frame,text=cmd, command=\
                       lambda: subprocess.Popen(cmd,\
                               shell=True)).pack(side=RIGHT,fill=X,expand=0)
                frame.pack(side=TOP,fill=X,expand=0)
             elif line.startswith("SAMPLER-TIME:"):
                sampler_time = line[13:]
                refresh_status()
             elif line.startswith("MASTER-METER:"):
                master_meter = line[13:]
                refresh_status()
             elif line.startswith("MASTER-GAIN:"):
                master_gain = line[12:]
                refresh_status()
             elif line.startswith("SAMPLE-RATE:"):
                DfGlobal()["sample-rate"] = float(line[12:])
             else:
                handle_read_line(line)
         else:
             print " ___ caught over-long line from i"
             line_start = line

      except IOError, err:
         if (err.errno != errno.EWOULDBLOCK):
            root.quit()
            return
         else:
            break
   #root.after(timer_delay, input_timer)
   

def console_cmd(event):
   """console_cmd(event)   handle command entered by user towards the backend"""
   global root, console, coninput, i, o, notebook
   cmd = coninput.get()
   coninput.delete(0,END)
   coninput.update()
   console.config(state=NORMAL)
   console.insert(END, "> "+cmd+"\n")
   console.see(END)
   console.config(state=DISABLED)
   console.update()
   o.write("CONSOLE:"+cmd+"\n")
   o.flush()

def python_cmd(event):
   """console_cmd(event)   handle command entered by user towards the frontend"""
   global i,o, frontconsole, frontinput
   cmd = frontinput.get()
   frontinput.delete(0,END)
   frontinput.update()
   frontconsole.config(state=NORMAL)
   frontconsole.insert(END, "> "+cmd+"\n")
   frontconsole.see(END)
   frontconsole.config(state=DISABLED)
   frontconsole.update()
   send_line("PYTHON", cmd)
   

def raise_console(event):
   global notebook
   notebook.selectpage('backend-console')

def raise_frontconsole(event):
   global notebook
   notebook.selectpage('python-shell')

def raise_samples(event):
   global notebook
   notebook.selectpage('samples')

def raise_info(event):
   global notebook
   notebook.selectpage('info')

def raise_control(event):
   global notebook
   notebook.selectpage('control')
   
def raise_view(event):
   global notebook
   notebook.selectpage('view')
   DfGlobal()["canvas"].focus_set()

   
def raise_legacy(event):
   global notebook
   notebook.selectpage('legacy')

def raise_utils(event):
   global notebook
   notebook.selectpage('utils')

def raise_database(event):
   global notebook
   notebook.selectpage('database')

def raise_ext(event):
   global notebook
   notebook.selectpage('ext')


def autosave_callback():
    g = DfGlobal()
    frontend_command("do_autosave()")
    if g["autosave_intervall"]:
        g["root.window"].after(g["autosave_intervall"], autosave_callback)

def set_autosave_intervall(s):
    g = DfGlobal()
    g["autosave_intervall"] = int(float(s)*60000.0) #min->msec
    if g["autosave_intervall"]:
        g["root.window"].after(g["autosave_intervall"], autosave_callback)

def do_ext_bounce(r):
    send_line("PYTHONBOUNCE",r)

def user_interface(i1, o1, path):
   """run the user interface fork()-branch of the frontend"""
   global root, console, coninput, i, o, notebook, frontconsole, \
          frontinput, do_raise, samplelist, info, backend_path,\
          status_widget, master_meter,  master_gain, line_start

   initialize_char_setup() # get instrument names
   set_default_snippets() # for snippet editor...
   print "UI: 0"
   backend_path = path
   i = i1
   o = o1
   do_raise = 0
   line_start = ""
   master_meter = ""
   master_gain = ""
   root = Tk()
   DfGlobal()["root.window"] = root
   # not sure whether we should call idletasks or not...
   #DfGlobal()["Tk.root.update_idletasks"] = root.update_idletasks
   def no_update():
       pass
   DfGlobal()["Tk.root.update_idletasks"] = no_update
   root.title("drums-frontend v0.1")
   root.geometry("1000x700")
   print "UI: 1"
   DfGlobal()["UI_O"] = o
   DfGlobal()["data_send_channel"] = o

   Pmw.initialise(root)

#   status_widget = Pmw.MessageBar(root, entry_relief='groove')
#   status_widget.message('state','(waiting for status information)')
#   status_widget._messageBarEntry.config(justify=RIGHT,\
#                                         font='Courier 10 bold',\
#                                         foreground='white',\
#                                         background='black')

#   status_widget.pack(side='bottom', fill='x', expand=0, padx=10, pady=10)
   status_widget = Label(root,justify=RIGHT,text="(waiting for status)",\
                         anchor=E)
   status_widget.pack(side=BOTTOM,fill=X,expand=0)

   notebook = Pmw.NoteBook(root,raisecommand=raise_cmd)
   print "UI: 2"   
   c_page = notebook.add('backend-console')
   notebook.tab('backend-console').focus_set()
   notebook.pack(fill = 'both', expand = 1, padx = 0, pady = 0)
   helper = Frame(c_page)

   coninput = Entry(c_page)
   coninput.config(bg="black",foreground="red",font="Courier 12",\
                   insertbackground='white')
   coninput.pack(side=BOTTOM,fill=X, expand=1, padx=10, pady=10)
   coninput.bind("<Return>",console_cmd)
   coninput.focus_set()
   print "UI: 3"   

   helper.pack(side=TOP,fill='both',expand=1)
   console = Text(helper, width=80, height= 65)
   console.config(bg="black",foreground='red',font='Courier 12')
   console.config(state=DISABLED)
   scrollcon = Scrollbar(helper,command=console.yview)
   console.config(yscrollcommand=scrollcon.set)
   scrollcon.pack(side=RIGHT, fill=Y)
   console.pack(side=RIGHT,fill='both', expand = 1, padx = 5, pady = 5)
   c_page = notebook.add('python-shell')
   helper = Frame(c_page)

   print "UI: 4"
   frontinput = Entry(c_page)
   frontinput.pack(side=BOTTOM,fill=X, expand=1, padx=10,pady=10)
   frontinput.config(bg="black",foreground="green",font="Courier 12",\
                   insertbackground='white')
   frontinput.bind("<Return>",python_cmd)

   helper.pack(side=TOP,fill='both',expand=1)

   frontconsole = Text(helper, width=80, height= 65)
   frontconsole.config(bg="black",foreground='green',font='Courier 12')
   frontconsole.config(state=DISABLED)
   scrollcon = Scrollbar(helper,command=frontconsole.yview)
   frontconsole.config(yscrollcommand=scrollcon.set)
   scrollcon.pack(side=RIGHT, fill=Y)
   frontconsole.pack(side=RIGHT,fill='both', expand = 1, padx = 5, pady = 5)

   print "UI: 5"
   c_page = notebook.add('samples')
   c_left = Frame(c_page)
   Label(c_left,text="Currently cached samples:").pack(side=TOP)
   samplelist2 = Pmw.ScrolledListBox(c_left)
   samplelist = samplelist2._listbox
   samplelist.config(selectmode=EXTENDED)
   samplelist2.pack(side=TOP,fill='both',expand=1,padx=5,pady=5)
   c_right = Frame(c_page, width="100")
   Label(c_right,text="Configuration tool box:").pack(side=TOP)

   Button(c_right,text="Add samples from directory", command=add_samples_dir).pack(side=TOP,pady=5,fill=X)
   Button(c_right,text="Add samples from directory hierarchy", command=add_samples_hierarchy).pack(side=TOP,pady=5,fill=X)
   Button(c_right,text="Add samples from file", command=add_samples_file).pack(side=TOP,pady=5,fill=X)
   Button(c_right,text="Remove selected samples", command=del_samples).pack(side=TOP,pady=5,fill=X)
   Button(c_right,text="Measure new samples in list", command=measure_new).pack(side=TOP,pady=10,fill=X)
   Button(c_right,text="Re-Measure samples in list", command=measure_all).pack(side=TOP,pady=5,fill=X)
   Button(c_right,text="Clear instrument list", command=clear_instrument_list).pack(side=TOP,pady=10,fill=X)
   Button(c_right,text="Re-Generate instrument list", command=regen_instrument_list).pack(side=TOP,pady=5,fill=X)

   c_right.pack(side=RIGHT,fill=Y,expand=0)
   c_left.pack(side=LEFT,fill='both',expand=1,padx=0,pady=0)
   print "UI: 6"

   c_page = notebook.add('info')
   info = Frame(c_page)

   info.pack(side=TOP,fill='both',expand=1)

   c_page = notebook.add('legacy')
   initialize_ui_legacy_control(c_page)
   
   c_page = notebook.add('utils')
   initialize_ui_utils(c_page)

   c_page = notebook.add('database')
   initialize_ui_database(c_page)

   c_page = notebook.add('ext')
   initialize_ext_control(c_page)

   c_page = notebook.add('control')
   initialize_ui_control(c_page)
   
   c_page = notebook.add('view')
   initialize_ui_view(c_page)
   print "UI: 7"
   do_raise = 1

   #root.after(timer_delay, input_timer)
   root.bind("<F1>",raise_console)
   root.bind("<F2>",raise_frontconsole)
   root.bind("<F3>",raise_samples)
   root.bind("<F4>",raise_info)
   root.bind("<F11>",raise_control)
   root.bind("<F12>",raise_view)
   root.bind("<F5>",raise_legacy)
   root.bind("<F6>",raise_utils)
   root.bind("<F7>",raise_database)
   root.bind("<F8>",raise_ext)   
   
   DfGlobal()["autosave_intervall"] = 0
   add_data_channel_handler("autosave.intervall",set_autosave_intervall)
   add_data_channel_handler("ext-bounce",do_ext_bounce)
   
   #main loop

   def wait_for_input_timer():
       waitfor = [i]
       select.select(waitfor,[],waitfor,timer_delay)
       try:
           input_timer()
       except Exception, err:
           print "input_timer gives: ", err

   
   g = DfGlobal()

   g["wait.for.input"] = wait_for_input_timer
   
   while 1:
       try:
           root.update()
       except TclError, err:
           print "root.update() gives ", err
           break
       except Exception, err:
           print "root.update() gives ", err
           
       g["wait.for.input"]()
   
   try:
      o.write("UI-FINISHED\n")
      o.flush()
   except IOError:
      pass
