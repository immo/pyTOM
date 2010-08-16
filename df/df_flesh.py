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
from math import *
import random

class Flesh(object):
    """class that handles all human-factor inaccuracies in drumming"""
    def __init__(self):
        self.accuracy = {}
        self.accuracy["left foot"] = 0.003
        self.accuracy["right foot"] = 0.002
        self.accuracy["left hand"] = 0.005
        self.accuracy["right hand"] = 0.004
        
        #fkt = 1.0 / 1.8
        fkt = 1.0 / 3.6
        
        self.potential_noise = {}
        self.potential_noise["left hand"] = 0.005 * fkt
        self.potential_noise["right hand"] = 0.004 * fkt
        self.potential_noise["left foot"] = 0.0035 * fkt
        self.potential_noise["right foot"] = 0.002 * fkt
        
        self.accumulator = 0.0
        self.threshold = 1.0/128.0
        
    def realStrength(self, limb, strength):
        """realStrength(self, limb, strength)   returns the real strength of a hit of limb with wanted strength"""
        return random.gauss(strength, self.accuracy[limb])
        
    def tick(self,dt):
        """tick(self,dt)   handles a time tick of length dt, by adding potential-noise to all limbs"""
        self.accumulator += dt
        if self.accumulator>= self.threshold:
            limbs = DfGlobal()["limbs"]
            for x in self.potential_noise:
                limbs[x].noise = random.gauss(0.0, self.potential_noise[x])
            self.accumulator -= self.threshold
        
