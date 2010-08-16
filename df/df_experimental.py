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
import random
import copy

class pgrammar(object):
    """a p-grammar is a grammar that works in a probabilistic way"""
    def __init__(self, rules):
        """ initialize the pgrammar object, where rules is a dictionary
            mapping non-terminals to lists of (omega, p) tuples """
        self.rules = rules
        self.nonterminals = self.rules.keys()
        self.p_sums = {}
        self.lower_bounds = {}
        self.random_maps = {}
        for A in self.nonterminals:
            total = sum( map( lambda x: x[1], self.rules[A] ) )
            self.p_sums[A] = total
            if total <= 0.0:
                total = 1.0
            self.lower_bounds[A] = []
            bound = 0.0
            boundmapstring = "0"
            count = 0
            for r in self.rules[A]:
                self.lower_bounds[A].append(bound)
                boundmapstring = repr(count) + " if (x>=" + repr(bound/total) \
                                  + ") else " + boundmapstring
                bound += r[1]
                count += 1
            boundmapstring = "lambda x: " + boundmapstring
            #print A,':',boundmapstring
            self.random_maps[A] = lambda x,A=A,fn=eval(boundmapstring):\
                                  self.rules[A][fn(x)][0]
            
    def __call__(self, word):
        tokens_list = filter(lambda x: x[1], word)
        tokens = {}
        for t in tokens_list:
            T = repr(t)
            if not T in tokens:
                def rulemap(x):
                    if x[1]:
                        return (x[0],t[1]+[x[1]])
                    else:
                        return (x[0],[])
                tokens[T] = map(rulemap, \
                                self.random_maps[t[0]](random.uniform(0.0,1.0)))
        w = []
        for x in word:
            X = repr(x)
            if X in tokens:
                w.extend(tokens[X])
            else: # make unknown non-terminals terminals
                w.append((x[0],[]))
        return w

def projectTerminals(word):
    return map(lambda x: x[0], filter(lambda x: not x[1], word))

def hasNonTerminals(word):
    for k in word:
        if k[1]:
            return True
    return False

def definiteTerminals(word):
    terms = []
    for k in word:
        if k[1]:
            return terms
        terms.append(k[0])
    return terms

def countDefiniteTerminals(word):
    count = 0
    for k in word:
        if k[1]:
            return count
        count += 1
    return count
        
def makeRule(code):
    """ make a rule data structure from code:
    NONTERMINAL: *TERMINAL(NUMBER) ... *TERMINAL(NUMBER): PVALUE
    where NUMBER=0 means terminal, and all nonterminals with
    the same NUMBER refer to the same instances of nonterminals. """
    c = map(lambda x: x.strip(), code.split(':'))
    if len(c) == 2:
        c.append("1.0")
        
    if not len(c) == 3:
        raise Exception("Wrong rule format: "+str(code))

    lefthand = c[0].strip()
    pvalue = float(c[2])

    termnums = filter(lambda x:x, c[1].split(")"))

    def int0(x):
        try:
            return int(x)
        except ValueError:
            return 0

    def mk_sym(x):
        s = x.split("(")
        if not len(s) == 2:
            raise Exception("Wrong bracket format: " + str(code))
        return (s[0].strip(),int0(s[1]))

    symbols = map(mk_sym, termnums)
    
    righthand = [(symbols, pvalue)]

    return {lefthand: righthand}

def makeWord(code):
    termnums = filter(lambda x:x, code.split(")"))

    def int0(x):
        try:
            return int(x)
        except ValueError:
            return 0

    def lint0(x):
        q = int0(x)
        if q:
            return [q]
        else:
            return []

    def mk_sym(x):
        s = x.split("(")
        if not len(s) == 2:
            raise Exception("Wrong bracket format: " + str(code))
        return (s[0].strip(),lint0(s[1]))

    symbols = map(mk_sym, termnums)

    return symbols

def simplifyWord(word):
    simplificator = {tuple(): []}
    varc = 1
    new_word = []
    for x in word:
        try:
            v = simplificator[tuple(x[1])]
        except KeyError:
            v = simplificator[tuple(x[1])] = [varc] 
            varc += 1        
        new_word.append((x[0], v))
    return new_word
    

def addRules(x, add):
    for k in add:
        x.setdefault(k,[]).extend(add[k])

def makeRules(rules, default=None):
    rlist = filter(lambda x:x, map(lambda x:x.strip(), rules.split("\n")))
    if default:
        r = copy.deepcopy(default)
    else:
        r = {}
        
    for x in rlist:
        addRules(r, makeRule(x))
    return r

    

if __name__ == '__main__':
    rules = {}
    rules['A'] = [([('A',1),('B',1),('A',1),('A',2)], 0.5),\
                  ([('C',1)], 1.1)]
    rules['B'] = [([('!',0)],0)]
    rules['C'] = [([('_',0)],0)]
    g = pgrammar(rules)
    initial = [('A',[1]),('A',[])]


class neuron(object):
    """a neuron has an inner level, an input level and output synapses"""
    def __init__(self, level=None, synapses=None, delta=None):
        """ initialize a neuron with its level and output synapses-weighting """
        if level:
            self.level = level
        else:
            self.level = 0.5

        if synapses:
            self.synapses = synapses
        else:
            self.synapses = {}
        #
        # self.synapses maps function objects on sets of neurons
        #

        self.input = 0

        if delta:
            self.delta = delta
        else:
            self.delta = lambda x: min(1.0,max(0.0,(x+self.level)))

    def react(self):
        self.level = self.delta(self.input)
        self.input = 0

    def feed(self):
        for fn in self.synapses:
            y = fn(self.level)
            for n in self.synapses[fn]:
                n.input += y

class cluster(object):
    """a cluster is a set of neurons that may have synapse connections"""
    def __init__(self, count=32, renormalization=None):
        """ initialize a neuron cluster with count neurons """
        self.neurons = [neuron() for i in range(count)]
        self.renormalization = renormalization
        
    def feedback(self):
        for n in self.neurons:
            n.feed()
        for n in self.neurons:
            n.react()
        if self.renormalization:
            factor = self.renormalization / sum(map(lambda n:n.level, self.neurons))
            for n in self.neurons:
                n.level *= factor

    def shock(self, energy):
        for n in self.neurons:
            n.level += energy

    def jolt(self, energy):
        for n in self.neurons:
            n.input += energy

    def connect(self, i, fn, j):
        self.neurons[i].synapses.setdefault(fn, set()).add(self.neurons[j])

    def levels(self):
        return map(lambda n: n.level, self.neurons)
    
def trigger_fn(limit,high,low=0.0):
    def fn(x,limit=limit,high=high,low=low):
        if x >= limit:
            return high
        return low
    return fn

