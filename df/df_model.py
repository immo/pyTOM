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
from math import *
import random

class Instrument(object):
   """class that handles abstraction of a single instrument, provides strength levels and hit routines"""
   def __init__(self):
      self.sample_infos = {}  # contains available sample infos
      self.low_energy = 1.0   # contains lowest available energy
      self.high_energy = 2.0  # contains highest available energy
      self.choose_from = 4    # choose from the 4 best matches randomly
      self.volume = 1.0       # adjust volume of the instrument
      self.energy_coeff = 0.0 # coefficient for energy calculation
      self.group_id = -1      # ignore group ids
      self.correct_gain = 1.0 # correct gain values (if you have samples with different record gain levels)
                              # (in this case, the actual energy put out has to be multiplied with the square of this)
      self.kill_groups = {}   # group_id ---> delta_t, where delta_t is the time before the hit where the group is killed
      self.matrix = "1"       # default matrix
      self.side_kick = []     # instruments that are triggered as well


   def setup(self):
      """setup(self)    setup instrument"""
      energies = map(lambda x: self.sample_infos[x]['energy'], self.sample_infos)
      if energies == []:
         return
      self.low_energy = min(energies)
      self.high_energy = max(energies)
      self.energy_coeff = log(self.high_energy / self.low_energy)

   def preload_cache(self, low_energy = None, high_energy = None, time=None, stepSize=None):
      """preload_cache(self, low_energy = None, high_energy = None, time=None, stepSize=None)   do fake hits to fool backend cache into loading the instruments samples"""
      if high_energy == None:
         high_energy = self.high_energy
      if low_energy == None:
         low_energy = self.energy(0.5)
      if time == None:
         time = now()
      if stepSize == None:
         stepSize = 0.1
      count = 0
      for x in self.sample_infos:
         if low_energy <= self.sample_infos[x]['energy'] <= high_energy:
            play(self.sample_infos[x]['id'],time,0.0,nosid=True)
            time = time + stepSize
            count = count + 1
      return count


   def add(self,keys):
      """add(self,keys)    add samples with keys to the instrument object"""
      if type(keys)==type([]):
         g = DfGlobal()
         feat = g["smp_feat"]
         smps = None
         for k in keys:
            if not k in feat:
               return
            if (smps == None):
               smps = feat[k]
            else:
               smps = meetleft(smps,feat[k])
               if (smps==[]):
                  return
         self.sample_infos = joinleft(smps,self.sample_infos)
         self.setup()
      else:
         add(self,[keys])

   def randomize_strategy(self,scores):
      """randomize_strategy(self,scores)   return randomizated sample for instrument from scores structure"""
      best = {}
      for i in range(self.choose_from):
         if (len(scores)==0):
            break
         best_score = min(map(lambda x: x[0], scores))
         for (s,x) in scores:
            if (s == best_score):
               break
         best[i] = x
         scores = filter(lambda l: l[1] != x, scores)
      return best[random.randint(0,len(best)-1)]

   def energy(self,level):
      """energy(self,level)   return the corresponding energy for level, which should range from 0.0 to 1.0"""
      return self.low_energy * exp(self.energy_coeff * float(level))

   def level(self,energy): 
      """level(self,energy)   return the corresponding level for energy, which should range from 0.0 to (lots)"""
      return log(float(energy) / self.low_energy) / self.energy_coeff

   def hit(self,energy,time=None,vol=None):
      """hit(self,energy,time=None,vol=None)   initiate instrument hit with energy at time and with correcting volume vol"""
      factors = {}
      scores = []

      if vol is None:
         vol = self.volume

      if time==None:
         time = now()

      if len(self.side_kick) > 0:
         lvl= self.level(energy)
         for skck in self.side_kick:
            skck.hit(skck.energy(lvl),time,vol)

      if len(self.sample_infos) == 0:
         return

      for x in self.sample_infos:
         f = sqrt(float(energy)/float(self.sample_infos[x]['energy']))
         factors[x] = f
         scores += [(abs(log(f)),x)]

      x = self.randomize_strategy(scores)
      #print "smp=",x, "f=",factors[x]

      uid = play(self.sample_infos[x]['id'],time-self.sample_infos[x]['pre-roll'],float(vol)*factors[x]*self.correct_gain,\
           group=self.group_id,matrix=self.matrix,nosid=True)

      #print "sid=",sid

      for gid in self.kill_groups:
         #kill(gid, group=1, t=time-self.kill_groups[gid],bound=sid)
         ukill(gid, group=1, t=time-self.kill_groups[gid],bound=uid)

   def hit2(self,energy,time=None,vol=None):
         """hit2(self,energy,time=None,vol=None)   initiate instrument alternative hit with energy at time and with correcting volume vol (for TESTING)"""
         k = self.sample_infos.keys()
         x = k[random.randint(0,len(k)-1)]
         f = sqrt(float(energy)/float(self.sample_infos[x]['energy']))

         if vol is None:
            vol = self.volume

         if time==None:
            time = now()

         uid = play(self.sample_infos[x]['id'],time-self.sample_infos[x]['pre-roll'],float(vol)*f*self.correct_gain,\
              group=self.group_id,matrix=self.matrix, nosid=True)

         for gid in self.kill_groups:
            #kill(gid, group=1, t=time-self.kill_groups[gid],bound=sid)
            ukill(gid, group=1, t=time-self.kill_groups[gid],bound=uid)
