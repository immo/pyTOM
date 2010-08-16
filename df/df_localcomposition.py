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
from df_global import *

def str2(x):
    if x == None:
        return ""
    else:
        return str(x)

class PartialLocalComposition(object):
    """class that represents a (partial) local composition"""
    def __init__(self, domain, vertexPos=None,codomains=None,vertexMaps=None,\
                 colorMaps=None, behaviours=None, tags=None, arrows=None):
        """create a partial local composition, where
        domain     is a CoDiMuGraph that is the common domain of all arrows
        vertexPos  is an associative array giving override-positions for
                   the vertices of the domain (for display purposes)
        codomains  is an associative array of CoDiMuGraphs that contains 
                   all arrows codomains
        vertexMaps is an associative array that contains all vertex maps
        colorMaps  is an associative array that contains all color maps
        behaviours is an associative array that contains all graph behaviours
        tags       is an associative array that contains tags associated with
                   the composition
        """

        if codomains == None:
            g = DfGlobal()
            pot = g["PotentialGraph"]
            str = g["StrengthGraph"]
            chg = g["ChangesGraph"]
            gtr = g["GuitarGraph"]            
            self.codomains = {'l': pot, 'r': pot, 'a': pot, 'b': pot, \
                              'L': str, 'R': str, 'A': str, 'B': str, \
                              "'L": chg, "'R":chg, "'A":chg, "'B":chg, \
                              " Gtr": gtr}
        else:
            self.codomains = codomains
        if vertexPos == None:
            self.vertexPos = {}
        else:
            self.vertexPos = vertexPos
        if vertexMaps == None:
            self.vertexMaps = {}
        else:
            self.vertexMaps = vertexMaps
        if colorMaps == None:
            self.colorMaps = {}
        else:
            self.colorMaps = colorMaps
        if behaviours == None:
            self.behaviours = {}
        else:
            self.behaviours = behaviours
        if arrows == None:
            arrows = {}
            for key in self.codomains:
                if key in self.colorMaps:
                    cmap = self.colorMaps[key]
                else:
                    cmap = None
                if key in self.vertexMaps:
                    vmap = self.vertexMaps[key]
                else:
                    vmap = None                
                arrows[key] = PartialCoDiMuGraphHom(domain,self.codomains[key],\
                                                    cmap,vmap,self.vertexPos)
                
            
        
        self.domain = domain
        self.arrows = arrows
        
        self.sorted_arrows = self.arrows.keys()
        self.sorted_arrows.sort()
        
        if tags != None:
            self.tags = tags
        else:
            self.tags = {}
        
        self.check()
    
    def __hash__(self):
        return hash(repr(self))
    
    def __repr__(self):
        return "PartialLocalComposition("  + repr(self.domain) + ","\
                    + repr(self.vertexPos) + "," + repr(self.codomains) + ","\
                    + repr(self.vertexMaps) + "," + repr(self.colorMaps) +","\
                    + repr(self.behaviours) + "," + repr(self.tags) + ")"
    
    def repr_as_editor(self):
        return "LocalCompositionEditor("  + repr(self.domain) + ","\
                    + repr(self.vertexPos) + "," + repr(self.codomains) + ","\
                    + repr(self.vertexMaps) + "," + repr(self.colorMaps) +","\
                    + repr(self.behaviours) + "," + repr(self.tags) + ")"
                    
    def __eq__(self,r):
        return self.domain==r.domain and self.vertexPos == r.vertexPos and\
               self.codomains==r.codomains and self.vertexMaps == r.vertexMaps and\
               self.behaviours==r.behaviours and self.tags == r.tags
    
    def check(self):
        """check PartialLocalComposition for integrity and errors"""
        self.errors = 0
        self.integrity_faults = 0
        self.incomplete = 0
        report = ""
        color_images = {}
        self.color_errors = 0
        for color in self.domain.color_set:
            try:
                im = tuple([self.arrows[key].colorMap[color] for key in self.sorted_arrows])
                if im in color_images:
                    self.errors += 1
                    self.color_errors += 1
                    color_images[im] += [color]
                else:
                    color_images[im] = [color]
            except:
                pass # maybe not all colors are defined yet
        if self.color_errors:
            sorted_colors = list(self.domain.color_set)
            sorted_colors.sort()
            report += "The local composition is not color-fast!\n"
            for im in color_images:
                if len(color_images[im]) > 1:
                    lst = color_images[im]
                    lst.sort()
                    report += "    " + ", ".join([repr(x) for x in lst]) + " have the same color images.\n"
                    
        self.arrow_errors = 0
        for name in self.sorted_arrows:
            cod = self.arrows[name]
            if cod.domain != self.domain:
                self.integrity_faults += 1
                report += "The arrow " + repr(name) + "'s domain is not equal to the local compositon domain!\n"
        incomplete_arrows = ""
        erroneous_arrows = ""
        for name in self.sorted_arrows:
            self.arrows[name].check()
            self.errors += self.arrows[name].errors
            self.arrow_errors += self.arrows[name].errors
            self.incomplete += self.arrows[name].incomplete
            if self.arrows[name].incomplete:
                incomplete_arrows += " " + str2(name)
            if self.arrows[name].errors:
                erroneous_arrows += " " + str2(name)
        if self.incomplete:
            report += "There are incomplete arrows:" + incomplete_arrows + "\n"
        if self.arrow_errors:
            report += "There are erroneous arrows:" + erroneous_arrows + "\n"
        report += "\n"
        
        for name in self.sorted_arrows:
            if self.arrows[name].incompatible:
                report += str2(name) + ":\n=" + "="*len(str2(name))+"\n"
                report += self.arrows[name].incompatible_text + "\n"
        
        self.report_text = report
        
    def getDrumCode(self):
        """returns a genConcept string consisting of the current local
        composition"""
        list = ["'A","'B","'L","'R","A","B","L","R","a","b","l","r"]
        strings = []
        if "pre" in self.tags:
            strings = [str2(self.tags["pre"]), "\n"]
        for l in list:
            if l in self.arrows:
                strings.append(":")
                strings.append(l)
                strings.append(" ")
                strings.append(str2(self.arrows[l].getBehaviour()))
                strings.append("\n")
        if "C" in self.tags:
            strings.append(":C ")
            strings.append(str2(self.tags["C"]))
            strings.append("\n")
        return "".join(strings)

    def getDrumAllels(self):
        """returns a genConcept string consisting of the current local
        composition"""
        list = ["'A","'B","'L","'R","A","B","L","R","a","b","l","r"]
        strings = {}
        for l in list:
            if l in self.arrows:
                strings[l] = str2(self.arrows[l].getBehaviour())+"\n"

        if "C" in self.tags:
            strings["C"] = str2(self.tags["C"]) + "\n"

        return strings
    

    def getJamDrumCode(self):
        """returns a genConcept string consisting of the current local
        composition to be used in jam mode """
        list = ["'A","'B","'L","'R","A","B","L","R","a","b","l","r"]
        strings = []
        for l in list:
            if l in self.arrows:
                strings.append(":")
                strings.append(l)
                strings.append(" ")
                strings.append(str2(self.arrows[l].getBehaviour()))
                strings.append("\n")
        if "C" in self.tags:
            strings.append(":C ")
            strings.append(str2(self.tags["C"]))
            strings.append("\n")
        return "".join(strings)                
        
