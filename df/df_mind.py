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
from df_concept import *
from df_database import *
from df_jam_session import *
from math import *
import random

class Mind(object):
    """class that coordinates what should be played and that keeps the time metrics"""
    def __init__(self):
        self.time = 0.0              # current time
        self.c_beatspersecond = 1.0  # current bpm-related value
        self.c_max_timewarp = 1.1875 # maximal time-warp
        self.c_min_timewarp = 1.0/self.c_max_timewarp
        self.c_l_max_timewarp = log(self.c_max_timewarp)
        self.c_l_min_timewarp = log(self.c_min_timewarp)
        self.c_timewarp = 1.0        # current time-warp
        self.c_timewarp_time = 0.0   # timewarp-slot timewarp
        self.c_timewarp_freq = 32.0  # time-warp event frequency
        self.c_timewarp_delta = 0.0  # current time-warp step delta
        self.warp_factor = 0.03      # adjust time-warp per length 
        self.c_timewarp_length = 1.0/self.c_timewarp_freq
        self.c_target_timewarp = 1.0 # target time-warp
        self.c_timewarp_next = 1.0   # timewarp factor for next step...
        self.c_l_target_timewarp = log(self.c_target_timewarp)
        self.c_microwarp = 0.01375   # micro time-warp
        self.c_timeunwarp = 0.0      # time-unwarping factor
        self.c_stepsize = 1.0/2048.0 # sampling time step length (in s)
        self.c_time = 0.0            # time (in s) of the end of the last 
                                     # sampling step
        self.tick = 2.0              # length of one tick (i.e. beat), used for
                                     # graphics only
        self.bar = 4.0               # length of one bar, used for graphics and
                                     # bar events
        self.length = 16.0           # length of one riff, used for graphics and
                                     # riff events
        self.concept = evalConcept('genConcept("")')
        self.next_concept = evalConcept('genConcept("")')
                                     # current "concept you have in mind" :),
                                     # this controls your "limbs"
        self.time_in_bar = 0.0       # = self.time% self.bar
        self.time_in_riff = 0.0      # = selftime%self.length
        self.bar_start = 0.0         # determines the start of the bar
        self.riff_start = 0.0        # determines the start of the riff
        self.bar_nr = 0              # keeps track of current riffs bar number
        self.overlap_start = 16.0-1.0/64.0
        self.determine_next = 0.95   # approx. 1 4th before end we determine
                                     # the next concept
        self.tick_start = 0          # independent tick measure...
        self.c_display_interval = 1.0/16.0 # update display each 16th second
        self.c_display_last = -100.0
        self.next_determined = False
        self.viz_level = DfGlobal()["viz_level"]
        self.show_arcs = self.viz_level >= 60
        self.show_potentials = self.viz_level >= 90
        self.show_tags = self.viz_level >= 5
        self.jam_mode = False
        self.jam_session = JamSession()
        send_line("speed-ctl-arc", "0")
        self.verbose = False
        self.bps_time_zero = 0.0
        self.c_beatspersecond_target = self.c_beatspersecond
        self.c_bps_target_cmp = lambda x,y=self.c_beatspersecond_target: x >= y
        self.c_bps_rate = 1.0

    def switchJamMode(self, mode=None):
        """switch between Jam mode and normal mode"""
        if mode==None:
            if self.jam_mode:
                self.jam_mode = False
                send_line("text-mode","list")
            else:
                self.jam_mode = True
                send_line("text-mode","JAM")
        else:
            if self.jam_mode != mode:
                self.switchJamMode()

    def set_beatspersecond(self,bps):
        """set the bps and handling routines to a given constant bps"""
        self.c_beatspersecond = bps
        self.beatspersecond = self.constant_beatspersecond

    def set_beatspersecond_constant_rate(self, start, end, within_secs):
        self.c_beatspersecond_target = end
        self.c_beatspersecond = start
        self.c_bps_rate = (end - start) / within_secs
        if start < end:
            self.c_bps_target_cmp = lambda x,y=end: x >= y
        else:
            self.c_bps_target_cmp = lambda x,y=end: x <= y
        self.bps_time_zero = self.c_time
        self.beatspersecond = self.constant_rate_beatspersecond

    def set_beatspersecond_relative_rate(self, start, end, within_beats):
        self.c_beatspersecond_target = end
        self.c_beatspersecond = start
        self.c_bps_rate = (end - start) / within_beats
        if start < end:
            self.c_bps_target_cmp = lambda x,y=end: x >= y
        else:
            self.c_bps_target_cmp = lambda x,y=end: x <= y
        self.bps_time_zero = self.time
        self.beatspersecond = self.relative_rate_beatspersecond

        
    def determineNextConcept(self):
        """determine the next concept that is played after the current concept
        """
        self.next_determined = True
        send_line("text-next","NEXT")        
        if self.jam_mode:
            self.next_concept = self.jam_session.get_next_concept()
        else:
            l = DfGlobal()["concept.list"]
            if len(l) > 0:
                self.next_concept = l[0]
                DfGlobal()["concept.list"] = l[1:]
            else:
                self.next_concept = evalConcept('genConcept("")')

    def quick_change(self, rest=1.0,bps=1.0):
        self.concept = evalConcept('genConcept("")')
        self.length = rest
        self.next_determined= False
        self.c_beatspersecond = bps
        self.beatspersecond = self.constant_beatspersecond
        self.riff_start= self.time
        self.time_in_riff = 0.0
        self.overlap_start = 0.0
        
    def determineStrength(self, limb):
        """determineStrength(self, limb)   determine the current strength of a hit of limb"""
        return self.concept.determineStrength(limb, self.time_in_riff, self.bar)
        
    def constant_beatspersecond(self):
        """constant_beatspersecond(self)   constant bps version"""
        return self.c_beatspersecond * self.timewarp()

    def constant_rate_beatspersecond(self):
        time_gone = self.c_time - self.bps_time_zero
        current_bps = time_gone * self.c_bps_rate + self.c_beatspersecond
        if self.c_bps_target_cmp(current_bps): #reached end
            self.set_beatspersecond(self.c_beatspersecond_target)
        return current_bps * self.timewarp()

    def relative_rate_beatspersecond(self):
        """this one uses bar-time instead of sampler time (beats instead of secs)"""
        time_gone = self.time - self.bps_time_zero
        current_bps = time_gone * self.c_bps_rate + self.c_beatspersecond
        if self.c_bps_target_cmp(current_bps): #reached end
            self.set_beatspersecond(self.c_beatspersecond_target)
        return current_bps * self.timewarp()
        
    def beatspersecond(self):
        """beatspersecond(self)   give the current beatspersecond parameter"""
        return self.c_beatspersecond * self.timewarp()

    def timewarp(self):
        time_gone = self.c_time - self.c_timewarp_time
        return self.c_timewarp + time_gone * self.c_timewarp_delta
        
    def stepsize(self):
        """stepsize(self)   give the current stepsize parameter"""
        return self.c_stepsize
        
    def step(self):
        """step(self)   run a simple time-step"""
        s = self.stepsize()
        bps = self.beatspersecond()
        tick =  s*bps
        self.time+= tick
        
        tib = (self.time - self.bar_start) % self.bar
        tir = (self.time - self.riff_start) % self.length
        scan_at_zero = False
        
        if tir < self.time_in_riff:
            if self.verbose:
                print "mind->concept.riff @",self.time_in_riff, " - vs ", tir
                
            new_tir = self.time_in_riff - self.length
            self.concept = self.next_concept
            send_line_at(self.c_time,"text-next","none")
            if self.jam_mode:
                self.jam_session.next_concept_entered(self.c_time)
                
            self.concept.riff(tir, self.c_time)
            self.next_determined = False

            g_limbs =  DfGlobal()["limbs"]
            for limbname in g_limbs:
                limb = g_limbs[limbname]
                early_hit = floor(limb.potential['next'])
                if early_hit:
                    self.concept.riff_stroke[limbname] = early_hit
                limb.potential['next'] = 0.0
                
            self.overlap_start = self.length - self.concept.pre_run_time
            self.time_in_riff = new_tir
            if self.verbose:
                print "mind->concept.riff -=->",self.time_in_riff, " - vs ", tir
            
            scan_at_zero = True

            
        if tib < self.time_in_bar:
            self.concept.bar(tib)
            
        if  self.length - tir <= self.determine_next:
            if not self.next_determined:
                #print "determining at",tir,"of",self.length
                self.determineNextConcept()

        if scan_at_zero:
            self.concept.tick(self.time_in_riff,tick,0,'current')
        else:
            self.concept.tick(self.time_in_riff,tick,tir,'current')
            
        
        if tir > self.overlap_start:
            self.next_concept.tick(self.time_in_riff - self.length, tick, \
                              tir - self.length, 'next')
        
        self.time_in_bar = tib
        self.time_in_riff = tir
        self.c_time += s

        if self.c_time - self.c_timewarp_time >= self.c_timewarp_length:
            self.adjust_timewarp()

        if self.c_time - self.c_display_last >= self.c_display_interval:
            self.c_display_last = self.c_time
            self.show_arcs_and_potentials()
        
        flesh = DfGlobal()["flesh"]
        flesh.tick(tick)
        for limb in DfGlobal()["limbs"].values():
            limb.tick(self.c_time,self.time_in_bar)
        
    def set_target_timewarp(self, w):
        self.c_target_timewarp = w
        self.c_l_target_timewarp = log(w)
        warp_deg = ((self.c_l_target_timewarp - self.c_l_min_timewarp) \
                        / (self.c_l_min_timewarp - self.c_l_max_timewarp) \
                        + 0.5) * (-180.0)
        self.c_timeunwarp = 0
        send_line("speed-ctl-arc", str(warp_deg))

    def unwarp_faster(self, w):
        self.c_timeunwarp += w

    def adjust_timewarp(self):
        self.c_timewarp = self.c_timewarp_next

        adjust_warp = (1.0 - self.warp_factor +\
                       self.warp_factor*(((1.0 + self.c_microwarp*(random.uniform(-1.0,1.0)))\
                                         *self.c_target_timewarp)/self.c_timewarp_next)) 

        
        self.c_timewarp_next *= adjust_warp

        if self.c_timewarp_next > self.c_max_timewarp:
            self.c_timewarp_next = self.c_max_timewarp
        elif self.c_timewarp_next < self.c_min_timewarp:
            self.c_timewarp_next = self.c_min_timewarp

        if self.c_timeunwarp:
            self.c_target_timewarp = (1.0 - self.c_timeunwarp) * self.c_target_timewarp \
                                     + self.c_timeunwarp
            self.c_l_target_timewarp = log(self.c_target_timewarp)
            warp_deg = ((self.c_l_target_timewarp - self.c_l_min_timewarp) \
                            / (self.c_l_min_timewarp - self.c_l_max_timewarp) \
                            + 0.5) * (-180.0)
            send_line("speed-ctl-arc", str(warp_deg))
            if abs(self.c_l_target_timewarp) < 0.001:
                self.c_timeunwarp = 0

        self.c_timewarp_time = self.c_time
        self.c_timewarp_delta = (self.c_timewarp_next - self.c_timewarp) * self.c_timewarp_length

    def show_arcs_and_potentials(self):
        """ send current data to useriterface display """
        end = self.c_time
        if self.show_arcs:
            warp_deg = ((log(self.c_timewarp) - self.c_l_min_timewarp) \
                        / (self.c_l_min_timewarp - self.c_l_max_timewarp) \
                        + 0.5) * (-180.0)
            send_line_at(end, "speed-arc", str(warp_deg))
            bi_arc = ((self.time - self.bar_start) % self.bar)*(720.0/self.bar)
            if bi_arc >= 360.0:
                send_line_at(end,  "outer_arc",  str(bi_arc) + ", "+str(bi_arc))
            else:
                send_line_at(end,  "outer_arc",  str(360.0-bi_arc)+", "+str(360.0-bi_arc))
            bi_arc = ((self.time - self.tick_start) % self.tick)*(360.0/self.tick)
            send_line_at(end,  "mid_arc",  str(-bi_arc) + ", "+str(360.0-bi_arc))
            bi_arc = ((self.time - self.riff_start) % self.length)*(360.0/self.length)
            send_line_at(end, "inner_arc",  str(bi_arc)+ ", "+str(bi_arc))
        if self.show_potentials:
            for limb in DfGlobal()["limbs"].values():
                limb.update_potential_bar(end)
        
        
    def fill_output(self, begin,  end):
        """fill_output(self, begin,  end)   fill output from begin to end"""
        
        # calculate state

        while self.c_time <= end:
            self.step()

