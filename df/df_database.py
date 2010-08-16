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
from df_guitar_graph import *
from df_localcomposition import *
import datetime
from df_data_channels import *
from df_global import *
from df_concept import *
import copy
import code

class AssociatedData(object):
    """This class couples a key with a value
    """
    def __init__(self, primary, secondary=None):
        self.primary = primary
        self.secondary = secondary

    def __hash__(self):
        return hash(self.primary)

    def __eq__(self,r):
        return self.primary == r.primary

    def __ne__(self,r):
        return self.primary != r.primary

    def __repr__(self):
        return "AssociatedData("+repr(self.primary)+","+repr(self.secondary)+")"

    def __lt__(self,r):
        return self.primary < r.primary

    def __le__(self,r):
        return self.primary <= r.primary

    def __gt__(self,r):
        return self.primary > r.primary

    def __ge__(self,r):
        return self.primary >= r.primary

    def __cmp__(self,r):
        return self.primary.__cmp__(r.primary)

    def __call__(self):
        return self.primary

class CompositionDatabase(object):
    """This class handles the (global) composition database
    """
    data = {'cur_id': 0,  \
            'compositions': {},\
            'last_modified': {},\
            'created': {},\
            'deleted': {None: []},\
            'tags': {},\
            'names': {},\
            'versions': {},\
            'songs' : {},\
            'riffs' : {},\
            'keys' : {},\
            'compositions.undo': [],\
            'compositions.undo.size': 10000,\
            'composition.description':{},\
            'desc':{},\
            'in':{},\
            'out':{}\
    } # class-wide dictionary
    
    send_changes = {}
    postpone_send_changes = {}
    postponed_changes = []

    jam_ids = set([])
    
    globals = {"PartialLocalComposition": PartialLocalComposition}

    loadSuccess = {}
    
    def __init__(self):
        pass    
    
    def store_database(self, file):
        """Store the current database as representing code in file"""
        # store the compositions
        file.write("\n# Restore CompositionDatabase..."+\
                   "\nprint 'Restoring CompositionDatabase...'\n")
        file.write("\nglobals()['LocalCompositionEditor'] ="+\
                   " PartialLocalComposition\n")
        file.write("\nsend_line('exec.db',"\
                   +repr("CompositionDatabase().unsetSendChanges()")+")\n")
        
        for key in filter(lambda x: x != "compositions" and \
                                    x != "compositions.undo"\
                          and x != "compositions.undo.size" ,self.data.keys()):
            cmd = "CompositionDatabase().setKey("+repr(key)+","\
                  +repr(self.data[key])+")"
            file.write("send_line('exec.db',"+repr(cmd)+")\n")
            file.write(cmd+"\n")

        compositions = self.data['compositions']
        for id in compositions:
            val = compositions[id]
            cmd = "CompositionDatabase().setComposition("+repr(id)+","\
                  +val.repr_as_editor()+")"
            file.write("send_line('exec.db'," + repr(cmd) + ")\n")
            file.write(cmd+"\n")

        # store persistent undo information
        cmd = "CompositionDatabase().setUndoSize("+\
              repr(self.data['compositions.undo.size'])+")"
        
        file.write("send_line('exec.db',"+repr(cmd)+")\n")
        for token in self.data['compositions.undo']:
            cmd = "CompositionDatabase().addUndoInformation(" + repr(token) +")"
            file.write("send_line('exec.db'," + repr(cmd) + ")\n")
            file.write(cmd+"\n")

        # setup write-back from GUI database...
        cmd = "CompositionDatabase().successfulLoaded()"

        file.write("send_line('exec.db'," + repr(cmd) + ")\n")
        file.write(cmd+"\n")

        file.write("\nsend_line('exec.db',"+\
                   repr("CompositionDatabase().setSendChanges()")+")\n")

                
        file.write("send_line('exec.db','DfGlobal()[\"updateDB\"]()')\n")
        
        file.write("print 'CompositionDatabase restored.'\n")

    def successfulLoaded(self):
        self.loadSuccess[""] = 1
        if self.send_changes:
            self.send_line("exec.pipe",\
                           "CompositionDatabase().successfulLoaded()")

    def isSuccessfulLoaded(self):
        return self.loadSuccess

    def getCompositionDescription(self, id):
        try:
            return self.data['composition.description'][id]
        except KeyError:
            return {'desc':[],'in':[],'out':[]}

    def getDescription(self, tags, composition):
        if '*' in tags:
            return None
        
        desc = {'in':[], 'out':[], 'desc':[]}
        try:
            desc['in'] = map(lambda x: x.strip().upper(), tags['in'].split(","))
        except:
            pass
        try:
            desc['out'] = map(lambda x: x.strip().upper(), \
                              tags['out'].split(","))
        except:
            pass
        try:
            desc['desc'] = map(lambda x: x.strip().upper(), \
                               tags['desc'].split(","))
        except:
            pass

        concept = evalConcept("genConcept(" +\
                              repr(composition.getJamDrumCode()) +\
                              ")")

        if concept.set_bps:
            desc['desc'].append("bpm="+str(int(concept.set_bps*60.0)))
        desc['desc'].append("bars="+str(concept.bar_lengths))
        desc['desc'].append("beats="+str(concept.riff_length))
        
        for x in desc:
            desc[x] = list(set(desc[x]))
            desc[x].sort()
        return desc        


    def setUndoSize(self, size=200):
        self.data['compositions.undo.size'] = size
        if self.send_changes:
            self.send_line("exec.pipe","CompositionDatabase().setUndoSize("+\
                           repr(size)+")")

    def addUndoInformation(self, undo_token):
        size = self.data['compositions.undo.size']
        if undo_token in self.data['compositions.undo']:
                                                 # do not allow duplicates
            self.data['compositions.undo'].remove(undo_token)
            
        self.data['compositions.undo'].append(undo_token)
        
        if len(self.data['compositions.undo']) > size:
            for i in range(len(self.data['compositions.undo']) - size):
                self.data['compositions.undo'].pop(0)

        if self.send_changes:
            self.send_line("exec.pipe","CompositionDatabase()."+\
                           "addUndoInformation("+repr(undo_token)+")")


            
    def getUndoList(self):
        return self.data['compositions.undo']

    def getUndoItem(self, nr):
        return self.data['compositions.undo'][nr]

    def isDeleted(self, id):
        return not (id in self.data['deleted'][None])

    def getNonDeletedList(self):
        return [id for id in self.data['deleted'][None]]

    def getJamIds(self):
        return self.jam_ids
    
    def setComposition(self, id, composition):
        self.data['compositions'][id] = composition
        tags = copy.deepcopy(composition.tags)
        self.setTags(id, tags)

        desc = self.getDescription(tags, composition)
        self.data['composition.description'][id] = desc

        if desc:
            self.jam_ids.add(id)
        else:
            try:
                self.jam_ids.remove(id)
            except KeyError:
                pass
            
        
        for key in self.data['in']:
            try:
                self.data['in'][key].remove(id)
            except ValueError:
                pass
            except KeyError:
                pass
        for key in self.data['out']:
            try:
                self.data['out'][key].remove(id)
            except ValueError:
                pass
            except KeyError:
                pass

        for key in self.data['desc']:
            try:
                self.data['desc'][key].remove(id)
            except ValueError:
                pass
            except KeyError:
                pass

        if desc:
            for x in desc:
                for key in desc[x]:
                    self.data[x].setdefault(key,[]).append(id)
        
        if self.send_changes:
            self.send_line("exec.pipe","CompositionDatabase().setComposition("\
                           +repr(id)+","+composition.repr_as_composition()+")")

    def getInKeys(self):
        return self.data['in']


    def getOutKeys(self):
        return self.data['out']

    def getDescKeys(self):
        return self.data['desc']
            
    def getComposition(self, id):
        return self.data['compositions'][id]
    
    def setSendChanges(self):
        self.send_changes[0] = 1

    def unsetSendChanges(self):
        self.send_changes.clear()

    def setPostponeSendChanges(self):
        self.postpone_send_changes[0] = 1

    def unsetPostponeSendChanges(self):
        self.postpone_send_changes.clear()

    def sendPostponedChanges(self):
        try:
            while 1:
                tp = self.postponed_changes.pop(0)
                send_line(tp[0],tp[1])
                print ".",
        except IndexError:
            pass

    def send_line(self, channel, data):
        if self.postpone_send_changes:
            self.postponed_changes.append( (channel,data,) )
        else:
            send_line(channel,data)
        
    def getKey(self,key):
        """get data object with certain key"""
        return self.data[key]
    
    def setKey(self,key,value):
        """set data object with certain key"""
        self.data[key] = value
        if self.send_changes:
            cmd = "CompositionDatabase().setKey("+repr(key)+","+repr(value)+")"
            self.send_line("exec.pipe",cmd)
            
    def delCurrentKeys(self, id):
        keys = self.data['keys'][id]
        
        m = {'names':'name', 'versions':'version','songs':'song','riffs':'riff',
        'created':'created', 'last_modified':'modified','deleted':'deleted'}
        for k in m:
            v = keys[m[k]]
            try:
                self.data[k][v].remove(id)
            except ValueError:
                pass
            except KeyError:
                pass

        t = repr(keys['tags'])
        try:
            self.data['tags'][t].remove(id)
        except KeyError:
            pass
        except ValueError:
            pass


        
        if self.send_changes:
            self.send_line("exec.pipe","CompositionDatabase().delCurrentKeys("\
                           +repr(id)+")")
            
    def addIdKeys(self, cur_id, name, version, song, riff, tags, created,\
                  modified, deleted):
        keys = {'name': name, 'version': version, 'song':song, 'riff':riff,\
                'tags':tags,\
           'created': created, 'modified': modified, 'deleted': deleted }     
        self.data['keys'][cur_id] = keys        
        if self.send_changes:
            self.send_line("exec.pipe","CompositionDatabase().data['keys']["\
                           +repr(cur_id)+"] = "+repr(keys))
        self.addToList('names',name,cur_id)
        self.addToList('versions',version,cur_id)        
        self.addToList('songs',song,cur_id)
        self.addToList('riffs',riff,cur_id)
        self.addToList('tags',repr(tags),cur_id)        
        self.addToList('created',created,cur_id)
        self.addToList('last_modified',modified,cur_id)        
        self.addToList('deleted',deleted,cur_id)

        DfGlobal()["db.default.name"] = name
        DfGlobal()["db.default.song"] = song

        dot = riff.rfind(".")
        if dot >= 0:
            new_riff = riff[0:dot+1]
            pt2 = riff[dot+1:]
            try:
                pt2 = str(int(pt2)+1)
            except ValueError:
                pt2 = pt2 + ".1"
            new_riff += pt2
        else:
            new_riff = riff + ".1"
        
        DfGlobal()["db.default.riff"] = new_riff
        
    def setModified(self, id, time):
        old_modified = self.data['keys'][id]['modified']
        try:
            self.data['last_modified'][old_modified].remove(id)
        except KeyError:
            pass
        if self.send_changes:
            self.send_line("exec.pipe",\
                           "CompositionDatabase().data['last_modified']["\
                           +repr(old_modified)+"].remove("+repr(id)+")")
        self.addToList('last_modified',time,id)
        self.data['keys'][id]['modified'] = time
        if self.send_changes:
            self.send_line("exec.pipe",\
                           "CompositionDatabase().data['keys']["\
                           +repr(id)+"]['modified'] = "+repr(time))

    def setTags(self, id, tags):
        try:
            old_tags = self.data['keys'][id]['tags']
            self.data['tags'][repr(old_tags)].remove(id)
        except KeyError:
            pass
        except ValueError:
            pass
        
        self.data['keys'].setdefault(id,{})['tags'] = tags
        try:
            self.data['tags'][repr(tags)].append(id)
        except KeyError:
            self.data['tags'][repr(tags)] = [id]

        try:
            self.getComposition(id).tags = copy.deepcopy(tags)
        except KeyError:
            pass #composition not initialized yet (happens during first load...)
        
        if self.send_changes:
            self.send_line("exec.pipe","CompositionDatabase().setTags(" + \
                           repr(id)+","+repr(tags)+")")
        
    def getIdKeys(self, id):
        keys = self.data['keys'][id]
        return keys['name'], keys['version'], keys['song'], keys['riff'],\
               keys['tags'], keys['created'], keys['modified'], keys['deleted']

    def getIdKeysAlt(self, id):
        keys = self.data['keys'][id]
        return (keys['name'], keys['song'], keys['riff'], keys['version'],\
               keys['modified'], id, keys['tags'])

    
    def getID(self):
        self.data['cur_id'] += 1
        if self.send_changes:
            self.send_line("exec.pipe","CompositionDatabase().getID()")
        return self.data['cur_id']
    
    def setID(self, id):
        self.data['cur_id'] = id
        
    def addToList(self, map, key, id):
        try:
            self.data[map][key].append(id)
        except KeyError:
            self.data[map][key] = [id]
        if self.send_changes:
            self.send_line("exec.pipe","CompositionDatabase().addToList("+\
                           repr(map)+","+repr(key)+","+repr(id)+")")
        
    def createNewLocalComposition(self, name=None, version=1,song=None,\
                                  riff=None,tags={}):
        if name == None:
            try:
                name = DfGlobal()["db.default.name"]
            except:
                name = "(author)"
        if song == None:
            try:
                song = DfGlobal()["db.default.song"]
            except:
                song = "(song)"
        if riff == None:
            try:
                riff = DfGlobal()["db.default.riff"]
            except:
                riff = "(riff)"
                
        cur_id = self.getID()
        self.setComposition(cur_id, self.globals["PartialLocalComposition"]\
                            (MkGraph(16,\
             "@red 00 @blue 00 @green 00 @yellow 00 @white 00")) )
        current_date = datetime.datetime.now().strftime("%Y-%m-%d %H.%M:%S")
    
        self.addIdKeys(cur_id, name, version, song, riff, tags, \
                       current_date, current_date, None)

        return cur_id

def filter_results(names_filter, versions_filter, songs_filter, \
                   riffs_filter, show_deleted):
    
    db = CompositionDatabase()
    nkey = filter(names_filter, db.data['names'].keys())
    vkey = filter(versions_filter, db.data['versions'].keys())
    skey = filter(songs_filter,db.data['songs'].keys())
    rkey = filter(riffs_filter,db.data['riffs'].keys())
    
    nids = [set(db.data['names'][key]) for key in nkey]
    vids = [set(db.data['versions'][key]) for key in vkey]
    sids = [set(db.data['songs'][key]) for key in skey]
    rids = [set(db.data['riffs'][key]) for key in rkey]
    idlist = [nids, vids, sids, rids]
    if not show_deleted:
        idlist.append([set(db.data['deleted'][None])])
    all_ids = [reduce(lambda x,y: x|y, ids + [set([-1])]) for ids in idlist]
    common_ids = reduce(lambda x,y:x&y, all_ids)
    common_ids.discard(-1)
    keys = db.data['keys']
    
    if not show_deleted:    
        results = [( " / ".join( map( lambda x: str(x), \
               [keys[id]['name'], keys[id]['song'], keys[id]['riff'],\
                keys[id]['version'],keys[id]['modified'], id, keys[id]['tags']\
                ]   ) ), id ) for id in common_ids]
    else:
        def is_del(id):
            if keys[id]['deleted']:
                return "[DEL] "
            else:
                return ""
        results = [(is_del(id) + " / ".join( map( lambda x: str(x), \
               [keys[id]['name'], keys[id]['song'], keys[id]['riff'],\
                keys[id]['version'],keys[id]['modified'], id, keys[id]['tags']\
                ]   ) ), id ) for id in common_ids]
    results.sort()
    return results

def gen_default_rules():
    db = CompositionDatabase()
    rules = {}
    try:
        ids = filter(lambda x: not db.isDeleted(x),\
                     db.getKey('songs')['##'])
    except KeyError:
        ids = []
    for i in ids:
        riff = (db.getIdKeys(i))[3]
        x = riff.rfind(".")
        lpart = (riff[0:x+1])[:-1].strip()
        rpart = riff[x+1:]
        rules.setdefault(lpart,[]).append( ([(riff,1)], 1.0) )
        rules.setdefault(riff,[]).append( ([(i,0)], 1.0) )
    DfGlobal()['default.rules'] = rules
    return rules


def db_install_callbacks():
    """install the frontend-non-ui-part-callbacks for the database"""
    DfGlobal()["gen_default_rules"] = gen_default_rules
    interpreter = code.InteractiveInterpreter(globals())
    def ex(x):
        try:
            interpreter.runsource(x)
        except:
            print "Error when running: ", x
            

    add_data_channel_handler("exec.pipe",ex)


if __name__ == '__main__':
    DfGlobal()['PotentialGraph'] = PotentialGraph()
    DfGlobal()['StrengthGraph'] = StrengthGraph()
    DfGlobal()['ChangesGraph'] = ChangesGraph() 
    DfGlobal()['GuitarGraph'] = GuitarGraph() 
    db = CompositionDatabase()    
