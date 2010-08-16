#!/usr/bin/python
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

import sys
import subprocess
import time
import getopt
import os
import fcntl
import select
import errno
import code
import string
import __main__
import datetime
from pysqlite2 import dbapi2 as sqlite
from df_global import *
from df_data_channels import *
from df_codimugraph import *
from df_guitar_graph import *
from df_database import *
import time
from my_readline import *
import df_snippets

DfGlobal()["data_channels"] = {}
DfGlobal()["data_channels_buffer"] = []
DfGlobal()["autosave_path"] = ""
DfGlobal()["setup_path"] = ""
DfGlobal()["viz_level"] = 100
DfGlobal()["volume.presets"] = {}
DfGlobal()["concept_decorator"] = lambda x:0.0
DfGlobal()["things"] = {}
DfGlobal()["no.calculate_preview"] = False
DfGlobal()["preset-functions"] = {'default':{}}
DfGlobal()["copied-snippet"] = None

DfGlobal()["PotentialGraph"] = PotentialGraph()
DfGlobal()["PotentialGraph"].representation = 'DfGlobal()["PotentialGraph"]'
DfGlobal()["StrengthGraph"] = StrengthGraph()
DfGlobal()["StrengthGraph"].representation = 'DfGlobal()["StrengthGraph"]'
DfGlobal()["ChangesGraph"] = ChangesGraph()
DfGlobal()["ChangesGraph"].representation = 'DfGlobal()["ChangesGraph"]'
DfGlobal()["GuitarGraph"] = GuitarGraph()
DfGlobal()["GuitarGraph"].representation = 'DfGlobal()["GuitarGraph"]'


def usage():
   print "usage: drums-frontend [{-b|--backend} PATH_TO_BACKEND]"
   print "       start drums-frontend using PATH_TO_BACKEND as command that"
   print "       starts the drums-backend"
   print "       drums-frontend [{-v|--viz-level} LEVEL]"
   print "       sets the visualization level to LEVEL (default:100)"

def count_ws(s):
   count = 0
   while ((len(s)>count)&(s[count] == ' ')):
      count = count + 1
   return count


print "drums-frontend, v0.1 (c) 2009, Immanuel Albrecht, GPLv3"


try:
    opts, args = getopt.getopt(sys.argv[1:], "hb:v:up:", ["help", "backend=", \
                                                "viz-level=", "user-interface","profile="])
except getopt.GetoptError, err:
   print err
   usage()
   sys.exit(2)

check_backend_path = ["./drums-backend", "./bin/drums-backend", \
                      "../bin/drums-backend", "./bin/Release/drums-backend",\
                      "../bin/Release/drums-backend", "./bin/Release.Quine/drums-backend",\
                      "../bin/Release.Quine/drums-backend","./drums-backend.exe",\
                      "./bin/drums-backend.exe", "../bin/drums-backend.exe",\
                      "./bin/Release.Win32/drums-backend.exe","../bin/Release.Win32/drums-backend.exe",\
                      "/usr/bin/drums-backend", "drums-backend", "drums-backend.exe"]

backend_path = ""

checked = [os.path.exists(path) for path in check_backend_path]

if 1 in checked:
   backend_path = check_backend_path[checked.index(1)]

do_profile = 0

for o,a in opts:
   if (o == "-b") | (o == "--backend"):
      backend_path = a
   elif (o == "-h") | (o == "--help"):
      usage()
      sys.exit(0)
   elif (o == "-u") | (o == "--user-interface"):
      user_interface(sys.stdin, sys.stdout)
      sys.exit(0)
   elif (o == "-v") | (o == "--viz-level"):
       DfGlobal()["viz_level"] = eval(a)
   elif (o == "-p") | (o == "--profile"):
       do_profile = 1
       profile_file = a
       print "Profiling to: ",profile_file

print "\nUsing backend command: ", backend_path, "\n"

readchild, writechild = os.pipe()
readparent, writeparent = os.pipe()

pid = os.fork()
if pid: #parent
   os.close(writechild)
   os.close(readparent)
   readchild = os.fdopen(readchild)
   fcntl.fcntl(readchild,fcntl.F_SETFL, os.O_NONBLOCK)
   writeparent = os.fdopen(writeparent, 'w')
else:
   from df_userinterface import user_interface
   init_data_channels('userinterface')
   os.close(writeparent)
   os.close(readchild)
   os.nice(3)
   writechild = os.fdopen(writechild, 'w')
   readparent = os.fdopen(readparent)
   fcntl.fcntl(readparent,fcntl.F_SETFL, os.O_NONBLOCK)
   if do_profile:
    def ui_call():
        user_interface(readparent, writechild, backend_path)
    import cProfile, pstats
    prof = cProfile.Profile()
    prof.runctx("ui_call()",globals(),locals())
    sys.stdout = open(a+"_userprof.log","w")
    stats = pstats.Stats(prof)
    stats.strip_dirs()
    stats.sort_stats("time")
    stats.print_stats(20)
    stats.print_callees(20)
    stats.print_callers(20)
   else:
    user_interface(readparent, writechild, backend_path)
   writechild.close()
   sys.exit(0)

from df_backend import *
from df_interpreter import *
from df_ontology import *
from df_model import *
from df_live import *
from math import *
from df_reinitialize_generators import *
from df_legacy import *
from df_data_channels import *
from df_mind import *
from df_limbs import *
from df_volume_control import *
from df_concept import *
from df_new_technology import *
from df_savestate import *
from df_gens import *
from df_keyboard import *
from df_hud_interaction import *
from df_scripting import *
from df_visual_concept_editor import *

def other_end():    
    db_install_callbacks()

    init_data_channels('frontend')
    
    ui_in = readchild
    ui_out = writeparent

    backend = subprocess.Popen(backend_path,\
               shell=True, stdin=subprocess.PIPE,\
                stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    backend_in = backend.stdout
    backend_out = backend.stdin
    backend_info = backend.stderr

    fcntl.fcntl(backend_in,fcntl.F_SETFL,os.O_NONBLOCK)
    fcntl.fcntl(backend_info,fcntl.F_SETFL,os.O_NONBLOCK)

    global_vars = DfGlobal()

    set_default_snippets()

    console = DfInterpreter(global_vars,__main__.__dict__)

    global_vars["asynchroneous_parameters"] = {}
    global_vars["asynchroneous_parameters_id"] = 1
    global_vars["reinitialize_generators"] = reinitialize_generators
    global_vars["ui_out"] = ui_out
    global_vars["out"] = backend_out
    global_vars["ui_in"] = ui_in
    global_vars["in"] = backend_in
    global_vars["log"] = backend_info
    global_vars["interactive_python"] = console
    global_vars["drop_nows"] = 0
    global_vars["@now"] = 0.0
    global_vars["output_rate"] = 1.0
    global_vars["loop-depth"] = 0 # This is the depth of nested main_loops
    global_vars["save-loop-depth"] = 1
    global_vars["DfInterpreter.console"] = console
    global_vars["keyboard-queue"] = []
    global_vars["root.call"] = [] # list of callees
    global_vars["timer.calls"] = [] # (@now-time, callee, identifier) list
    global_vars["hud.interaction"] = False # true if hud interaction is on
    init_hud_interaction_globals()
    #reinitialize_generators()

    global_vars["sleep_amount"] = 1.0/50.0
    global_vars["regenerate_instruments"] = 0
    global_vars["current_command"] = ""
    sout = sys.stdout
    serr = sys.stderr
    sys.stdout = console
    sys.stderr = console
    console.runsource("print 'drums-frontend interactive Python shell'")
    sys.stdout = sout
    sys.stderr = serr


    def pad(x,y,p):
       if (len(x)<y):
          return p*(y-len(x)) + x
       else:
          return x
          
    global_vars["data_send_channel"] = ui_out

    def do_compile_command(cmd):
        try:
            co = code.compile_command(cmd,"<input>","exec")
        except:
            co = cmd
        return co

    def do_run_code(co,string=""):
        """ return True on error.... (via showtraceback) """
        if co:
            console = DfGlobal()["interactive_python"]
            sys.stdout = console
            sys.stderr = console
            console.runcode(co)
            traced = console.hasTracebacked()
            if traced and string:
                if g('show.code',True):
                    print "CODE FOLLOWS:\n<<<\n",string,"\n>>>\n"
            sys.stdout = sout
            sys.stderr = serr
            return traced
        else:
            return False
                
        
    def python_input(line):
        line += "\n"
        gl = DfGlobal()
        old_lines = gl["current_command"]
        nbr_spaces = count_ws(line)
        if nbr_spaces > 0:
            gl["current_command"] = old_lines + line
        else:
            oldcode = do_compile_command(old_lines)
            do_run_code(oldcode)
            newcode = do_compile_command(line)
            if newcode:
                do_run_code(newcode)
                gl["current_command"] = ""
            else:
                gl["current_command"] = line
        if gl["current_command"]:
            send_line("PYTHON","(continue)")
        

    def python_bounce(lines):
        gl = DfGlobal()
        gl["current_bounce"] = ""
        lines = eval(lines) + "\n\n"
        def runner(line):
            line += "\n"
            old_lines = gl["current_bounce"]
            nbr_spaces = count_ws(line)
            if nbr_spaces > 0:
                gl["current_bounce"] = old_lines + line
                return True
            else:
                oldcode = do_compile_command(old_lines)
                if not do_run_code(oldcode,old_lines):
                    newcode = do_compile_command(line)
                    if newcode:
                        gl["current_bounce"] = ""                        
                        if not do_run_code(newcode,line):
                            return True
                        else:
                            return False
                    else:
                        gl["current_bounce"] = line
                        return True
                else:
                    return False

        do_echo = gl("bounce.echo",False)
        
        for part in lines.split("\n"):
            stripped = part.strip()
            if stripped or gl["current_bounce"].endswith('\\\n'):
                if do_echo:
                    send_line("PYTHON'","] "+part)                
                if not runner(part):
                    break
                
        if gl["current_bounce"]:
            cmd = gl["current_bounce"] + "\n"
            code = do_compile_command(cmd)
            do_run_code(code,cmd)
            
            

    def OLDpython_bounce(lines):
        global_vars = DfGlobal()
        global_vars["current_bounce"] = ""
        lines = eval(lines) + "\n\n"
        #print "BOUNCED LINES=",lines
        def runner(line):
            line = line + "\n"
            global_vars["current_bounce"] = global_vars["current_bounce"] + line
            console = global_vars["interactive_python"]
            ui_out = global_vars["ui_out"]
            retval = True
            if ((count_ws(global_vars["current_bounce"]) >= count_ws(line)) \
                & (not line.endswith("\\\n"))):
                try:
                    co = code.compile_command(global_vars["current_bounce"],"<input>","exec")
                except:
                    co = 1
                    retval = False
            else:
                co = 0
            if co:
                sys.stdout = console
                sys.stderr = console
                console.runsource(global_vars["current_bounce"])
                sys.stdout = sout
                sys.stderr = serr
                if not global_vars["current_bounce"].strip():
                    retval = True
                global_vars["current_bounce"] = ""
                return retval
            else:
                return True
        
        for part in lines.split("\n"):
            send_line("PYTHON'","ext> "+part)
            if not runner(part):
                print "DO NOT CONTINUE FOR", part
                break

    DfGlobal()["python.bouncer.fn"] = python_bounce

    add_data_channel_handler("PYTHON",python_input)
    add_data_channel_handler("PYTHONBOUNCE",python_bounce)

    DfGlobal()["broken.line.start.ui"] = ""
    DfGlobal()["broken.line.start.backend"] = ""
    DfGlobal()["broken.line.input.backendinfo"] = ""

    DfGlobal()["no-waste-time"] = False
    DfGlobal()["default.depth"] = 8
    DfGlobal()["default.steps"] = 8


    def main_wait_for_input():
       global_vars = DfGlobal()
       backend_out = global_vars["out"]
       backend_in = global_vars["in"]
       backend_info = global_vars["log"]
       ui_out = global_vars["ui_out"]
       ui_in = global_vars["ui_in"]
       global_vars["loop-depth"] += 1
       for loop_idx in range(32):
           if global_vars["no-waste-time"]:
               do_sleep = -1
           else:
               do_sleep = 1           
           try:
              #line = ui_in.readline()
              line = my_readline(ui_in)
              if (len(line)==0):
                 global_vars["loop-depth"] -= 1
                 return -1
              do_sleep = 0
              line = global_vars["broken.line.start.ui"] + line
              if line.endswith('\n'):
                  global_vars["broken.line.start.ui"] = ""
                  if line.startswith("CONSOLE:"):
                     backend_out.write(line[8:])
                     print " >>> ", line[8:].strip()
                     backend_out.flush()
                  elif line == "MEASURED!\n":
                     initialize_measures()
                  elif line == "REGENERATE-INSTRUMENTS!\n":
                     global_vars["regenerate_instruments"] = 1
                     global_vars["reinitialize_generators"]()
                  else:
                      handle_read_line(line[0:len(line)-1])
              else:
                  print " ___ caught over-long line from ui_in"
                  global_vars["broken.line.start.ui"] = line

           except IOError, err:
              if (err.errno != errno.EWOULDBLOCK):
                 print "Error communicating with user-interface: ",err
                 global_vars["loop-depth"] -= 1
                 return -1

           try:
              #line = backend_in.readline()
              line = my_readline(backend_in)
              if (len(line)==0):
                 global_vars["loop-depth"] -= 1
                 return -1
              do_sleep = 0
              line = global_vars["broken.line.start.backend"] + line
              if line.endswith('\n'):
                  global_vars["broken.line.start.backend"] = ""
                  if (not line.startswith("@now ")) \
                  and (not line.startswith("@sid "))\
                  and (not line.startswith("@caching "))\
                  and (not line.startswith("@id "))\
                  and (not line.startswith("@ml_")):
                     print " <*> ", line.strip()
                     ui_out.write("CONSOLE: <*> "+line)
                     ui_out.flush()
                  line = line[0:len(line)-1]
                  if line.startswith("@"):
                     if ' ' in line:
                        varname = line[0:line.index(' ')]
                        varvalue = line[line.index(' ')+1:]
                        if varname == "@now":
                           varvalue = float(varvalue)
                           timer_calls = global_vars["timer.calls"]
                           while timer_calls:
                               head = timer_calls[0][0]
                               if head <= varvalue:
                                   add_root_call(timer_calls.pop(0)[1])
                               else:
                                   break                           
                     else:
                        varname = line
                        varvalue = ""
                     global_vars[varname] = varvalue

                  if line.startswith("@main_start"):
                     initialize_backend()
                     ui_out.write("CHANNUM:"+str(global_vars["sampler_channels"])+"\n")
                     ui_out.flush();
                     initialize_new_technology()
                  elif line.startswith("@now "):
                     global_vars["@now-callback"]()
                     global_vars["drop_nows"] += 1
                     if (global_vars["drop_nows"] == 25):
                        stime = int(global_vars["@now"])/int(global_vars["output_rate"])
                        mtime = int(stime/60)
                        htime = int(mtime/60)
                        mtime = mtime % 60
                        stime = stime % 60
                        timestr = str(htime)+"h"+pad(str(mtime),2,'0')+"'"+pad(str(stime),2,'0')+'"'
                        ui_out.write("SAMPLER-TIME:"+timestr+"\n")
                        ui_out.flush()
                        global_vars["drop_nows"] = 0
                        backend_out.write("mlinfo\n")
                        backend_out.flush()
                  elif line.startswith("@ml_meter "):
                     meter = map(float, line[10:].split(" "))
                     l10 = log(10.0)
                     def safe_calc_meter_value(x):
                        try:
                           if x > 0.0:
                              val = int(round(10.0*log(x)/l10))
                           else:
                              val = -100.0
                        except OverflowError:
                           val = -100.0
                        return val

                     meter = map(safe_calc_meter_value, meter)
                     mstring = "["
                     for m in meter:
                        if (m <= -100):
                           sm = "-99"
                        else:
                           sm = str(m)
                           if (len(sm)<3):
                              sm = " "*(3-len(sm))+sm
                        mstring = mstring + sm +","

                     mstring = mstring[0:len(mstring)-1] + "]dB"
                     ui_out.write("MASTER-METER:"+mstring+"\n")
                     ui_out.flush()
                  elif line.startswith("@ml_current_gain "):
                     meter = map(float, line[17:].split(" "))
                     l10 = log(10.0)
                     try:
                        meter = map(lambda x: int(round(20.0*log(x)/l10)) , meter)
                     except OverflowError:
                        meter = map(lambda x: 0, meter)
                     mstring = "["
                     for m in meter:
                        sm = str(m)
                        if (len(sm)<3):
                           sm = " "*(3-len(sm))+sm
                        mstring = mstring + sm +","

                     mstring = mstring[0:len(mstring)-1] + "]dB"
                     ui_out.write("MASTER-GAIN:"+mstring+"\n")
                     ui_out.flush()
              else:
                  print " ___ caught over-long line from backend_in"
                  global_vars["broken.line.start.backend"] = line

           except IOError, err:
              if (err.errno != errno.EWOULDBLOCK):
                 print "Error communicating with backend: ", err
                 global_vars["loop-depth"] -= 1
                 return -1
           try:
              #line = backend_info.readline()
              line = global_vars["broken.line.input.backendinfo"] + my_readline(backend_info)
              if (len(line)==0):
                 global_vars["loop-depth"] -= 1
                 return -1
              if line.endswith("\n"):
                  global_vars["broken.line.input.backendinfo"] = ""
                  do_sleep = 0
                  ui_out.write("CONSOLE: *** "+line)
                  ui_out.flush()
                  print " *** ",line.strip()
              else:
                  global_vars["broken.line.input.backendinfo"] = line
           except IOError:
              pass

           if handle_keyboard_if_root():
               do_sleep = 0
               
           if run_root_call():
               do_sleep = 0
               
           if do_sleep>0:
              #time.sleep(global_vars["sleep_amount"])
              # we now use select
              waiting_for = [ui_in,backend_in,backend_info]
              select.select(waiting_for,[],waiting_for,global_vars["sleep_amount"])
              break
           elif do_sleep<0:
              break
       #if loop_idx >= 31:
       #    print "MAIN LOOP HIT CEILING!"
       global_vars["loop-depth"] -= 1
       return 1

    global_vars["main_input_loop"] = main_wait_for_input

    while (1):
       if global_vars["main_input_loop"]() < 0:
          break

    do_autosave()

    print "Sending '.quit\\n'..."
    try:
       backend.communicate('.quit\n')
    except OSError:
       pass
    backend.wait()
    print "...backend finished."

    print "Sending 'UI-FINISH!\\n'"
    ui_out.write("UI-FINISH!\n")
    try:
       ui_out.close()
    except IOError:
       pass

    os.waitpid(pid, 0)
    print "...user-interface finished."

    print "\ndrums-frontend finished."
    

if do_profile:
    import cProfile, pstats
    prof = cProfile.Profile()
    prof.runctx("other_end()",globals(),locals())
    sys.stdout = open(a+"_interprof.log","w")
    stats = pstats.Stats(prof)
    stats.strip_dirs()
    stats.sort_stats("time")
    stats.print_stats(20)
    stats.print_callees(20)
    stats.print_callers(20)
else:
    other_end()
    
sys.exit(0)
