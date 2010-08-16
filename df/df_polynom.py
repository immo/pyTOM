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



from math import *

class Polynom(object):
    def __init__(self,coefficients={}):
        """
Polynom(coefficients) -> Polynom    where coefficients is a dict mapping powers to their
                                    respective coefficients in the polynom"""
        if type(coefficients) == type({}):
            self.coefficients = coefficients
        elif type(coefficients) == Polynom:
            self.coefficients = coefficients.coefficients
        else:
            self.__init__({0: coefficients})          

    def __call__(self,x):
        """
evaluate the polynom at x"""
        summands = [self.coefficients[pwr] * (x**pwr) for pwr in self.coefficients]
        return sum(summands)

    def __getitem__(self, x):
        """
evaluate the antiderivative of the polynom at x"""
        summands = [self.coefficients[pwr] * (x**(pwr+1)) / float(pwr+1) for pwr in self.coefficients if pwr != -1]
        if -1 in self.coefficients:
            summands += [self.coefficients[pwr] * log(abs(x))]
        return sum(summands)
        
            
    def __repr__(self):
        return "Polynom(" + repr(self.coefficients) + ")"

    def __eq__(self, r):
        return self.coefficients == r.coefficients

    def __hash__(self):
        return hash(repr(self))
        
    def __pow__(self, i):
        if type(i) != int:
            if len(self.coefficients) == 0:
                return Polynom()
            elif len(self.coefficients) == 1:
                k = self.coefficients.keys()[0]
                return Polynom({k*i : self.coefficients[k]**i})
            elif (len(self.coefficients) == 2 and 0 in self.coefficients and self.coefficients[0] == 0):
                k = self.coefficients.keys()[0]
                if k == 0:
                    k = self.coefficients.keys()[1]
                return Polynom({k*i : self.coefficients[k]**i})
            else:
                raise Exception(type(i),' is not a valid type for doing power of a polynom')
        if i==0:
            return Polynom(1)
        if i<0:
            raise Exception(i,' is not a valid power to apply to a polynom')
        result = Polynom(1)
        for j in range(i):
            result = result * self
        return result
        
    def __add__(self, r):
        if type(r) == Polynom:
            coefficients = {}
            left_pwrs = Set(self.coefficients.keys())
            right_pwrs = Set(r.coefficients.keys())
            both_pwrs = left_pwrs & right_pwrs
            for pwr in both_pwrs:
                coefficients[pwr] = self.coefficients[pwr] + r.coefficients[pwr]
            for pwr in left_pwrs - both_pwrs:
                coefficients[pwr] = self.coefficients[pwr]
            for pwr in right_pwrs - both_pwrs:
                coefficients[pwr] = r.coefficients[pwr]
            return Polynom(coefficients)
        else:
            return self + Polynom(r)

    def shift(self, s):
        coefficients = {}
        for pwr in self.coefficients:
            coefficients[pwr + s] = self.coefficients[pwr]
        return Polynom(coefficients)

    def scale(self, s):
        coefficients = {}
        for pwr in self.coefficients:
            coefficients[pwr] = s * self.coefficients[pwr]
        return Polynom(coefficients)            

    def __mul__(self,r):
        if type(r) == Polynom:
            summands = [r.scale(self.coefficients[pwr]).shift(pwr) for pwr in self.coefficients]
            return Polynom(sum(summands))
        else:
            return self + Polynom(r)

    def __radd__(self, r):
        return Polynom(r) + self

    def __rmul__(self, r):
        return Polynom(r) * self
