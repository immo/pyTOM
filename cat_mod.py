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

#
#  ##   #######        ####
#  ##   ##    ##      ##
#  ##   ##    ##      ##
#  ##   ##    ##       ####
#  ##   ##  ###   ##      ##
#  ##   #####     ##  #####
#

class EquivalenceTest(object):
    """Base class for testing equivalences"""
    def __new__(type,*args):
        if not '_list' in type.__dict__:
            type._list = {}
        if args in type._list:
            return type._list[args]
        type._list[args] = object.__new__(type)
            
        return type._list[args]

    def __init__(self,*parts):
        for p in parts:
            if not type(p) == type(lambda x:0):
                raise Exception('EquivalenceTest requires a set of monary functions!')
        self._parts = parts

    def __call__(self, candidate):
        """Checks whether the candidate fullfills the equivalence"""
        if len(self._parts) < 2:
            return True
        y = self._parts[0](candidate)
        for f in self._parts[1:]:
            if not (f(candidate) == y):
                return False
        return True
#
#  ######    ##    ##    ##    #####     ####
#  ##   ##   ##    ####  ##   ##        ##
#  ##   ##   ##    ## ## ##   ##        ##
#  ######    ##    ##  ####   ## ####    ####
#  ##   ##   ##    ##   ###   ##   ##       ##
#  ##    #   ##    ##    ##    #####    #####
#

class Ring(object):
    """Base class that defines the interfaces that a ring should provide"""
    def __init__(self):
        raise Exception('Ring is an abstract class that cannot be instantiated')

    def __contains__(self,item):
        """Returns true if the given item is element of the ring"""
        raise Exception('Element relation not defined!')

    def __call__(self,name):
        """Returns a special element that is denoted by name, for instance,
        0 and 1 are mapped to the neutral elements accordingly"""
        if name == 0:
            return self.add()
        elif name == 1:
            return self.mul()
        raise Exception('Named element not defined!')        

    def add(self,*elements):
        """Adds the given elements and returns the result, if no element is
        given, returns the neutral element"""
        raise Exception('Ring addition not defined!')

    def mul(self,*elements):
        """Multiplies the given elements (in reading order), if no element is
        given, returns the neutral element"""
        raise Exception('Ring multiplication not defined!')

    def inv(self,e):
        """Returns the additive inverse of the element e"""
        raise Exception('Ring additive-inversion not defined!')

    def Zlmul(self,z,e):
        """Returns (e+e+...+e), the z-fold sum of e"""
        if not type(z) in [int,long]:
            raise Exception('Invalid left-Z-multiplication with non-integer on the left!')
        if z == 0:
            return self.add()
        elif z > 1:
            return self.add(*[e for x in range(z)])
        elif z < -1:
            i = self.inv(e)
            return self.add(*[i for x in range(-z)])
        elif z == 1:
            return e
        elif z == -1:
            return self.inv(e)

    def gen(self):
        """Returns a finite generating set (if exists), i.e. a set such that
        every ring element is representable as finite sum of generating elements"""
        raise Exception('Ring does not have a finite generator!')

    def getterm(self,item):
        """Returns a term in variables and constants that evaluates to a NullaryTerm
        bound to item, when every constant is bound via __call__ and every variable
        is bound as n-th tuple-part of gen(), '+' is bound to add(..) and '*' is
        bound to mul(..) and '.' is bound to Zlmul(..)"""
        raise Exception('Ring does not give terms in generators for elements!')

    def test(self):
        """Returns a set of EquivalenceTests that is sufficient to tell whether a morphism
        defined by the images of gen() that respects 0 and 1 is also a RingHom"""
        raise Exception('Ring does not have a testing set for homomorphisms')

class RingHom(object):
    """Base class for ring homomorphisms"""
    def __init__(self):
        raise Exception\
              ('RingHom is an abstract class that cannot be instantiated')

    def __contains__(self,item):
        """Returns true, if item is a pair (x,y) with y = f(x)"""
        if type(item) == tuple:
            if len(item) == 2:
                if item[0] in self.dom() and \
                   item[1] in self.cod():
                    return item[1] == self(item[0])
        return False

    def __call__(self,item):
        """Returns the image of the item under the homomorphism."""
        raise Exception('Map is not defined!')

    def dom(self):
        """Returns the domain of the homomorphism"""
        raise Exception('Domain is not defined!')
    
    def cod(self):
        """Returns the codomain of the homomorphism"""
        raise Exception('Codomain is not defined!')

    def __mul__(self, r):
        """Returns the covariantly composed RingHom of both operands"""
        return ComposedRingHom(self,r)

class IdRingHom(RingHom):
    """Identity RingHom for given Ring."""
    def __new__(type,*args):
        if not '_list' in type.__dict__:
            type._list = {}
        if args in type._list:
            return type._list[args]
        type._list[args] = object.__new__(type)
            
        return type._list[args]
    
    def __init__(self, ring):
        if not isinstance(ring,Ring):
            raise Exception('IdRingHom needs a Ring as domain')
        self.ring = ring

    def __call__(self,item):
        return item

    def dom(self):
        return self.ring

    def cod(self):
        return self.ring

class ComposedRingHom(RingHom):
    """Composed RingHom for a sequence of given RingHom-s"""        
    def __new__(type, *args):
        if not '_list' in type.__dict__:
            type._list = {}
        flatArgs = flattenComposedRingHomSeries(args)
        if flatArgs in type._list:
            return type._list[flatArgs]
        type._list[flatArgs] = object.__new__(type)
        return type._list[flatArgs]
    
    def __init__(self, *homs):
        if len(homs) < 2:
            raise Exception \
                  ('ComposedRingHom only works with 2 or more RingHom objects')
        self.homs = flattenComposedRingHomSeries(homs)
        for i in range(1,len(self.homs)):
            if not (self.homs[i-1].cod() == self.homs[i].dom()):
                raise Exception \
                      ('At least one codomain in the series is not equal'+\
                       ' to the domain of the following arrow!')

    def __call__(self,item):
        return reduce(lambda i,f:f(i),[lambda x: h(x) for h in self.homs],item)

    def dom(self):
        return self.homs[0].dom()

    def cod(self):
        return self.homs[-1].cod()

def flattenComposedRingHomSeries(homs):
    series = []
    for h in homs:
        if not isinstance(h, RingHom):
            raise Exception('ComposedRingHom only works on RingHom-Series!')
        if type(h) == ComposedRingHom:
            series.extend(h.homs)
        else:
            series.append(h)
    return tuple(series)


class RingZn(Ring):
    """Ring class for integers modulo n"""
    def __new__(type,*args):
        if not '_list' in type.__dict__:
            type._list = {}
        if args in type._list:
            return type._list[args]
        type._list[args] = object.__new__(type)        
        return type._list[args]
    
    def __init__(self,n):
        self._n = n

    def __contains__(self,item):
        return type(item) in [int, long] and 0 <= item < self._n

    def __call__(self,name):
        return int(name)

    def add(self,*elements):
        return sum(elements) % self._n

    def mul(self,*elements):
        return reduce(lambda x,y:x*y, elements, 1) % self._n

    def inv(self,e):
        return (-e) % self._n

    def Zlmul(self,z,e):
        return self.mul(z,e)

    def gen(self):
        return (1,)

    def getterm(self,e):
        return TA.ZConstant(e,1)

    def test(self):
        return (EquivalenceTest(lambda f:f(1), lambda f:f.cod()(1),\
                                lambda f:f.cod().add(*((f(1),)*(self._n+1))))\
                ,)

class RingZ(Ring):
    """Ring class for integers"""
    def __new__(type,*args):
        if not '_the_instance' in type.__dict__:
            type._the_instance = object.__new__(type)
        return type._the_instance
        
    def __init__(self):
        pass

    def __contains__(self,item):
        return type(item) in [int, long]

    def __call__(self,name):
        return int(name)

    def add(self,*elements):
        return sum(elements)

    def mul(self,*elements):
        return reduce(lambda x,y:x*y, elements, 1)

    def inv(self,e):
        return -e

    def Zlmul(self,z,e):
        return self.mul(z,e)    

    def gen(self):
        return (1,)

    def getterm(self,e):
        return TA.ZConstant(e,1)

    def test(self):
        return (EquivalenceTest(lambda f:f(1), lambda f:f.cod()(1))\
                ,)

def evaluateInRing(term,ring,varmap):
    """Evaluates a term in a ring as far as possible, where varmap is a
    dictionary that will be used to map variables to ring objects"""
    t = term
    for v in term.variables():
        t = t.bindvariable(v,varmap[v])
    for c in term.constants():
        t = t.bindconstant(c,ring(c))
    return t.bindfunction('+',ring.add).bindfunction('*',ring.mul)\
           .bindfunction('.',ring.Zlmul).evaluate()

#
#  ##   ##    ####    #####     ##   ##   ##       ######    #####
#  ### ###   ##  ##   ##   ##   ##   ##   ##       ##       ##
#  ## # ##   ##  ##   ##   ##   ##   ##   ##       ##       ##
#  ##   ##   ##  ##   ##   ##   ##   ##   ##       ####      #####
#  ##   ##   ##  ##   ##  ##    ##   ##   ##       ##            ##
#  ##   ##    ####    #####      #####    ######   ######   #####
#


class Module(object):
    """Base class that defines the interfaces a left-R Module should provide"""
    def __init__(self):
        raise Exception \
              ('Module is an abstract class that cannot be instantiated')

    def __contains__(self,item):
        """Returns true if the given item is element of the module"""
        raise Exception('Element relation not defined!')

    def __call__(self,name):
        """Returns a special element that is denoted by name, for instance,
        0 to the neutral element of the module"""
        if name == 0:
            return self.add()
        raise Exception('Named element not defined!')

    def add(self,*elements):
        """Adds the given elements and returns the result, if no element is
        given, returns the neutral element"""
        raise Exception('Module addition not defined!')

    def lmul(self,scalar,item):
        """Evaluates the left ring-action R×M -> M of the module"""
        raise Exception('Left-R action is not defined!')

    def ring(self):
        """Returns the Ring R for which the object is an left-R module"""
        raise Exception('The underlying Ring is not defined!')

    def gen(self):
        """Returns a finite generating set (if exists) of the module"""
        raise Exception('Module does not have a finite generator!')

    def test(self):
        """Returns a set of EquivalenceTests that is sufficient to tell whether a morphism
        defined by the images of gen() that respects 0 is also a ModuleHom"""
        raise Exception('Module does not have a testing set for homomorphisms')

class Module0(Module):
    """Singleton class for the 0-module"""
    def __new__(type,*args):
        if not '_the_instance' in type.__dict__:
            type._the_instance = object.__new__(type)
        return type._the_instance

    def __init__(self):
        self._ring = RingZn(2)
        
    def __contains__(self,item):
        return item == 0

    def add(self,*elements):
        return 0

    def lmul(self,scalar,item):
        return 0

    def ring(self):
        return self._ring

    def gen(self):
        return ()

    def test(self):
        return ()
        

class RingAsModule(Module):
    """Class that will allow a Ring to be viewed as Module"""
    def __new__(type,*args):
        if not '_list' in type.__dict__:
            type._list = {}
        if args in type._list:
            return type._list[args]
        type._list[args] = object.__new__(type)
            
        return type._list[args]
    
    def __init__(self, ring):
        if not isinstance(ring,Ring):
            raise Exception('RingAsModule needs a Ring as domain')
        self._ring = ring

    def __contains__(self,item):
        return self._ring.__contains__(item)

    def add(self,*elements):
        return self._ring.add(*elements)

    def lmul(self,scalar,item):
        return self._ring.mul(scalar,item)

    def ring(self):
        return self._ring

    def gen(self):
        return (self._ring(1),)

    def test(self):
        return ()
    
class ModuleHom(object):
    """Base class for module homomorphisms"""
    def __init__(self):
        raise Exception\
              ('ModuleHom is an abstract class that cannot be instantiated')

    def __contains__(self,item):
        """Returns true, if item is a pair (x,y) with y = f(x)"""
        if type(item) == tuple:
            if len(item) == 2:
                if item[0] in self.dom() and \
                   item[1] in self.cod():
                    return item[1] == self(item[0])
        return False

    def __call__(self,item):
        """Returns the image of the item under the homomorphism."""
        raise Exception('Map is not defined!')

    def dom(self):
        """Returns the domain of the homomorphism"""
        raise Exception('Domain is not defined!')
    
    def cod(self):
        """Returns the codomain of the homomorphism"""
        raise Exception('Codomain is not defined!')

    def phi(self):
        """Returns the underlying ring homomorphism"""
        raise Exception('RingHom is not defined!')

    def __mul__(self, r):
        """Returns the covariantly composed ModuleHom of both operands"""
        return ComposedModuleHom(self,r)

class IdModuleHom(ModuleHom):
    """Identity ModuleHom for given Module."""
    def __new__(type,*args):
        if not '_list' in type.__dict__:
            type._list = {}
        if args in type._list:
            return type._list[args]
        type._list[args] = object.__new__(type)
            
        return type._list[args]
    
    def __init__(self, module):
        if not isinstance(module,Module):
            raise Exception('IdModuleHom needs a Module as domain')
        self.module = module

    def __call__(self,item):
        return item

    def dom(self):
        return self.module

    def cod(self):
        return self.module

    def phi(self):
        return IdRingHom(self.module.ring())

class ComposedModuleHom(ModuleHom):
    """Composed ModuleHom for a sequence of given ModuleHom-s"""        
    def __new__(type, *args):
        if not '_list' in type.__dict__:
            type._list = {}
        flatArgs = flattenComposedModuleHomSeries(args)
        if flatArgs in type._list:
            return type._list[flatArgs]
        type._list[flatArgs] = object.__new__(type)
        return type._list[flatArgs]
    
    def __init__(self, *homs):
        if len(homs) < 2:
            raise Exception \
                  ('ComposedModuleHom only works with 2 or' + \
                   ' more ModuleHom objects')
        self.homs = flattenComposedModuleHomSeries(homs)
        for i in range(1,len(self.homs)):
            if not (self.homs[i-1].cod() == self.homs[i].dom()):
                raise Exception \
                      ('At least one codomain in the series is not equal'+\
                       ' to the domain of the following arrow!')
        self._phi = reduce(lambda f,g:f*g, [h.phi() for h in self.homs])

    def __call__(self,item):
        return reduce(lambda i,f:f(i),[lambda x: h(x) for h in self.homs],item)

    def dom(self):
        return self.homs[0].dom()

    def cod(self):
        return self.homs[-1].cod()

    def phi(self):
        return self._phi

def flattenComposedModuleHomSeries(homs):
    series = []
    for h in homs:
        if not isinstance(h, ModuleHom):
            raise Exception('ComposedModuleHom only works on ModuleHom-Series!')
        if type(h) == ComposedModuleHom:
            series.extend(h.homs)
        else:
            series.append(h)
    return tuple(series)

class DiaffineMap(object):
    """Base class for diaffine maps between Modules"""
    def __new__(type, *args):
        if not '_list' in type.__dict__:
            type._list = {}
        if args in type._list:
            return type._list[args]
        type._list[args] = object.__new__(type)
        return type._list[args]

    def __init__(self,hom,offset):
        """Creates a DiaffineMap from a ModuleHom and an Module element"""
        if not isinstance(hom,ModuleHom):
            raise Exception('DiaffineMap has to be constructed from ModuleHom')
        if not (offset in hom.cod()):
            raise Exception('DiaffineMap offset has to be element of codomain')
        self.hom = hom
        self.offset = offset

    def __call__(self,item):
        """returns the image of item under the diaffine map"""
        return self.hom.cod().add(self.hom(item),self.offset)

    def dom(self):
        """returns the domain of the diaffine map"""
        return self.hom.dom()

    def cod(self):
        """returns the codomain of the diaffine map"""
        return self.hom.cod()    

    def f(self):
        """returns the linear part of the diaffine morphism"""
        return self.hom

    def x(self):
        """returns the offset part of the diaffine morphism"""
        return self.offset

    def __mul__(self,r):
        """returns the covariant composition of diaffine morphisms"""
        return DiaffineMap(self.f() * (r.f()),\
                           r.cod().add(r.f()(self.x()),r.x()))

