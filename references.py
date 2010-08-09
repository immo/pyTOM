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

class ImmutableObject(object):
    def __setattr__(self,x):
        raise Exception("ImmutableObject cannot be changed")
    __delattr__ = __setattr__
    def __getattribute__(self,x):
        return super(ImmutableObject, self).__getattribute__("_obj")\
               .__getattribute__(x)
    def __init__(self,obj):
        super(ImmutableObject, self).__setattr__('_obj',obj)

class ReferenceObject(object):  
    def __init__(self, o):
        """Create an ReferenceObject wrapper for an mutable object o"""
        super(ReferenceObject, self).__setattr__('_watchers',set())        
        super(ReferenceObject, self).__setattr__('_o',o)
        
    def __getattribute__(self,a):
        if str(a).endswith('____ref'):
            return super(ReferenceObject, self).__getattribute__('_o')
        elif str(a).endswith('____update'):
            return super(ReferenceObject, self).__getattribute__('update')
        elif str(a).endswith('____readonly'):
            return ImmutableObject(super(ReferenceObject, self)\
                               .__getattribute__('_o'))
        elif str(a).endswith('____watchers'):
            return super(ReferenceObject, self).__getattribute__('_watchers')
        elif str(a).endswith('____watch'):
            return super(ReferenceObject, self).__getattribute__('watch')
        elif str(a).endswith('____unwatch'):
            return super(ReferenceObject, self).__getattribute__('unwatch')
        return super(ReferenceObject, self).__getattribute__('_o')\
               .__getattribute__(a)
    
    def __setattr__(self,a,x):
        super(ReferenceObject, self).__getattribute__('_o').__setattr__(a,x)
        super(ReferenceObject, self).__getattribute__('update')(a,x)
        
    def update(self,attribute,newvalue):
        watchers = super(ReferenceObject, self).__getattribute__('_watchers')
        for w in watchers:
            if type(w) == type(lambda x:0):
                w(attribute,newvalue)
            else:
                w.update(attribute,newvalue)

    def watch(self,watcher):
        watchers = super(ReferenceObject, self).__getattribute__('_watchers')
        watchers.add(watcher)

    def unwatch(self,watcher):
        watchers = super(ReferenceObject, self).__getattribute__('_watchers')
        watchers.remove(watcher)
