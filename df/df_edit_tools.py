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

from df_codimugraph import *
from math import *
from df_localcomposition import *
from df_global import *
import copy

def addColoredArrows(domain, arrows):
    """ returns a graph with added colored arrows to the domain such that
    there is no (new) violation of the local composition compatibility rules.
    """
    
    new_dom = copy.deepcopy(domain)
    N = new_dom.vertices
    C = new_dom.color_set
    has_arrows = new_dom.colored_common_domains
    test_list = [(i,j,c) for i in range(N) for j in range(N) for c in C]
    for ar in test_list:
        if not ar in has_arrows:
            can_add = True
            for codom in arrows.values():
                if (not ar[2] in codom.colorMap) or \
                   (not ar[0] in codom.vertexMap) or \
                   (not ar[1] in codom.vertexMap):
                    continue
                if not (codom.vertexMap[ar[0]], codom.vertexMap[ar[1]],\
                        codom.colorMap[ar[2]]) in codom.codomain.colored_common_domains:
                    can_add = False
                    break
                
            if can_add:
                new_dom.edges.append((ar[0],ar[1]))
                new_dom.colors.append(ar[2])
    
    new_dom.recalculate_representation()
    return new_dom

def delColoredArrows(domain, arrows):
    """ returns a graph with added removed arrows to the domain such that
    there are no violations of the local composition compatibility rules left.
    """
    
    new_dom = copy.deepcopy(domain)
    
    keep_arrows = []
    
    ccD = new_dom.colored_common_domains
    for ar in ccD:
        current_maximum = len(ccD[ar])
        for codom in arrows.values():
            if (not ar[2] in codom.colorMap) or \
               (not ar[0] in codom.vertexMap) or \
               (not ar[1] in codom.vertexMap):
                continue
            key = (codom.vertexMap[ar[0]], codom.vertexMap[ar[1]],\
                        codom.colorMap[ar[2]])
            if not key in codom.codomain.colored_common_domains:
                current_maximum = 0
                break
            l2 = len(codom.codomain.colored_common_domains[key])
            if l2 < current_maximum:
                current_maximum = l2
                
        keep_arrows.extend(ccD[ar][0:current_maximum])

    new_dom.edges = [domain.edges[i] for i in keep_arrows]
    new_dom.colors = [domain.colors[i] for i in keep_arrows]
    
    new_dom.recalculate_representation()
    return new_dom
