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

import sys,fcntl,subprocess,os,tempfile,math
from base64 import b64encode

randStr = lambda n: b64encode(os.urandom(int(math.ceil(0.75*n))),'-_')[:n]



print("drums-frontend, v0.2 (c) 2009/10, Immanuel Albrecht, GPLv3")

frontend_path = os.path.dirname(sys.argv[0]) + os.path.sep
print(frontend_path)

pipename = os.path.join(tempfile.mkdtemp(),randStr(12))

os.mkfifo(pipename+"-x")
os.mkfifo(pipename+"-ui")

ui_args = tuple([frontend_path+"drums-frontend-ui.py",pipename]+sys.argv[1:])
ui = subprocess.Popen(ui_args)
x_args = tuple([frontend_path+"drums-frontend-x.py",pipename]+sys.argv[1:])
x = subprocess.Popen(x_args)

ui.wait()
x.wait()

os.remove(pipename+"-x")
os.remove(pipename+"-ui")
os.rmdir(os.path.dirname(pipename))
