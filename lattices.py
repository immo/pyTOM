#
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

i_priorities = {"left hand":['sn14wrock(ord,stxl)',\
                             'sn14wrock(rms,stxl)',\
                             'sn14wrock(prs,stxl)',\
                             'sn14wrock(xtk)',\
                             'tm12rock(ord,stxl)',\
                             'tm12rock(rms,stxl)',\
                             'tm10rock(ord,stxl)',\
                             'tm10rock(rms,stxl)',\
                             'tm14rock(ord,stxl)',\
                             'tm14rock(rms,stx)',\
                             'cy15crash(bel)',\
                             'cy15crash(top)',\
                             'cy15crash(ord)',\
                             'cy15crash(rim)',\
                             'cy15crash(grb)',\
                             'cy18crash(bel)',\
                             'cy18crash(top)',\
                             'cy18crash(ord)',\
                             'cy18crash(rim)',\
                             'cy18crash(grb)',\
                             'cy20ride(bel)',\
                             'cy20ride(ord)',\
                             'cy20ride(rim)',\
                             'cy20ride(grb)',\
                             'hh13(stxl,top)',\
                             'hh13(ord,stxl)',\
                             'hh13(grb)',\
                             'cy8splash(bel)',\
                             'cy8splash(ord)',\
                             'cy8splash(grb)',\
                             'cy19china(top)',\
                             'cy19china(ord)',\
                             'cy19china(grb)'],\
                'right hand': ['sn14wrock(ord,stxr)',\
                               'sn14wrock(rms,stxr)',\
                               'sn14wrock(prs,stxr)',\
                               'sn14wrock(xtk)',\
                               'tm12rock(ord,stxr)',\
                               'tm12rock(rms,stxr)',\
                               'tm10rock(ord,stxr)',\
                               'tm10rock(rms,stxr)',\
                               'tm14rock(ord,stxr)',\
                               'tm14rock(rms,stx)',\
                               'cy15crash(bel)',\
                               'cy15crash(top)',\
                               'cy15crash(ord)',\
                               'cy15crash(rim)',\
                               'cy15crash(grb)',\
                               'cy18crash(bel)',\
                               'cy18crash(top)',\
                               'cy18crash(ord)',\
                               'cy18crash(rim)',\
                               'cy18crash(grb)',\
                               'cy20ride(bel)',\
                               'cy20ride(ord)',\
                               'cy20ride(rim)',\
                               'cy20ride(grb)',\
                               'hh13(stxr,top)',\
                               'hh13(ord,stxr)',\
                               'hh13(grb)',\
                               'cy8splash(bel)',\
                               'cy8splash(ord)',\
                               'cy8splash(grb)',\
                               'cy19china(top)',\
                               'cy19china(ord)',\
                               'cy19china(grb)'],\
                'feet': ['kd20punch','hh13ped']}

def get_empty_rhythmlet():
    x = {}
    for k in i_priorities:
        x[k] = {}
    return x
