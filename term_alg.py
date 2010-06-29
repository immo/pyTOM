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

class Term(object):
    """Abstract base class for terms"""
    def __init__(self):
        raise Exception('Term is an abstract class that cannot be instantiated')

    def variables(self):
        """returns the set of all free variables that occur in the term"""
        raise Exception('Term is not defined!')

    def constants(self):
        """returns the set of all constants that occur in the term"""
        raise Exception('Term is not defined!')

    def bound(self):
        """returns the set of all intermediate elements in the term"""
        raise Exception('Term is not defined!')

    def functions(self):
        """returns the set of all unbound non-0-ary symbols in the term"""
        raise Exception('Term is not defined!')

    def boundfunctions(self):
        """returns the set of all bound non-0-ary symbols in the term"""
        raise Exception('Term is not defined!')

    def subterms(self):
        """returns an ordered tuple that consists of all second level subterms"""
        raise Exception('Term is not defined!')

    def isbound(self):
        """returns True, if the main term part (not the necessarily the subterms) has been bound to a function"""
        raise Exception('Term is not defined!')

    def bindfunction(self,name,fn):
        """returns a term where every occurence of name is bound to fn"""
        raise Exception('Abstract Term cannot bind function!')

    def bindvariable(self,name,item):
        """returns a term where every occurence of name is bound to fn"""
        raise Exception('Abstract Term cannot bind variable!')

    def bindconstant(self,name,item):
        """returns a term where every occurence of name is bound to fn"""
        raise Exception('Abstract Term cannot bind constant!')

    def rebindnullary(self,fn):
        """returns a term where every bound nullary term is mapped by fn"""
        raise Exception('Abstract Term cannot bind constant!')

    def evaluate(self):
        """returns a partially evaluated term, possibly a bound NullaryTerm"""
        raise Exception('Abstract Term cannot evaluate')

    def __add__(self,r):
        return FunctionTerm('+',False,self,r)

    def __mul__(self,r):
        return FunctionTerm('*',False,self,r)

    def __mod__(self,r):
        return FunctionTerm('%',False,self,r)

    def __pow__(self,r):
        return FunctionTerm('**',False,self,r)

    def __sub__(self,r):
        return FunctionTerm('-',False,self,r)

    def __div__(self,r):
        return FunctionTerm('/',False,self,r)


class NullaryTerm(Term):
    """Class for 0-ary terms (elementary terms)"""
    def __new__(type,*args):
        if not '_list' in type.__dict__:
            type._list = {}
        if args in type._list:
            return type._list[args]
        type._list[args] = object.__new__(type)
            
        return type._list[args]

    def __init__(self, element, t):
        self._constants = frozenset()
        self._variables = frozenset()
        self._bound = frozenset()
        if not t in ['x','c','b']:
            raise Exception('NullaryTerm must either be of type x,c or b!')
        elif t == 'x':
            self._variables = frozenset((element,))
        elif t == 'c':
            self._constants = frozenset((element,))
        elif t == 'b':
            self._bound = frozenset((element,))            
        self._element = element
        self._b = t == 'b'
        self._t = t

    def constants(self):
        return self._constants

    def variables(self):
        return self._variables

    def bound(self):
        return self._bound

    def subterms(self):
        return ()

    def functions(self):
        return frozenset()

    def boundfunctions(self):
        return frozenset()

    def isbound(self):
        return self._b

    def getelement(self):
        return self._element

    def bindfunction(self,name,fn):
        return self
    
    def bindvariable(self,name,item):
        if self._t == 'x' and self._element == name:
            return NullaryTerm(item,'b')
        return self
    
    def bindconstant(self,name,item):
        if self._t == 'c' and self._element == name:
            return NullaryTerm(item,'b')
        return self

    def rebindnullary(self,fn):
        if self._t == 'b':
            return NullaryTerm(fn(self._element),'b')
        return self

    def evaluate(self):
        return self

    def __str__(self):
        if self._b:
            return str(self._element)
        elif self._t == 'x':
            return 'X'+str(self._element)
        else:
            return 'C'+str(self._element)
    
def Constant(x):
    """wrapper for NullaryTerm(x,'c')"""
    return NullaryTerm(x,'c')

def Variable(x):
    """wrapper for NullaryTerm(x,'x')"""
    return NullaryTerm(x,'x')

def Bound(x):
    """wrapper for NullaryTerm(x,'b')"""
    return NullaryTerm(x,'b')

def ZBound(z,x):
    """wrapper for FunctionTerm('.',False,Bound(z),Bound(x))"""
    return FunctionTerm('.',False,Bound(z),Bound(x))

def ZVariable(z,x):
    """wrapper for FunctionTerm('.',False,Bound(z),Variable(x))"""
    return FunctionTerm('.',False,Bound(z),Variable(x))

def ZConstant(z,x):
    """wrapper for FunctionTerm('.',False,Bound(z),Constant(x))"""
    return FunctionTerm('.',False,Bound(z),Constant(x))

def Function(symbol,*terms):
    """wrapper for FunctionTerm(symbol,False,*terms)"""
    return FunctionTerm(symbol,False,*terms)

def ZFunction(z,symbol,*terms):
    """wrapper for FunctionTerm('.',False,Bound(z),Function(symbol,*terms))"""
    return FunctionTerm('.',False,Bound(z),Function(symbol,*terms))

def ZLMul(z,term):
    """wrapper for FunctionTerm('.',False,Bound(z),term)"""
    return FunctionTerm('.',False,Bound(z),term)

# even shorter

C = Constant
X = Variable
B = Bound
F = Function
ZB = ZBound
ZX = ZVariable
ZC = ZConstant
ZF = ZFunction
Z = ZLMul

def f(*terms):
    """wrapper for FunctionTerm('f',False,*terms)"""
    return FunctionTerm('f',False,*terms)

class FunctionTerm(Term):
    """Class for non-0-ary terms"""
    def __new__(type,*args):
        if not '_list' in type.__dict__:
            type._list = {}
        if args in type._list:
            return type._list[args]
        type._list[args] = object.__new__(type)
            
        return type._list[args]

    def __init__(self, element, b, *subterms):
        for t in subterms:
            if not isinstance(t,Term):
                raise Exception('FunctionTerm: subterms must be Terms!')
        if not type(b) == bool :
            raise Exception('FunctionTerm: b must be boolean (bound)')
        if b:
            self._bound = frozenset((element,))
            self._functions = frozenset()
        else:
            self._bound = frozenset()
            self._functions = frozenset((element,))
        self._element = element
        self._subterms = subterms
        self._b = b

    def constants(self):
        return frozenset(set().union(*[t.constants() for t in self.subterms()]))

    def variables(self):
        return frozenset(set().union(*[t.variables() for t in self.subterms()]))

    def bound(self):
        return frozenset(set().union(*[t.bound() for t in self.subterms()]))

    def boundfunctions(self):
        return frozenset(set().union(self._bound,\
                           *[t.boundfunctions() for t in self.subterms()]))

    def functions(self):
        return frozenset(set().union(self._functions,\
                           *[t.functions() for t in self.subterms()]))

    def subterms(self):
        return self._subterms

    def isbound(self):
        return self._b

    def bindfunction(self,name,fn):
        if (not self._b) and self._element == name:
            return FunctionTerm(fn,True,\
                                *[t.bindfunction(name,fn) for t in self._subterms])
        return FunctionTerm(self._element,self._b,\
                            *[t.bindfunction(name,fn) for t in self._subterms])
    
    def bindvariable(self,name,item):
        return FunctionTerm(self._element,self._b,\
                        *[t.bindvariable(name,item) for t in self._subterms])
    
    def bindconstant(self,name,item):
        return FunctionTerm(self._element,self._b,\
                        *[t.bindconstant(name,item) for t in self._subterms])

    def rebindnullary(self,fn):
        return FunctionTerm(self._element,self._b,\
                        *[t.rebindnullary(fn) for t in self._subterms])

    def evaluate(self):
        ev_subterms = [t.evaluate() for t in self._subterms]
        if not self._b:
            return FunctionTerm(self._element,self._b,*ev_subterms)
        for t in ev_subterms:
            if not (isinstance(t,NullaryTerm) and t.isbound()):
                return FunctionTerm(self._element,self._b,*ev_subterms)
        y = self._element(*[t.getelement() for t in ev_subterms])
        return NullaryTerm(y,'b')

    def __str__(self):
        if len(self._subterms) == 1:
            return str(self._element)+'('+str(self._subterms[0])+')'
        elif len(self._subterms) == 2:
            return '('+str(self._subterms[0])+" "+str(self._element)+" "+\
                   str(self._subterms[1])+')'
        else:
            return str(self._element)+'('+\
                   ", ".join([str(x) for x in self._subterms])+')'
    

