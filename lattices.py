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

def is_all(v,array):
    return all(map(lambda x: x==v, array))

def zip_with(fn, *arrays):
    return map(lambda x:fn(*x), zip(*arrays))

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
                    'feet': ['kd20punch','hh13ped',None]}

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

    def at(self,t,key):
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
        print(meet.times)
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
        

class Chordlet(object):
    g_tuning = [2,-3,-7,-12,-17,-22,-29]
    def __init__(self,chordstring):
        self.chordstring = chordstring
        pass
