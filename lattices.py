#
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

# general helpers

def is_all(v,array):
    return all(map(lambda x: x==v, array))

def zip_with(fn, *arrays):
    return map(lambda x:fn(*x), zip(*arrays))

# local rhythms

class Rhythmlet(object):
    i_priorities = {"left_hand":['sn14wrock(ord,stxl)',\
                                 'sn14wrock(rms,stxl)',\
                                 'sn14wrock(prs,stxl)',\
                                 'sn14wrock(xtk)',\
                                 'tm12rock(ord,stxl)',\
                                 'tm12rock(rms,stxl)',\
                                 'tm10rock(ord,stxl)',\
                                 'tm10rock(rms,stxl)',\
                                 'tm14rock(ord,stxl)',\
                                 'tm14rock(rms,stx)',\
                                 'cy15crash(bel)',\
                                 'cy15crash(top)',\
                                 'cy15crash(ord)',\
                                 'cy15crash(rim)',\
                                 'cy15crash(grb)',\
                                 'cy18crash(bel)',\
                                 'cy18crash(top)',\
                                 'cy18crash(ord)',\
                                 'cy18crash(rim)',\
                                 'cy18crash(grb)',\
                                 'cy20ride(bel)',\
                                 'cy20ride(ord)',\
                                 'cy20ride(rim)',\
                                 'cy20ride(grb)',\
                                 'hh13(stxl,top)',\
                                 'hh13(ord,stxl)',\
                                 'hh13(grb)',\
                                 'cy8splash(bel)',\
                                 'cy8splash(ord)',\
                                 'cy8splash(grb)',\
                                 'cy19china(top)',\
                                 'cy19china(ord)',\
                                 'cy19china(grb)',\
                                 None],\
                    'right_hand': ['sn14wrock(ord,stxr)',\
                                   'sn14wrock(rms,stxr)',\
                                   'sn14wrock(prs,stxr)',\
                                   'sn14wrock(xtk)',\
                                   'tm12rock(ord,stxr)',\
                                   'tm12rock(rms,stxr)',\
                                   'tm10rock(ord,stxr)',\
                                   'tm10rock(rms,stxr)',\
                                   'tm14rock(ord,stxr)',\
                                   'tm14rock(rms,stx)',\
                                   'cy15crash(bel)',\
                                   'cy15crash(top)',\
                                   'cy15crash(ord)',\
                                   'cy15crash(rim)',\
                                   'cy15crash(grb)',\
                                   'cy18crash(bel)',\
                                   'cy18crash(top)',\
                                   'cy18crash(ord)',\
                                   'cy18crash(rim)',\
                                   'cy18crash(grb)',\
                                   'cy20ride(bel)',\
                                   'cy20ride(ord)',\
                                   'cy20ride(rim)',\
                                   'cy20ride(grb)',\
                                   'hh13(stxr,top)',\
                                   'hh13(ord,stxr)',\
                                   'hh13(grb)',\
                                   'cy8splash(bel)',\
                                   'cy8splash(ord)',\
                                   'cy8splash(grb)',\
                                   'cy19china(top)',\
                                   'cy19china(ord)',\
                                   'cy19china(grb)',\
                                   None],\
                    'feet': ['kd20punch','hh13(ped)',None]}

    def __init__(self,*x):
        self.times = x
        d = self.__dict__
        for k in self.i_priorities:
            d[k] = [None] * len(x)

    def actual_hit_times(self):
        return set([self.times[i] for i in range(len(self.times))\
                if not is_all(None,[self.__dict__[k][i] \
                                    for k in self.i_priorities])])

    def get_at(self,t):
        i = self.times.index(t)
        return [self.__dict__[k][i] for k in self.i_priorities]

    def height_at(self,t):
        i = self.times.index(t)
        return [self.i_priorities[k].index(self.__dict__[k][i])\
                for k in self.i_priorities]

    def at(self,t,k):
        try:
            i = self.times.index(t)
            return self.__dict__[k][i]
        except:
            return None
        
    def at_h(self,t,k):
        try:
            i = self.times.index(t)
            return self.i_priorities[k].index(self.__dict__[k][i])
        except:
            return self.i_priorities[k].index(None)

    def sort(self):
        sorted_time = list(self.times)
        sorted_time.sort()
        for k in self.i_priorities:
            sorted = [self.at(sorted_time[i],k) \
                      for i in range(len(sorted_time))]
            self.__dict__[k] = sorted
        self.times = sorted_time

    def add_to_time_grid(self,*times):
        new_times = [t for t in times if not t in self.times]
        new_none = [None]*len(new_times)
        self.times = list(self.times) + new_times
        for k in self.i_priorities:
            self.__dict__[k] = list(self.__dict__[k]) + new_none

    def del_times(self,*times):
        new_times = [t for t in self.times if not t in times]
        for k in self.i_priorities:
            updated = [self.at(new_times[i],k) \
                      for i in range(len(new_times))]
            self.__dict__[k] = updated
        self.times = new_times

    def compactify_times(self):
        new_times = [t for t in self.times \
                     if any([self.at(t,k) for k in self.i_priorities])]
        for k in self.i_priorities:
            updated = [self.at(new_times[i],k) \
                      for i in range(len(new_times))]
            self.__dict__[k] = updated
        self.times = new_times
        

    def cmp(self,r):
        lt = self.actual_hit_times()
        rt = r.actual_hit_times()
        if (not (lt <= rt)) and (not (rt <= lt)):
            return "|"
        r_bigger = rt > lt
        l_bigger = lt > rt
        for t in (rt & lt):
            lv = self.height_at(t)
            rv = r.height_at(t)
            if any(zip_with(lambda x,y:x>y,lv,rv)):
                r_bigger = True
            if any(zip_with(lambda x,y:x>y,rv,lv)):
                l_bigger = True
            if l_bigger and r_bigger:
                break
            
        if (not r_bigger) and (not l_bigger):
            return "="
        elif r_bigger and (not l_bigger):
            return "<"
        elif l_bigger and (not r_bigger):
            return ">"
        else:
            return "|"

    def __ge__(self,r):
        return self.cmp(r) in [">","="]

    def __gt__(self,r):
        return self.cmp(r) == ">"

    def __le__(self,r):
        return self.cmp(r) in ["<","="]

    def __lt__(self,r):
        return self.cmp(r) == "<"

    def __eq__(self,r):
        return self.cmp(r) == "="

    def __and__(self,r):
        meet = Rhythmlet(*(set(self.times) & set(r.times)))
        for i in range(len(meet.times)):
            for k in self.i_priorities:
                x = max(self.at_h(meet.times[i],k),r.at_h(meet.times[i],k))
                meet.__dict__[k][i] = self.i_priorities[k][x]
        return meet

    def __or__(self,r):
        join = Rhythmlet(*(set(self.times) | set(r.times)))
        for i in range(len(join.times)):
            for k in self.i_priorities:
                x = min(self.at_h(join.times[i],k),r.at_h(join.times[i],k))
                join.__dict__[k][i] = self.i_priorities[k][x]
        return join

# local chords
        
def namepitch(pitch,sharp=1):
    """ name a pitch """
    names = {0:('c','c'), 1:('cis','des'), 2:('d','d'), 3:('dis','es'),\
             4:('e','e'), 5:('f','f'), 6:('fis','ges'), 7:('g','g'),\
             8:('gis','as'), 9:('a','a'), 10:('ais','bes'), 11:('b','b')}
    octave = pitch / 12
    if octave < -1:
        octave = ','*(-octave-1)
    elif octave > -1:
        octave = "'"*(octave+1)
    else:
        octave = ""
    if sharp:
        vpitch = names[pitch%12][0]
    else:
        vpitch = names[pitch%12][1]
    return vpitch+octave

def collapseempty(l):
    out = []
    last = l[0]
    if last == "":
        last = 1
    for x in l[1:]:
        if x == "":
            if type(last) == int :
                last += 1
                continue
            else:
                x = 1
        out.append(last)
        last = x
    out.append(last)
    return out            

def splitspace(s):
    if s and s[0] == " ":
        return collapseempty(s[1:].split(" "))
    else:
        return collapseempty(s.split(" "))

def processtabline(s,tuning):
    spacemap = {0:1,1:1,2:2,3:2,4:3,5:3,6:4,7:4,8:4,9:4,10:5,11:5,12:5,\
            13:6,14:6,15:6} # interpret indentation space count
    l = collapseempty(splitspace(s))
    chord = [None] * len(tuning)
    frets = [None] * len(tuning)
    style = ""
    index = 0
    if l and (type(l[0])==int): #initial spacing is different
        index = spacemap[l[0]] - 1
        l = l[1:]
    for x in l:
        if type(x) == int: #spacing
            try:
                index += spacemap[x]
            except KeyError:
                index += len(tuning)
        else: #fret-string
            while x: #process first string part
                c = x[0]
                x = x[1:]
                if c.isdigit(): #process fret-nbr
                    f = int(c)
                    if x and (x[0].isdigit()): #stick up to 24th fret
                        f2 = int(x[0])
                        if 10*f + f2 <= 24:
                            f = 10*f + f2
                            x = x[1:]
                    if index < len(tuning):
                        frets[index] = f
                        chord[index] = f + tuning[index]
                    index += spacemap[0]
                else: #process modifier and mute strings
                    if c in '.ls': #p.m., legato, squeal
                        style = c
                    index += spacemap[0]                                                
    return chord, frets, style

def makefretting(sortedchord, tuning): #TODO, dummy placeholder
    frets = [None] * len(tuning)
    index = 0
    for x in sortedchord:
        if index < len(tuning):
            while index < len(tuning) and (x-tuning[index]) > 24:
                index += 1
            frets[index] = x - tuning[index]
        index += 1
    return frets

class Chordlet(object):
    g_tuning = [2,-3,-7,-12,-17,-22,-29]
    g_tuning.reverse()
    s_priority = ['.','l',"",'s']

    def __init__(self,chordstring):
        self.chordstring = chordstring
        chordarray, self.frets, self.style = processtabline(chordstring, self.g_tuning)
        self.chord = [x for x in chordarray if not x == None]
        self.chord.sort()

    def cmp(self,r):
        if r == None:
            return "|"
        l_less = self.s_priority.index(self.style) <= self.s_priority.index(r.style)
        r_less = self.s_priority.index(self.style) >= self.s_priority.index(r.style)
        if len(self.chord) <= len(r.chord):
            d = len(r.chord) - len(self.chord)
            if any(zip_with(lambda x,y:x>y, self.chord, r.chord[d:])):
                l_less = False
        else:
            l_less = False
        if len(self.chord) >= len(r.chord):
            d = len(self.chord) - len(r.chord)
            if any(zip_with(lambda x,y:x>y, r.chord, self.chord[d:])):
                r_less = False
        else:
            r_less = False
        if l_less and r_less:
            return "="
        elif l_less:
            return "<"
        elif r_less:
            return ">"
        else:
            return "|"

    def __ge__(self,r):
        return self.cmp(r) in [">","="]

    def __gt__(self,r):
        return self.cmp(r) == ">"

    def __le__(self,r):
        return self.cmp(r) in ["<","="]

    def __lt__(self,r):
        return self.cmp(r) == "<"

    def __eq__(self,r):
        return self.cmp(r) == "="

    def __and__(self,r):
        style = self.s_priority[ min(self.s_priority.index(self.style),\
                                     self.s_priority.index(r.style)) ]
        c_len = min(len(self.chord), len(r.chord))
        chord = [min(self.chord[-i-1],r.chord[-i-1]) for i in range(c_len)]
        chord.sort()
        meet = Chordlet(style)
        meet.chord = chord
        meet.frets = makefretting(chord,self.g_tuning)
        return meet

    def __or__(self,r):
        style = self.s_priority[ max(self.s_priority.index(self.style),\
                                     self.s_priority.index(r.style)) ]
        c_len = min(len(self.chord), len(r.chord))
        if c_len > 0:
            chord = [max(self.chord[-i-1],r.chord[-i-1]) for i in range(c_len)] + \
                    self.chord[:-c_len] + r.chord[:-c_len]
        else:
            chord = self.chord + r.chord
        chord.sort()
        join = Chordlet(style)
        join.chord = chord
        join.frets = makefretting(chord,self.g_tuning)
        return join

# onset-hold-*let for chords

class Metalet(object):
    none_default = Chordlet("")
    
    def __init__(self,*x):
        self.times = x
        d = self.__dict__
        self.lets = [None] * len(x)
        
    def actual_hit_times(self):
        return set([self.times[i] for i in range(len(self.times))\
                if not self.lets[i] == None])

    def at(self,t):
        try:
            i = self.times.index(t)
            return self.lets[i]
        except:
            return None

    def hold_at(self,t):
        before = [x for x in self.times if x <= t and self.at(x)]
        if before:
            return self.at(max(before))
        else:
            return None

    def hold_cmp(self,t):
        x = self.hold_at(t)
        if x == None:
            return self.none_default
        else:
            return x
    
    def sort(self):
        sorted_time = list(self.times)
        sorted_time.sort()
        sorted = [self.at(sorted_time[i]) \
                    for i in range(len(sorted_time))]
        self.lets = sorted
        self.times = sorted_time

    def add_to_time_grid(self,*times):
        new_times = [t for t in times if not t in self.times]
        new_none = [None]*len(new_times)
        self.times = list(self.times) + new_times
        self.lets = list(self.lets) + new_none

    def del_times(self,*times):
        new_times = [t for t in self.times if not t in times]
        updated = [self.at(new_times[i]) \
                     for i in range(len(new_times))]
        self.lets = updated
        self.times = new_times

    def compactify_times(self):
        new_times = [t for t in self.times \
                     if self.at(t)]
        updated = [self.at(new_times[i]) \
                      for i in range(len(new_times))]
        self.lets = updated
        self.times = new_times

    def compactify(self):
        actual = list(self.actual_hit_times())
        actual.sort()
        del_t = []
        for t0,t1 in zip(actual[:-1],actual[1:]):
            if self.hold_cmp(t0) == self.hold_cmp(t1):
                del_t.append(t1)
        self.del_times(*del_t)
        self.compactify_times()

    def __ge__(self,r):
        return self.cmp(r) in [">","="]

    def __gt__(self,r):
        return self.cmp(r) == ">"

    def __le__(self,r):
        return self.cmp(r) in ["<","="]

    def __lt__(self,r):
        return self.cmp(r) == "<"

    def __eq__(self,r):
        return self.cmp(r) == "="

    def cmp(self,r):
        sample_t = set(self.actual_hit_times()) |\
                   set(r.actual_hit_times())
        l_not_less = False
        r_not_less = False
        for t in sample_t:
            l = self.hold_cmp(t)
            r = r.hold_cmp(t)
            if not l <= r:
                l_not_less = True
            if not r <= l:
                r_not_less = True
        if l_not_less and r_not_less:
            return "|"
        elif l_not_less:
            return ">"
        elif r_not_less:
            return "<"
        else:
            return "="

    def __and__(self,r):
        sample_t = list(set(self.actual_hit_times()) |\
                   set(r.actual_hit_times()))
        sample_t.sort()
        meet = Metalet(*sample_t)
        for i in range(len(sample_t)):
            meet.lets[i] = self.hold_cmp(sample_t[i]) &\
                           r.hold_cmp(sample_t[i])
        meet.compactify()
        return meet


    def __or__(self,r):
        sample_t = list(set(self.actual_hit_times()) |\
                   set(r.actual_hit_times()))
        sample_t.sort()
        join = Metalet(*sample_t)
        for i in range(len(sample_t)):
            join.lets[i] = self.hold_cmp(sample_t[i]) |\
                           r.hold_cmp(sample_t[i])
        join.compactify()
        return join
