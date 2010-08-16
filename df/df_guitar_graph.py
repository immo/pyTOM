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

from df_codimugraph import *
from df_global import *
import copy
import tempfile
import os
from sys import version_info

def compileWithLilyPond(lily):
    """ writes lily to a temporary file and calls lilypond on it,
    returns the path to a png file that contains the lilypond data"""
    if version_info < (2,6):
        f = tempfile.NamedTemporaryFile()
        file_name = f.name
        f.close()
        f = open(file_name,"w+b")
    else:
        f = tempfile.NamedTemporaryFile(delete=False)
    f.write(lily)
    name = f.name
    f.close()
    command = "lilypond -dresolution=104 -dno-point-and-click -dbackend=eps -dno-gs-load-fonts -dinclude-eps-fonts --png -o %s %s" % (name,name)
    pngname = name + ".png"
    os.system(command)
    return pngname

    

def splitMulti2(string, sep=[" ,;"], i0=0, l=0, head=""):
    """seperate string at each occurence of an elt of sep helper"""
    if i0 < l:
        s0 = string[i0]
        if s0 in sep:
            if head:
                return [head, s0] + splitMulti2(string,sep,i0+1,l,"")
            else:
                return [s0] + splitMulti2(string,sep,i0+1,l,"")
        else:
            return splitMulti2(string,sep,i0+1,l,head+s0)
    else:
        if head:
            return [head]
        else:
            return []

def splitMulti(string, sep=[" ,;"]):
    """seperate string at each occurence of an elt of sep helper"""
    return splitMulti2(string,sep,0,len(string),"")

    
class GuitarMN(object):
    def __init__(self,state=None):
        if state == None:
            self.state = self.fix({})
        else:
            self.state = state
        self.last = {}
        for k in self.state:
            self.last[k] = None
        self.last["time"] = -1

    def __repr__(self):
        return "GuitarMN(" + repr(self.state) + ")"

    def fix(self, state):
        """ fix the given state argument, if possible """
        if "art" in state: # articulations
            if not state["art"] in ["none","pm","once-pm","once-squeak",\
                                    "sweep-up","sweep-down","sweep",\
                                    "once-up", "once-down", "once-sweep"]:
                state["art"] = "none"
        else:
            state["art"] = "none"
            
        if "trem" in state: # tremolo variants
            if not state["trem"] in ["none","tremolo","trill+1","trill+2",\
                                     "trill+3","trill+4"]:
                state["trem"] = "none"
        else:
            state["trem"] = "none"

        if "scale" in state: # scale
            state["scale"] = [int(i) for i in state["scale"]]
        else:
            state["scale"] = [0,2,4,5,7,9,11]

        if "base" in state: # base tone, GDGCFAD = -29,-22,-17,-12,-7,-3,2
            state["base"] = int(state["base"])
        else:
            state["base"] = -24 # 5th fret on 7th string

        if "chord" in state: # chord type, offsets of base tone
            state["chord"] = [int(i) for i in state["chord"]]
        else:
            state["chord"] = [0]

        if "pitch" in state: # current referenced scale position
            state["pitch"] = int(state["pitch"])
        else:
            state["pitch"] = 0

        if "octave" in state: # current octave for referenced scale
            state["octave"] = int(state["octave"])
        else:
            state["octave"] = 0

        if "time" in state: # current time-length, 3 indicates 2/3,
            #                 5 indicates 1.5-length
            state["time"] = int(state["time"])
        else:
            state["time"] = 4
                
        return state

    def getPitch(self, p):
        """ return the pitch p as lilypond string """
        q = int(p)
        octave = (q+12)/12
        note = q % 12
        txt = ["c","cis","d","dis","e","f","fis","g","gis","a","ais","b"]
        return txt[note] + "'"*octave + ","*(-octave)

    def getStringChoice(self, pitches):
        """returns a list of strings that are suggested for the pitches"""
        tuning = [2,-3,-7,-12,-17,-22,-29] # string tuning of my guitar :)
        good_shapes = [[0]] + [[0,i] for i in range(5)]\
                      + [[i,0] for i in range(4)] \
                      + [[0,-1,0],[0,-1,1],[0,-1,2],[0,-1,3], \
                         [0,2,2],[0,1,2],[0,0,2],[0,2,3],[3,2,0],\
                         [3,1,0],[0,1,3],[1,0,3],[2,0,3],[3,1,0,0],\
                         [3,2,0,0],[1,0,1,1],[1,0,2,3],[1,0,2],[1,0,2,2],\
                         [0,0,0,2],[0,0,0,2,2],[0,0,0,3],[0,0,0,2,3],\
                         [0,0,3],[0,0,2,2],[0,0,2,3],[1,0,2,2],[2,0,0],\
                         [0,1,2,3],[0,1,2,2],[1,0,1],[2,0,2],[0,1,1]] \
                        + [[0]*i for i in range(2,8)]
        pitch_count = map(lambda x: len(filter(lambda y: y >= 0,x)),\
                          good_shapes)
        nbr = len(pitches)
        candidates = map(lambda x:x[0], \
                         filter(lambda x: x[1] == nbr,\
                                zip(good_shapes,pitch_count) ) )
        s = []
        p = []
        for c in candidates:
            for lowest in range( len(c), 8):
                s_assign = []
                p_assign = []
                for q in zip(c,xrange(0,-8,-1)):
                    if q[0] >= 0:
                        s_assign += [lowest + q[1]]
                        p_assign += [tuning[lowest+q[1]-1]]
                p_choice = map(lambda x: x[1] - x[0], zip(p_assign,pitches))
                correct = 1
                d = filter(lambda x:x>=0, c)
                for i in range(1,len(p_choice)):
                    if p_choice[i]-p_choice[0] != d[i]-d[0]:
                        correct = 0
                        break
                if correct:
                    if min(p_choice) >= 0 and max(p_choice) <= 24:
                        s += [s_assign]
                        p += [p_choice]

        best = []
        results = zip(s,p)
        if results:
            best = results[0]
            
        for choice in results[1:]:
            if (min(best[1]) < 5 and min(choice[1]) >= 5) or \
               (max(best[1]) > 12 and max(choice[1]) <= 12) or \
               (min(best[1]) > min(choice[1]) and (min(choice[1]) >= 5)\
                and (max(choice[1]) <= 12)):
                best = choice

        if best:
            return best[0]
        else:
            return []



                                     
                
                        

    def getStateCode(self, rest=False, adjust_strings=False):
        """ express the current state as played note(s) w.r.t. the last state """
        state = self.state
        last = self.last

        time = state["time"]
        last_time = last["time"]

        triplet = ""
        
        if last_time != time:
            if (last_time%3 == 0) != (time%3 == 0):
                if time%3:
                    triplet = " } { "
                else:
                    triplet = " } \\times 2/3 { "
            if time%15 == 0:
                time = str(time/15) + "."
            elif time%5 == 0:
                time = str(time/5) + "."
            elif time%3 == 0:
                time = str(time/3)
            else:
                time = str(time)
        else:
            time = ""

        base = state["base"]
        scale = state["scale"]
        n_scale = len(scale)
        if rest:
            lily_pitch = "r"
        else:
            ptch = state["pitch"]

            pitch = base + scale[ptch % n_scale] + 12*(ptch / n_scale) + 12*state["octave"]
            pitches = [pitch + i for i in state["chord"] ]

            if adjust_strings:
                string_suggestion = self.getStringChoice(pitches)
            else:
                string_suggestion = []

            if len(pitches) > 1:
                if string_suggestion:
                    lily_pitch = "< " + " ".join(map(lambda x:self.getPitch(x[0])+"\\"+str(x[1]), zip(pitches,string_suggestion))) + " >"
                else:
                    lily_pitch = "< " + " ".join(map(lambda x:self.getPitch(x), pitches)) + " >"
            else:
                lily_pitch = self.getPitch(pitches[0])
                if string_suggestion:
                    time += "\\"+str(string_suggestion[0])
                
        self.last = copy.deepcopy(state)

        modifier = ""
        if not rest:
            if state["art"] in ["sweep-up","once-up"]:
                modifier += '_\\markup{\\fontsize #-5 "up"}'

            if state["art"] in ["sweep-down","once-down"]:
                modifier += '_\\markup{\\fontsize #-5 "dn."}'

            if state["art"] in ["sweep","once-sweep"]:
                modifier += '_\\markup{\\fontsize #-5 "sw."}'
                
            if state["art"] in ["pm","once-pm"]:
                modifier += '_\\markup{\\fontsize #-5 "p.m."}'

            if state["art"] == "once-squeak":
                modifier += '_\\markup{\\fontsize #-5 "sq."}'

            if state["trem"] != "none":
                if state["trem"].startswith("trill"):
                    modifier += '^\\markup{\\fontsize #-4 "' \
                                + state["trem"][5:] +'"}'
                else:
                    modifier += '^\\markup{\\fontsize #-4 "tr."}'


        if state["art"].startswith("once-"):
            state["art"] = "none"

                
        return triplet + lily_pitch + time + modifier + "\n\t\t"

    def lily(self, command, adjust_strings=False):
        """ return a string with lilypond code corresponding to command,
        generated with current object as starting point """

        chord_stack = []
        scale_stack = []
        base_stack = []

        nbr_stack = {0: chord_stack, 1:[]}

        def sel_base():
            nbr_stack[0] = base_stack
            return ""

        def sel_chord():
            nbr_stack[0] = chord_stack
            return ""

        def sel_scale():
            nbr_stack[0] = scale_stack
            return ""

        def sel_free():
            nbr_stack[0] = []
            return ""

        def app_base():
            try:
                self.state["base"] = base_stack[0] - 24
                base_stack.__delitem__(0)
            except IndexError:
                pass
            return ""        

        def app_scale():
            if len(scale_stack):
                self.state["scale"] = scale_stack
            else:
                self.state["scale"] = [0,2,4,5,7,9,11]
            return ""

        def app_chord():
            if len(chord_stack):
                self.state["chord"] = chord_stack
            else:
                self.state["chord"] = [ 0 ]
            return ""

        def nbr_push():
            nbr_stack[1].append(copy.copy(nbr_stack[0]))
            return ""

        def nbr_pop():
            nbr_stack[0].__init__()            
            try:
                nbr_stack[0].extend(nbr_stack[1].pop())
            except IndexError:
                pass
            return ""

        def nbr_reset():
            nbr_stack[0].__init__()
            return ""

        def nbr_remove():
            nbr_stack[0].pop()
            return ""

        def nbr_duplicate_top():
            try:
                nbr_stack[0].append(nbr_stack[0][-1])
            except IndexError:
                pass
            return ""

        def set_squeak():
            self.state["art"] = "once-squeak"
            return ""

        def set_once_pm():
            self.state["art"] = "once-pm"
            return ""

        def set_sweep():
            self.state["art"] = "sweep"
            return ""

        def set_sweep_up():
            self.state["art"] = "sweep-up"
            return ""

        def set_sweep_down():
            self.state["art"] = "sweep-down"
            return ""

        def set_sweep_once():
            self.state["art"] = "once-sweep"
            return ""

        def set_sweep_up_once():
            self.state["art"] = "once-up"
            return ""

        def set_sweep_down_once():
            self.state["art"] = "once-down"
            return ""

        def set_pm():
            self.state["art"] = "pm"
            return ""

        def set_normal_art():
            self.state["art"] = "none"
            return ""

        def set_normal_stroke():
            self.state["trem"] = "none"
            return ""

        def set_trem():
            lvls = ["none","tremolo","trill+1","trill+2",\
                                     "trill+3","trill+4"]
            rot = ["tremolo","trill+1","trill+2","trill+3",\
                                     "trill+4","none"]
            try:
                self.state["trem"] = rot[lvls.index(self.state["trem"])]
            except:
                pass
            return ""

        def set_pitch0():
            self.state["pitch"] = 0
            return ""

        def set_pitchup():
            self.state["pitch"] = self.state["pitch"] + 1
            return ""

        def set_pitchdown():
            self.state["pitch"] = self.state["pitch"] - 1
            return ""

        def set_time4():
            self.state["time"] = 4
            return ""

        def set_time3():
            if self.state["time"] % 3:
                self.state["time"] = 3*self.state["time"]
            return ""

        def set_time5():
            if self.state["time"] % 5:
                self.state["time"] = 5*self.state["time"]
            return ""

        def set_timeStraight():
            if self.state["time"] % 3 == 0:
                self.state["time"] = self.state["time"]/3
            if self.state["time"] % 5 == 0:
                self.state["time"] = self.state["time"]/5
            return ""

        def set_time_up():
            if self.state["time"] % 32:
                self.state["time"] = 2 * self.state["time"]
            return ""

        def set_time_down():
            if self.state["time"] % 2 == 0:
                self.state["time"] = self.state["time"] / 2
            return ""

        def mk_code():
            return self.getStateCode(adjust_strings=adjust_strings)

        def mk_rest():
            return self.getStateCode(True,adjust_strings=adjust_strings)

        def set_time_from_stack():
            try:
                v = nbr_stack[0].pop()
                self.state["time"] = v
            except:
                pass
            return ""

        def set_pitch_from_stack():
            try:
                v = nbr_stack[0].pop()
                self.state["pitch"] = v
            except:
                pass
            return ""

        def mk_pitch_from_stack():
            set_pitch_from_stack()
            return mk_code()

        def set_octave0():
            self.state["octave"] = 0
            return ""

        def set_octave_up():
            self.state["octave"] += 1
            return ""

        def set_octave_down():
            self.state["octave"] -= 1
            return ""
        

        cmd_list = splitMulti(command,list(" [](){}&$%_sxXtT#+-~!=:@^'\"/\\,.;<>OrUDBudb"))

        actions = {'[': sel_scale, '(': sel_chord, '{': sel_base,\
                   ']': app_scale, ')': app_chord, '}': app_base,\
                   '&': nbr_push,  '$': nbr_pop,   '%': nbr_reset,\
                   '_': set_normal_art, 'x': set_once_pm,\
                   'X': set_pm, 's': set_squeak, 't': set_normal_stroke,\
                   'T': set_trem, '#': set_pitch0, '+': set_pitchup,\
                   '-': set_pitchdown, '~': sel_free, '!': nbr_remove,\
                   '=': nbr_duplicate_top, ":":mk_code, '@': set_time4,\
                   '^': set_time3, "'": set_timeStraight, '"': set_time5, \
                   '/': set_time_up, "\\": set_time_down, ',': set_time_from_stack,\
                   '.': set_pitch_from_stack, ';': mk_pitch_from_stack, \
                   '<': set_octave_down, '>': set_octave_up, 'O': set_octave0, \
                   'r': mk_rest, 'U':set_sweep_up,'D':set_sweep_down,\
                   'B': set_sweep, 'u':set_sweep_up_once,'d':set_sweep_down_once,\
                   'b': set_sweep_once \
                   }
        
        def token_fct(t):
            fn = actions.get(t,None)
            if fn:
                return fn()
            else:
                try:
                    nbr = int(t)
                    s = nbr_stack[0]
                    s.append(nbr)
                except ValueError:
                    pass
                return ""
            
        lily_list = map(token_fct, cmd_list)
        # debug info
        print nbr_stack
        print "chord:", chord_stack
        print "scale:", scale_stack
        print "base:", base_stack
        print "-"*20
        print self.state
        return "".join(["{ "] + lily_list + [" }"])


def gtr2lily(s, adjust_strings=False):
    return GuitarMN().lily(s, adjust_strings)

def gtr2LY(s):
    clef = gtr2lily(s)
    tab = gtr2lily(s,True)
    return """
\\version "2.12.1"

tuning = #'(2 -3 -7 -12 -17 -22 -29) %% set tuning to GDGCFAD


\\paper{
indent=0\\mm
%% #(define dump-extents #t)
line-width=120\\mm
oddFooterMarkup=##f
oddHeaderMarkup=##f
bookTitleMarkup = ##f
scoreTitleMarkup = ##f
print-page-number = ##f
between-system-padding=100\\cm
page-top-space = 0\\cm
head-separation = 0\\cm
}



  \\score{

    \\new StaffGroup <<
      \\new Staff \\transpose c c {
        \\clef "treble_15"
        %s
        }
        
      \\new TabStaff \\transpose c c {
        \\set TabStaff.stringTunings = #tuning
        %s
        }
    >>


  }

        """% (clef,tab)
        

class GuitarGraph(CoDiMuGraph): #work in progress
    """ Hard-coded graph for parameter space """
    def __init__(self):
        self.universal_colors = []
        self.wildcard_vertices = []

        self.scales = { 'major': [0,2,4,5,7,9,11],\
                        'minor': [0,2,3,5,7,8,10],\
                        'phrygian': [0,1,3,5,7,8,10],\
                        'bimodal': [0,2,3,4,5,7,8,9,10,11],\
                        'blues': [0,3,5,6,7,10], \
                        'pentatonic': [0,2,5,7,9] }

        self.chords = { 'base note': [0],\
                        'base note+1':[1],\
                        'base note-1':[-1],\
                        'quint': [0,7],\
                        'power': [0,7,12],\
                        'quart': [0,5],\
                        'inv.power': [0,5,12],\
                        '3rd maj.': [0,4],\
                        '3rd min.': [0,3],\
                        '3rd maj.+5': [0,4,7],\
                        '3rd min.+5': [0,3,7],\
                        'okt': [0,12],\
                        'sep.min.+5': [0,7,10],\
                        'bi-quart': [0,5,10],\
                        'bi-quint': [0,7,14],\
                        'power+':[0,7,12,19,24],\
                        '3rd maj.+8': [0,4,12],\
                        '3rd min.+8': [0,3,12],\
                        'dim-power':[0,6,11],\
                        'bi-triton.':[0,6,12],\
                        'tritonus': [0,6],\
                        'bi-3rdmaj.':[0,4,8],\
                        'power+3':[0,7,12,16],\
                        'power+3m':[0,7,12,15],\
                        'power+3-':[0,7,12,14],\
                        'tri-quart':[0,5,10,15],\
                        '3maj.+7+9#':[0,4,10,15],\
                        '3maj.+7+10':[0,4,10,16],\
                        'quint+8#':[0,7,13],\
                        'quart+8#':[0,5,13],\
                        'quint#':[0,8],\
                        'quint#+8':[0,8,12]\
                        }

        self.base_notes = {'c':0,'cis':1,'d':2,'dis':3,\
                           'e':4,'f':5,'fis':6,'g':-5,\
                           'gis':-4,'a':-3,'ais':-2,'b':-1}

        timings =      {'whole'      :1,\
                        'half'       :2,\
                        'quarter'    :4,\
                        'eighth'     :8,\
                        '16th'       :16,\
                        '32nd'       :32 }

        self.timings = {}
        for k in timings:
            self.timings[k] = timings[k]
            self.timings[k+" [2/3]"] = timings[k]*3
            self.timings[k+"."] = timings[k]*5
            self.timings[k+".[2/3]"] = timings[k]*15

        self.expressions = {'oct.up': '>',\
                            'oct.zero': 'O',\
                            'oct.down':'<',\
                            'pitch up':'+',\
                            'pitch down':'-',\
                            'pitch zero':'#',\
                            'time up':'/',\
                            'time 4th': '@',\
                            'time down':'\\',\
                            'straight':"'",\
                            'triplet':'^',\
                            'dotted':'"',\
                            'normal':'_',\
                            'once-pm':'x',\
                            'pm':'X',\
                            'squeak':'s',\
                            'single':'t',\
                            'tremolo':'tT',\
                            'trill+1':'tTT',\
                            'trill+2':'tTTT',\
                            'trill+3':'tTTTT',\
                            'trill+4':'tTTTTT',\
                            'rest':'r',\
                            'chord':':',\
                            'chord*2':'::',\
                            'chord*3':':::',\
                            'chord*5':':::::',\
                            'chord*7':':::::::',\
                            'sweep': 'B',\
                            'sweep-up': 'U',\
                            'sweep-down': 'D',\
                            'once-sweep':'b',\
                            'once-up':'u',\
                            'once-down':'d' }

                            
        
        expressions_order = ['oct.up','oct.zero','oct.down','pitch up',\
                             'pitch zero','pitch down','time up',\
                             'time 4th','time down','straight','triplet',\
                             'dotted','normal','once-pm','pm','squeak',\
                             'sweep','sweep-up','sweep-down',\
                             'once-sweep','once-up','once-down',\
                             'single','tremolo','trill+1','trill+2',\
                             'trill+3','trill+4','rest','chord', 'chord*2',\
                             'chord*3', 'chord*5','chord*7']

        self.pitches =  {}
        for i in range(-5,12):
            self.pitches[str(i)+"-step"] = i
                        
        
        self.annotations = []
        self.tips = []

        for i in range(-5,12):
            self.tips.append(str(i)+";")
            self.annotations.append(str(i)+"-step")

        for key in expressions_order:
            self.tips.append(self.expressions[key])
            self.annotations.append(key)

        scales_order = self.scales.keys()
        scales_order.sort()
        
        for key in scales_order:
            self.tips.append("[%"+" ".join(map(str, self.scales[key]))\
                                    +"]")
            self.annotations.append(key)

        chords_order = self.chords.keys()[:]
        chords_order.sort()
            
        for key in chords_order:
            self.tips.append("(%"+" ".join(map(str, self.chords[key]))\
                                    +")")
            self.annotations.append(key)
            
        for key in ['c','d','e','f','g','a','b','cis',\
                    'dis','fis','gis','ais']:
            self.tips.append("{%" + str(self.base_notes[key]) + "}")
            self.annotations.append(key)

        time_order = ['whole','half','quarter','eighth','16th','32nd']
            
        for key in time_order + map(lambda x: x+".",time_order)\
            + map(lambda x: x+ " [2/3]",time_order)\
            + map(lambda x: x+ ".[2/3]",time_order):
            self.tips.append(str(self.timings[key])+",")
            self.annotations.append(key)

            
        self.vertices = len(self.annotations)

        self.edges = []
        self.colors = []

        for s in range(self.vertices):
            for t in range(self.vertices):
                c = self.getAllEdges(s,t)
                self.edges.extend([(s,t)] * len(c))
                self.colors.extend(c)
        
        self.representation = "GuitarGraph()"

        
        self.default_graph_name = "guitar_graph"

        self.add_wildcard_node(self.vertices)
        self.vertices += 1
        self.annotations.append('* * *')
        self.tips.append(' ')

        self.add_universal_color()
        
        self.calculate_further_data()
        self.make_thin()
        self.calculate_further_data()
        self.behaviour_strings = self.tips

    def getAllEdges(self, source, target):
        if source == target:
            colors = ["identity"]
        else:
            colors = ["non-identity"]
        styp = self.annotations[source]
        ttyp = self.annotations[target]
        if ttyp in self.scales:
            colors += ["scale"]
            if styp in self.scales:
                if set(self.scales[styp]) < set(self.scales[ttyp]):
                    colors += ["super-structure"]
                elif set(self.scales[styp]) > set(self.scales[ttyp]):
                    colors += ["sub-structure"]
                elif styp != ttyp:
                    colors += ["other-structure"]
                delta =   (set(self.scales[styp])|set(self.scales[ttyp]))\
                        - (set(self.scales[styp])&set(self.scales[ttyp]))
                colors += [str(len(delta))+"-step"]
            else:
                colors += ["other-semantic"]
        elif ttyp in self.chords:
            colors += ["chord"]
            if styp in self.chords:
                if set(self.chords[styp]) < set(self.chords[ttyp]):
                    colors += ["super-structure"]
                elif set(self.chords[styp]) > set(self.chords[ttyp]):
                    colors += ["sub-structure"]
                elif styp != ttyp:
                    colors += ["other-structure"]
                delta =   (set(self.chords[styp])|set(self.chords[ttyp]))\
                        - (set(self.chords[styp])&set(self.chords[ttyp]))
                colors += [str(len(delta))+"-step"]
            else:
                colors += ["other-semantic"]                
        elif ttyp in self.pitches:
            colors += ["pitch"]
            colors += ["note"]
            if styp in self.pitches:
                st = self.pitches[styp]
                tt = self.pitches[ttyp]
                if (st + 4) % 7 == tt % 7:
                    colors += ["sub-structure"]
                elif (st + 5) % 7 == tt % 7:
                    colors += ["super-structure"]
                elif st != tt:
                    colors += ["other-structure"]
                colors += [str((tt-st)%7)+"-step"]
            else:
                colors += ["other-semantic"]                
        elif ttyp in self.timings:
            colors += ["time"]
            if styp in self.timings:
                st = self.timings[styp]
                tt = self.timings[ttyp]
                if tt % st == 0 and tt != st:
                    colors += ["sub-structure"]
                elif st % tt == 0 and tt != st:
                    colors += ["super-structure"]
                elif st != tt:
                    colors += ["other-structure"]
                factors = {2:1,3:1,4:2,5:1,6:2,7:1,8:3,9:2,10:2,11:1,12:3,\
                           13:1,14:2,15:2,16:4,17:1,18:3,19:1,20:3,21:2,22:2,\
                           23:1,24:4,25:2,26:2,27:3,28:3,29:1,30:3,31:1,32:5}
                for k in factors:
                    if st*k == tt:
                        colors += [str(factors[k])+"-step"]
                        break
                    elif tt*k == st:
                        colors += ["-"+str(factors[k])+"-step"]
            else:
                colors += ["other-semantic"]                        
        elif ttyp in self.base_notes:
            colors += ["base"]
            if styp in self.base_notes:
                st = self.base_notes[styp]
                tt = self.base_notes[ttyp]
                if (st + 5) % 12 == tt % 12:
                    colors += ["sub-structure"]
                elif (st + 7) % 12 == tt % 12:
                    colors += ["super-structure"]
                elif st != tt:
                    colors += ["other-structure"]
                colors += [str((tt-st)%12)+"-step"]
            else:
                colors += ["other-semantic"]                
        elif ttyp in self.expressions:
            colors += ["expression"]
            ['oct.up','oct.zero','oct.down','pitch up',\
                             'pitch zero','pitch down','time up',\
                             'time 4th','time down','straight','triplet',\
                             'dotted','normal','once-pm','pm','squeak',\
                             'single','tremolo','trill+1','trill+2',\
                             'trill+3','trill+4','rest','chord', 'chord*2',\
                             'chord*3', 'chord*5','chord*7']

            if ttyp in ['oct.up','oct.zero','oct.down',\
                        'pitch up','pitch zero','pitch down']:
                colors += ["pitch"]
                if ttyp in ['pitch up']:
                    colors += ["1-step"]
                elif ttyp in ['pitch down']:
                    colors += ["-1-step"]
                elif ttyp in ['oct.up']:
                    colors += ["8-step"]
                elif ttyp in ['oct.down']:
                    colors += ["-8-step"]

                if styp in self.pitches or \
                       styp in ['oct.up','oct.zero','oct.down',\
                        'pitch up','pitch zero','pitch down']:
                    if ttyp in ['oct.up','pitch up']:
                        colors += ["super-structure"]
                    elif ttyp in ['oct.down','pitch down']:
                        colors += ["sub-structure"]
                    else:
                        colors += ["other-structure"]
                else:
                    colors += ["other-semantic"]
                        
            elif ttyp in ['time up','time 4th','time down',\
                          'straight','triplet','dotted']:
                colors += ["time"]
                if styp in self.timings or \
                   styp in ['time up','time 4th','time down',\
                          'straight','triplet','dotted']:
                    if ttyp in ['time up','triplet','dotted']:
                        colors += ["sub-structure"]
                    elif ttyp in ['time down']:
                        colors += ["super-structure"]
                    else:
                        colors += ["other-structure"]
                else:
                    colors += ["other-semantic"]
                        
            elif ttyp in ['normal','once-pm','pm','squeak',\
                          'single','tremolo','trill+1','trill+2',\
                          'trill+3','trill+4','sweep','once-sweep',\
                          'sweep-up','once-up','sweep-down','once-down']:
                colors += ["technique"]
                if styp in ['normal','once-pm','pm','squeak',\
                          'single','tremolo','trill+1','trill+2',\
                          'trill+3','trill+4','sweep','once-sweep',\
                          'sweep-up','once-up','sweep-down','once-down']:
                    substruk = 0
                    superstruk = 0
                    otherstruk = 0
                    for stepladder in [['normal','once-pm','pm'],\
                                        ['normal','squeak'],\
                                        ['single','tremolo','trill+1',\
                                         'trill+2','trill+3','trill+4'],\
                                        ['normal','once-up','up','sweep'],\
                                        ['normal','once-down','down','sweep'],\
                                        ['normal','once-sweep','sweep'],\
                                        ]:
                        if styp in stepladder and ttyp in stepladder:
                            si = stepladder.index(styp)
                            ti = stepladder.index(ttyp)
                            if si < ti:
                                superstruk = 1
                            elif ti < si:
                                substruk = 1
                            colors += [str(ti-si)+"-step"]

                    if ttyp != styp:
                        if superstruk:
                            colors += ["super-structure"]
                        if substruk:
                            colors += ["sub-structure"]
                        if not (superstruk or substruk):
                            colors += ["other-structure"]
                    
                else:
                    colors += ["other-semantic"]
                    
            elif ttyp in ['rest','chord', 'chord*2',\
                          'chord*3', 'chord*5','chord*7']:
                colors += ["note"]
                if styp in ['rest','chord', 'chord*2',\
                          'chord*3', 'chord*5','chord*7']:
                    super_structures = {
                        'rest':['chord', 'chord*2','chord*3', 'chord*5','chord*7'],\
                        'chord':['chord*3', 'chord*5','chord*7'],\
                        'chord*2':['chord*5'],\
                        'chord*3':['chord*7'],\
                        'chord*5':[],\
                        'chord*7':[]}
                    if ttyp in super_structures[styp]:
                        colors += ["super-structure"]
                        colors += [str(super_structures[styp].index(ttyp)+1)+"-step"]
                    elif styp in super_structures[ttyp]:
                        colors += ["sub-structure"]
                        colors += [str(-super_structures[ttyp].index(styp)-1)+"-step"] 
                    else:
                        colors += ["other-structure"]
                else:
                    colors += ["other-semantic"]
            
        return colors



if __name__ == '__main__':
    DfGlobal()['PotentialGraph'] = PotentialGraph()
    DfGlobal()['StrengthGraph'] = StrengthGraph()
    DfGlobal()['ChangesGraph'] = ChangesGraph() 
    DfGlobal()['GuitarGraph'] = GuitarGraph() 
