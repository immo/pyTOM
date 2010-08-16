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

import copy

class CoDiMuGraph(object):
    """class that stores a colored directed multi-graph with annotated vertices
    """
    def __init__(self, vertices=0, edges=[], colors=[], annotations=[], tips=[]):
        """CoDiMuGraph(vertices, edges, colors, annotations,tips)   where
        vertices is the number of vertices of the colored directed multi-graph
        edges is list of pairs of vertices of the form (source, target) and
        color is the list of colors that gives the color for each edge and
        annotations is a list of annotations for each vertex
        tips is a list of tool-tip strings for each vertex
        """
        self.behaviour = ""
        self.universal_colors = []
        self.wildcard_vertices = []
        self.vertices = vertices
        self.edges = edges
        ledges = len(edges)
        self.n_edges = ledges
        lcolors = len(colors)
        if lcolors > ledges:
            self.colors = colors[0:ledges]
        elif lcolors == ledges:
            self.colors = colors
        elif lcolors > 0:
            self.colors = (colors * ((ledges + lcolors - 1)/lcolors))[0:ledges]
        else:
            self.colors = [None] * ledges
        lannotations = len(annotations)
        if lannotations > vertices:
            self.annotations = annotations[0:vertices]
        elif lannotations == vertices:
            self.annotations = annotations
        elif lannotations > 0:
            self.annotations= (annotations * \
                               ((vertices + lannotations -1)/lannotations))\
                               [0:vertices]
        else:
            self.annotations = [None] * vertices
        ltips = len(tips)
        if ltips > vertices:
            self.tips = tips[0:vertices]
        elif ltips == vertices:
            self.tips = tips
        elif ltips > 0:
            self.tips = (tips * ((vertices + ltips -1)/ltips))[0:vertices]
        else:
            self.tips = [""] * vertices
        self.representation = "CoDiMuGraph(" + repr(vertices) + "," +\
                                              repr(self.edges) + "," +\
                                              repr(self.colors) + "," +\
                                              repr(self.annotations) +\
                                              "," + repr(self.tips) + ")"

        
        self.default_graph_name = "custom_graph"
        
        self.calculate_further_data()

    def recalculate_representation(self):
        """ recalculate the representation (used for domain-changes) """
        self.calculate_further_data()
        self.representation = "CoDiMuGraph(" + repr(self.vertices) + "," +\
                                               repr(self.edges) + "," +\
                                               repr(self.colors) + "," +\
                                               repr(self.annotations) +\
                                         "," + repr(self.tips) + ")"

        if self.vertices > 64:
            return
        for col in self.color_set:
            if type(col) != type("string"):
                print col
                print "No string!!"
                return
            
        ccD = copy.deepcopy(self.colored_common_domains)
        ccK = map(lambda x: (x[2],x[1],x[0]), ccD.keys())
        ccK.sort()
        ccK = map(lambda x: (x[2],x[1],x[0]), ccK)
        
        mkRep = "MkGraph(" + repr(self.vertices) + ",'"
        current_color = None
        while ccK:
            head = ccK[0]
            if current_color != head[2]:
                mkRep += "@" + str(head[2]) + " "
                current_color = head[2]
            vtx_list = [head[0], head[1]]
            ccD[head].pop()
            if not ccD[head]:
                ccK.remove(head)
            while 1:
                candidates = filter(lambda x: x[2] == current_color and \
                                    x[0] == vtx_list[-1], ccK)
                if candidates:
                    head = candidates[0]
                    vtx_list += [head[1]]
                    ccD[head].pop()
                    if not ccD[head]:
                        ccK.remove(head)
                else:
                    break
            mkRep += "".join(map(vertexToChar, vtx_list)) + " "
            
        mkRep += "')"
        self.representation = mkRep

    def calculate_further_data(self):
        self.common_domains = {}
        edges = self.edges
        ledges = len(edges)
        for i in range(ledges):
            (s,t) = edges[i]
            if (s,t) in self.common_domains:
                self.common_domains[(s,t)].append(i)
            else:
                self.common_domains[(s,t)] = [i]
        self.nbr_of_edges = ledges
        colors = self.colors
        self.colored_common_domains = {}
        for i in range(ledges):
            (s,t) = edges[i]
            c = colors[i]
            if (s,t,c) in self.colored_common_domains:
                self.colored_common_domains[(s,t,c)].append(i)
            else:
                self.colored_common_domains[(s,t,c)] = [i]
        self.nbr_colored_common_domains = len(self.colored_common_domains)
        self.color_set = set(colors)
        self.behaviour_strings = self.annotations
        keylist = self.colored_common_domains.keys()[:]
        keylist.sort()
        vallist = [len(self.colored_common_domains[k]) for k in keylist]
        self.hash = hash(repr(keylist) + ":" + repr(vallist))

    def add_universal_color(self,name="universal"):
        self.edges += [(i,j) for i in range(self.vertices)\
                             for j in range(self.vertices)]
        self.colors += [name] * (self.vertices * self.vertices)
        self.universal_colors.append(name)
        # might need to redo calculate_further_data after call

    def add_wildcard_node(self,vertex,colorset=None):
        if colorset == None:
            colorset = set(self.colors)
        wildcard_arrows = [(vertex,i) for i in range(self.vertices)] +\
                          [(i,vertex) for i in range(self.vertices)]
        self.edges += wildcard_arrows * len(colorset)
        for color in colorset:
            self.colors += [color] * (self.vertices * 2)
        self.wildcard_vertices.append(vertex)
        # might need to redo calculate_further_data after call

    def make_thin(self):
        ccD = self.colored_common_domains
        keepArrows = map(lambda x: x[1][0],\
            filter(lambda x: len(x[1]) >= 1, [(k, ccD[k]) for k in ccD]))       
        self.edges = [self.edges[k] for k in keepArrows]
        self.colors = [self.colors[k] for k in keepArrows]
        # might need to redo calculate_further_data after call
    
    def __repr__(self):
        return self.representation

    def __hash__(self):
        return self.hash

    def __eq__(self,r):
        if self.hash != r.hash:
            return False
        if self.vertices != r.vertices:
            return False
        if self.color_set != r.color_set:
            return False
        if self.nbr_of_edges != r.nbr_of_edges:
            return False
        if self.nbr_colored_common_domains != r.nbr_colored_common_domains:
            return False
        ccD = self.colored_common_domains
        ccDr = r.colored_common_domains
        for d in ccD:
            if not d in ccDr:
                return False
            if len(ccD[d]) != len(ccDr[d]):
                return False
        return True

    def __ne__(self,r):
        return not self == r
            
    
    def source(self, edge):
        return self.edges[edge][0]
    
    def target(self, edge):
        return self.edges[edge][1]
    
    def color(self, edge):
        return self.colors[edge]
        
    def annotation(self, vertex):
        return self.annotations[vertex]

    def behaviourString(self, vertex):
        return self.behaviour_strings[vertex]
    
    def tooltip(self, vertex):
        return self.tips[vertex]

    def getUniversalColors(self):
        return self.universal_colors

    def getWildcardVertices(self):
        return self.wildcard_vertices
        
    def countVertices(self):
        return self.vertices
        
    def countEdges(self):
        return self.n_edges
    
    def dotSource(self, name=None):
        if name == None:
            name = self.default_graph_name
        source = "digraph " + name + " {" + "\n"
        
        for i in range(self.vertices):
            source += "\n    v" + str(i)+ " [label=\"" \
                                             + self.annotations[i] + "\"];"
        source += "\n"
        edges = self.edges
        colors = self.colors
        colors_define = {}
        color_list = [mod+col for col in \
         "red,green,blue,cyan,lime,magenta,maroon,orchid".split(",")\
                  for mod in ["","dark","light","medium"]]
        cnum = 0
        for i in range(self.n_edges):
            source += "\n    v" + str(edges[i][0]) + " -> v" + str(edges[i][1])\
                   + " ["
            clr = colors[i]
            if clr not in colors_define:
                source += "label=\"" + clr +"\""
                colors_define[clr] = color_list[cnum]
                cnum += 1
            
            source += " color=" + colors_define[clr] + "];"
        source += "\n}\n"
        return source

def transitive_closure(list):
    """where list is a list of lists of list-indices,
    returns the list of lists that are transitive closed"""
    closure = list
    n = len(list)
    while 1:
        stepped = 0
        for i in range(n):
            for x in closure[i]:
                for y in closure[x]:
                    if not y in closure[i]:
                        closure[i].append(y)
                        stepped = 1
        if not stepped:
            return closure
        
def inverted_list(list):
    """where list is a list of list-indices,
    returns the inside-out list of list-indices"""
    n = len(list)
    inversion = [ [i for i in range(n) if j in list[i] ] for j in range(n)]
    return inversion

class PotentialGraph(CoDiMuGraph):
    """ Hard-coded graph for parameter space """
    def __init__(self):
        self.behaviour = ""
        self.universal_colors = []
        self.wildcard_vertices = []
        
        #self.annotations = [n+d for n in ["[1]","[2/3]"] for d in "TSEQHW"]
        durations = "TSEQHW"
        durations_multiple = transitive_closure([[]]+[[i] for i in range(5)])
        durations_fraction = transitive_closure([[1],[2],[3],[4],[5],[]])
        ntoles = ["[1]","[2/3]"]
        expressions = [c for c in ",rR! ."] + ["..","...",".....","......."]
        #                          012345       6    7     8      9
        expressions_multiple = transitive_closure([[],[2],[],[],[3,4,0],[3,4,0],[5],[5,6],[7]])
        expressions_fraction = inverted_list(expressions_multiple)
        factors = ["{"+f+"}" for f in ["2/3","1","4/3","2","8/3","3","4","6","8","12"]]
        #                                 0   1    2    3    4    5   6   7   8   9
        factors_multiple = transitive_closure([[],[],[0],[1,0],[2],[1],[3,2],[5,3],[6],[6,7]])
        factors_fractions = inverted_list(factors_multiple)
        self.annotations= list(durations) + ntoles + list(expressions)  + factors
        self.vertices = len(self.annotations)
        self.tips = ["32nd","16th","8th","4th","half","whole",\
                     "straight","triole",\
                     "repeat time","rest next hit","rest time",\
                     "immediate hit","(nothing)","repeat time"] +\
                     ["repeat times"] * 4 + ["length factor"]*10
        
        edges = []
        colors= []
        
        startlist = [0]
        multiplelist = [durations_multiple,[],expressions_multiple,factors_multiple]
        fractionlist = [durations_fraction,[],expressions_fraction,factors_fractions]
        
        edges += [(s,t) for t in range(len(durations))\
                        for s in range(self.vertices)]
        
        colors += ["duration" for t in range(len(durations))\
                        for s in range(self.vertices)]
        
        start = len(durations)
        startlist += [start]
        
        edges += [(s,t+start) for t in range(len(ntoles))\
                        for s in range(self.vertices)]
        
        colors += ["n-feel" for t in range(len(ntoles))\
                        for s in range(self.vertices)]
        
        start += len(ntoles)
        startlist += [start]
        
        edges += [(s,t+start) for t in range(len(expressions))\
                        for s in range(self.vertices)]
        
        colors += ["expression" for t in range(len(expressions))\
                        for s in range(self.vertices)]
        
        start += len(expressions)
        startlist += [start]
        
        edges += [(s,t+start) for t in range(len(factors))\
                        for s in range(self.vertices)]
        
        colors += ["factor" for t in range(len(factors))\
                        for s in range(self.vertices)]        
        
        start += len(factors)
        startlist += [start]
        
        for i in range(1,len(startlist)):
            indices = range(startlist[i-1],startlist[i])
            edges += [(s,t) for s in indices for t in indices]
            colors += ["same-type" for s in indices for t in indices]
            edges += [(s,t) for s in indices for t in range(self.vertices) \
                                 if not t in indices]
            colors += ["other-type"  for s in indices \
                        for t in range(self.vertices) \
                                 if not t in indices]
            edges += [(x-1,x) for x in indices[1:]]
            colors += ["successor"] * (len(indices) - 1)
            edges += [(x,x-1) for x in indices[1:]]
            colors += ["predecessor"] * (len(indices) - 1)
            edges += [(x,y) for x in indices for y in indices if x < y]
            colors += ["greater" for x in indices for y in indices if x < y]
            edges += [(x,y) for x in indices for y in indices if x > y]
            colors += ["less" for x in indices for y in indices if x > y]
            
            s0 = startlist[i-1]            
            is_multiple = multiplelist[i-1]
            for t in range(len(is_multiple)):
                edges += [(s+s0,t+s0) for s in is_multiple[t]]
                colors += ["multiple"] * len(is_multiple[t])
            is_fraction = fractionlist[i-1]
            for t in range(len(is_fraction)):
                edges += [(s+s0,t+s0) for s in is_fraction[t]]
                colors += ["fraction"] * len(is_fraction[t])
        
        
        edges += [(x,x) for x in range(self.vertices)]
        colors += ["identity"] * self.vertices
        
        edges += [(x,y) for x in range(self.vertices) \
                        for y in range(self.vertices) \
                        if x != y]
        colors += ["non-identity"] * self.vertices * (self.vertices- 1)
        
        self.edges = edges
        self.n_edges = len(edges)
        self.colors= colors
        
        self.representation = "PotentialGraph()"

        
        self.default_graph_name = "potential_graph"

        self.add_wildcard_node(12)
        self.add_universal_color()
        
        self.calculate_further_data()
        self.make_thin()
        self.calculate_further_data()

class StrengthGraph(CoDiMuGraph):
    """ Hard-coded graph for parameter space """
    def __init__(self):
        self.universal_colors = []
        self.wildcard_vertices = []
        
        self.behaviour = ""
        durations = "TSEQHW"
        durations_multiple = transitive_closure([[]]+[[i] for i in range(5)])
        durations_fraction = transitive_closure([[1],[2],[3],[4],[5],[]])
        ntoles = ["[1]","[2/3]"]
        deltas = ["<0.0>","<0.02>","<0.05>","<0.1>","<0.15>"]
        deltas_multiple = transitive_closure([[],[0],[0],[1,2],[3]])
        deltas_fraction = inverted_list(deltas_multiple)
        expressions = [c for c in ",umM! ."] + ["..","...",".....","......."] 
        #                          0123456       7    8     9       10
        expressions_multiple = transitive_closure([[],[],[],[2],[1],[],[5,0],[5,0],[6],[6,7],[8]])
        expressions_fraction = inverted_list(expressions_multiple)
        factors = ["{"+f+"}" for f in ["2/3","1","4/3","2","8/3","3","4","6","8","12"]]
        #                                 0   1    2    3    4    5   6   7   8   9
        factors_multiple = transitive_closure([[],[],[0],[1,0],[2],[1],[3,2],[5,3],[6],[6,7]])
        factors_fractions = inverted_list(factors_multiple)
        strengths = ["(1.0)","(0.9)","(0.8)","(0.75)"]
        strengths_multiple = [[1,2,3],[2],[],[]]
        strengths_fraction = inverted_list(strengths_multiple)
        
        #self.annotations = [n+d for n in ["[1]","[2/3]"] for d in "TSEQHW"]
        self.annotations= list(durations) + ntoles + list(expressions) +deltas\
                            + strengths +factors
        self.vertices = len(self.annotations)
        self.tips = ["32nd","16th","8th","4th","half","whole",\
                     "straight","triole",\
                     "repeat time","start unstressed",\
                     "from stressed to stressed",\
                     "from stressed to unstressed","start stressed",\
                     "(nothing)","repeat time"] + ["repeat times"] * 4 +\
                     ["stressed/unstressed delta"]*4 +\
                     ["strength level"]*5 + ["length factor"]*10
        edges = []
        colors= []
        startlist =  [0]
        multiplelist = [durations_multiple,[],expressions_multiple,deltas_multiple,strengths_multiple,factors_multiple]
        fractionlist = [durations_fraction,[],expressions_fraction,deltas_fraction,strengths_fraction,factors_fractions]        
        
        edges += [(s,t) for t in range(len(durations))\
                        for s in range(self.vertices)]
        
        colors += ["duration" for t in range(len(durations))\
                        for s in range(self.vertices)]
        
        start = len(durations)
        startlist += [start]
        
        edges += [(s,t+start) for t in range(len(ntoles))\
                        for s in range(self.vertices)]
        
        colors += ["n-feel" for t in range(len(ntoles))\
                        for s in range(self.vertices)]
        
        start += len(ntoles)
        startlist += [start]
        
        edges += [(s,t+start) for t in range(len(expressions))\
                        for s in range(self.vertices)]
        
        colors += ["expression" for t in range(len(expressions))\
                        for s in range(self.vertices)]
        
        start += len(expressions)
        startlist += [start]
        
        edges += [(s,t+start) for t in range(len(deltas))\
                        for s in range(self.vertices)]
        
        colors += ["delta-value" for t in range(len(deltas))\
                        for s in range(self.vertices)]
        
        start += len(deltas)
        startlist += [start]
        
        edges += [(s,t+start) for t in range(len(strengths))\
                        for s in range(self.vertices)]
        
        colors += ["strength-value" for t in range(len(strengths))\
                        for s in range(self.vertices)]
        
        start += len(strengths)
        startlist += [start]
        
        edges += [(s,t+start) for t in range(len(factors))\
                        for s in range(self.vertices)]
        
        colors += ["factor" for t in range(len(factors))\
                        for s in range(self.vertices)]        
        
        start += len(factors)
        startlist += [start]
        
        for i in range(1,len(startlist)):
            indices = range(startlist[i-1],startlist[i])
            edges += [(s,t) for s in indices for t in indices]
            colors += ["same-type" for s in indices for t in indices]
            edges += [(s,t) for s in indices for t in range(self.vertices) \
                                 if not t in indices]
            colors += ["other-type"  for s in indices \
                        for t in range(self.vertices) \
                                 if not t in indices]
            edges += [(x-1,x) for x in indices[1:]]
            colors += ["successor"] * (len(indices) - 1)
            edges += [(x,x-1) for x in indices[1:]]
            colors += ["predecessor"] * (len(indices) - 1)
            edges += [(x,y) for x in indices for y in indices if x < y]
            colors += ["greater" for x in indices for y in indices if x < y]
            edges += [(x,y) for x in indices for y in indices if x > y]
            colors += ["less" for x in indices for y in indices if x > y]
            
            s0 = startlist[i-1]            
            is_multiple = multiplelist[i-1]
            for t in range(len(is_multiple)):
                edges += [(s+s0,t+s0) for s in is_multiple[t]]
                colors += ["multiple"] * len(is_multiple[t])
            is_fraction = fractionlist[i-1]
            for t in range(len(is_fraction)):
                edges += [(s+s0,t+s0) for s in is_fraction[t]]
                colors += ["fraction"] * len(is_fraction[t])
        
        edges += [(x,x) for x in range(self.vertices)]
        colors += ["identity"] * self.vertices
        
        edges += [(x,y) for x in range(self.vertices) \
                        for y in range(self.vertices) \
                        if x != y]
        colors += ["non-identity"] * self.vertices * (self.vertices- 1)
        
        
        self.edges = edges
        self.n_edges = len(edges)
        self.colors= colors
        self.representation = "StrengthGraph()"

        
        self.default_graph_name = "strength_graph"
        
        self.add_wildcard_node(13)
        self.add_universal_color()
        
        self.calculate_further_data()
        self.make_thin()
        self.calculate_further_data()

class ChangesGraph(CoDiMuGraph):
    """ Hard-coded graph for parameter space """
    def __init__(self):
        self.universal_colors = []
        self.wildcard_vertices = []
        
        self.behaviour = ""
        groups = ["CbcVv","YBy","jhG","Rtrz","wds","~^*","xpXg","nN",\
                       "mM","fF"]
        gtype = ["cymbal","cymbal","cymbal","cymbal","cymbal","cymbal","drum",\
                 "drum","drum","drum"]
        similars = ["BGORT","BGO","GOT","BGOR","BGO","GOT","oprx","or",\
                       "or","or"]
        instruments = list("".join(groups))
        durations = "TSEQHW"
        durations_multiple = transitive_closure([[]]+[[i] for i in range(5)])
        durations_fraction = transitive_closure([[1],[2],[3],[4],[5],[]])
        ntoles = ["[1]","[2/3]"]
        expressions = [c for c in ", ."] + ["..","...",".....","......."]
        #                          012       3    4     5       6
        expressions_multiple = transitive_closure([[],[],[1,0],[1,0],[2],[2,3],[4]])
        expressions_fraction = inverted_list(expressions_multiple)
        factors = ["{"+f+"}" for f in ["2/3","1","4/3","2","8/3","3","4","6","8","12"]]
        #                                 0   1    2    3    4    5   6   7   8   9
        factors_multiple = transitive_closure([[],[],[0],[1,0],[2],[1],[3,2],[5,3],[6],[6,7]])
        factors_fractions = inverted_list(factors_multiple)
        #self.annotations = [i+" " + n + " "+d+ "  " for n in ["[1]","[2/3]"]\
        #                    for d in "TSEQHW" for i in instruments]
        self.annotations = list(durations) + ntoles + list(expressions) \
                            +instruments+factors
        
        self.vertices = len(self.annotations)
        self.tips = ["32nd","16th","8th","4th","half","whole",\
                     "straight","triole",\
                     "repeat time",\
                     "(nothing)","repeat time"] + ["repeat times"] * 4 +\
                     ["cy15crash(bel)","cy15crash(grb)","cy15crash(ord)",\
                      "cy15crash(rim)","cy15crash(top)","cy18crash(bel)",\
                      "cy18crash(grb)","cy18crash(ord)","cy19china(grb)",\
                      "cy19china(ord)","cy19china(top)","cy20ride(bel)",\
                      "cy20ride(grb)","cy20ride(ord)","cy20ride(rim)",\
                      "cy8splash(bel)","cy8spalsh(grb)","cy8splash(ord)",\
                      "hh13(grb)","hh13(ord)","hh13(top)","sn14wrock(ord)",\
                      "sn14wrock(prs)","sn14wrock(rms)","sn14wrock(xtk)",\
                      "tm10rock(ord)","tm10rock(rms)","tm12rock(ord)",\
                      "tm12rock(rms)","tm14rock(ord)","tm14rock(rms)"\
                     ]+ ["length factor"]*10
        
        edges = []
        colors = []
        startlist = [0]
        multiplelist = [durations_multiple,[],expressions_multiple,[],factors_multiple]
        fractionlist = [durations_fraction,[],expressions_fraction,[],factors_fractions]
        
        edges += [(s,t) for t in range(len(durations))\
                        for s in range(self.vertices)]
        
        colors += ["duration" for t in range(len(durations))\
                        for s in range(self.vertices)]
        
        start = len(durations)
        startlist += [start]
        
        edges += [(s,t+start) for t in range(len(ntoles))\
                        for s in range(self.vertices)]
        
        colors += ["n-feel" for t in range(len(ntoles))\
                        for s in range(self.vertices)]
        
        start += len(ntoles)
        startlist += [start]
        
        edges += [(s,t+start) for t in range(len(expressions))\
                        for s in range(self.vertices)]
        
        colors += ["expression" for t in range(len(expressions))\
                        for s in range(self.vertices)]
        
        start += len(expressions)
        startlist += [start]
        
        edges += [(s,t+start) for t in range(len(instruments))\
                        for s in range(self.vertices)]
        
        colors += ["instrument" for t in range(len(instruments))\
                        for s in range(self.vertices)]
        
        start_instruments = start
        
        start += len(instruments)
        startlist += [start]
        
        edges += [(s,t+start) for t in range(len(factors))\
                        for s in range(self.vertices)]
        
        colors += ["factor" for t in range(len(factors))\
                        for s in range(self.vertices)]        
        
        start += len(factors)
        startlist += [start]
        
        for i in range(1,len(startlist)):
            indices = range(startlist[i-1],startlist[i])
            edges += [(s,t) for s in indices for t in indices]
            colors += ["same-type" for s in indices for t in indices]
            edges += [(s,t) for s in indices for t in range(self.vertices) \
                                 if not t in indices]
            colors += ["other-type"  for s in indices \
                        for t in range(self.vertices) \
                                 if not t in indices]
            edges += [(x-1,x) for x in indices[1:]]
            colors += ["successor"] * (len(indices) - 1)
            edges += [(x,x-1) for x in indices[1:]]
            colors += ["predecessor"] * (len(indices) - 1)
            edges += [(x,y) for x in indices for y in indices if x < y]
            colors += ["greater" for x in indices for y in indices if x < y]
            edges += [(x,y) for x in indices for y in indices if x > y]
            colors += ["less" for x in indices for y in indices if x > y]
            
            s0 = startlist[i-1]
            is_multiple = multiplelist[i-1]
            for t in range(len(is_multiple)):
                edges += [(s+s0,t+s0) for s in is_multiple[t]]
                colors += ["multiple"] * len(is_multiple[t])
            is_fraction = fractionlist[i-1]
            for t in range(len(is_fraction)):
                edges += [(s+s0,t+s0) for s in is_fraction[t]]
                colors += ["fraction"] * len(is_fraction[t])
        
        c_start = start_instruments
        kinds = {}
        for i in range(len(groups)):
            l = len(groups[i])
            indices = range(c_start, c_start + l)
            edges += [(s,t) for s in indices for t in indices]
            colors += ["same-group"] * l * l
            edges += [(s,t) for s in indices for t in range(self.vertices)\
                                      if not t in indices]
            colors += ["other-group"   for s in indices \
                                      for t in range(self.vertices)\
                                      if not t in indices]
            edges += [(s,t)      for t in indices \
                                 for s in range(self.vertices)]
            colors += [gtype[i]  for t in indices \
                                 for s in range(self.vertices)]
            for j in range(len(similars[i])):
                chr = similars[i][j]
                if chr in kinds:
                    kinds[chr] += [c_start+j]
                else:
                    kinds[chr] = [c_start+j]
            c_start += l
        
        for k in kinds:
            indices = kinds[k]
            l = len(indices)
            edges += [(s,t) for s in indices for t in indices]
            colors += ["same-kind"] * l * l
            edges += [(s,t) for s in indices for t in range(self.vertices)\
                                      if not t in indices]
            colors += ["other-kind"   for s in indices \
                                      for t in range(self.vertices)\
                                      if not t in indices]
            edges += [(s,t)      for t in indices \
                                 for s in range(self.vertices)]
            colors += ["("+k+")"  for t in indices \
                                 for s in range(self.vertices)]
        
        edges += [(x,x) for x in range(self.vertices)]
        colors += ["identity"] * self.vertices
        
        edges += [(x,y) for x in range(self.vertices) \
                        for y in range(self.vertices) \
                        if x != y]
        colors += ["non-identity"] * self.vertices * (self.vertices- 1)
        
        
        self.edges = edges
        self.n_edges = len(edges)
        self.colors= colors
        
        self.representation = "ChangesGraph()"

        
        self.default_graph_name = "changes_graph"

        self.add_wildcard_node(9)
        self.add_universal_color()
        
        self.calculate_further_data()
        self.make_thin()        
        self.calculate_further_data()

def mapConcat(lMap, rMap):
    result = {}
    for key in lMap:
        result[key] = rMap[ lMap[key] ]
    return result

def isInjective(map):
    image = []
    for key in map:
        if map[key] in image:
            return False
        else:
            image.append(map[key])
    return True


def charToVertex(c):
    charList ="0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz!"
    if not c in charList:
        return len(charList)
    else:
        return charList.index(c)

def vertexToChar(v):
    charList ="0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz!"
    if v >= len(charList):
        return str(v)
    else:
        return charList[v]

def MkGraph(n,s):
    """MkGraph(n,s)
    Converts a string s to a CoDiMuGraph object with n vertices
    
    s is split at each space character and then every block is seen as
    a chain of edges with the current color, where 0..9 are interpreted
    as vertices 0 through 9 and A..Z is interpreted as edges 10 through 36,
    a..z 37 through 62, and ! is 63
    blocks starting with @ change the current color
    """
    current_color = None
    edges = []
    colors = []
    annotations = [vertexToChar(i) + " " for i in range(n)]
    for block in s.split(" "):
        lenblock = len(block)
        if lenblock > 0:
            if block[0] == "@":
                current_color = block[1:]
            else:
                vertices = filter(lambda x: 0<=x<n, \
                                  map(charToVertex, block))
                lenblock = len(vertices)
                edges += [(vertices[i-1],vertices[i]) \
                            for i in range(1,lenblock)]
                colors += [current_color] * (lenblock - 1)
                
                
    graph = CoDiMuGraph(n, edges, colors, annotations)
    graph.representation = "MkGraph("+repr(n)+","+repr(s)+")"

    return graph



class PartialCoDiMuGraphHom(object):
    """class that represents parts of a CoDiMuGraph-Homomorphism"""
    def __init__(self, domain, codomain, colorMap=None, vertexMap=None, vertexPos=None, override_initialization=None):
        """create a Partial CoDiMuGraphHom object
        domain,codomain   CoDiMuGraph objects,
        colorMap          dictionary mapping colors
        vertexMap         dictionary mapping vertex indices
        vertexPos         dictionary overriding graphical layout of vertices
        """
        if override_initialization:
            return
        
        self.domain = domain
        self.codomain = codomain
        self.colorMap = {}
        if not colorMap == None:
            self.colorMap = colorMap
        self.vertexMap = {}
        if not vertexMap == None:
            self.vertexMap = vertexMap
        self.vertexPos = {}
        if not vertexPos == None:
            self.vertexPos = vertexPos
            
        self.check()
    
    def __repr__(self):
        return "PartialCoDiMuGraphHom("+repr(self.domain)+","+\
                              repr(self.codomain)+","+repr(self.colorMap)+","+\
                              repr(self.vertexMap)+","+repr(self.vertexPos)+")"

    def __hash__(self):
        return hash(repr(self))

    def __eq__(self,r):
        if self.colorMap != r.colorMap or \
           self.vertexMap != r.vertexMap or \
           self.vertexPos != r.vertexPos or \
           self.domain != r.domain or \
           self.codomain != r.codomain:
            return False
        return True
        
    def __ne__(self,r):
        return not self == r

    def __deepcopy__(self, memo={}):
        # Note that we DO NOT COPY THE CODOMAIN OBJECT
        cpy = self.__class__(None,None,override_initialization=True)
        #cpy = PartialCoDiMuGraphHom(None,None,override_initialization=True)
        memo[id(self)] = cpy
        cpy.domain = copy.deepcopy(self.domain)
        cpy.codomain = self.codomain #!!
        cpy.colorMap =  copy.deepcopy(self.colorMap)
        cpy.vertexMap = copy.deepcopy(self.vertexMap)
        cpy.vertexPos = copy.deepcopy(self.vertexPos)
        cpy.errors = copy.deepcopy(self.errors)
        cpy.incomplete = copy.deepcopy(self.incomplete)
        cpy.incompatible = copy.deepcopy(self.incompatible)
        cpy.incompatible_text = copy.deepcopy(self.incompatible_text)
        cpy.report_text = copy.deepcopy(self.report_text)
        try:
            cpy.behaviour = copy.deepcopy(self.behaviour)
        except AttributeError:
            pass # behaviour not yet set
        return cpy
    
    def checkDiPair(self, s, t, simage, timage):
        error = ""
        for color in self.colorMap:
            dom_tripel = (s,t,color)
            cod_tripel = (simage,timage,self.colorMap[color])
            if dom_tripel in self.domain.colored_common_domains:
                dom_len = len(self.domain.colored_common_domains[dom_tripel])
                if not cod_tripel in self.codomain.colored_common_domains:
                    cod_len = 0
                else:
                    cod_len = len(self.codomain.colored_common_domains[cod_tripel])
                if cod_len < dom_len:
                    error += " " + repr(color) + "x" +str(dom_len) + " `-/-> "\
                           + repr(cod_tripel[2]) + "x" + str(cod_len)
        if error != "":
            return error
        else:
            return None
        
    def check_image(self, s, simage):
        if self.checkDiPair(s,s,simage,simage) != None:
            return 1
        for vtx in self.vertexMap:
            if vtx != s:
                if self.checkDiPair(s,vtx,simage,self.vertexMap[vtx]) != None \
                or self.checkDiPair(vtx,s,self.vertexMap[vtx],simage) != None:
                    return 2
        return 0
        
    def check(self):
        """check current graph hom for validity, set self.incomplete, self.errors and self.report_text"""
        report = ""
        self.errors = 0
        self.incomplete = 0
        self.incompatible = 0
        self.incompatible_text = ""
        for color in self.domain.color_set:
            if not color in self.colorMap:
                report += "Color map is incomplete.\n"
                self.incomplete += 2
                break
        for vtx in range(self.domain.vertices):
            if not vtx in self.vertexMap:
                report += "Vertex map is incomplete.\n"
                self.incomplete += 1
                break
            
        report += "\nErroneous colors:"
        colorErrors = ""
        for clr in self.colorMap:
            error = 0
            try:
                image = self.colorMap[clr]
                if not image in self.codomain.color_set:
                    error = 1
            except:
                error = 1
            if error == 1:
                self.errors += 1                
                report += " " + repr(clr)
                colorErrors += "Color " + repr(clr) + ": image invalid\n"
        report += "\n"
        
        vertexErrors = ""
        report += "Erroneous vertices:"
        for vtx in self.vertexMap:
            error = 0
            try:
                image = self.vertexMap[vtx]
                if image < 0 or \
                   image >= self.codomain.vertices:
                    error = 1
            except:
                error = 1
            if error == 1:
                self.errors += 1                
                report += " "+ str(vtx)
                vertexErrors +="Vertex " + str(vtx) + ": image invalid\n"
        report += "\n"
        report += colorErrors
        report += "\n"
        report += vertexErrors
        report += "\nIncompatible edges:\n"
        for v1 in self.vertexMap:
            for v2 in self.vertexMap:
                error = self.checkDiPair(v1,v2, self.vertexMap[v1], self.vertexMap[v2])
                if error != None:
                    self.errors += 1
                    self.incompatible += 1
                    report += str(v1)+"->"+str(v2)+": "+error + "\n"
                    self.incompatible_text += str(v1)+"->"+str(v2)+": "+error + "\n"
        self.report_text = report

    def getBehaviour(self):
        try:
            data = map(lambda x: self.codomain.behaviourString(\
                self.vertexMap[x]),\
                   filter(lambda x: x in self.vertexMap,\
                          range(self.domain.vertices)))
        except:
            data = []
        if len(data):
            b = reduce(lambda a,b: a + b, data)
        else:
            b = None
        self.behaviour = str(b)
        return b
