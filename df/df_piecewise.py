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

class PiecewiseFun(object):
    def __init__(self, *fns):
        """
PiecewiseFun (*fns)          where fns is a tuple of boundaries and callable
                             objects in the form
                             ([lower], fn1, boundary, ..., fni, [upper])"""
        self.fns = fns
        lower_bound = float("-infinity")
        upper_bound = float("+infinity")
        start_i = 0
        inner_funs = []
        if len(fns) > 0:
            if not hasattr(fns[0],"__call__"):
                lower_bound = fns[0]
                start_i = 1
        boundaries = [lower_bound]                
        for i in range(start_i, len(fns)):
            if (i-start_i) % 2 == 0:
                if not hasattr(fns[i],"__call__"):
                    raise Exception(fns[i]," is not callable!")
                else:
                    inner_funs += [fns[i]]
            else:
                if boundaries[-1] >= fns[i]:
                    raise Exception(fns[i]," is not strictly bigger than ", boundaries[-1])
                else:
                    boundaries += [fns[i]]
        if (len(fns)-start_i) % 2 != 0:
            self.boundaries = boundaries + [upper_bound]
        else:
            self.boundaries = boundaries
        self.funs = inner_funs
        self.areas = {}

    def __eq__(self,r):
        return self.boundaries == r.boundaries and self.funs == r.funs

    def __hash__(self):
        return hash(repr(self))   

    def __call__(self,x):
        """
Return the value of the function call for the correct piecewise function.
Lower bounds are inclusive."""
        if x < self.boundaries[0] or x >= self.boundaries[-1]:
            return 0
        else:
            for i in range(0,len(self.boundaries)-1):
                if x < self.boundaries[i+1]:
                    return self.funs[i](x)

    def __getitem__(self,tpl):
        if type(tpl) != type(()):
            return self[0,tpl]
        else:
            lower,upper = tpl
            if lower > upper:
                return - self[upper,lower]
            else:
                complete_parts = [i for i in range(len(self.boundaries)-1) if lower <= self.boundaries[i] and self.boundaries[i+1] <= upper]
                summands = []
                for i in complete_parts:
                    if not i in self.areas:
                        self.areas[i] = self.funs[i][self.boundaries[i+1]] - self.funs[i][self.boundaries[i]]
                    summands += [self.areas[i]]
                same_section = True
                for i in range(len(self.boundaries)):
                    if lower <= self.boundaries[i] <= upper:
                        same_section = False
                        break
                if same_section:
                    if lower >= self.boundaries[0] and upper <= self.boundaries[-1]:
                        for i in range(0,len(self.boundaries)-1):
                            if lower < self.boundaries[i+1]:
                                summands += [ self.funs[i][upper] - self.funs[i][lower] ]
                                break
                else:
                    if lower > self.boundaries[0]:
                        for i in range(0,len(self.boundaries)-1):
                            if lower <= self.boundaries[i+1]:
                                summands += [ self.funs[i][self.boundaries[i+1]] - self.funs[i][lower] ]
                                break
                    if upper < self.boundaries[-1]:
                        for i in range(0,len(self.boundaries)-1):
                            if upper < self.boundaries[i+1]:
                                summands += [ self.funs[i][upper] - self.funs[i][self.boundaries[i]] ]
                                break
                return sum(summands)
        
    def __repr__(self):
        return "PiecewiseFun"+repr(self.fns)

