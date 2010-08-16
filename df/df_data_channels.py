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
from bisect import *
from df_global import *

def handle_read_line(line):
    """handle_read_line(line)   handle a read line that contains data sent via the df_data_channels module."""
    g = DfGlobal()
    dc = g["data_channels"]
    if ":" in line:
        channel = line[0:line.index(":")]
        data = line[line.index(":")+1:]
        if channel in dc:
            dc[channel](data)
        else:
            print " ### (", channel,") ",data
    else:
        print "#### ", line
        
def send_line(channel,  data): # data should not contain the ending '\n'
        """send_line(channel,  data)   send out data immediately on channel"""
        g = DfGlobal()
        o = g["data_send_channel"]
        o.write(channel+":"+data+"\n")
        o.flush()

def repr_exec(line):
    exec(eval(line))

def send_exec(commands):
    send_line("repr_exec",repr(commands))

def set_global_key(line):
    key,data = eval(line)
    DfGlobal()[key] = data

def send_global_key(key):
    send_line("set_global_key",repr((key,DfGlobal()[key])))
        
def send_lines(channel, data): # data is still a string but with '\n' in it
        """send_line(channel,  data)   send out data immediately on channel
        (this version allows for data to contain several lines sep. by '\n')
        """
        g = DfGlobal()
        o = g["data_send_channel"]
        for line in data.split('\n'):
            o.write(channel+":"+line+"\n")
        o.flush()
        
def send_line_at(time, channel,  data):
        """send_line_at(time, channel,  data)   send out data at time on channel"""
        g = DfGlobal()
        buffer = g["data_channels_buffer"]
        tuple = (time+g["viz_lag"], channel, data)
        insort(buffer, tuple)
        
        
def send_lines_at(time, channel,  data):
        """send_line_at(time, channel,  data)   send out data at time on channel"""
        g = DfGlobal()
        buffer = g["data_channels_buffer"]
        lines = [(time+g["viz_lag"],channel,dta) for dta in data.split("\n")]
        position = bisect(buffer,(time+g["viz_lag"],channel,""))
        new = buffer[:position]
        new.extend(lines)
        new.extend(buffer[position:])
        g["data_channels_buffer"] = new

def init_data_channels(which):
    # channels that send state snapshots do not need unnecessary changes
    if which == 'frontend':
        def bounce_ext(name):
            try:
                send_line("bounce_ext",repr(DfGlobal()["ext"][name]))
            except Exception,err:
                print "Error bouncing ext: ",name
                print "   reason:  ",err
        add_data_channel_handler("bounce_ext",bounce_ext)        
        DfGlobal()["data_channels.collapsable"] = ['outer_arc','inner_arc','mid_arc',\
                                                   'left hand','left foot',\
                                                   'right hand','right foot',\
                                                   'left hand.potential',\
                                                   'right hand.potential','left foot.potential',\
                                                   'right foot.potential',\
                                                   'text1','text2','text3','text4',\
                                                   'text5','text6','text-mode','text-cmd',\
                                                   'text-next','text-keyboard','text-chord',\
                                                   'speed-arc','speed-ctl-arc',\
                                                   'headupdisplay']
    elif which == 'userinterface':
        DfGlobal()["data_channels.collapsable"] = []
    else:
        DfGlobal()["data_channels.collapsable"] = []
    add_data_channel_handler("repr_exec",repr_exec)
    add_data_channel_handler("set_global_key",set_global_key)
                                      

def send_lines_up_to(time):
        """send_lines_up_to(time)   send out all lines that requested to be sent before time"""
        g = DfGlobal()
        buffer = g["data_channels_buffer"]
        o = g["data_send_channel"]
        
        if len(buffer) > 0:
            collapsable = {}
            for key in g["data_channels.collapsable"]:
                collapsable[key] = None
            
            index = 0
            length = len(buffer)
            while buffer[index][0] <= time:
                chan = buffer[index][1]
                if chan in collapsable:
                    collapsable[chan] = buffer[index][2]
                else:
                    o.write(chan+":"+buffer[index][2]+"\n")
                index += 1
                if index == length:
                    break

            for k in collapsable:
                data = collapsable[k]
                if data != None:
                    o.write(k+":"+data+"\n")
            
            if index:
                o.flush()
                g["data_channels_buffer"] = buffer[index:]

def add_data_channel_handler(name,  func):
    """add_data_channel_handler(name,  func)   add a handling routine for data channel determinded by name, func takes the data line as parameter."""
    g = DfGlobal()
    g["data_channels"][name] = func
    
def del_data_channel_handler(name):
    """del_data_channel_handler(name)   delete a handling routine for data channel determinded by name."""
    g = DfGlobal()
    g["data_channels"].__delitem__(name)
