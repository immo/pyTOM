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

from df_global import *
from df_ontology import *
from df_backend import *
from df_data_channels import *
from df_concept import *
from df_database import *
from df_experimental import *
from math import *
import random
import re
from df_visual_concept_editor import *

def get_concept_decorator():
    """ returns the current concept decorator function"""
    return DfGlobal()["concept_decorator"]

def set_concept_decorator(fn=lambda x:0.0):
    """ sets the concept decorator function (or removes it)
    a decorator is a function that is called with the next concept as argument,
    which might change the concepts behaviour (decorate it).
    """
    DfGlobal()["concept_decorator"] = fn

class List2Float(object):
    """class that will have a [.]-function that will return 1.0 if the requested
    element is in the objects list and 0.0 otherwise. Has (.)-function that returns
    the number of unique elements in the list that match the given regular expression
    """
    def __init__(self, items, items2=None):
        self.items = {}
        self.items_cache = {}
        if items2==None:
            for key in items:
                self.items[key] = 1.0
                self.items_cache[key] = 1.0
        else:
            for key in items:
                if key in items2:
                    self.items[key] = 1.0
                    self.items_cache[key] = 1.0
                    
        self.regexp_cache = {}

    def __repr__(self):
        return "List2Float("+repr(self.items.keys())+")"

    def __eq__(self, r):
        return self.items == r.items

    def __ne__(self,r):
        return self.items != r.items
    
    def __getitem__(self, key):
        return self.items_cache.setdefault(key,0.0)

    def __call__(self, regexp):
        try:
            return self.regexp_cache[regexp]
        except KeyError:
            r = re.compile(regexp)
            count = float(len(filter(r.match,self.items.keys())))
            self.regexp_cache[regexp] = count
            return count

def default_scoring(info, desc, out2in):
    """ default scoring function """
    try:
        info_desc = info['desc']
        d_sum = sum([info_desc[x] * desc(x) for x in info_desc])
    except KeyError:
        d_sum = 0

    try:
        info_conn = info['conn']
        c_sum = sum([info_conn[x] * out2in(x) for x in info_conn])        
    except KeyError:
        c_sum = out2in("")
        
    return d_sum + c_sum

def default_info(info, riff):
    """ return the next info structure """
    return info.copy()

class JamSession(object):
    """class that coordinates a jam session"""
    def __init__(self, history={},state={}, riff_nr=None):
        self.db = CompositionDatabase()
        self.g = DfGlobal()
        
        self.history = history # riff_nr \mapsto (db_id , info_dict ) )
        # where special ids:    -1 ... waiting
        #                       -2 ... count in, float bps
        
        if riff_nr:
            self.riff_nr = riff_nr
        else:
            self.riff_nr = 0

        self.state = {'wait':False, 'text_vars':{}, 'next_bound': False,\
                      'nbr_next': 4, 'next':[], 'current': -1,\
                      'info': [ ], 'current.info': {},\
                      'fn.scoring': default_scoring, 'fn.info': default_info,\
                      'mode': 'info', 'prepared_title':''}

        # wait        ... bool ... whether in waiting mode
        # text_vars   ...          text to display
        # next_bound  ... bool ... whether the next riff is already set
        # nbr_next    ... int  ... nbr of riffs to plan ahead
        # next        ... [int]... planned riffs to be played next (comp id)
        # info        ... [{*}]... history info for planned riffs
        # current     ... int  ... currently played riff
        # current.info... (*)  ... info of currently played riff
        # fn.scoring  ... (info, desc, out2in) -> score
        #                      ... maps the current info (dict.), and the
        #                          List2Float-s desc, out2in onto a score
        #                          where high scores mean better fit as next
        #                          concept
        # fn.info     ... (info, riff) -> info
        #                      ... maps the previous info and the current riff
        #                          to the next riffs info
        # mode        ... str  ... current playback mode
        
        for key in state:
            self.state[key] = state[key]

    def remove_prepared_title(self):
        self.state['prepared_title'] = ''
        if self.state['mode'] == 'ext':
            self.ext_update_text4()

    def plan_again(self, keep=False):
        """ this function re-does the planning for the next riffs,
            keep indicates whether to keep the already planned riffs """
        if self.state['mode'] != 'info':
            return
        
        if not keep:
            if self.state['next_bound']:
                self.state['next'] = self.state['next'][0:1]
                self.state['info'] = self.state['info'][0:1]                
            else:
                self.state['next'] = []
                self.state['info'] = []

        if not self.state['next']:
            previous = self.state['current']
            prev_info = self.state['current.info']
        else:
            previous = self.state['next'][-1]
            prev_info = self.state['info'][-1]

        id_list = filter(lambda x:not self.db.isDeleted(x),self.db.getJamIds())

        append_riffs = []
        append_infos = []

        fn_scoring = self.state['fn.scoring']
        fn_info = self.state['fn.info']

        if not self.db.isDeleted(previous):
            out_desc = self.db.getCompositionDescription(previous)['out']
        else:
            out_desc = []
            
        descs = map(lambda x:self.db.getCompositionDescription(x), id_list)

        for i in range(len(self.state['next']),self.state['nbr_next']):
            next_riff = -1
            next_info = {}

            scores = [fn_scoring(prev_info, List2Float(d['desc']),\
                                 List2Float(out_desc,d['in'])) for d in descs]

            best_score = max(scores)

            best_candidates = map(lambda x:x[1], \
                                  filter(lambda x: x[0] == best_score,\
                                         zip(scores, id_list)))

            try:
                next_riff = random.choice(best_candidates)
            except IndexError:
                pass
            else:
                next_info = fn_info(prev_info, next_riff)
            
            append_riffs.append(next_riff)
            append_infos.append(next_info)
            previous = next_riff
            prev_info = next_info
            if not self.db.isDeleted(previous):
                out_desc = self.db.getCompositionDescription(previous)['out']
            else:
                out_desc = []

        self.state['next'].extend(append_riffs)
        self.state['info'].extend(append_infos)

        riff_infos = [self.get_concept_quick_info(i) for \
                      i in self.state['next']]

        text4_update = repr( "\n".join(riff_infos) )
        send_line('text4', text4_update)

    def generateWord(self, dic, prefix="", min_determined=1):
        """generates the next part riff word from dic"""
        if len(prefix) >= dic["max.depth"]:
            return dic.setdefault("ext.word"+prefix, [])
        
        main_loop = self.g["main_input_loop"]
        ext = dic["ext.dict"]
        index = "ext.word"+prefix
        current_word = dic.setdefault(index, [])
        definite = len(current_word)
        
        if definite < min_determined:
            generator_word = dic[index+":"] = self.generateWord(dic, prefix+":")

            main_loop()
            count = len(generator_word)
            idx = 0
            generator = None
            dic[index+"-generator"] = ""
            while idx < count:
                try:
                    generator = ext[prefix+":"+generator_word[idx]]
                    dic[index+"-generator"] = prefix+":"+generator_word[idx]
                    idx += 1
                    break
                except KeyError:
                    print "Generator-KeyError:",prefix+":"+generator_word[idx]
                    idx += 1
            dic[index+":"] = generator_word[idx:]
            if generator:
                try:
                    g = generator['grammar']
                    i = generator['initial']
                except KeyError:
                    pass
                else:
                    try:
                        depth = generator['depth']
                    except KeyError:
                        depth = self.g['default.depth']
                    try:
                        steps = generator['steps']
                    except KeyError:
                        steps = self.g['default.steps']

                    for d in range(steps):
                        for c in range(depth):
                            try:
                                i = g(i)
                            except KeyError, err:
                                print "Generator-Key-Error", str(err)
                            except:
                                pass
                            main_loop()
                        if d < steps-1:
                            i = simplifyWord(i)
                            if not hasNonTerminals(i):
                                break
                            
                    current_word = projectTerminals(i)

        return current_word

    def generateRiff(self, dic):
        self.g["no.calculate_preview"] = True
        main_loop = self.g["main_input_loop"]
        word = dic["ext.word"] = self.generateWord(dic)
        #print "gRiff word=",word
        ext = dic['ext.dict']
        if word:
            count = len(word)
            idx = 0
            generator = None
            dic["ext.riff-generator"] = ""
            while idx < count:
                try:
                    generator = ext[word[idx]]
                    dic["ext.riff-generator"] = word[idx]
                    idx += 1                    
                    break
                except KeyError:
                    print "Riff-Generator-KeyError:", word[idx]
                    idx += 1
            dic["ext.word"] = word[idx:]

            if generator:
                force_set_length = False
                try:
                    g = generator['grammar']
                    i = generator['initial']
                except KeyError:
                    pass
                else:
                    try:
                        depth = generator['depth']
                    except KeyError:
                        depth = self.g['default.depth']
                    try:
                        steps = generator['steps']
                    except KeyError:
                        steps = self.g['default.steps']
                    try:
                        length = generator['length*']
                        force_set_length = True
                    except KeyError:
                        try:
                            length = generator['length']
                        except KeyError:
                            length = 16.0

                    for d in range(steps):
                        for c in range(depth):
                            try:
                                i = g(i)
                            except KeyError, err:
                                print "Generator-Key-Error", str(err)
                            except:
                                pass
                            main_loop()
                        if d < steps-1:
                            i = simplifyWord(i)
                            if not hasNonTerminals(i):
                                break

                    current_word = filter(lambda x: not self.db.isDeleted(x),\
                                          filter(lambda x: type(x)==int,\
                                                 projectTerminals(i)) )
                    concept_dictionary = {}
                    def getConceptById(i):
                        try:
                            return concept_dictionary[i]
                        except KeyError:
                            self.g["no.calculate_preview"] = False
                            concept = evalConcept('genConcept('+\
                                   repr(self.db.getComposition(i).getJamDrumCode())+')')
                            self.g["no.calculate_preview"] = True
                            concept_dictionary[i] = concept
                            return concept
                    title_dictionary = {}
                    def getTitleById(i):
                        try:
                            return title_dictionary[i]
                        except KeyError:
                            title = (self.db.getIdKeys(i))[3]
                            title_dictionary[i] = title
                            return title

                    concept_list = []
                    title_list = []
                    uptohere = 0.0
                    for i in current_word:
                        c = getConceptById(i)
                        concept_list.append(c)
                        title_list.append(getTitleById(i))
                        uptohere += c.riff_length
                        if uptohere >= length:
                            break
                    concept = concatConceptsL(concept_list, length)
                    try:
                        concept.set_bps = generator['bpm']/60.0
                    except KeyError:
                        concept.set_bps = None

                        
                    # now apply decorators
                    ignore_keys = ['bpm', 'depth', 'steps', 'length',\
                                   'initial', 'grammar', 'postprocess',\
                                   'things','length*']
                    redo_preview = 0
                    new_potential_funs = {}
                    new_strength_funs = {}
                    for dk in generator:
                        if not dk in ignore_keys:
                            if dk.startswith('hit.'):
                                limbname = dk[4:]
                                if not limbname in concept.potential_funs:
                                    print 'generateRiff: hit-decorator: Unknown limb function: ',limbname
                                else:
                                    gencode = generator[dk]
                                    if gencode[0] == ":":
                                        gencode = ","+ gencode[1:]
                                    else:
                                        gencode = ": "+gencode
                                    funcode = 'lambda x,c=concept,fn=concept' +\
                                              '.potential_funs['+repr(limbname)+'] '+ gencode
                                    try:
                                        newfun = eval(funcode)
                                    except Exception, err:
                                        print "Error when evaluating decorator ",dk, ": ", err
                                        print "Eval-Code:", funcode
                                    else:
                                        new_potential_funs[limbname] = newfun
                                        redo_preview = 1
                            if dk.startswith('strength.'):
                                limbname = dk[9:]
                                gencode = generator[dk]
                                if gencode[0] == ":":
                                    gencode = ","+ gencode[1:]
                                else:
                                    gencode = ": "+gencode
                                funcode = 'lambda x,c=concept,fn=concept' +\
                                          '.getStrengthFun('+repr(limbname)+') '+ gencode
                                try:
                                    newfun = eval(funcode)
                                except Exception, err:
                                    print "Error when evaluating decorator ",dk, ": ", err
                                    print "Eval-Code:", funcode
                                else:
                                    new_strength_funs[limbname] = newfun
                                        
                            elif dk.startswith('at.'):
                                try:
                                    timecode = eval(dk[3:])

                                except Exception,err:
                                    print "Error when evaluating at-timecode",err
                                    print "Eval-Tag: ", dk
                                else:
                                    gencode = generator[dk]
                                    if gencode[0] == ":":
                                        gencode = ","+ gencode[1:]
                                    else:
                                        gencode = ": "+gencode
                                    funcode = 'lambda c' + gencode
                                    try:
                                        newfun = eval(funcode)
                                    except Exception, err:
                                        print "Error when evaluating at-decorator ",dk, ": ", err
                                        print "Eval-Code:", funcode
                                    else:
                                        concept.add_timed_command(timecode,\
                                                                  newfun)


                            else:
                                print 'generateRiff: Unknown decorator: ', dk
                    
                    dic['generateRiff.titles'] = title_list

                    for lname in new_potential_funs:
                        concept.potential_funs[lname] = new_potential_funs[lname]

                    for lname in new_strength_funs:
                        concept.strength_funs[lname] = new_strength_funs[lname]


                    #call things
                    if 'things' in generator:
                        things_dic = self.g["things"]
                        for thing in generator['things']:
                            t = thing.strip()
                            start_time = 0.0
                            if '@' in t:
                                [t, start_time] = t.split('@')
                                try:
                                    start_time = float(start_time)
                                except Exception,err:
                                    print "Error converting: start_time = ",start_time
                                    print "   reason:  ",err
                            if t in things_dic:
                                apply_things(things_dic[t],concept,start_time)
                                redo_preview = True
                            else:
                                print "Error decorating thing: ",t
                                print "   reason:  not found!"
                            main_loop()

                    if force_set_length:
                        print "force set len"
                        concept.riff_length = length
                        for ilimb in concept.potential_funs:
                            old_fn = concept.potential_funs[ilimb]
                            concept.potential_funs[ilimb] = \
                                                   lambda t,o=old_fn,\
                                                   l=length:o(t)\
                                                   if t < (l-1.0/64.0) else 0.0
                            
                    try:
                        concept.calculate_preview()
                    except Exception,err:
                        print "Error when trying to calculate preview data from decorated concept!"
                        print "Error: ",err
                                

                    main_loop()
                    
                    #call postprocessing

                    if 'postprocess' in generator:
                        gencode = generator['postprocess']
                        if gencode[0] == ":":
                            gencode = ","+ gencode[1:]
                        else:
                            gencode = ": "+gencode
                        funcode = 'lambda c=concept'+ gencode
                        try:
                            newfun = eval(funcode)
                        except Exception, err:
                            print "Error when evaluating postprocess decorator ", ": ", err
                            print "Eval-Code:", funcode
                        else:
                            newfun(concept)

                    main_loop()

                    # call the global concept decorator
                    get_concept_decorator()(concept)
                    
                    self.g["no.calculate_preview"] = False
                    return concept
        self.g["no.calculate_preview"] = False
        return None
                    
                

    def setup_from_ext(self, key, nocounting=False, append=None):
        nowaste = self.g["no-waste-time"]
        save_depth = self.g["save-loop-depth"]

        if append == None:
            append = nocounting
        
        self.g["save-loop-depth"] = 2
        self.g["no-waste-time"] = True

        main_loop = self.g["main_input_loop"]
        
        try:
            data = "\n"+self.g['ext'][key]
        except KeyError:
            return
        
        merge_state = {}
        
        slices = data.split("\n:")
        part_dictionary = {}
        songname = ""
        grammar_cache = {}
        conversions = {}
        conversions['bpm'] = lambda x: float(x)
        conversions['steps'] = lambda x: int(x)
        conversions['depth'] = lambda x: int(x)                
        conversions['length'] = lambda x: float(x)
        conversions['length*'] = lambda x: float(x)                
        conversions['grammar'] = lambda x:\
                  grammar_cache.setdefault(x,\
                                           pgrammar( \
                                           makeRules(self.g['ext'][x],\
                                                     self.g['default.rules'])) )
        conversions['initial'] = lambda x: makeWord(x)
        def thingsconvert(x):
            print "thing-string",x
            return str(x).split(";")
        conversions['things'] = thingsconvert

        conversions['prefetch_riffs'] = lambda x: int(x)
        merge_state['prefetch_riffs'] = 3

        conversions['taxa'] = lambda x: str(x)

        conversions['ext.count.next'] = lambda x: bool(x)
        merge_state['ext.count.next'] = not nocounting

        conversions['postprocess'] = lambda x: str(x)

        conversion_schemes = {}
        conversion_schemes['hit.'] = lambda x: str(x)
        conversion_schemes['strength.'] = lambda x: str(x)        
        conversion_schemes['at.'] = lambda x: str(x)

        
        if slices:
            lines = slices[0].split("\n")
            for l in lines:
                if l.strip():
                    main_loop()
                    idx = l.find("=")
                    lhs = l[0:idx].strip()
                    rhs = l[idx+1:].strip()
                    try:
                        merge_state[lhs] = conversions[lhs](rhs)
                    except Exception, err:
                        converted = 0
                        for scheme in conversion_schemes:
                            if lhs.startswith(scheme):
                                merge_state[lhs] = conversion_schemes[scheme](rhs)
                                converted = 1
                                break
                        if not converted:
                            print "Cannot convert ",lhs,": ", err
                            merge_state[lhs] = rhs
        
        main_loop()
        for x in slices[1:]:
            lines = x.split("\n")
            name = lines[0].strip()
            maxdep = merge_state.setdefault("max.depth",0)
            prefixcount = 0
            
            while name[prefixcount:prefixcount+1] == ":":
                prefixcount += 1
                
            if prefixcount > maxdep:
                merge_state["max.depth"] = prefixcount
                songname = name[prefixcount:]
                
            lines = lines[1:]
            dictionary = {}
            for l in lines:
                if l.strip():
                    main_loop()
                    idx = l.find("=")
                    lhs = l[0:idx].strip()
                    rhs = l[idx+1:].strip()
                    try:
                        dictionary[lhs] = conversions[lhs](rhs)
                    except Exception, err:
                        converted = 0
                        for scheme in conversion_schemes:
                            if lhs.startswith(scheme):
                                dictionary[lhs] = conversion_schemes[scheme](rhs)
                                converted = 1
                                break
                        if not converted:
                            print "Cannot convert ",lhs,": ", err
                            dictionary[lhs] = rhs
            part_dictionary[name] = dictionary

        
        for n in range(merge_state["max.depth"]):
            merge_state['ext.word'+":"*n] = []

        merge_state['ext.word'+":"*merge_state["max.depth"]] = [ songname ]

        merge_state['ext.name'] = songname
        merge_state['ext.dict'] = part_dictionary
        main_loop()
        if not append:
            merge_state['ext.riffs'] = []
            merge_state['ext.titles'] = []
            merge_state['ext.future'] = []
            merge_state['ext.left'] = []
        else:
            merge_state['ext.riffs'] = self.state['ext.riffs']
            merge_state['ext.titles'] = self.state['ext.titles']
            merge_state['ext.future'] = self.state['ext.future']
            merge_state['ext.left'] = self.state['ext.left']
        
        merge_state['mode'] = 'ext'

        for key in merge_state:
            self.state[key] = merge_state[key]
        
        self.g["no-waste-time"] = nowaste
        self.g["save-loop-depth"] = save_depth

        self.refillExtRiffs(self.state)

    def refillExtRiffs(self, dic):
        if self.g["loop-depth"] > 1:
            add_root_call( lambda : self.refillExtRiffs(dic) )
            return False
        
        have = len(dic['ext.riffs'])
        prefetch = dic['prefetch_riffs']
        if have < prefetch:
            nowaste = self.g["no-waste-time"]
            save_depth = self.g["save-loop-depth"]      
            self.g["save-loop-depth"] = 2
            self.g["no-waste-time"] = True

            for i in range(have,prefetch):
                
                riff = self.generateRiff(dic)
                
                if riff != None:
                    dic['ext.riffs'].append(riff)
                    title = dic['ext.riff-generator']
                    prefix = ""
                    while ('ext.word'+prefix+'-generator' in dic):
                        if len(prefix) > dic['max.depth']:
                            break
                        title += "//" + dic['ext.word'+prefix+'-generator']\
                                 .lstrip(":")
                        prefix += ":"
                    if riff.set_bps:
                        title += "\nbpm=" + str( round(riff.set_bps*60.0) )
                    dic['ext.titles'].append(title)

                    #dic['ext.left'].append(", ".join(\
                    #dic['generateRiff.titles']))
                    
                    dic['ext.left'].append("")                    

                    future = ""

                    prefix = ""
                    
                    while 'ext.word'+prefix in dic:
                        if len(prefix) > dic['max.depth']:
                            break
                        future += "> ".join(dic['ext.word'+prefix][0:3])
                        if len(dic['ext.word'+prefix])>3:
                            future += "> ("+str(len(dic['ext.word'+prefix])-3)\
                                      +")\n"
                        else:
                            future += "\n"
                        prefix += ":"
                    
                    dic['ext.future'].append(future)
                    
                    
                else:
                    break

            self.g["no-waste-time"] = nowaste
            self.g["save-loop-depth"] = save_depth

            self.ext_update_text4()
            
            self.fill_jam_textvars()
        
        return True

    def ext_update_text4(self,timed=None):
        if self.state['prepared_title']:
            text4_update = repr(\
                       self.state['prepared_title'].replace("\n"," | ")+"\n"+\
                              "\n".join( \
                            map(lambda x: x.replace("\n"," | "),\
                            self.state['ext.titles']) ) )
            
            
        else:
            text4_update = repr( "\n".join( \
                            map(lambda x: x.replace("\n"," | "),\
                            self.state['ext.titles']) ) )

        if timed == None:
            send_line('text4',text4_update)
        else:
            send_line_at(timed,'text4',text4_update)
        

    def from_ext_generate_riff_word(self, name, ext, nonterms=4):
        main_loop = self.g["main_input_loop"]
        #print "name=",name
        #print "ext=",ext
        try:        
            A = ext[name]
            g = A['grammar']
            i = A['initial']
        except KeyError:
            return []

        try:
            depth = A['depth']
        except KeyError:
            depth = self.g['default.depth']

        try:
            steps = A['steps']
        except KeyError:
            steps = self.g['default.steps']

        if nonterms:
            for c in range(depth):
                for d in range(steps):
                    try:
                        i = g(i)
                    except KeyError, err:
                        print "Generator-Key-Error", str(err) 
                    except:
                        pass
                    main_loop()
                i = simplifyWord(i)
                cnt = countDefiniteTerminals(i)
                if cnt >= nonterms or cnt == len(i):
                    return i
        else:
            for c in range(depth):
                for d in range(steps):
                    try:
                        i = g(i)
                    except KeyError, err:
                        print "Generator-Key-Error", str(err)
                    except:
                        pass
                    main_loop()
                i = simplifyWord(i)
                if not hasNonTerminals(i):
                    return i
                
        return i

    def from_ext_generate_riffs(self, merge_state, nonterms=4):
        main_loop = self.g["main_input_loop"]
        count = 0
        ext = merge_state['ext.dict']
        riffslist = []
        while count < nonterms:
            rword = merge_state['ext.riffword']
            if not rword:
                return riffslist
            if rword[0][1]:
                return riffslist
            name = rword.pop(0)[0]
            main_loop()
            
            try:
                A = ext[name]
                count += 1
            except KeyError:
                pass
            else:
                try:
                    length = A['length']
                except KeyError:
                    length = 4.0
                if count == 1:
                    try:
                        control_addition = ":C @"+str(A['bpm'])+"@\n"
                    except KeyError:
                        control_addition = ""
                else:
                    control_addition = ""
                main_loop()
                l = self.from_ext_generate_riff_word(name,ext,None)
                main_loop()
                l = map(lambda x: x[0], l)
                q = filter(lambda x: type(x)==int, l)
                accumulated_length = 0.0
                c = []
                for x in q:
                    if not self.db.isDeleted(x):
                        main_loop()
                        composition = self.db.getComposition(x)
                        code = composition.getJamDrumCode()
                        concept = evalConcept('genConcept('+\
                                              repr(code+control_addition)+')')
                        accumulated_length += concept.riff_length
                        c.append(concept)
                    if accumulated_length >= length:
                        break
                if len(c) == 1:
                    riffslist.append(c[0])
                elif len(c) > 1:
                    riffslist.append(concatConceptsL(c,length))


        return riffslist
            

    def setup_info_and_plan_again(self, info):
        self.state['info'] = [info]
        self.state['next'] = [-1]
        self.state['current.info'] = info
        self.state['current'] = [-1]
        self.state['mode'] = 'info'
        self.plan_again()
        
            
    def get_info(self):
        if self.state['mode'] == 'info':
            if self.state['next_bound']:
                return self.state['info'][0]
            else:
                return self.state['current.info']
        return {}

        
    def get_concept_quick_info(self, next):
        if self.state['mode'] == 'info':
            if self.db.isDeleted(next):
                if next == -1:
                    return "(waiting state)"
                elif next == -2:
                    return "(count in)"
                else:
                    return "!!! unknown/deleted id " + str(next) + " !!!"

            composition = self.db.getComposition(next)
            c_str = "genConcept("+repr(composition.getJamDrumCode())+")"
            concept = evalConcept(c_str)
            (name, version, song, riff, tags, created, modified, deleted) = \
                   self.db.getIdKeys(next)

            if concept.set_bps:
                quickinfo = str(int(concept.set_bps*60.0))+"bpm / "
            else:
                quickinfo = str(int(self.g['mind'].c_beatspersecond*60.0))\
                            +"bpm / "
            quickinfo += str(concept.riff_length)

            return  quickinfo + " - " + str(riff) + " - " + str(song) + " v" + str(version)
        else:
            return "..."
                       
        

    def get_next_concept(self):
        """ this function is called when the next concept is determined """
        if self.state['mode'] == 'info':
            if self.state['wait'] or len(self.state['next'])==0:
                concept = evalConcept('genConcept(":C @120@")')
                self.state['text_vars']['text1'] = "'waiting...'"
                self.state['next'] = [-1] + self.state['next']
                self.state['info'] = [ self.state['current.info'] ] + self.state['info']
            else:
                next = self.state['next'][0]
                info = self.state['info'][0]
                if self.db.isDeleted(next):
                    if next == -2:
                        bps = None
                        try:
                            next2 = self.state['next'][1]
                        except KeyError:
                            pass
                        else:
                            composition = self.db.getComposition(next2)
                            c_str = "genConcept("+repr(composition.getJamDrumCode())+")"
                            concept = evalConcept(c_str)
                            bps = concept.set_bps
                        if bps:
                            concept = evalConcept('genConcept('+\
                                                  repr('":L<0.0>(0.5) \n:\'L g \n:l !Q\n:C (4) @' + str(bps*60.0) + '@')\
                                                  + ')')
                            self.state['text_vars']['text1'] = "'(count in)\\n" + str(bps*60.0) + "'"               
                        else:
                            concept = evalConcept('genConcept(' +\
                                                  repr(':L<0.0>(0.5) \n:\'L g \n:l !Q\n:C (4)') + ')')
                            self.state['text_vars']['text1'] = "'(count in)'"

                        self.state['text_vars']['text2'] = "''"
                        self.state['text_vars']['text3'] = "''"                

                    else:
                        concept = evalConcept('genConcept(":C @120@")')
                        if next == -1:
                            self.state['text_vars']['text1'] = "'(waiting state)'"
                        else:
                            self.state['text_vars']['text1'] = "'invalid riff id ("\
                                                           +str(next)+")'"
                        self.state['next'][0] = -1
                        self.state['info'][0] = {"invalid riff id": next,\
                                                 "info": self.state['info'][0]}
                    self.state['text_vars']['text2'] = "''"
                    self.state['text_vars']['text3'] = "''"                
                else:
                    composition = self.db.getComposition(next)
                    c_str = "genConcept("+repr(composition.getJamDrumCode())+")"
                    concept = evalConcept(c_str)
                    (name, version, song, riff, tags, created, modified, deleted) = \
                           self.db.getIdKeys(next)
                    if concept.set_bps:
                        quickinfo = str(int(concept.set_bps*60.0))+"bpm / "
                    else:
                        quickinfo = str(int(self.g['mind'].c_beatspersecond*60.0))\
                                    +"bpm / "
                    quickinfo += str(concept.riff_length)

                    self.state['text_vars']['text1'] = repr( \
                        str(riff) + " - " + str(song) + " v" \
                        + str(version) + "\n" + quickinfo)
                    desc = self.db.getCompositionDescription(next)
                    desc_string = " ".join(filter(lambda x: not x[0].islower(),\
                                                  desc['desc']))
                    
                    self.state['text_vars']['text2'] = repr(desc_string)
                    out_string = " ".join(desc['out'])
                    self.state['text_vars']['text3'] = repr(out_string)
        elif self.state['mode'] == 'ext':
            if self.state['wait']:
                concept = evalConcept('genConcept(":C (16)")')
                self.state['text_vars']['text1'] = "'[waiting...]'"
                
                #self.state['text_vars']['text4'] = \
                #           repr( "\n".join( \
                #        map(lambda x: x.replace("\n"," | "),\
                #            self.state['ext.titles']) ) )
                
            elif self.state['ext.count.next']:
                self.state['ext.count.next'] = False
                try:
                    bps = self.state['ext.riffs'][0].set_bps
                except KeyError:
                    bps = None
                except IndexError:
                    bps = None
                #self.state['text_vars']['text4'] = \
                #           repr( "\n".join( \
                #        map(lambda x: x.replace("\n"," | "),\
                #            self.state['ext.titles']) ) )
                if bps:
                    concept = evalConcept('genConcept(' + \
                        repr('":L<0.0>(0.5) \n:\'L g \n:l !Q\n:C (4) @' +\
                             str(bps*60.0) + '@') + ')')
                    self.state['text_vars']['text1'] = \
                          "'[count in...]\\n" + str(bps*60.0) + "'"
                else:
                    concept = evalConcept('genConcept(' + \
                        repr(':L<0.0>(0.5) \n:\'L g \n:l !Q\n:C (4)') + ')')
                    self.state['text_vars']['text1'] = "'[count in...]'"

                
            else:
                if self.state['ext.riffs']:
                    concept = self.state['ext.riffs'].pop(0)
                    
                    current_title = self.state['ext.titles'].pop(0)
                    
                    self.state['text_vars']['text1'] = \
                           repr(current_title)

                    self.state['prepared_title'] = current_title
                    
                    if not 'text2' in concept.text_vars:
                        self.state['text_vars']['text2'] = \
                           repr(self.state['ext.left'].pop(0))
                    else:
                        self.state['text_vars']['text2'] = repr(concept.text_vars['text2'])
                        try:
                            self.state['ext.left'].pop(0)
                        except:
                            pass
                        
                    if not 'text3' in concept.text_vars:
                        self.state['text_vars']['text3'] = \
                           repr(self.state['ext.future'].pop(0))
                    else:
                        self.state['text_vars']['text3'] = repr(concept.text_vars['text3'])
                        try:
                            self.state['ext.future'].pop(0)
                        except:
                            pass
                        
                    #self.state['text_vars']['text4'] = \
                    #       repr( "\n".join( \
                    #    map(lambda x: x.replace("\n"," | "),\
                    #        self.state['ext.titles']) ) )
                else:
                    concept = evalConcept('genConcept(":C @120@")')
                    self.state['text_vars']['text1'] = "'[done.]'"
                    self.state['text_vars']['text2'] = "''"
            self.fill_jam_textvars()
        else:
            concept = evalConcept('genConcept(":C @120@")')
            self.state['text_vars']['text1'] = "'[unknown mode]'"
            self.state['next'] = [-1] + self.state['next']
            self.state['info'] = [ self.state['current.info'] ] \
                                 + self.state['info']

        self.state['next_bound'] = True
        concept.text_vars = self.state['text_vars']
        return concept

    def fill_jam_textvars(self):

        left = ""
        if self.state['mode'] == 'info':
            info = self.get_info()            
            try:
                left = " ".join([str(info['desc'][x])+"*"+str(x)\
                             for x in info['desc']])
            except KeyError:
                pass

        if self.state['wait']:
            right = "(waiting)\n"
        else:
            right = ""

        if self.state['mode'] == 'info':
            right += "riff #"+str(self.riff_nr)
        elif self.state['mode'] == 'ext':
            if self.state['ext.count.next']:
                right +=  "count in...\n"
                                     
        self.state['text_vars']['text5'] = repr( left )
        self.state['text_vars']['text6'] = repr( right )
        send_line('text5', self.state['text_vars']['text5'])
        send_line('text6', self.state['text_vars']['text6'])

    def add_or_remove_count_in(self):
        if self.state['mode'] == 'info':
            if self.state['next_bound']:
                idx = 1
            else:
                idx = 0
            try:
                nbr = self.state['next'][idx]
                if nbr == -2:
                    self.state['next'].pop(idx)
                    self.state['info'].pop(idx)
                else:
                    self.state['next'].insert(idx, -2)
                    self.state['info'].insert(idx,self.state['info'][idx])
            except:
                pass
            self.plan_again(keep=True)        
            self.fill_jam_textvars()
        elif self.state['mode'] == 'ext':
            self.state['ext.count.next'] = not self.state['ext.count.next']


    def add_desc_value(self, key, value):
        info = self.get_info()
        try:
            desc = info['desc']
        except KeyError:
            desc = {}
            info['desc'] = desc

        desc[key] = value

        if value == 0:
            desc.remove(key)
            
        self.fill_jam_textvars()

    def next_concept_entered(self, time):
        """ this function is called when next_concept -> concept, i.e.
        at the concept boundaries, just before concept.riff is called """

        self.state['next_bound'] = False

        if self.state['mode'] == 'info':
            try:
                self.state['current'] = self.state['next'].pop(0)
            except:
                pass
            try:
                self.state['current.info'] = self.state['info'].pop(0)
            except:
                pass
        elif self.state['mode'] == 'ext':
            add_timed_call(lambda s=self: s.remove_prepared_title(), \
                           self.g['viz_lag'])
            add_root_call(lambda :self.refillExtRiffs(self.state) )
            

        if self.state['wait']:
            try:
                if self.history[self.riff_nr][0] != -1:
                    self.riff_nr += 1
                    self.history[self.riff_nr] = (self.state['current'],repr( self.state['current.info']))
            except KeyError:
                pass
        else:
            self.riff_nr += 1
            self.history[self.riff_nr] = (self.state['current'],repr( self.state['current.info']))

        self.fill_jam_textvars()

        self.plan_again(keep=True)
        

    def set_wait_state(self, wait=True):
        self.state['wait'] = wait
        self.fill_jam_textvars()

    def switch_wait_state(self):
        self.state['wait'] = not self.state['wait']
        self.fill_jam_textvars()
        if not self.state['wait']:
            self.g['mind'].quick_change(0.25)
            self.state['ext.count.next'] = True
            

    def __repr__(self):
        return "JamSession("+repr(self.history)+","\
               +repr(self.state)+","\
               +repr(self.riff_nr)+")"

    def __hash__(self):
        return hash(repr(self.state))

    def __eq__(self,r):
        return self.state == r.state

    def __ne__(self,r):
        return not self.__eq__(r)
