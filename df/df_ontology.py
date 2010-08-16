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

def make_keys1(s):
   """make_keys1(s)    turn string s into a list of keys by magic"""
   ckey = ""
   nkey = 0
   keys = {}
   for c in s+",":
      if c.isalpha():
         ckey = ckey + c
      else:
         if len(ckey) > 0:
            if keys.has_key(ckey):
               keys[ckey] = keys[ckey] + 1
            else:
               keys[ckey] = 1
         ckey = ""
         if c.isdigit():
            nkey = nkey*10 + int(c)
   keys["#"] = nkey
   return keys

def make_keys2(s):
   """make_keys2(s)    turn string s into a list of keys by magic"""
   ckey = ""
   keys = {}
   for c in s+",":
      if c.isalnum():
         ckey = ckey + c
      else:
         if len(ckey) > 0:
            if keys.has_key(ckey):
               keys[ckey] = keys[ckey] + 1
            else:
               keys[ckey] = 1
         ckey = ""
   return keys

def join_keys(k,l):
   """join_keys(k,l)   join the keys lists k and l"""
   j = k
   for x in l:
      if j.has_key(x):
         j[x] = j[x] + l[x]
      else:
         j[x] = l[x]
   return j

def filter_vals_with_key(v, key):
   """filter_vals_with_key(v, key)   filter values from v with key"""
   f = {}
   for x in v:
      k = v[x]
      if k.has_key(key):
         f[x] = k
   return f

def filter_vals_with_any_key(v, keys):
   """filter_vals_with_any_key(v, keys)    filter values from v with any key from keys"""
   f = {}
   for x in v:
      k = v[x]
      for key in keys:
         if k.has_key(key):
            f[x] = k
            break
   return f

def meetleft(features, partners):
   """meetleft(features, partners)   meet features with partners"""
   f = {}
   for x in features:
      if x in partners:
         f[x] = features[x]
   return f

def joinleft(defaultfeatures, newfeatures):
   """joinleft(defaultfeatures, newfeatures)   join features with partners"""
   f = newfeatures
   for x in defaultfeatures:
      f[x] = defaultfeatures[x]
   return f

def get_atomic_depends(vals, keys):
   """get_atomic_depends(vals, keys)    get depends of vals and keys"""
   depends = {}
   for x in keys:
      depends[x] = set([y for y in keys])
   for v in vals:
      has = set([x for x in vals[v] if x in keys])
      for a in has:
         for b in [x for x in depends[a] if x not in has]:
               depends[a].remove(b)
   return depends


def make_keys(s):
   """make_keys(s)    make keys from s by joining both variants"""
   return join_keys(make_keys1(s),make_keys2(s))

def make_feature_list(vals, keys, infos):
   """make_feature_list(vals, keys, infos)   turn vals and keys with infos into a feature_list structure"""
   flist = {}
   for k in keys:
      v = filter_vals_with_key(vals,k)
      i = {}
      for y in [x for x in v if x in infos]:
         i[y] = infos[y]
      flist[k] = i
   return flist
