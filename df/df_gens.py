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
from df_concept import *
import random

def create_all_ntuples(width, height):
    """create_all_ntuples(width, height)     creates a list of tuples such that
    each height^width combination of values from 0..(height-1) of width-tuples
    are in the list"""
    if width == 0:
        return [()]
    else:
        left_part = create_all_ntuples(width - 1, height)
        result = []
        for l in left_part:
            l2 = list(l)
            result += [tuple(l2 + [i]) for i in range(height)]
        return result
        
def create_ntuples(heights):
    """create_ntuples(heights)     creates a list of tuples such that every
    tuple t with width len(heights) and t[i] < heights[i] is created"""
    if heights == []:
        return [()]
    else:
        right_part = create_ntuples(heights[1:])
        h = heights[0]
        result = []
        for r in right_part:
            r2 = list(r)
            result += [tuple([i] + r2) for i in range(h)]
        return result
        
def unique_crossover(parents):
    """unique_crossover(parents)    parents is a list of genConcept-strings
    returns a list of unique block-wise crossovers from all parents
    (!!) the length of the returned list is <= len(parents)**13 (!!)"""
    genes = map(splitConceptString, parents)
    chromosomes = DfGlobal()["chromosomes"]
    gene_parts = {}
    for c in chromosomes:
        gene_parts[c] = set(map(lambda x: x[c], genes))
    heights = [len(gene_parts[chromosomes[c]]) for c in range(len(chromosomes))]
    offspring = create_ntuples(heights)
    next_generation = []
    for n in offspring:
        q = ""
        for c in range(len(chromosomes)):
            name = chromosomes[c]
            q += ":" + name + genes[n[c]][name]
        next_generation += [q]
    return next_generation

def complete_crossover(parents):
    """complete_crossover(parents)    parents is a list of genConcept-strings
    returns a complete list of block-wise crossovers from all parents
    (!!) the length of the returned list is len(parents)**13 (!!)"""
    genes = map(splitConceptString, parents)
    chromosomes = DfGlobal()["chromosomes"]
    offsprings = create_all_ntuples(len(chromosomes), len(genes))
    next_generation = []
    for n in offsprings:
        q = ""
        for c in range(len(chromosomes)):
            name = chromosomes[c]
            q += ":" + name + genes[n[c]][name]
        next_generation += [q]
    return next_generation
    
def random_string(min, max, choices):
    """random_string(min, max, choices)   generates a random string of length l where min <= l <= max,
    by choosing randomly from choices (might be either a string or a list/tuple of strings)"""
    l = random.randint(min,max)
    w = len(choices)-1
    return "".join([choices[random.randint(0,w)] for x in range(0,l)])
    


def initialize_gens():
    """initialize global variables used by gens"""
    g = DfGlobal()
    g["mutators"] = {}
    g["crossover"] = {}
    g["chromosomes"] = splitConceptString("").keys()[:]
    g["chrome.complement"] = [["l","L","'L"],["r","R","'R"],["a","A","'A"],["b","B","'B"],["C"]]
    g["chrome.alike"] = [["l","r","a","b"],["L","R"],["A","B"],["'L","'R"],["'A","'B"],["C"]]
