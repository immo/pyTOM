#
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

from df_global import *
from df_ontology import *
from df_backend import *
from df_data_channels import *
from df_presets import *
from math import *
import random

def initialize_limbs():
   """initialize limb data structure DfGlobal()["limbs"]"""
   g = DfGlobal()
   instrument_list = {}
   instrument_list["left hand"] = ['cy15crash(bel)','cy15crash(grb)',\
   'cy15crash(ord)','cy15crash(rim)','cy15crash(top)','cy18crash(bel)',\
   'cy18crash(grb)','cy18crash(ord)','cy18crash(rim)','cy18crash(top)',\
   'cy19china(ord)','cy19china(grb)','cy19china(top)','cy20ride(bel)',\
   'cy20ride(grb)','cy20ride(ord)','cy20ride(rim)','cy8splash(bel)', \
   'cy8splash(grb)', 'cy8splash(ord)', 'hh13(grb)','hh13(ord,stxl)', \
   'hh13(stxl,top)','sn14wrock(ord,stxl)','sn14wrock(prs,stxl)',\
   'sn14wrock(rms,stxl)','sn14wrock(xtk)','tm10rock(ord,stxl)',\
   'tm10rock(rms,stxl)','tm12rock(ord,stxl)','tm12rock(rms,stxl)',\
   'tm14rock(ord,stxl)','tm14rock(rms,stx)']
   instrument_list["right hand"] = ['cy15crash(bel)','cy15crash(grb)',\
   'cy15crash(ord)','cy15crash(rim)','cy15crash(top)','cy18crash(bel)',\
   'cy18crash(grb)','cy18crash(ord)','cy18crash(rim)','cy18crash(top)',\
   'cy19china(ord)','cy19china(grb)','cy19china(top)','cy20ride(bel)',\
   'cy20ride(grb)','cy20ride(ord)','cy20ride(rim)','cy8splash(bel)', \
   'cy8splash(grb)', 'cy8splash(ord)', 'hh13(grb)', 'hh13(ord,stxr)',\
   'hh13(stxr,top)','sn14wrock(ord,stxr)','sn14wrock(prs,stxr)',\
   'sn14wrock(rms,stxr)','sn14wrock(xtk)','tm10rock(ord,stxr)',\
   'tm10rock(rms,stxr)','tm12rock(ord,stxr)','tm12rock(rms,stxr)',\
   'tm14rock(ord,stxr)','tm14rock(rms,stx)']
   instrument_list["left foot"] = ['hh13(ped)','kd20punch(b)']
   instrument_list["right foot"] = ['kd20punch(a)','hh13(ped)']
   current_list = {}
   current_list["left foot"] = 'kd20punch(b)'
   current_list["right foot"] = 'kd20punch(a)'
   current_list["left hand"] = 'sn14wrock(ord,stxl)'
   current_list["right hand"] = 'hh13(ord,stxr)'
   potential_list = {}
   potential_list["left foot"] = 0.5
   potential_list["right foot"] = 0.0
   potential_list["left hand"] = 0.5
   potential_list["right hand"] = 0.0
   limb_list = {}
   for limb in instrument_list:
      l = Limb()
      l.name = limb
      l.potential_bar_channel = limb + ".potential"
      for x in instrument_list[limb]:
         if not x in g["instruments"]:
            print "(!!!) Error: Instrument '"+str(x)+"' not found!"
         else:
            l.instruments[x] = g["instruments"][x]
      l.current = current_list[limb]
      limb_list[limb] = l

   #limb_list['left foot'].verbose = True

   #limb_list['left foot'].set_strength_reduction(0.85, 0.75)
   #limb_list['right foot'].set_strength_reduction(0.85, 0.78)

   def lf_strength_red():
       print "lf-default-strength-reduction"
       limb_list['left foot'].set_strength_reduction(0.85, 0.45)
   add_preset_fn(lf_strength_red,"default-s.r.","left foot")

   def rf_strength_red():
       print "rf-default-strength-reduction"
       limb_list['right foot'].set_strength_reduction(0.85, 0.47)
   add_preset_fn(rf_strength_red,"default-s.r.","right foot")

   def lh_strength_red():
       print "lh-default-strength-reduction"
       limb_list['left hand'].set_strength_reduction(0.55, 2.0)
   add_preset_fn(lh_strength_red,"default-s.r.","left hand")

   def rh_strength_red():
       print "rh-default-strength-reduction"
       limb_list['right hand'].set_strength_reduction(0.55, 2.0)
   add_preset_fn(rh_strength_red,"default-s.r.","right hand")

   def lf_strength_red():
       print "lf-no-strength-reduction"
       limb_list['left foot'].set_strength_reduction(1.0, 0.45)
   add_preset_fn(lf_strength_red,"no-s.r.","left foot")

   def rf_strength_red():
       print "rf-no-strength-reduction"
       limb_list['right foot'].set_strength_reduction(1.0, 0.47)
   add_preset_fn(rf_strength_red,"no-s.r.","right foot")

   def lh_strength_red():
       print "lh-no-strength-reduction"
       limb_list['left hand'].set_strength_reduction(1.0, 2.0)
   add_preset_fn(lh_strength_red,"no-s.r.","left hand")

   def rh_strength_red():
       print "rh-no-strength-reduction"
       limb_list['right hand'].set_strength_reduction(1.0, 2.0)
   add_preset_fn(rh_strength_red,"no-s.r.","right hand")   

   def lf_strength_red():
       print "lf-weak-strength-reduction"
       limb_list['left foot'].set_strength_reduction(0.95, 0.45)
   add_preset_fn(lf_strength_red,"weak-s.r.","left foot")

   def rf_strength_red():
       print "rf-weak-strength-reduction"
       limb_list['right foot'].set_strength_reduction(0.95, 0.47)
   add_preset_fn(rf_strength_red,"weak-s.r.","right foot")

   def lh_strength_red():
       print "lh-weak-strength-reduction"
       limb_list['left hand'].set_strength_reduction(0.85, 2.0)
   add_preset_fn(lh_strength_red,"weak-s.r.","left hand")

   def rh_strength_red():
       print "rh-weak-strength-reduction"
       limb_list['right hand'].set_strength_reduction(0.85, 2.0)
   add_preset_fn(rh_strength_red,"weak-s.r.","right hand")


   def lf_strength_red():
       print "lf-middle-strength-reduction"
       limb_list['left foot'].set_strength_reduction(0.95, 0.45)
   add_preset_fn(lf_strength_red,"middle-s.r.","left foot")

   def rf_strength_red():
       print "rf-middle-strength-reduction"
       limb_list['right foot'].set_strength_reduction(0.95, 0.47)
   add_preset_fn(rf_strength_red,"middle-s.r.","right foot")

   def lh_strength_red():
       print "lh-middle-strength-reduction"
       limb_list['left hand'].set_strength_reduction(0.75, 2.0)
   add_preset_fn(lh_strength_red,"middle-s.r.","left hand")

   def rh_strength_red():
       print "rh-middle-strength-reduction"
       limb_list['right hand'].set_strength_reduction(0.75, 2.0)
   add_preset_fn(rh_strength_red,"middle-s.r.","right hand")


   for l in limb_list:
       call_preset_fn("default-s.r.",l)
   
   
   
   g["limbs"] = limb_list
   
   initialize_char_setup()

def initialize_char_setup():
   """initialize the instrument-character bindings for genChanges..."""
   g = DfGlobal()
   lf_setup = {'x':'kd20punch(b)', '~':'hh13(ped)', '^':'hh13(ped)', '*':'hh13(ped)'}
   rf_setup = {'x':'kd20punch(a)','~':'hh13(ped)', '^':'hh13(ped)', '*':'hh13(ped)'}
   lh_setup = {'C':'cy15crash(bel)','b':'cy15crash(grb)',\
   'c':'cy15crash(ord)','V':'cy15crash(rim)','v':'cy15crash(top)','Y':'cy18crash(bel)',\
   'B':'cy18crash(grb)','y':'cy18crash(ord)','X':'cy18crash(rim)','x':'cy18crash(top)',\
   'h':'cy19china(ord)','j':'cy19china(grb)','G':'cy19china(top)','R':'cy20ride(bel)',\
   't':'cy20ride(grb)','r':'cy20ride(ord)','z':'cy20ride(rim)','w':'cy8splash(bel)', \
   'd':'cy8splash(grb)', 's':'cy8splash(ord)', '~':'hh13(grb)','^':'hh13(ord,stxl)', \
   '*':'hh13(stxl,top)','x':'sn14wrock(ord,stxl)','p':'sn14wrock(prs,stxl)',\
   'X':'sn14wrock(rms,stxl)','g':'sn14wrock(xtk)','n':'tm10rock(ord,stxl)',\
   'N':'tm10rock(rms,stxl)','m':'tm12rock(ord,stxl)','M':'tm12rock(rms,stxl)',\
   'f':'tm14rock(ord,stxl)','F':'tm14rock(rms,stx)' }
   rh_setup = {'C':'cy15crash(bel)','b':'cy15crash(grb)',\
   'c':'cy15crash(ord)','V':'cy15crash(rim)','v':'cy15crash(top)','Y':'cy18crash(bel)',\
   'B':'cy18crash(grb)','y':'cy18crash(ord)','X':'cy18crash(rim)','x':'cy18crash(top)',\
   'h':'cy19china(ord)','j':'cy19china(grb)','G':'cy19china(top)','R':'cy20ride(bel)',\
   't':'cy20ride(grb)','r':'cy20ride(ord)','z':'cy20ride(rim)','w':'cy8splash(bel)', \
   'd':'cy8splash(grb)', 's':'cy8splash(ord)', '~':'hh13(grb)','^':'hh13(ord,stxr)', \
   '*':'hh13(stxr,top)','x':'sn14wrock(ord,stxr)','p':'sn14wrock(prs,stxr)',\
   'X':'sn14wrock(rms,stxr)','g':'sn14wrock(xtk)','n':'tm10rock(ord,stxr)',\
   'N':'tm10rock(rms,stxr)','m':'tm12rock(ord,stxr)','M':'tm12rock(rms,stxr)',\
   'f':'tm14rock(ord,stxr)','F':'tm14rock(rms,stxr)' }
   g["setup.left hand"] = lh_setup
   g["setup.right hand"] = rh_setup
   g["setup.left foot"] = lf_setup
   g["setup.right foot"] = rf_setup   
   left_foot_groups = {'kick':['kd20punch(b)'],'cymbal':['hh13(ped)']}
   right_foot_groups = {'kick':['kd20punch(a)'],'cymbal':['hh13(ped)']}
   left_hand_groups = {'bell':['cy20ride(bel)','cy15crash(bel)','cy18crash(bel)',\
                               'cy8splash(bel)'],\
                       'crash':['cy15crash(ord)','cy18crash(ord)','cy15crash(top)',\
                                'cy18crash(top)','cy15crash(rim)','cy18crash(rim)',\
                                'cy15crash(grb)','cy18crash(grb)'],\
                       'splash':['cy8splash(ord)','cy8splash(grb)'],\
                       'china':['cy19china(ord)','cy19china(top)','cy19china(grb)'],\
                       'ride':['cy20ride(ord)','cy20ride(bel)','cy20ride(rim)','cy20ride(grb)'],\
                       'hihat':['hh13(ord,stxl)','hh13(stxl,top)','hh13(grb)'],\
                       'hit':['sn14wrock(ord,stxl)','tm10rock(ord,stxl)',\
                              'tm12rock(ord,stxl)','tm14rock(ord,stxl)'],\
                       'ghost':['sn14wrock(xtk)'],\
                       'roll':['sn14wrock(prs,stxl)'],\
                       'rimshot':['sn14wrock(rms,stxl)','tm10rock(rms,stxl)',\
                                  'tm12rock(rms,stxl)','tm14rock(rms,stx)']}
   right_hand_groups = {'bell':['cy20ride(bel)','cy15crash(bel)','cy18crash(bel)',\
                               'cy8splash(bel)'],\
                        'crash':['cy15crash(ord)','cy18crash(ord)','cy15crash(top)',\
                                'cy18crash(top)','cy15crash(rim)','cy18crash(rim)',\
                                'cy15crash(grb)','cy18crash(grb)'],\
                       'splash':['cy8splash(ord)','cy8splash(grb)'],\
                       'china':['cy19china(ord)','cy19china(top)','cy19china(grb)'],\
                       'ride':['cy20ride(ord)','cy20ride(bel)','cy20ride(rim)','cy20ride(grb)'],\
                       'hihat':['hh13(ord,stxr)','hh13(stxr,top)','hh13(grb)'],
                       'hit':['sn14wrock(ord,stxr)','tm10rock(ord,stxr)',\
                              'tm12rock(ord,stxr)','tm14rock(ord,stxr)'],\
                       'ghost':['sn14wrock(xtk)'],\
                       'roll':['sn14wrock(prs,stxr)'],\
                       'rimshot':['sn14wrock(rms,stxr)','tm10rock(rms,stxr)',\
                                  'tm12rock(rms,stxr)','tm14rock(rms,stx)']}
   g["groups.left foot"] = left_foot_groups
   g["groups.right foot"] = right_foot_groups
   g["groups.left hand"] = left_hand_groups
   g["groups.right hand"] = right_hand_groups
   dual_limb = {'left hand':'right hand',
                'right hand':'left hand',
                'left foot':'right foot',
                'right foot':'left foot'}
   g["dual.limbs"] = dual_limb

   used_instruments = set()
   used_instruments = used_instruments.union(lh_setup.values())
   used_instruments = used_instruments.union(rh_setup.values())
   used_instruments = used_instruments.union(lf_setup.values())
   used_instruments = used_instruments.union(rf_setup.values())
   for x in left_foot_groups.values():
       used_instruments = used_instruments.union(x)
   for x in right_foot_groups.values():
       used_instruments = used_instruments.union(x)
   for x in left_hand_groups.values():
       used_instruments = used_instruments.union(x)
   for x in right_hand_groups.values():
       used_instruments = used_instruments.union(x)

   g["used.instruments"] = used_instruments

   
def char_setup2tex():
    """return tex code that can be inserted into a latex document that will produce a table with the current
    symbol-instrument-map for left/right hand/foot."""
    g = DfGlobal()
    lh =g["setup.left hand"]
    rh = g["setup.right hand"]
    lf = g["setup.left foot"]
    rf = g["setup.right foot"]
    tex = r"""\documentclass{scrartcl}
\begin{document}
\begin{tabular}{l|l|l|l|l}
    & \texttt{:'L} & \texttt{:'R} & \texttt{:'A} & \texttt{:'B} \\ \hline &&&& \\[-4mm]
    """
    newline = r"""\\ \hline &&&& \\[-4mm]
    """
    list_keys = {}
    for k in lh:
        list_keys[k] = "1"
    for k in rh:
        list_keys[k] = "1"
    for k in lf:
        list_keys[k] = "1"
    for k in rf:
        list_keys[k] = "1"
    keys = list_keys.keys()
    symlist = []
    for k in keys:
        if k in lh:
            lh1 = lh[k]
        else:
            lh1 = ""
        if k in lf:
            lf1 = lf[k]
        else:
            lf1 = ""
        if k in rh:
            rh1 = rh[k]
        else:
            rh1 = ""
        if k in rf:
            rf1 = rf[k]
        else:
            rf1 = ""
        symlist += [(lh1,rh1,lf1,rf1,k)]
    symlist.sort()
    for s in symlist:
        tex += r"""\texttt{""" + s[4] + "} & " + s[0] + " & " + s[1] + " & " + s[2] + "&" + s[3] + newline
    tex += r"""\end{tabular}
    \end{document}
    """
    return tex


class Limb(object):
    """class that controls each virtual limb you have"""
    def __init__(self):
        self.instruments = {} # List of instruments associated with limb
        self.current = ''     # Name of the instrument that the limb points to currently
        self.potential = {'current':0.0}    # Current hit potential sum
        self.noise = 0.0        # Current hit noise value
        self.stroke = 0.0       # Current stroke subsidient
        self.strength = 0.8    # Current strength of hits
        self.barrier = 1.0       # Barrier that will cause the limb to hit the 
                                 # drum, once potential > barrier
        self.rebound = 0.0187  # rebound hit time in seconds
        self.last_stroke = -100.0# last drum hit
        self.last_stroke_red = -100.0 # last drum hit regarding strength red.n
        self.name = None     # Name of the limb
        self.viz_level = DfGlobal()["viz_level"]
        self.indicate_hits = self.viz_level >= 85
        self.indicate_potential = self.viz_level >= 90
        self.indicator_cooldown_time = 0.15
        self.indicator_last_hit = 0
        self.show_dublettes = True
        self.potential_bar_channel = None # potential bar channel name
        self.latch_mark = self.barrier*0.99 # do not forget hits that occur too late before a rest
        self.is_latched = False
        self.valley_depth = 0.55
        self.peak_height = self.barrier
        self.verbose = False
        self.energy_reductor = lambda t:(1.0-exp(-2.0*t))*0.4+0.7
        self.showed_dublette = False


    def set_strength_reduction(self, minimal, release):
        self.energy_reductor = eval('lambda t:(1.0-exp('+repr(-4.0/release)+\
                                    '*t))*'+repr(1.0-minimal)+"+"+repr(minimal))
    
        
    def reset(self):
        """called after a hit was done, should reset the limb's potential"""
        self.stroke += self.barrier
        self.is_latched = False
        
    def getStrength(self): 
        """getStrength(self)    Strength callback, used to determine strength of a hit"""
        return self.strength * DfGlobal()["mind"].determineStrength(self.name)

    def update_potential_bar(self, beat_end):
        if self.indicate_potential:
            indicator = (sum(self.potential.values()) + self.noise - self.stroke) / self.barrier
            send_line_at(beat_end, self.potential_bar_channel, repr(indicator))
    
    def tick(self, beat_end, time_in_bar=None):
        """tick(self, beat_end, time_in_bar=None)   
        do all test done at each tick, i.e. whether the limb should hit or not
        beat_end gives the time that is used to generate drum hit events,
        time_in_bar is used for debug output only."""
        current_potential = sum(self.potential.values()) - self.stroke
        if (current_potential + self.noise >= self.barrier) or \
               (self.is_latched and \
                (self.barrier - current_potential >= self.valley_depth) and \
                (current_potential + self.noise + self.peak_height >= self.barrier)):
            if beat_end >= self.last_stroke + self.rebound:
                instrument = self.instruments[self.current]
                flesh = DfGlobal()["flesh"]
                reduction = self.energy_reductor(beat_end-self.last_stroke_red)
                strength = flesh.realStrength(self.name,self.getStrength())\
                           *reduction
                energy = instrument.energy(strength)
                instrument.hit(energy, time=beat_end)
                self.showed_dublette = False
                self.reset()
                self.last_stroke = beat_end
                self.last_stroke_red = beat_end
                if self.verbose:
                    print " HIT  ", self.name, " at ", time_in_bar,\
                          " (", beat_end,") with ", strength,\
                          "@",repr(self.potential), " :: ",\
                          self.barrier+self.stroke,\
                          " < ", current_potential + self.stroke
                    print "     REDUCTION  ", reduction
                if self.indicate_hits:
                    if beat_end - self.indicator_last_hit >= self.indicator_cooldown_time:
                        send_line_at(beat_end, self.name, "hit")
                        send_line_at(beat_end+0.03, self.name, "reset")
                        send_line_at(beat_end-0.02, self.name, "climax")
                        self.indicator_last_hit = beat_end
            else:
                if self.verbose or self.show_dublettes:
                    if not self.showed_dublette:
                        print " xxx  ", self.name, " at ", time_in_bar,\
                              "@",repr(self.potential)
                        self.showed_dublette = True
        elif (not self.is_latched) and current_potential >= self.latch_mark:
            if self.verbose:
                print " LATCH  ", self.name, " at ", time_in_bar, " (", current_potential, ")","@",repr(self.potential)
            self.is_latched = True
