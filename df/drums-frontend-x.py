#!/usr/bin/python
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

import sys,os
from df_global import *
from df_print import *

DfGlobal()["prnt.marker"] = "df-x  | "

prnt("   ... drums-frontend-x")

if len(sys.argv) < 2:
    prnt("Error: No pipe basename given! (Try running ./frontend.py instead!)")
    sys.exit(-1)

pipename = sys.argv[1]

pipename_read = pipename+"-x"
prnt("Open",pipename_read,"for reading...")
pipe_read = open(pipename_read,"r")

pipename_write = pipename+"-ui"
prnt("Open",pipename_write,"for writing...")
pipe_write = open(pipename_write,"w")

