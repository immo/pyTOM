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

builtin_id = id

from df_global import *
from df_ontology import *
from df_backend import *
from df_data_channels import *
from math import *
import random
from df_piecewisepolynomialfunction import *

class Concept(object):
    """class that stores a musical concept, that is, the information needed to
    drive your limbs in order to make a certain rhythm"""
    def __init__(self, potential_strings={}, strength_strings={}, \
                 riff_strings={}, bar_strings={}, change_instruments={}, \
                 def_strength_string="lambda x:0.8", def_riff_stroke=0.0, \
                 def_bar_stroke=None, pre_run_time = 1.0/16.0,\
                 riff_length=16.0, bar_lengths = [4.0], timed_commands={},\
                 riff_command=None, set_bps=None, text_vars={},represent=True):
        """self, potential_strings={}, strength_strings={}, riff_strings={}, 
        bar_strings={}, def_strength_string="lambda x:0.8", def_riff_stroke=0.0,
        def_bar_stroke=None, pre_run_time = 1.0/16.0, riff_length=16.0,
        bar_lengths = [4.0,4.0,4.0,4.0]), timed_commands={}, riff_command=None,
         set_bps = None, text_vars={}
        """
        
        # dictionary for user extensions
        
        self.ext = {}
        
        self.set_bps = set_bps
        
        self.tick_parameters = None

        self.text_vars = text_vars

        self.potential_strings = potential_strings
        self.strength_strings = strength_strings
        self.riff_strings = riff_strings
        self.bar_strings = bar_strings
        self.def_strength_string = def_strength_string
        
        self.strength_funs = {}
        for i in strength_strings:
            self.strength_funs[i] = eval(strength_strings[i])
        self.default_strength = eval(def_strength_string)
        
        self.potential_funs = {}
        for i in potential_strings:
            self.potential_funs[i] = eval(potential_strings[i])
        
        self.riff_stroke = {}
        for i in riff_strings:
            self.riff_stroke[i] = eval(riff_strings[i])
        self.default_riff_stroke = def_riff_stroke
        
        self.bar_stroke = {}
        for i in bar_strings:
            self.bar_stroke[i] = eval(bar_strings[i])
        self.default_bar_stroke = def_bar_stroke
        
        self.change_instruments = change_instruments
        
        self.pre_run_time = pre_run_time
        self.riff_length = riff_length
        self.bar_lengths = bar_lengths
        
        self.timed_commands = timed_commands
        self.riff_command = riff_command 

        if represent:
            self.representation = "Concept(" + repr(potential_strings) + "," + \
                                       repr(strength_strings) + "," + \
                                       repr(riff_strings) + "," + \
                                       repr(bar_strings) + "," +\
                                       repr(change_instruments) + "," +\
                                       repr(def_strength_string) + "," + \
                                       repr(def_riff_stroke) + "," + \
                                       repr(def_bar_stroke) + "," + \
                                       repr(pre_run_time) + "," + \
                                       repr(riff_length) + "," + \
                                       repr(bar_lengths) + "," + \
                                       repr(timed_commands) + "," + \
                                       repr(riff_command) + "," + \
                                       repr(set_bps) + "," + \
                                       repr(text_vars) + ")"
        else:
            self.representation = "<Concept at "+str(builtin_id(self))+">"
                                       
        self.alt_representation = self.representation
        
        compiler = DfGlobal()["DfInterpreter.console"].compile
        if riff_command != None:
            self.c_riff_command = compiler(riff_command)
            
        self.c_timed_commands = {}
        for t in timed_commands:
            precompiled_fun = compiler(timed_commands[t])
            self.c_timed_commands[t] = lambda x, fn=precompiled_fun:fn()

        if not DfGlobal()["no.calculate_preview"]:
            self.calculate_preview()
        else:
            self.preview_string = "clear"
        
        self.prepare_change_instruments()
        self.change_instruments_index = 0
        
        self.c_timed_commands_keys = self.c_timed_commands.keys()[:]
        self.c_timed_commands_keys.sort()
        self.c_timed_commands_values = [self.c_timed_commands[k] \
                                         for k in self.c_timed_commands_keys]
        self.c_timed_commands_len = len(self.c_timed_commands_keys)
        self.c_timed_commands_index = 0
        
        self.viz_level = DfGlobal()["viz_level"]
        self.show_previews = self.viz_level >= 70
        self.show_textvars = self.viz_level >= 4
        
        self.hash = hash( repr(self) )

        self.update_vars = ["text"+str(i) for i in [1,2,3,5,6]]

    def prepare_change_instruments(self):
        self.change_instruments_keys = self.change_instruments.keys()[:]
        self.change_instruments_keys.sort()
        self.change_instruments_values = [self.change_instruments[k] \
                                          for k in self.change_instruments_keys]
        self.change_instruments_len = len(self.change_instruments_keys)
        

    def add_change_instruments(self, time, limb, instrument):
        """ adds a request to change an instrument """
        if not time in self.change_instruments:
            self.change_instruments[time] = {}
        self.change_instruments[time][limb] = instrument
        if self.change_instruments_index < self.change_instruments_len:
            if self.change_instruments_index > 0:
                t = self.change_instruments_keys[self.change_instruments_index-1]
            else:
                t = -10000.0
            if t > time:
                self.change_instruments_index += 1
        self.prepare_change_instruments()


    def add_timed_command(self, time, fn):
        """ adds a timed command for time, where fn is a function that
        takes the concepts self reference as argument
        """

        if time in self.c_timed_commands:
            other_hand = self.c_timed_commands[time]
            self.c_timed_commands[time] = lambda x: (other_hand(x),fn(x))
        else:
            if self.c_timed_commands_index > 0:
                last = self.c_timed_commands_keys[self.c_timed_commands_index-1]
            else:
                last = 0.0
            if time <= last:
                self.c_timed_commands_index += 1 #forget it for this run
            self.c_timed_commands[time] = fn
            
        self.c_timed_commands_keys = self.c_timed_commands.keys()[:]
        self.c_timed_commands_keys.sort()
        self.c_timed_commands_values = [self.c_timed_commands[k] \
                                         for k in self.c_timed_commands_keys]
        self.c_timed_commands_len = len(self.c_timed_commands_keys)
        

    def calculate_preview(self):
        """Calculate all preview relevant data"""

        self.hit_time_instruments = {}
            
        current_instruments = {}
        last_potential = {}
            
        for lmb in self.potential_funs:
            current_instruments[lmb] = "(undefined)"
            last_potential[lmb] = 0.0
        
        resolution = 1.0/36.0 #1.0/128.0
        
        time = 0.0

        change_instruments = self.change_instruments
        riff_length = self.riff_length
                    
        for t in change_instruments:
            if t <= time:
                chg = change_instruments[t]
                for lmb in chg:
                    current_instruments[lmb] = chg[lmb]
                    
        self.hit_times = []
        
        while time < riff_length:
            instrument_list = []
            for lmb in self.potential_funs:
                if self.potential_funs[lmb](time) - last_potential[lmb]\
                   >= 1.0:
                       last_potential[lmb] += 1.0
                       instrument_list += [current_instruments[lmb]]
                       
            if instrument_list != []:
                instrument_list.sort()
                self.hit_time_instruments[time] = instrument_list
                self.hit_times += [time]

            for t in change_instruments:
                if time <= t <= time + resolution:
                    chg = change_instruments[t]
                    for lmb in chg:
                        current_instruments[lmb] = chg[lmb]
            time += resolution

        self.nbr_of_hits = last_potential
            
        instrumentations = [uniq for uniq in self.hit_time_instruments.values()\
                             if uniq not in locals()['_[1]']]
        instrumentations.sort()
        
        colornames = ["red","green","blue","yellow","white", "purple", "gold",\
                    "cyan","aquamarine1", "cornsilk1"]
        
        ins_colors = {}
        ctr = 0
        for i in instrumentations:
            ins_colors[repr(i)] = colornames[ctr % len(colornames)]
            ctr += 1
        
        self.preview_string = "clear"
        for t in self.hit_times:
            amount = t / riff_length
            degree = 2.0*pi*amount
            outer_rim = float(len(self.hit_time_instruments[t]))*0.013+0.23
            x0 = 1.0 + 0.23*sin(degree)
            x1 = 1.0 + outer_rim*sin(degree)
            y0 = 0.5 - 0.23*cos(degree)
            y1 = 0.5 - outer_rim*cos(degree)
            color = ins_colors[repr(self.hit_time_instruments[t])]
            self.preview_string += "\n" + str(x0) + "," +\
                                    str(y0) + "," + str(x1) +\
                                    "," + str(y1) + "," + color
            

    def __eq__(self,r):
        return self.strength_funs == r.strength_funs and \
               self.default_strength == r.default_strength and \
               self.potential_funs == r.potential_funs and \
               self.riff_stroke == r.riff_stroke and \
               self.default_riff_stroke == r.default_riff_stroke and \
               self.bar_stroke == r.bar_stroke and \
               self.change_instruments == r.change_instruments and \
               self.default_bar_stroke == r.default_bar_stroke and \
               self.pre_run_time == r.pre_run_time and \
               self.riff_length == r.riff_length and \
               self.bar_lengths == r.bar_lengths and \
               self.timed_commands == r.timed_commands and \
               self.riff_command == r.riff_command and \
               self.text_vars == r.text_vars

    def __sub__(self, r):
        difference = self.riff_length - r.riff_length
        if len(r.hit_times) > 0:
            for x in self.hit_times:
                d = min([abs(y-x) for y in r.hit_times])
                difference += d
                self_instr = self.hit_time_instruments[x]
                d2 = len(self.hit_time_instruments)
                for c in [y for y in r.hit_times if abs(x-y) <= d+0.01]:
                    candidates = r.hit_time_instruments[c]
                    count = 0
                    count2 = 0
                    for q in self_instr:
                        if q in candidates:
                            count += 1
                    for q in candidates:
                        if q in self_instr:
                            count2 += 1
                    new_d2 = float(len(self_instr)+len(candidates)\
                                   -count-count2)*0.25
                    if new_d2 < d2:
                        d2 = new_d2
                difference += d2
        else:
            difference += sum(self.hit_times) + len(self.hit_times)*3.0
        if len(self.hit_times) > 0:
            for y in r.hit_times:
                difference += min([abs(y-x) for x in self.hit_times])
        else:
            difference += sum(r.hit_times) + len(r.hit_times)*3.0
        difference += abs(float(len(r.hit_times)-len(self.hit_times)))
        if len(r.change_instruments.keys())>0:
            for x in self.change_instruments.keys():
                difference += min([abs(y-x) for y in r.change_instruments.keys()])
        else:
            difference += sum(self.change_instruments.keys()) \
            + len(self.change_instruments.keys())*3.0
        if len(self.change_instruments.keys()) > 0:
            for y in r.change_instruments.keys():
                difference += min([abs(y-x) for x in self.change_instruments.keys()])
        else:
            difference += sum(r.change_instruments.keys()) \
            + len(r.change_instruments.keys())*3.0
        return difference



    def __hash__(self):
        return self.hash



    def __repr__(self):
        return self.representation



    def tick(self,time,tick, time_after, pot_id): # This is called every single small portion of beat time, the length of the step is in tick
        """tick(self, time, tick, time_afer,pot_id)    
        process a single tick-length portion of beat-time, mainly adding up 
        potential to DfGlobal()["limbs"] objects, where time represents the 
        time in riff of the start point, and time_after the time in riff of 
        the end point of the tick interval. pot_id is the concepts id."""
        if time_after < self.riff_length:
            limbs = DfGlobal()["limbs"]
            while self.change_instruments_index < self.change_instruments_len:
                t = self.change_instruments_keys[self.change_instruments_index]
                if t > time_after:
                    break
                else:
                    chg = self.change_instruments_values\
                              [self.change_instruments_index]
                    for limb in chg:
                        limbs[limb].current = chg[limb]
                        #print limb,"-->",chg[limb],"@",time_after,"=?",t
                        
                self.change_instruments_index += 1
            #for t in self.change_instruments:
            #    if time < t <= time_after:
            #        chg = self.change_instruments[t]
            #        for limb in chg:
            #            limbs[limb].current = chg[limb]
            #for t in self.c_timed_commands:
            #    if time < t <= time_after:
            #        exec(self.c_timed_commands[t])
            
            while self.c_timed_commands_index < self.c_timed_commands_len:
                t = self.c_timed_commands_keys[self.c_timed_commands_index]
                if time_after < t:
                    break
                else:
                    self.tick_parameters = {'time':time,'tick':tick,\
                                            'time_after':time_after,\
                                            'pot_id':pot_id}
                    self.c_timed_commands_values\
                             [self.c_timed_commands_index](self)
                    self.c_timed_commands_index += 1
                
            for limb in limbs:
                if limb in self.potential_funs:
                    limbs[limb].potential[pot_id] = \
                                     self.potential_funs[limb](time_after)




    def determineStrength(self, limb, time, bar):
        """determineStrength(self, limb, time, bar)    determine the strength that a certain limb is supposed to hit with at specified time and bar length, where time is the current time in the riff"""
        #print "strength ", limb, " at ", time, " is ", self.strength_funs[limb](time)
        if limb in self.strength_funs:
            return self.strength_funs[limb](time)
        else:
            return self.default_strength(time)

    def getStrengthFun(self, limb):
        """ return the strength of a limb as a function of the elapsed time """
        if limb in self.strength_funs:
            return self.strength_funs[limb]
        else:
            return self.default_strength



    def riff(self, offs, c_time): # This is called upon entering a new riff
        """riff(self, offs, c_time)    process the start of a new riff,
        offs is the time already gone in the riff, time is the time marker"""
        mind = DfGlobal()["mind"]
        mind.bar_nr = 0
        mind.riff_start = mind.time - offs
        #mind.riff_start += mind.length
        mind.length = self.riff_length
        
        if self.set_bps != None:
            mind.set_beatspersecond(self.set_bps)
        
        if self.riff_command!= None:
            exec(self.c_riff_command)
        
        limbs = DfGlobal()["limbs"]
        for limb in limbs:
            if limb in self.riff_stroke:
                #try:
                #    print self.text_vars['text1'], " -> limbs[",repr(limb),"] = ",repr(self.riff_stroke[limb])
                #except:
                #    print self, " -> limbs[",repr(limb),"] = ",repr(self.riff_stroke[limb])                    
                limbs[limb].stroke = self.riff_stroke[limb]
            else:
                #try:
                #    print self.text_vars['text1'], __builtins__.id(self), " *-> limbs[",repr(limb),"] = ",repr(self.default_riff_stroke)
                #except:
                #    print self, " *-> limbs[",repr(limb),"] = ",repr(self.default_riff_stroke)
                limbs[limb].stroke = self.default_riff_stroke
                
        if self.show_previews:
            send_lines_at(c_time,"preview",self.preview_string)

        if self.show_textvars:
            for k in self.update_vars: 
                send_line_at(c_time,k,self.text_vars.setdefault(k,"''"))
        
        self.change_instruments_index = 0
        
        #limbs = DfGlobal()["limbs"]
        
        #while self.change_instruments_index< self.change_instruments_len:
        #    t = self.change_instruments_keys[self.change_instruments_index]
        #    if 0.0 < t:
        #        break
        #    else:
        #        chg = self.change_instruments_values\
        #                  [self.change_instruments_index]
        #        for lmb in chg:
        #            limbs[lmb] = chg[lmb]
        #        self.change_instruments_index += 1
                
        self.c_timed_commands_index = 0
        
        #while self.c_timed_commands_index < self.c_timed_commands_len:
        #    t = self.c_timed_commands_keys[self.c_timed_commands_index]
        #    if 0.0 < t: # t > 0: wait until we get there
        #        break
        #    else:
        #        print "Calling:",t,self.c_timed_commands_index,"at riff start"
        #        self.c_timed_commands_values[self.c_timed_commands_index](self)
        #        self.c_timed_commands_index += 1



    def bar(self, offs): # This is called upon entering a new bar
        """bar(self, offs)    process the start of a new bar,
        offs is the time already gone in the bar"""
        mind = DfGlobal()["mind"]
        if mind.bar_nr < len(self.bar_lengths):
            mind.bar_start = mind.time - offs
            mind.bar = self.bar_lengths[mind.bar_nr]
            mind.bar_nr += 1
        
        limbs = DfGlobal()["limbs"]
        for limb in limbs:
            if limb in self.bar_stroke:
                set_stroke = self.bar_stroke[limb]
            else:
                set_stroke = self.default_bar_stroke
            if not set_stroke == None:
                #print limb, ".stroke =", set_stroke
                limbs[limb].stroke = set_stroke



def extractTokens(s):
    """extractTokens(s)   convert string s into a list of token strings"""
    if len(s) == 0:
        return []
    else:
        if s[0] == '(':
            rbracket = s.find(')')+1
            if rbracket == 0:
                rbracket = len(s)
            return [s[0:rbracket]] + extractTokens(s[rbracket:])
        elif s[0] == '[':
            rbracket = s.find(']')+1
            if rbracket == 0:
                rbracket = len(s)
            return [s[0:rbracket]] + extractTokens(s[rbracket:])
        elif s[0] == '<':
            rbracket = s.find('>')+1
            if rbracket == 0:
                rbracket = len(s)
            return [s[0:rbracket]] + extractTokens(s[rbracket:])
        elif s[0] == '@':
            rbracket = s[1:].find('@')+2
            if rbracket == 0:
                rbracket = len(s)
            return [s[0:rbracket]] + extractTokens(s[rbracket:])
        elif s[0] == '$':
            rbracket = s[1:].find('$')+2
            if rbracket == 0:
                rbracket = len(s)
            return [s[0:rbracket]] + extractTokens(s[rbracket:])
        elif s[0] == '{':
            rbracket = s.find('}')+1
            if rbracket == 0:
                rbracket = len(s)
            return [s[0:rbracket]] + extractTokens(s[rbracket:])
        else:
            return [s[0:1]] + extractTokens(s[1:])
    
def genStrength(s):
    """genStrength(s)    generate a strength lambda expression string from 
    meta data string s
    
    Token   Meaning
    u       "unstressed"   (start unstressed)
    !       "stressed"     (start stressed)
    W       "whole"        (set stress pattern length to whole notes & express)
    H       "half"         (set stress pattern length to half notes & express)
    Q       "quarter"      (set stress pattern length to 4th notes & express)
    E       "eighth"       (set stress pattern length to 8th notes & express)
    S       "16th"         (set stress pattern length to 16th notes & express)
    T       "32nd"         (set stress pattern length to 32nd notes & express)
    [###]   "n-tole"       (set ntole to ###, slope in the above is always
                            multiplied with the ntole factor. ### may be 0.666 
                            or 3/2 etc.)
    .       "another"      (repeat current stress pattern)
    ,       "again"        (repeat current stress pattern & express)
    {###}   "factor"       (set lenfactor to the value of ###)
    (###)   "stressed l."  (set the level of the stressed notes to ###)
    <###>   "delta l."     (set the level-amount that an unstressed note is less
                            than a stessed note to ###)
    @###@   "set offset"   (set the offset of the curve functions)
    $###$   "split at"     (the right part starts at time ###, always & express)
    m       "stress mode"  (a stress pattern length is from one stressed to 
                            another stressed note (default))
    M       "binary mode"  (a stress pattern length is from one stressed to
                            one unstressed note or vice versa)
    x       "express"(force the current part to be expressed)
    """
    tokens = extractTokens(s)
    stressed = 1.0
    delta_unstressed = -0.1
    length = 1.0
    lenfactor = 1.0
    current_x = 0.0
    start_x = 0.0
    offset_x = 0.0
    ntole = 1.0
    start_stressed = 1
    mode = 0 #mode 0 = length equals stressd, 1 = 2*length equals stressed
    left_injections = ""
    def tokenwise(toks, stressed=stressed, delta_unstressed=delta_unstressed,\
                  length=length, start_stressed=start_stressed, mode=mode,\
                  current_x=current_x,lenfactor=lenfactor,start_x=start_x,\
                  offset_x=offset_x, ntole=ntole, \
                  left_injections=left_injections):
        if toks == []:
            if mode == 0:
                if start_stressed == 1:
                    fct = "sin"
                else:
                    fct = "cos"
                return left_injections,\
                        "( " + str(stressed) + " + abs("\
                         + fct + "((x - " + str(start_x) + ") * " \
                                                 + str(pi/length) \
                                                 + " + " + str(offset_x*pi)\
                                                 + ")) * "\
                                                 + str(delta_unstressed) + " )"
            else:
                if start_stressed == 1:
                    fct = "sin"
                else:
                    fct = "cos"
                return left_injections,\
                        "( " + str(stressed) + " + abs("\
                         + fct + "((x - " + str(start_x) + ") * " \
                                                + str(pi/(2.0*length)) \
                                                + " + " + str(offset_x*pi)\
                                                + ")) * "\
                                                + str(delta_unstressed) + " )"
        else:
            if mode == 0:
                if start_stressed == 1:
                    fct = "sin"
                else:
                    fct = "cos"
                l_expression = "( " + str(stressed) + " + abs("\
                         + fct + "((x - " + str(start_x) + ") * " \
                                                 + str(pi/length) \
                                                 + " + " + str(offset_x*pi)\
                                                 + ")) * "\
                                                 + str(delta_unstressed) + " )"
            else:
                if start_stressed == 1:
                    fct = "sin"
                else:
                    fct = "cos"
                l_expression = "( " + str(stressed) + " + abs("\
                         + fct + "((x - " + str(start_x) + ") * " \
                                                + str(pi/(2.0*length)) \
                                                + " + " + str(offset_x*pi)\
                                                + ")) * "\
                                                + str(delta_unstressed) + " )"
            l_guard = " if x <= " + str(current_x) + " else "
            express = False
            t = toks[0]
            if t == '.':
                current_x += length*lenfactor
            elif t == ",":
                current_x += length*lenfactor
                express = True
            elif t == "T":
                express = True
                length = 1.0/(8.0*ntole)
                current_x += length*lenfactor
            elif t == "S":
                express = True
                length = 1.0/(4.0*ntole)
                current_x += length*lenfactor
            elif t == "E":
                express = True
                length = 1.0/(2.0*ntole)
                current_x += length*lenfactor
            elif t == "Q":
                express = True
                length = 1.0/(1.0*ntole)
                current_x += length*lenfactor
            elif t == "H":
                express = True
                length = 2.0/(ntole)
                current_x += length*lenfactor
            elif t == "W":
                express = True
                length = 4.0/(ntole)
                current_x += length*lenfactor
            elif t == "x":
                express = True
            elif t == "!":
                start_stressed = 1
            elif t == "u":
                start_stressed = 0
            elif t == "m":
                mode = 0
            elif t == "M":
                mode = 1
            elif len(t) > 0:
                try:
                    type = t[0]
                    if type == "[":
                        ntole = eval("1.0*"+t[1:len(t)-1]) #trick to force float
                    elif type == "{":
                        lenfactor = eval("1.0*"+t[1:len(t)-1]) #trick to force float
                    elif type == "(":
                        stressed = eval("1.0*"+t[1:len(t)-1]) #trick to force float
                    elif type == "<":
                        delta_unstressed = eval("-1.0*"+t[1:len(t)-1]) #trick to force float
                    elif type == "@":
                        offset_x = eval("1.0*"+t[1:len(t)-1]) #trick to force float
                    elif type == "$":
                        time = eval("1.0*"+t[1:len(t)-1]) #trick to force float
                        left_injections = "( " + left_injections
                        l_guard = ") if x < " + str(time) + " else "
                        start_x = time
                        current_x = time
                        express = True
                except SyntaxError:
                    pass
            if express == False:
                l_expression = ""
            else:
                start_x = current_x
                l_expression += l_guard
            lhs, rhs = tokenwise(toks[1:],stressed,delta_unstressed,\
                                            length, start_stressed, mode,\
                                            current_x,lenfactor,start_x,\
                                            offset_x,ntole,\
                                            left_injections)
            return lhs, l_expression + rhs
    lhs, rhs = tokenwise( tokens )
    return "lambda x: (" + lhs + rhs + ")"



def genPotential(s, max_time, left_side):
    """genPotential(s)    generate a potential lambda expression string from s
    
    Token   Meaning
    R       "Rest!"  (same as r.)
    !       "hit"    (force a hit by adding +1 to constant, use for hits on 1)
    r       "rest"   (remove a hit by adding -1 to constant, use for rests)
    W       "whole"  (set slope to 1/4 and lenfactor/slope to length & express)
    H       "half"   (set slope to 1/2 and lenfactor/slope to length & express)
    Q       "quarter"(set slope to 1 and lenfactor/slope to length & express)
    E       "eighth" (set slope to 2 and lenfactor/slope to length & express)
    S       "16th"   (set slope to 4 and lenfactor/slope to length & express)
    T       "32nd"   (set slope to 8 and lenfactor/slope to length & express)
    [###]   "n-tole" (set ntole to ###, slope in the above is always multiplied
                      with the ntole factor. ### may be 0.666 or 3/2 etc.)
    .       "another"(add another lenfactor/slope to the length)
    ,       "again"  (same as .)
    {###}   "factor" (set lenfactor to the value of ###)
    (###)   "add p." (add the value of ### to constant)
    <###>   "add l." (add the value of ### to the length)
    @###@   "set p." (set the potential at the current point to the value of ###
                      & express)
    $###$   "split"  (the right part starts at time ###, always & express)
    """
    tokens = extractTokens(s)
    slope = 0.0
    lenfactor = 1.0
    length = 0.0
    ntole = 1.0
    constant = 0.0
    left_injections = ""
    riff_start_time = 0.0
    def tokenwise(toks,slope=slope,lenfactor=lenfactor,length=length,\
                  ntole=ntole,constant=constant,\
                  left_injections=left_injections, up_to_here = "",
                  riff_start_time=riff_start_time):
        if length < riff_start_time:
            riff_start_time = length
        if toks==[]:
            return left_injections, \
                    "(float("+str(slope) + ")*x + float("+str(constant)+"))", \
                    riff_start_time
        else:
            t = toks[0]
            l_expression = "(float("+str(slope) +\
                           ")*x + float("+str(constant)+"))"
            l_guard =  " if x <= " + str(length) + " else "
            express = False
            if t == '.':
                length += lenfactor/slope
            elif t == ",":
                length += lenfactor/slope
                express = True
            elif t == "T":
                express = True
                constant = (slope*length + constant) - 8.0*ntole*length
                slope = 8.0*ntole
                length += lenfactor/slope
            elif t == "S":
                express = True
                constant = (slope*length + constant) - 4.0*ntole*length
                slope = 4.0*ntole
                length += lenfactor/slope
            elif t == "E":
                express = True
                constant = (slope*length + constant) - 2.0*ntole*length
                slope = 2.0*ntole
                length += lenfactor/slope
            elif t == "Q":
                express = True
                constant = (slope*length + constant) - 1.0*ntole*length
                slope = 1.0*ntole
                length += lenfactor/slope
            elif t == "H":
                express = True
                constant = (slope*length + constant) - 0.5*ntole*length
                slope = 0.5*ntole
                length += lenfactor/slope
            elif t == "W":
                express = True
                constant = (slope*length + constant) - 0.25*ntole*length
                slope = 0.25*ntole
                length += lenfactor/slope
            elif t == "r":
                constant -= 1.0
            elif t == "R":
                constant -= 1.0
                express = True
                length += lenfactor/slope
            elif t == "!":
                constant += 1.0
            elif t == "x":
                express = True
            elif len(t) > 0:
                try:
                    type = t[0]
                    if type == "[":
                        ntole = eval("1.0*"+t[1:len(t)-1]) #trick to force float
                    elif type == "{":
                        lenfactor = eval("1.0*"+t[1:len(t)-1]) #trick to force float
                    elif type == "(":
                        constant += eval("1.0*"+t[1:len(t)-1]) #trick to force float
                    elif type == "<":
                        length += eval("1.0*"+t[1:len(t)-1]) #trick to force float
                    elif type == "@":
                        express = True
                        pot = eval("1.0*"+t[1:len(t)-1]) #trick to force float
                        constant = pot - (slope*length)
                    elif type == "$":
                        time = eval("1.0*"+t[1:len(t)-1]) #trick to force float
                        left_injections = "( " + left_injections
                        l_guard = ") if x < " + str(time) + " else "
                        fval = eval("lambda x: " + up_to_here + l_expression)(time)
                        constant = fval - (time * slope)
                        length = time
                        express = True
                except SyntaxError:
                    pass
            if not express:
                l_expression = ""
            else:
                l_expression += l_guard
            lhs,rhs,riff_start_time = tokenwise(toks[1:], slope,lenfactor,length,\
                                   ntole,constant,left_injections,\
                                   up_to_here + l_expression)
            return lhs, l_expression + rhs, riff_start_time
    lhs, rhs, riff_start_time = tokenwise(tokens)
    inner_fun = "lambda x: ((" + lhs + rhs + ")" + max_time + ")" + left_side
    return inner_fun
#    return "lambda t: (" + inner_fun + ")(t) if t >= " + repr(riff_start_time) + \
#           " else ( " + "("+ inner_fun+")("+repr(riff_start_time)+")*8.0*(t-(" +\
#           repr(riff_start_time-0.125) + ")) if t >= " + repr(riff_start_time-0.125)+\
#           " else 0.0 )"




def genChanges(s1,s2,s3,s4):
    """genChanges(s1,s2,s3,s4)   generate a instrument change list string where
    s1 is a meta data string for left hand, s2 for right hand, s3 for left foot
    and s4 for right foot
    
    
    Token   Meaning
    W       "whole"  (set length to 1/4 & tick)
    H       "half"   (set length to 1/2 & tick)
    Q       "quarter"(set length to 1 & tick)
    E       "eighth" (set length to 2 & tick)
    S       "16th"   (set length to 4 & tick)
    T       "32nd"   (set length to 8 & tick)
    [###]   "n-tole" (set ntole to ###, slope in the above is always multiplied
                      with the ntole factor. ### may be 0.666 or 3/2 etc.)
    .       "tick"   (tick one current length*lenfactor)
    ,       "tick"   (tick one current length*lenfactor)
    $###$   "split"  (set start_time to ###)
    {###}   "factor" (set lenfactor to the value of ###)
    <###>   "add l." (set amount of ### to start position)
    @###@   "delta t"(set the delta_t value for the instrument change earliness)
    """
    g = DfGlobal()
    lh = g["setup.left hand"]
    rh = g["setup.right hand"]
    lf = g["setup.left foot"]
    rf = g["setup.right foot"]
    delta_t = 1.0/64.0
    start_time = 0.0
    length = 1.0
    lenfactor = 1.0
    ntole = 1.0
    chgs = {}
    def processTokens( toks, instruments, changes=chgs, start_time=start_time, \
                      delta_t=delta_t,length=length, lenfactor=lenfactor,\
                      ntole=ntole):
        if toks == []:
            return changes
        t = toks[0]
        if t == '.' or t== ',' or t=='R':
            start_time += length * lenfactor
        elif t == 'W':
            length = 4.0/ntole
            start_time += length * lenfactor
        elif t == 'H':
            length = 2.0/ntole
            start_time += length * lenfactor
        elif t == 'Q':
            length = 1.0/ntole
            start_time += length * lenfactor
        elif t == 'E':
            length = 1.0/(2.0*ntole)
            start_time += length * lenfactor
        elif t == 'S':
            length = 1.0/(4.0*ntole)
            start_time += length * lenfactor
        elif t == 'T':
            length = 1.0/(8.0*ntole)
            start_time += length * lenfactor
        elif len(t) > 0:
            try:
                type = t[0]
                if type == "[":
                    ntole = eval("1.0*"+t[1:len(t)-1]) #trick to force float
                elif type == "{":
                    lenfactor = eval("1.0*"+t[1:len(t)-1]) #trick to force float
                elif type == "@":
                    delta_t = eval("1.0*"+t[1:len(t)-1]) #trick to force float
                elif type == "<":
                    start_time += eval("1.0*"+t[1:len(t)-1]) #trick to force float
                elif type == "$":
                    start_time = eval("1.0*"+t[1:len(t)-1]) #trick to force float
            except SyntaxError:
                pass
        if t in instruments:
            changes[start_time - delta_t] = instruments[t]
        return processTokens(toks[1:],instruments,changes, start_time, delta_t,\
                             length,lenfactor, ntole)
    delta_t = 1.0/64.0
    start_time = 0.0
    length = 1.0
    lenfactor = 1.0
    ntole = 1.0
    chgs = {}
    c1 = processTokens(extractTokens(s1),lh,chgs, start_time, delta_t,\
                             length,lenfactor, ntole)
    delta_t = 1.0/64.0
    start_time = 0.0
    length = 1.0
    lenfactor = 1.0
    ntole = 1.0
    chgs = {}
    c2 = processTokens(extractTokens(s2),rh,chgs, start_time, delta_t,\
                             length,lenfactor, ntole)
    delta_t = 1.0/64.0
    start_time = 0.0
    length = 1.0
    lenfactor = 1.0
    ntole = 1.0
    chgs = {}
    c3 = processTokens(extractTokens(s3),lf,chgs, start_time, delta_t,\
                             length,lenfactor, ntole)
    delta_t = 1.0/64.0
    start_time = 0.0
    length = 1.0
    lenfactor = 1.0
    ntole = 1.0
    chgs = {}
    c4 = processTokens(extractTokens(s4),rf,chgs, start_time, delta_t,\
                             length,lenfactor, ntole)
    commands = {}
    for k in c1:
        if k in commands:
            commands[k]["left hand"] = c1[k]
        else:
            commands[k] = {"left hand": c1[k]}
    for k in c2:
        if k in commands:
            commands[k]["right hand"] = c2[k]
        else:
            commands[k] = {"right hand": c2[k]}
    for k in c3:
        if k in commands:
            commands[k]["left foot"] = c3[k]
        else:
            commands[k] = {"left foot": c3[k]}
    for k in c4:
        if k in commands:
            commands[k]["right foot"] = c4[k]
        else:
            commands[k] = {"right foot": c4[k]}
    return commands


def splitConceptString(s):
    """This functions splits the concept string s into its parts"""
    # first, we split at each : the whole string
    parts = s.split(':')
    # next we need to collate the genom information parts
    leftHand = ''
    rightHand = ''
    leftFoot = ''
    rightFoot = ''
    leftHandI = ''
    rightHandI = ''
    leftFootI = ''
    rightFootI = ''
    leftHandMeta = ''
    rightHandMeta = ''
    leftFootMeta = ''
    rightFootMeta = ''
    controlData = ''
    for pt in parts:
        if len(pt)>=1:
            if pt[0] == 'l':
                leftHand += pt[1:]
            elif pt[0] == 'L':
                leftHandMeta += pt[1:]
            elif pt[0] == 'r':
                rightHand += pt[1:]
            elif pt[0] == 'R':
                rightHandMeta += pt[1:]
            elif pt[0] == 'a':
                leftFoot += pt[1:]
            elif pt[0] == 'A':
                leftFootMeta += pt[1:]
            elif pt[0] == 'b':
                rightFoot += pt[1:]
            elif pt[0] == 'B':
                rightFootMeta += pt[1:]
            elif pt[0] == 'C':
                controlData += pt[1:]
            elif pt[0] == "'":
                if len(pt)>=2:
                    if pt[1] == 'L':
                        leftHandI += pt[2:]
                    elif pt[1] == 'R':
                        rightHandI += pt[2:]
                    elif pt[1] == 'A':
                        leftFootI += pt[2:]
                    elif pt[1] == 'B':
                        rightFootI += pt[2:]
                    else:
                        controlData += pt
                else:
                    controlData += pt
            else:
                controlData += pt
    return {'l':leftHand, 'L': leftHandMeta, 'r':rightHand, 'R':rightHandMeta,\
           'a':leftFoot, 'A':leftFootMeta, 'b':rightFoot, 'B':rightFootMeta,\
           "'L": leftHandI, "'R": rightHandI, "'A":leftFootI, "'B":rightFootI,\
           'C': controlData}

def genConcept(s):
    """This function converts a genom string to a Concept() object
    
    Where s is a string that is partitioned into several section by : signs
    
    The first character of a section determines what it does describe:
    l   left hand potential
    L   left hand meta data (strength & instrument changes)
    'L  left hand instrument data (instrument changes)
    r   right hand potential
    R   right hand meta data
    'R  right hand instrument data (instrument changes)
    a   left foot potential
    A   left foot meta data
    'A  left foot instrument data (instrument changes)
    b   right foot potential
    B   right foot meta data
    'B  right foot instrument data (instrument changes)
    
    If the first character is none of these, the section will be regarded as 
    control data. (For example, use C for control)
    
    All sections are added to a single string for each data portion and then 
    potential strings are evaluated into lambda expression strings by using 
    genPotential, meta data strings are evaluated into lambda expressions and
    change instruments by genStrength and genChanges respectively. The control
    string is evaluated in genConcept and controls several global parameters.
    
    Control strings:
    
    (####)    set length of riff
    [####]    push bar length
    {####}    set pre-run time
    <####>    set current time mark
    $####$    set current string
    @####@    set bpm at riff-start to ####
    l,r,a,b   set respective max_time strings to current string 
              (@R@ will be replaced by the riffs length)
    L,R,A,B   set resprective left_side strings to current string
    !         set current string to be executed at current time mark
              (@@BPS@@ is replaced by DfGlobal()['mind'].c_beatspersecond)
    x         set current string to be executed at start of riff
    """
    # first, we split at each : the whole string
    parts = s.split(':')
    # next we need to collate the genom information parts
    leftHand = ''
    rightHand = ''
    leftFoot = ''
    rightFoot = ''
    leftHandI = ''
    rightHandI = ''
    leftFootI = ''
    rightFootI = ''
    leftHandMeta = ''
    rightHandMeta = ''
    leftFootMeta = ''
    rightFootMeta = ''
    controlData = ''
    for pt in parts:
        if len(pt)>=1:
            if pt[0] == 'l':
                leftHand += pt[1:]
            elif pt[0] == 'L':
                leftHandMeta += pt[1:]
            elif pt[0] == 'r':
                rightHand += pt[1:]
            elif pt[0] == 'R':
                rightHandMeta += pt[1:]
            elif pt[0] == 'a':
                leftFoot += pt[1:]
            elif pt[0] == 'A':
                leftFootMeta += pt[1:]
            elif pt[0] == 'b':
                rightFoot += pt[1:]
            elif pt[0] == 'B':
                rightFootMeta += pt[1:]
            elif pt[0] == 'C':
                controlData += pt[1:]
            elif pt[0] == "'":
                if len(pt)>=2:
                    if pt[1] == 'L':
                        leftHandI += pt[2:]
                    elif pt[1] == 'R':
                        rightHandI += pt[2:]
                    elif pt[1] == 'A':
                        leftFootI += pt[2:]
                    elif pt[1] == 'B':
                        rightFootI += pt[2:]
                    else:
                        controlData += pt
                else:
                    controlData += pt
            else:
                controlData += pt
    tokens = extractTokens(controlData)
    max_time1 = " if x < @R@-1.0/16.0 else 0.0 "
    left_side1 = " if x >= 0.0 else 0.0 "
    max_time2 = " if x < @R@-1.0/16.0 else 0.0 "
    left_side2 = " if x >= 0.0 else 0.0 "
    max_time3 = " if x < @R@-1.0/16.0 else 0.0 "
    left_side3 = " if x >= 0.0 else 0.0 "
    max_time4 = " if x < @R@-1.0/16.0 else 0.0 "
    left_side4 = " if x >= 0.0 else 0.0 "
    current_string = ""
    current_time = 0.0
    timed_commands = {}
    bar_lens = []
    riff_len = 16.0
    pre_run_time = 1.0/8.0
    riff_command = None
    set_bps = None
    for t in tokens:
        if t == "l":
            max_time1 = current_string
        elif t == "r":
            max_time2 = current_string
        elif t == "a":
            max_time3 = current_string
        elif t == "b":
            max_time4 = current_string
        elif t == "L":
            left_side1 = current_string
        elif t == "R":
            left_side1 = current_string
        elif t == "A":
            left_side1 = current_string
        elif t == "B":
            left_side1 = current_string
        elif t == "!":
            cmd = current_string.replace("@@BPS@@","DfGlobal()['mind'].c_beatspersecond")
            timed_commands[current_time] = cmd
        elif t == "x":
            cmd = current_string.replace("@@BPS@@","DfGlobal()['mind'].c_beatspersecond")
            riff_command = cmd
        elif len(t) > 1:
            try:
                if t[0] == "$":
                    current_string = t[1:len(t)-1]
                elif t[0] == "(":
                    riff_len = eval("1.0*"+t[1:len(t)-1]) #trick to force float
                elif t[0] == "[":
                    bar_lens += [eval("1.0*"+t[1:len(t)-1])] #trick to force float
                elif t[0] == "{":
                    pre_run_time = eval("1.0*"+t[1:len(t)-1]) #trick to force float
                elif t[0] == "<":
                    current_time = eval("1.0*"+t[1:len(t)-1]) #trick to force float
                elif t[0] == "@":
                    set_bps = eval("1.0*"+t[1:len(t)-1])/60.0 #trick to force float
            except SyntaxError:
                pass
            
    if bar_lens == []:
        bar_lens = [riff_len/4.0]
    max_time1 = max_time1.replace("@R@",repr(riff_len))
    max_time2 = max_time2.replace("@R@",repr(riff_len))
    max_time3 = max_time3.replace("@R@",repr(riff_len))
    max_time4 = max_time4.replace("@R@",repr(riff_len))

    if set_bps:
        text = repr(str( int(set_bps*60.0)) + " bpm, " +   str(riff_len) + " beats = " + str(bar_lens))
    else:
        text = repr(str(riff_len) + " beats = " + str(bar_lens))
    if s == "":
        text = "''"
    

    concept = Concept({'left hand':genPotential(leftHand, max_time1, left_side1),\
                       'right hand':genPotential(rightHand, max_time2, left_side2),\
                       'left foot':genPotential(leftFoot, max_time3, left_side3),\
                       'right foot':genPotential(rightFoot, max_time4, left_side4)},\
                      {'left hand':genStrength(leftHandMeta),\
                       'right hand':genStrength(rightHandMeta),\
                       'left foot':genStrength(leftFootMeta),\
                       'right foot':genStrength(rightFootMeta)},\
                       change_instruments=genChanges(leftHandI,rightHandI,\
                                                     leftFootI,rightFootI),\
                                riff_length = riff_len, bar_lengths = bar_lens,\
                                riff_command = riff_command, timed_commands = \
                                timed_commands, pre_run_time=pre_run_time,\
                      set_bps=set_bps, text_vars={"text1":text}, represent=False)


        
    concept.representation = "genConcept("+repr(s)+")"
    return concept

def addConceptToPool(concept):
    """Add new concept to concept pool."""
    pool = DfGlobal()["concept.pool"]
    pool[repr(concept)] = concept

def evalConcept(representation):
    """evaluate concept expression, use cached concept if possible"""
    pool = DfGlobal()["concept.pool"]
    if representation in pool:
        return pool[representation]
    else:
        concept = eval(representation)
        addConceptToPool(concept)
        return concept
        
def evalGenConcept(genom):
    """evaluate concept genom expression, use cached concept if possible"""
    gene_pool = DfGlobal()["gene.pool"]
    if genom in gene_pool:
        gene_pool[genom] += 1
    else:
        gene_pool[genom] = 1
    return evalConcept("genConcept("+repr(genom)+")")
        
def processSketchList(data):
    sketch_pool = DfGlobal()["sketch.pool"]
    if data in sketch_pool:
        sketch_pool[data] += 1
    else:
        sketch_pool[data] = 1
    parts = data.split("\n\n\n")
    l = []
    for ptws in parts:
        pt = ptws.strip()
        repeat_factor = 1
        if pt.startswith("(x"):
            rbracket = pt.find(')')
            if rbracket == 0:
                rbracket = len(pt)
            repeat_factor = eval(pt[2:rbracket])
            pt = pt[rbracket+1:]
        l += [evalGenConcept(pt)]*repeat_factor
    return l

def concatConceptsL(c, max_len=None):
    main_loop = DfGlobal()["main_input_loop"]
    
    if not c:
        return genConcept("")
    if len(c) < 2:
        return copy.deepcopy(c[0])

    riff_length = sum(map(lambda x: x.riff_length, c))
    if max_len:
        if riff_length > max_len:
            riff_length = max_len


    head = c.pop(0)
    tail = c

    main_loop()
    

    change_instruments = head.change_instruments.copy()

    start_offset = head.riff_length

    starts = [start_offset]

    for c2 in tail:
        for t in c2.change_instruments:
            change_instruments[t + start_offset] = c2.change_instruments[t]
        start_offset += c2.riff_length
        starts.append(start_offset)

    main_loop()        

    potential_strings = {}

    limbs = set(head.potential_strings.keys())
    for c2 in tail:
        limbs |= set(c2.potential_strings.keys())

    for limb in limbs:
        if limb in head.potential_strings:
            code1 = head.potential_strings[limb]
        else:
            code1 = "lambda x: 0.0"

        if limb in head.nbr_of_hits:
            offset = [head.nbr_of_hits[limb]]
        else:
            offset = [0.0]
            
        code2 = []
        for c2 in tail:
            if limb in c2.potential_strings:
                code2.append( c2.potential_strings[limb] )
            else:
                code2 = "lambda x: 0.0"
            if limb in c2.nbr_of_hits:
                offset.append(offset[-1] + c2.nbr_of_hits[limb])
            else:
                offset.append(offset[-1])

        #print limb,":", offset

        fn = "".join( ["lambda x, fn1=",code1] \
                      + [", fn"+str(i+2)+"="+code2[i] for i in range(len(code2))] \
                      + [":  fn1(x) if x < "] \
                      + [repr(starts[i])+" else fn"+str(i+2)+"(x-"+repr(starts[i])+") + "+repr(offset[i])\
                         + " if x < "  for i in range(len(code2))] \
                      + [ repr(riff_length- 1.0/16.0)," else 0.0 "] \
                      )
        #print limb,":",fn
        
        potential_strings[limb] = fn

    main_loop()        

    limbs = set(head.strength_strings.keys())
    for c2 in tail:
        limbs |= set(c2.strength_strings.keys())

    strength_strings = {}        

    for limb in limbs:
        if limb in head.strength_strings:
            code1 = head.strength_strings[limb]
        else:
            code1 = "lambda x: 0.0"

        if limb in head.nbr_of_hits:
            offset = [head.nbr_of_hits[limb]]
        else:
            offset = [0.0]
            
        code2 = []
        for c2 in tail:
            if limb in c2.strength_strings:
                code2.append( c2.strength_strings[limb] )
            else:
                code2 = "lambda x: 0.0"
            if limb in c2.nbr_of_hits:
                offset.append(offset[-1] + c2.nbr_of_hits[limb])
            else:
                offset.append(offset[-1])

        fn = "".join( ["lambda x, fn1=",code1] \
                      + [", fn"+str(i+2)+"="+code2[i] for i in range(len(code2))] \
                      + [": fn1(x) if x < "] \
                      + [repr(starts[i])+" else fn"+str(i+2)+"(x-"+repr(starts[i])\
                         + ") if x < "  for i in range(len(code2))] \
                      + [repr(riff_length)," else 1.0 "] \
                      )
        
        strength_strings[limb] = fn

    main_loop()

    bar_lengths = head.bar_lengths[:]

    for c2 in tail:
        bar_lengths.extend(c2.bar_lengths)

    timed_commands = head.timed_commands.copy()

    start_offset = head.riff_length

    for c2 in tail:
        for t in c2.timed_commands:
            timed_commands[t+start_offset] = c2.timed_commands[t]
        start_offset += c2.riff_length

    main_loop()
    
    concept = Concept(potential_strings,\
                      strength_strings,\
                      change_instruments=change_instruments,\
                      riff_length = riff_length,\
                      bar_lengths = bar_lengths,\
                      riff_command = head.riff_command,\
                      timed_commands = timed_commands,\
                      pre_run_time=head.pre_run_time,\
                      set_bps=head.set_bps, text_vars={}, represent=False)

    main_loop()    

   
    return concept

            

    
    

def concatConcepts(c1,c2,max_len=None):
    riff_length = c1.riff_length + c2.riff_length
    if max_len:
        if riff_length > max_len:
            riff_length = max_len

    change_instruments = c1.change_instruments.copy()

    for t in c2.change_instruments:
        v = c2.change_instruments[t]
        change_instruments[t+c1.riff_length] = v

    potential_strings = {}
    
    for limb in set(c1.potential_strings.keys()) | set(c2.potential_strings.keys()):
        if limb in c1.potential_strings:
            code1 = c1.potential_strings[limb]
        else:
            code1 = "lambda x: 0.0"

        if limb in c1.nbr_of_hits:
            offset = c1.nbr_of_hits[limb]
        else:
            offset = 0.0
            
        if limb in c2.potential_strings:
            code2 = c2.potential_strings[limb]
        else:
            code2 = "lambda x: 0.0"

        fn = "lambda x, fn1=" + code1+", fn2="+code2 + \
             ": fn1(x) if x < " + repr(c1.riff_length) + " else fn2(x-" + \
             repr(c1.riff_length) + ") + " + \
             repr(offset) + " if x < " + repr(riff_length) + "-1.0/16.0 else 0.0"

        potential_strings[limb] = fn

    strength_strings = {}

    for limb in set(c1.strength_strings.keys()) | set(c2.strength_strings.keys()):
        if limb in c1.strength_strings:
            code1 = c1.strength_strings[limb]
        else:
            code1 = "lambda x: 0.0"
            
        if limb in c2.strength_strings:
            code2 = c2.strength_strings[limb]
        else:
            code2 = "lambda x: 0.0"

        fn = "lambda x, fn1=" + code1 +", fn2=" + code2 + \
             ": fn1(x) if x < " + repr(c1.riff_length) + " else fn2(x-" +\
             repr(c1.riff_length) + ")"

        strength_strings[limb] = fn

    bar_lengths = c1.bar_lengths + c2.bar_lengths

    timed_commands = c1.timed_commands.copy()

    for t in c2.timed_commands:
        v = c2.timed_commands[t]
        timed_commands[t+c1.riff_length] = v

    try:
        text = c1.text_vars["text1"]
    except KeyError:
        text = ""

    try:
        text += " "+ c2.text_vars["text1"]
    except KeyError:
        pass
    
    
    concept = Concept(potential_strings,\
                      strength_strings,\
                      change_instruments=change_instruments,\
                      riff_length = riff_length,\
                      bar_lengths = bar_lengths,\
                      riff_command = c1.riff_command,\
                      timed_commands = timed_commands,\
                      pre_run_time=c1.pre_run_time,\
                      set_bps=c1.set_bps, text_vars={"text1":text},\
                      represent=False)


        
    concept.representation = "concatConcepts("+repr(c1)+","+\
                             repr(c2)+","+repr(max_len)+")"
    return concept



if __name__ == '__main__':
    from df_limbs import *
    import code
    initialize_char_setup()
    DfGlobal()["DfInterpreter.console"] = code.InteractiveInterpreter()
    DfGlobal()["viz_level"] = 100
