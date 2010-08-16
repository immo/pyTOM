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

from math import *
from bisect import bisect

def get_linear_interpolation_fn(xy_map):
    """ returns a linear function that will have f(x) = xy_map[x]
    for each x in xy_map.keys() """
    if not xy_map:
        return lambda x: 0.0
    xs = xy_map.keys()
    xs.sort()
    low_fn = lambda x,y0=xy_map[xs[0]]:y0
    hi_fn = lambda x,y0=xy_map[xs[-1]]:y0
    fns = [low_fn]
    for index in range(1,len(xs)):
        xlo = xs[index-1]
        xhi = xs[index]
        ylo = xy_map[xlo]
        yhi = xy_map[xhi]
        alpha = float(yhi-ylo)/float(xhi-xlo)
        fn = lambda x,x0=xlo,a=alpha,y0=ylo:(x-x0)*a+y0
        fns.append(fn)
    fns.append(hi_fn)
    def interfn(x,fns=fns,xs=xs):
        idx = bisect(xs,x)
        return fns[idx](x)
    return interfn

def get_hit_point_map(fn,lo,hi,steps=20):
    """ returns a map that will contain all hit points
    from a given potential function between lo and hi"""
    if lo < hi:
        f = lambda x,fn=fn:floor(fn(x))
        ylo = f(lo)
        yhi = f(hi)
        xs = [lo,hi]
        ys = [ylo,yhi]
        for steps in range(steps):
            ixs = [(xs[i]+xs[i-1])/2.0 for i in range(1,len(xs))]
            iys = [f(x) for x in ixs]
            nxs = []
            nys = []
            for i in range(len(ixs)):
                nxs.append(xs[i])
                nxs.append(ixs[i])
                nys.append(ys[i])
                nys.append(iys[i])
            nxs.append(xs[-1])
            nys.append(ys[-1])
            count = 1
            y = nys[0]
            counts = [count]
            for i in range(1,len(nys)):
                if nys[i] != y:
                    count = 1
                    y = nys[i]
                else:
                    count += 1
                counts.append(count)
            counts.append(0)
            idx = [i for i in range(len(counts)-1) \
                   if counts[i] == 1 or counts[i+1] == 1]
            xs = [nxs[i] for i in idx]
            ys = [nys[i] for i in idx]
        xy = {xs[0]:ys[0]}
        for i in range(1,len(xs)):
            if ys[i] != ys[i-1]:
                xy[xs[i]] = ys[i]
        return xy
    else:
        return {}
