# NER using MetaMap for disease (and other) term extraction

from pymetamap import MetaMap
from configparser import ConfigParser
import itertools
import re

config = ConfigParser()
config.read('pymetamap/config.ini') #you must change this file
path = config['DEFAULT']['mm_path']
mm_loc = config['DEFAULT']['mm_loc']

mm = MetaMap.get_instance(path)


def str_to_list(string):
    li = list(string[1:-1].split(","))
    return li


def multResolve(concepts): #if a concept occurs multiple times it will be saved as one finding with several indexes. This function unpacks the indexes to make several findings
    newlist = []
    for concept in concepts:

        if concept[1]!= 'MMI': #disregard entries from AA
            continue
        if concept[8].startswith('['):
            allindexes = concept[8].replace('[', '').replace(']', '')
            allindexes = re.split(';|,',allindexes)
            for index in allindexes:
                newcon = [concept[0],concept[1],concept[2],concept[3],concept[4],concept[5],concept[6],concept[7],index,concept[9]]
                newlist.append(newcon)
        elif concept[8].count('/') > 1:
            #print(concept[8])
            allindexes = concept[8].replace('[', '').replace(']', '')
            allindexes = re.split(';|,', allindexes)
            for index in allindexes:
                newcon = [concept[0],concept[1],concept[2],concept[3],concept[4],concept[5],concept[6],concept[7],index,concept[9]]
                newlist.append(newcon)
        else:
            newcon = [concept[0], concept[1], concept[2], concept[3], concept[4], concept[5], concept[6], concept[7],
                      concept[8], concept[9]]
            newlist.append(newcon)
    return newlist


def filterCons(concepts): # MetaMap may return several matches for one concept. This function filters out the most important match for each,
    concepts = multResolve(concepts)

    #concepts = reduceCons(concepts) #remove concepts that are not diseases
    #it is necessary to do this step here as f.e. 'Metastatic Breast Cancer' is of type 'cell' and thus wouldn't be matched
    #if the reduction was done later

    for i, j in itertools.combinations(concepts, 2):
        if i!=j:
            jpos = j[8]
            ipos = i[8]
            jsl = jpos.split('/')
            isl = ipos.split('/')
            if int(isl[0]) == int(jsl[0]): #if both concept start at same index

                if len(i[9]) != 0 and len(j[9])==0: #if 2 concepts have same span but one has MeSH code and the other one hasn't, we keep Mesh concept
                    try:
                        concepts.remove(j)
                    except:
                        continue
                elif len(j[9]) != 0 and len(i[9])==0:
                    try:
                        concepts.remove(i)
                    except:
                        continue
                else:

                    if isl[1] > jsl[1]: # match i has wider span than match j
                        try:
                            concepts.remove(j)
                        except:
                            continue
                    if isl[1] < jsl[1]: # match j has wider span than match i
                        try:
                            concepts.remove(i)
                        except:
                            continue
                    if isl[1] == jsl[1]: #matches have same length
                        jscore = float(j[2])
                        iscore = float(i[2])
                        if jscore > iscore: # take match with higher score
                            try:
                                concepts.remove(i)
                            except:
                                continue
                        if jscore < iscore: # take match with higher score
                            try:
                                concepts.remove(j)
                            except:
                                continue
                        else:
                            try:
                                concepts.remove(j)
                            except:
                                continue

    return concepts


def reduceCons(concepts): #returns all concepts that are diseases
    relevant = []
    for concept in concepts:
        semtype = str_to_list(concept[5])
        print(semtype)
        if not set(semtype).isdisjoint(['dsyn', 'sosy', 'neop']):  # list of all semantic types: https://lhncbc.nlm.nih.gov/ii/tools/MetaMap/Docs/SemanticTypes_2018AB.txt
            relevant.append(concept)
        '''if not set(semtype).isdisjoint(['genf', 'gngm', 'aapp', 'amas', 'cell', 'celc', 'comd']):  # list of all semantic types: https://lhncbc.nlm.nih.gov/ii/tools/MetaMap/Docs/SemanticTypes_2018AB.txt
            relevant.append(concept)'''
    return relevant



def NER(t): #takes string and returns the tagged string + a lookup dictionary containing all entities.

    t = re.sub(r'\s[1-9]+\s',' ', str(t)) # single numerical chars mess with the algorithm and are not of interest for the purpose of this model
    t = t.encode("ascii", errors="ignore").decode()
    text = [t]

    cons, error = mm.extract_concepts(text, [1])

    cons = filterCons(cons)

    for i in range(len(cons)):
        cons[i] = [cons[i][y] for y in (3,4,9)]

    cons.sort()

    return list(k for k,_ in itertools.groupby(cons)) #remove duplicates