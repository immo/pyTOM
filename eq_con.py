# coding: utf-8
#
#   Copyright (C) 2010   C.D. Immanuel Albrecht
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

from __future__ import print_function

class Constraint(object):
    """Abstract class modelling a constraint"""
    def __init__(self):
        raise Exception('Constraint is an abstract class that cannot be'+\
                        ' instantiated')

    def __call__(self,obj):
        """Returns True, if obj satisfies the constraint, False otherwise"""
        raise Exception('Constraint satisfaction not defined!')

class OneConstraint(Constraint):
    """An all-rejecting constraint singleton class"""
    def __new__(type,*args):
        if not '_the_instance' in type.__dict__:
            type._the_instance = object.__new__(type)
        return type._the_instance
        
    def __init__(self):
        pass

    def __call__(self,obj):
        return False

def flattenConjConstraints(c):
    conj_c = [l for l in c if isinstance(l,ConjunctionConstraint)]
    plain_c = set([l for l in c if not isinstance(l,ConjunctionConstraint)])
    s = frozenset(plain_c.union(*[x._constraints for x in conj_c]))
    return s

class ConjunctionConstraint(Constraint):
    """Constraint consisting of the conjunction of other constraints"""
    def __new__(type, *args):
        if not '_list' in type.__dict__:
            type._list = {}
        flatArgs = flattenConjConstraints(args)
        if flatArgs in type._list:
            return type._list[flatArgs]
        type._list[flatArgs] = object.__new__(type)
        return type._list[flatArgs]

    def __init__(self,*constraints):
        self._constraints = flattenConjConstraints(constraints)

    def __call__(self,obj):
        for c in self._constraints:
            if not c(obj):
                return False
        return True

    def __str__(self):
        if len(self._constraints) == 0:
            return "¯|¯"
        elif len(self._constraints) == 1:
            return str(tuple(self._constraints)[0])
        else:
            return ' ^ '.join([str(x) for x in self._constraints])

def flattenDisjConstraints(c):
    disj_c = [l for l in c if isinstance(l,DisjunctionConstraint)]
    conj_c = set([ConjunctionConstraint(l) for l in c \
                  if not isinstance(l,DisjunctionConstraint)])
    plain_conjunctions = set()
    for x in conj_c:
        disjunctions = [d for d in x._constraints \
                        if isinstance(d,DisjunctionConstraint)]
        other = [o for o in x._constraints \
                 if not isinstance(o,DisjunctionConstraint)]
        if not other:
            other = [ConjunctionConstraint()]
        for d in disjunctions:
            other = [ConjunctionConstraint(d1,o) for o in other\
                     for d1 in d._constraints]
        plain_conjunctions = plain_conjunctions.union(other)
            
    s = frozenset(plain_conjunctions.union(*[x._constraints for x in disj_c]))
    if ConjunctionConstraint() in s:
        return frozenset([ConjunctionConstraint()])
    return s


class DisjunctionConstraint(Constraint):
    """Constraint consisiting of the disjunction of other constraints"""
    def __new__(type, *args):
        if not '_list' in type.__dict__:
            type._list = {}
        flatArgs = flattenDisjConstraints(args)
        if flatArgs in type._list:
            return type._list[flatArgs]
        type._list[flatArgs] = object.__new__(type)
        return type._list[flatArgs]

    def __init__(self,*constraints):
        self._constraints = flattenDisjConstraints(constraints)

    def __call__(self,obj):
        for c in self._constraints:
            if c(obj):
                return True
        return False

    def __str__(self):
        if len(self._constraints) == 0:
            return "_|_"
        elif len(self._constraints) == 1:
            return str(tuple(self._constraints)[0])
        else:
            return '('+' v '.join([str(x) for x in self._constraints])+')'
    
def ZeroConstraint():
    return DisjunctionConstraint(ConjunctionConstraint())

def OneConstraint():
    return DisjunctionConstraint()
