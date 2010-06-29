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

import term_alg as TA

class Constraint(object):
    """Abstract class modelling a constraint"""
    def __init__(self):
        raise Exception('Constraint is an abstract class that cannot be'+\
                        ' instantiated')

    def __call__(self,obj):
        """Returns True, if obj satisfies the constraint, False otherwise"""
        raise Exception('Constraint satisfaction not defined!')

    def __or__(self,r):
        """Returns the disjunction of self and r"""
        return DisjunctionConstraint(self,r)

    def __and__(self,r):
        """returns the conjunction of self and r"""
        return DisjunctionConstraint(ConjunctionConstraint(self,r))

    def and_domains(self):
        """returns a set of domains that the constraint is part of, useful for
        simplification of general constraints where possible"""
        return frozenset()
    
    def or_domains(self):
        """returns a set of domains that the constraint is part of, useful for
        simplification of general constraints where possible"""
        return frozenset()
    

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
            return '^'.join([str(x) for x in self._constraints])


def flattenDisjConstraints(c):
    disj_c = [l for l in c if isinstance(l,DisjunctionConstraint)]
    conj_c = set([ConjunctionConstraint(l) for l in c \
                  if not isinstance(l,DisjunctionConstraint)])
    plain_conjunctions = set()
    for x in conj_c:
        disjunctions = [d for d in x._constraints \
                        if isinstance(d,DisjunctionConstraint)]
        if not disjunctions:
            plain_conjunctions.add(x)
        else:
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

class AtomarConstraint(Constraint):
    """Constraint with symbolic name and given evaluation function"""
    def __new__(type,*args):
        if not '_list' in type.__dict__:
            type._list = {}
        if args in type._list:
            return type._list[args]
        type._list[args] = object.__new__(type)
            
        return type._list[args]
    
    def __init__(self, name, test):
        self._name = name
        self._test = test

    def __call__(self,obj):
        if self._test(obj):
            return True
        return False

    def __str__(self):
        return str(self._name)


def PseudoNormalize(c):
    """returns the Disjunction-Conjunction-Closure of c"""
    return DisjunctionConstraint(ConjunctionConstraint(c))

def Atom(name,fn=lambda x:False):
    """returns a new atomar constraint, possibly symbolic"""
    return PseudoNormalize(AtomarConstraint(name,fn))
    
def ZeroConstraint():
    """returns the True-projection constraint"""
    return DisjunctionConstraint(ConjunctionConstraint())

def OneConstraint():
    """returns the False-projection constraint"""
    return DisjunctionConstraint()

if __name__ == '__main__':
    A = Atom('A')
    B = Atom('B')
    C = Atom('C')
    D = Atom('D')
    Top = ZeroConstraint()
    Bottom = OneConstraint()

def flattenEqTermArgs(eqs):
    eq_set = []
    for tn in eqs:
        if len(tn) > 1:
            ts = set(tn)
            in_eqs = [e for e in eq_set if ts & e]
            if len(in_eqs) == 1:
                in_eqs[0].update(ts)
            else:
                for e in in_eqs:
                    ts.update(e)
                    eq_set.remove(e)
                eq_set.append(ts)
    return frozenset([frozenset(e) for e in eq_set])

class EqualityTermConstraints(Constraint):
    """class for constraints that equalities on mapped terms,
    i.e. we have a list of tuples like (t_1, .., t_n) which
    represent the formal equation t_1 = ... = t_n. Then the constraint
    tests term-mappings (valuations) phi, whether phi(t_1) = .. = phi(t_n)."""
    def __new__(type,*args):
        if not '_list' in type.__dict__:
            type._list = {}
        flatArgs = flattenEqTermArgs(args)
        if flatArgs in type._list:
            return type._list[flatArgs]
        type._list[flatArgs] = object.__new__(type)
            
        return type._list[flatArgs]

    def __init__(self,*equations):
        """creates the equation frozensets from a list of tuples of terms,
        that represent n-fold equations t_1 = t_2 = .. = t_n"""
        eqs = flattenEqTermArgs(equations)
        self._eqs = eqs

    def __call__(self,phi):
        """test whether for all equations, phi(t_1) = .. = phi(t_n)"""
        for eq in self._eqs:
            it = iter(eq)
            y = phi(it.next())
            try:
                while True:
                    if not (y == phi(it.next())):
                        return False
            except StopIteration:
                return True

    def and_domains(self):
        return frozenset([EqualityTermConstraints])

    def __and__(self,r):
        return EqualityTermConstraints(*(self._eqs | r._eqs))

    def __str__(self):
        def eqstring(eq):
            return "=".join([str(x) for x in eq])
        return '[ ' + " & ".join([eqstring(x) for x in self._eqs])+ ' ]'

def Eq(*terms):
    """Short for EqualityTermConstraints(terms), a single equation"""
    return EqualityTermConstraints(terms)
