import Mention
import canEntity
import random
import itertools
import math
import copy
import Feature

### read the entity-entity recor

###########################################################################################################3
def add_factors(mapping, theta):
    numerator = 1
    intAs = []  # {the assignment of entities, only entities}
    for k in mapping:
        f_rtf = mapping[k].get_rtf()
        f_es = Feature.es(mention2ID[k].get_name(), mapping[k].get_name())
        numerator = numerator * math.exp(f_rtf * theta[0])
        numerator = numerator * math.exp(f_es * theta[1])
        f_rpm = mapping[k].get_rpm()
        numerator = numerator * math.exp(f_rpm * theta[2])
        intAs.append(mapping[k]) # iniAs <- mappings

    for com in itertools.combinations(intAs, 2):
        f_tspr = Feature.tspr(com[0].get_name(), com[1].get_name(),eeDic)
        numerator = numerator * math.exp(f_tspr * theta[3])
    return intAs, numerator
###########################################################################################################
def remove_canEntities(mentions, iter_canEntities,mapping):
    for i in range(0, len(mentions)): # remove the assigned ones from the candidates
        ents = iter_canEntities[mentions[i]]
        if mapping[mentions[i]] in ents:
            ents.remove(mapping[mentions[i]])
            iter_canEntities[mentions[i]] = ents
    return iter_canEntities

def findmax(record, Score):
    return record[max(Score.items(), key=lambda x: x[1])[0]], Score[max(Score.items(), key=lambda x: x[1])[0]]
########################################################################################################################
def mstep(state, theta, iter_canEntities, mentions, sign):
    mapping = state[0]
    Sco = state[1]
    record = {}  # {No, mapping}
    Score = {}  # {No,score(probability)}
    W_score = {}
    record[len(record)] = mapping
    Score[len(record) - 1] = Sco
    iter_canEntities = remove_canEntities(mentions, iter_canEntities, mapping)

    for i in range(0,len(mentions)): # iteration over the rest...
        m = mentions[i]
        for en in iter_canEntities[m]:
            itermapping = copy.deepcopy(mapping)
            itermapping[m] = en
            record[len(record)] = itermapping  # record the mapping with a number
            intAs, numerator = add_factors(itermapping, theta)
            sco = numerator
            Score[len(record) - 1] = sco  # store the score
            W_score[len(record) - 1] = get_wscore(itermapping)  # store the score

    if sign == 't':
        bestMap, S = findmax(record, W_score)
        for item in record:
            if record[item] == bestMap:
                id = item
        Sco = Score[id]
    else:
        bestMap, Sco = findmax(record, Score)
    return [bestMap, Sco]

########################################################################################################################
def get_wscore(ma):
    counter = 0
    for item in ma:
        men = mention2ID[item]
        true = men.get_trueEn()
        re = ma[item].get_name()
        if true == re:
            counter += 1
    #print  str(counter) + ' / ' + str(len(ma))
    return float(counter) / float(len(ma))
########################################################################################################################

def inference(mentions, canEntities, theta):
    # mentions are fixed in the graph but the assigned entities could change
    record = {} # {No, mapping}
    Score = {} #{No,score(probability)}
    mapping = {} # mentions and the assignment of entities
    State = [] # record the atomic change

    print canEntities
    for i in range(0,len(mentions)):
        mapping[mentions[i]] = canEntities[mentions[i]][random.randint(0, len(canEntities[mentions[i]]) -1)] # generate
        # the random initial assignment of entities to each mention
    record[len(record)] = mapping # record the mapping with a number
    intAs, numerator = add_factors(mapping, theta)
    sco = numerator
    # after a round, store the score, remove the assigned ones from the candidates, remove the assignment from the graph
    Score[len(record)-1] = sco # store the score
    State.append([mapping, sco])
    ######################### eva
    print get_wscore(mapping)
    print sco

    for step in range(0, len(mapping)):
        iter_canEntities = copy.deepcopy(canEntities)
        state = mstep(State[step], theta, iter_canEntities, mentions, 'i')
        last_state = State[len(State)-1]
        if state[1] > last_state[1]:
            State.append(state)
        else:
            break
        mapping = state[0]
        print get_wscore(mapping)

    return State

########################################################################################################################
def cal_del(y_max, y_min):
    #find the difference
    dif_ent_max = None
    dif_ent_min = None
    dif_men = None
    nalda = [0,0,0,0]
    for item in y_max:
        if y_max[item].get_name() != y_min[item].get_name():
            dif_men = item
            dif_ent_max = y_max[item]
            dif_ent_min = y_min[item]
    if dif_men is not None and dif_ent_max is not None and dif_ent_min is not None:
        f_rtf_max = dif_ent_max.get_rtf()
        f_rtf_min = dif_ent_min.get_rtf()
        nalda[0] = f_rtf_max - f_rtf_min
        f_es_max = Feature.es(dif_ent_max.get_name(), mention2ID[dif_men].get_name())
        f_es_min = Feature.es(dif_ent_min.get_name(), mention2ID[dif_men].get_name())
        nalda[1] = f_es_max - f_es_min
        f_rpm_max = dif_ent_max.get_rpm()
        f_rpm_min = dif_ent_min.get_rpm()
        nalda[2] = f_rpm_max - f_rpm_min
        f_tspr_max = 0
        f_tspr_min = 0
        for m in y_max:
            if m != dif_men:
                f_tspr_max += Feature.tspr(dif_ent_max.get_name(), y_max[m].get_name(),eeDic)
                f_tspr_min += Feature.tspr(dif_ent_min.get_name(), y_min[m].get_name(),eeDic)
        nalda[3] = f_tspr_max - f_tspr_min
    return nalda

# train with Sample rank
def traning(mentions, canEntities, theta):
    eta = 0.001
    mapping = {} # mentions and the assignment of entities
    State = [] # record the atomic change

    for i in range(0,len(mentions)):
        mapping[mentions[i]] = canEntities[mentions[i]][random.randint(0, len(canEntities[mentions[i]]) -1)] # generate
        # the random initial assignment of entities to each mention
    intAs, numerator = add_factors(mapping, theta)
    sco = numerator

    State.append([mapping, sco])
    turn = 0
    state = None
    for step in range(0, len(mapping)):
        turn += 1
        iter_canEntities = copy.deepcopy(canEntities)
        state = mstep(State[step], theta, iter_canEntities, mentions, 't')
        last_state = State[len(State)-1]
        if state[1] > last_state[1] or turn ==1:
            State.append(state)
            ## update theta
            w_t = get_wscore(last_state[0])
            w_t1 = get_wscore(state[0])
            y_max = last_state if w_t >w_t1 else state
            y_min = last_state if w_t <=w_t1 else state
            gap = w_t - w_t1 if w_t >w_t1 else w_t1 - w_t
            Nabla = cal_del(y_max[0], y_min[0])
            cambiar = 0
            for i in range(0,4):
                cambiar += Nabla[i]*theta[i]
            ### update of theta
            if cambiar < gap and gap!=0:
                for j in range(0,4):
                    theta[j] += Nabla[j]*eta
                print theta
                reout.write(str(it) + '\t' )
                for i in range(0,4):
                    reout.write(str(theta[i]) + '\t')
                reout.write('\n')
                reout.flush()
                    #Theta.append(theta)
            #print theta
        else:
            break
    if state is not None:
        print get_wscore(state[0]) #only record the last one
    return theta

########################################################################################################################
reout = open('./recordTheta_four.txt', 'w')
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
theta = [0,0,0,0]
for iteration in range(0,5):
    for it in range(1,1164):
        eeDic = {}
        if it>=1 and it<= 946:
            eeinput = open('./data_new/train/record_' + str(it) + '.txt', 'r')
        elif it>=947 and it<= 1162:
            eeinput = open('./data_new/dev/record_' + str(it) + '.txt', 'r')
        else:
            eeinput = open('./data_new/test/record_' + str(it) + '.txt', 'r')

        for eeline in eeinput:
            strs = eeline.strip().split('\t')
            if strs[0] not in eeDic:
                ents = {}
            else:
                ents = eeDic[strs[0]]
            ents[strs[1]] = float(strs[2])
            eeDic[strs[0]] = ents
        ## read the document
        if it>=1 and it<= 946:
            docinput = open('./data_new/train/canEnt_' + str(it) + '.txt','r')
        elif it>=947 and it<= 1162:
            docinput = open('./data_new/dev/canEnt_' + str(it) + '.txt', 'r')
        else:
            docinput = open('./data_new/test/canEnt_' + str(it) + '.txt', 'r')

        mention2ID = {}
        Amentions = [] # all the mentions
        mentions = []
        canEntities = {} # all the mentions and their candidate entities (full)
        result = {}
        for line in docinput:
            line = line.strip()
            strs = line.split('\t')
            men = Mention.Mention(len(mentions), strs[0], strs[1])
            if strs[2] == 'NIL':
                result[men] = 'NIL'
            else:
                can = []
                for i in range(2, len(strs)):
                    canE = canEntity.canEntity(strs[i].split('*')[0], float(strs[i].split('*')[1]), float(strs[i].split('*')[2]), len(mentions))
                    can.append(canE)
                canEntities[men.get_id()] = can
                mention2ID[men.get_id()] = men
                mentions.append(men.get_id())
            Amentions.append(men)
        theta = traning(mentions, canEntities, theta)