#!/bin/python

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
#
# NOTE: This file contains transcribed code from alsa_eq_plugin-0.0.2 which
#       was released under GPLv2
#
from math import *

def limit(v,l,u):
   """limit(v,l,u)    returns v if l <= v <= r, or the nearest bound otherwise"""
   if (v<l):
      return l
   else:
      if (v>u):
         return u
      else:
         return v

def band_biquad(fc, gain, bw, fs):
   """band_biquad(fc, gain, bw, fs)    Calculate biquad for band eq filter with center frequency, gain, bandwidth and sample frequency given."""
   w = 2.0 * pi * limit(fc, 1.0, fs/2.0) / fs
   cw = cos(w)
   sw = sin(w)
   J = 10.0**(gain * 0.025)
   #print (log(2.0)/2.0) * limit(bw, 0.0001, 4.0) * w / sw
   g = sw * sinh((log(2.0)/2.0) * limit(bw, 0.0001, 4.0) * w / sw)
   a0r = 1.0 / (1.0 + (g / J))
   a = [(1.0 + (g * J)) * a0r,\
        (-2.0 * cw) * a0r, \
        (1.0 - (g * J)) * a0r]
   b = [-(a[1]), ((g / J) - 1.0) * a0r]
   return a,b

def lowshelf_biquad(fc, gain, slope, fs):
   """lowshelf_biquad(fc, gain, slope, fs)    Calculate biquad for low shelf filter with center frequency, gain, slope and sample frequency given."""
   w = 2.0 * pi * limit(fc, 1.0, fs/2.0) / fs
   cw = cos(w)
   sw = sin(w)
   A = 10.0**(gain * 0.025)
   b = sqrt(((1.0 + A * A) / limit(slope, 0.0001, 1.0)) \
                      - ((A -  1.0) * (A - 1.0)))
   apc = cw * (A + 1.0);
   amc = cw * (A - 1.0);
   bs = b * sw;
   a0r = 1.0 / (A + 1.0 + amc + bs);

   a = [a0r * A * (A + 1.0 - amc + bs),   \
        a0r * 2.0 * A * (A - 1.0 - apc),  \
        a0r * A * (A + 1.0 - amc - bs) ]
   b = [a0r * 2.0 * (A - 1.0  + apc),     \
        a0r * (-A - 1.0 - amc + bs)]
   return a,b

def highshelf_biquad(fc, gain, slope, fs):
   """highshelf_biquad(fc, gain, slope, fs)    Calculate biquad for high shelf filter with center frequency, gain, slope and sample frequency given."""
   w = 2.0 * pi * limit(fc, 1.0, fs/2.0) / fs
   cw = cos(w)
   sw = sin(w)
   A = 10.0**(gain * 0.025)
   b = sqrt(((1.0 + A * A) / limit(slope, 0.0001, 1.0)) \
            - ((A - 1.0) * (A - 1.0)))
   apc = cw * (A + 1.0)
   amc = cw * (A - 1.0)
   bs = b * sw
   a0r = 1.0 / (A + 1.0 - amc + bs)

   a = [a0r * A * (A + 1.0 + amc + bs),       \
        a0r * -2.0 * A * (A - 1.0 + apc),     \
        a0r * A * (A + 1.0 + amc - bs)]
   b = [a0r * -2.0 * (A - 1.0 - apc),      \
        a0r * (-A - 1.0 + amc + bs)]
   return a,b

def bandpass_biquad(fc, bw, fs):
   """bandpass_biquad(fc, bw, fs)    Calculate biquad for band pass filter with center frequency, bandwidth and sample frequency given."""
   omega = 2.0 * pi * fc/fs
   sn = sin(omega)
   cs = cos(omega)
   alpha = sn * sinh(log(2.0) / 2.0 * bw * omega / sn)
   a0r = 1.0 / (1.0 + alpha)
   a = [a0r * alpha, 0.0, a0r * -alpha]
   b = [a0r * (2.0 * cs), a0r * (alpha - 1.0)]
   return a,b

def lowpass_biquad(fc, bw, fs):
   """lowpass_biquad(fc, bw, fs)    Calculate biquad for low pass filter with center frequency, bandwidth and sample frequency given."""
   omega = 2.0 * pi * fc/fs
   sn = sin(omega)
   cs = cos(omega)
   alpha = sn * sinh(log(2.0) / 2.0 * bw * omega / sn)
   a0r = 1.0 / (1.0 + alpha)
   a = [a0r * (1.0 - cs) * 0.5, a0r * (1.0 - cs), \
        a0r * (1.0 - cs) * 0.5]
   b = [a0r * (2.0 * cs), a0r * (alpha - 1.0)]
   return a,b

def highpass_biquad(fc, bw, fs):
   """highpass_biquad(fc, bw, fs)    Calculate biquad for high pass filter with center frequency, bandwidth and sample frequency given."""
   omega = 2.0 * pi * fc/fs
   sn = sin(omega)
   cs = cos(omega)
   alpha = sn * sinh(log(2.0) / 2.0 * bw * omega / sn)
   a0r = 1.0 / (1.0 + alpha)
   a = [a0r * (1.0 + cs) * 0.5, a0r * -(1.0 + cs), \
        a0r * (1.0 + cs) * 0.5]
   b = [a0r * (2.0 * cs), a0r * (alpha - 1.0)]
   return a,b
