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

import xml.dom.minidom as minidom
import xml.dom.ext as xmlext

class ostringstream(object):
    def __init__(self):
       self.s = ""
    def __str__(self):
        return self.s
    def write(self,x):
        self.s += str(x)


def dic_extend(dic, dic2):
    for key in dic2:
        dic[key] = dic2[key]

def copy_dic_thing(thing):
    c = {}
    for k in thing:
        if not k.startswith('*'):
            c[k] = thing[k]
    return c

def copy_things(things):
    return map(copy_dic_thing,things)


def things_to_xml(things):
    """returns an xml representation of the things"""
    plain_data = copy_things(things)
    doc = minidom.Document()
    root = doc.createElement("things")
    doc.appendChild(root)
    for t in plain_data:
        node = doc.createElement("thing")
        keys = t.keys()
        keys.sort()
        for key in keys:
            knode = doc.createElement(key)
            node.appendChild(knode)
            value = doc.createTextNode(repr(t[key]))
            knode.appendChild(value)
        root.appendChild(node)
    as_str = ostringstream()
    xmlext.PrettyPrint(doc,as_str)
    return str(as_str)

def xml_to_things(doc):
    """returns a list of maps representation of things from xml"""
    xmlroot = minidom.parseString(doc)
    things = []
    for node in xmlroot.childNodes:
        if node.nodeName == "things":
            for thingnode in node.childNodes:
                if thingnode.nodeName == "thing":
                    thing = {}
                    keys = filter(lambda x:x.nodeType==1,\
                                  thingnode.childNodes)
                    for k in keys:
                        thing[k.nodeName] = eval(k.firstChild.data)
                    things.append(thing)
    return things
