import Mention
import canEntity
import random
import itertools
import math
import copy
import Feature

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
            #G = remove_factors(G, intAs, factors)
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

#    print canEntities
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
#    print get_wscore(mapping)
#    print sco

    for step in range(0, len(mapping)):
        iter_canEntities = copy.deepcopy(canEntities)
        state = mstep(State[step], theta, iter_canEntities, mentions, 'i')
        last_state = State[len(State)-1]
        if state[1] > last_state[1]:
            State.append(state)
        else:
            break

        #mapping = state[0]
        #print get_wscore(mapping)

    return State
    # first... how to calculate the probability... ***

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
    #print dif_ent_max.get_name() + '\t' + dif_ent_min.get_name()
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

# train with Sample rank... to get better assignment of theta = [0.25,0.25,0.25,0.25]
def traning(mentions, canEntities,theta):
    eta = 0.01
    if theta != [0,0,0,0]:
        Theta = [theta]
    else:

        Theta = []
    mapping = {} # mentions and the assignment of entities
    State = [] # record the atomic change

    for i in range(0,len(mentions)):
        mapping[mentions[i]] = canEntities[mentions[i]][random.randint(0, len(canEntities[mentions[i]]) -1)] # generate
        # the random initial assignment of entities to each mention
    intAs, numerator = add_factors(mapping, theta)
    sco = numerator
#    G = remove_factors(G, intAs, factors)

    State.append([mapping, sco])
    ### eva
    #print get_wscore(mapping)
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
            Theta.append(theta)
            #print theta
        else:
            break
    if state is not None:
        print get_wscore(state[0]) #only record the last one

    final_theta = [0,0,0,0]
    for item in Theta:
        for i in range(0,4):
            final_theta[i] += item[i]
    for i in range(0,4):
        final_theta[i] = final_theta[i]/len(Theta)
    return final_theta

########################################################################################################################
# precision : all mentions that are linked by the system and determin correctnes
# recall : all mentions should be linked
# fi = harmonic mean of it...

# theta = [0.09837000000000012,0.13587424631063386,0.7018899999999987,0.33513741447784107] 0.773195876289random1 train
# theta = [0.08190999999999969, 0.12587459977205429, 0.6847000000000029, 0.3266415003490769] 0.772956125629 random2 train
# theta = [0.25,0.25,0.25,0.25] 0.745864301127
# theta = [0.09886999999999972, 0.08795646723074878, 0.6951400000000039, 0.37944988942470276] 0.77271637497 random2 train+dev
# theta = [0.11419999999999962, -0.005882426974839623, 0.7338399999999984, 0.39916584869740085] 0.772956125629 random3 train+dev
# theta = [0.1584000000000004, 0.13998986156014137, 0.9100000000000029, 0.46015197309721106] 0.772476624311
# theta = [0.21414000000000127, 0.09636238594105033, 1.0667000000000078, 0.5840387429895233] 0.771517621673
theta = [0.2308199999999999, 0.06587297857687167, 1.102400000000009, 0.6409893368280525] # 0.774154878926
# theta = [0.29393000000000113, 0.07491127167747598, 1.187840000000021, 0.7821407368557122] 0.773915128267
# theta = [0.07053000000000052, 0.1760155087154423, 0.6483199999999992, 0.1974958271669585] 0.767202109806
# theta = [0.10034000000000078, 0.16563528110523015, 0.7204199999999991, 0.2938456336182005] 0.770079117718
# theta = [0.15853270137524525, 0.10462837737358223, 0.8347315569744581, 0.49268039595909763] #0.772476624311
p_counter = 0
r_counter = 0
true_counter = 0

for it in range(1163, 1394):
    eeDic = {}
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

    docinput = open('./data_new/test/canEnt_' + str(it) + '.txt','r')
    mention2ID = {}
    Amentions = [] # all the mentions
    mentions = []
    canEntities = {} # all the mentions and their candidate entities (full)
    result = {}
    for line in docinput:
        line = line.strip()
        strs = line.split('\t')
        men = Mention.Mention(len(Amentions), strs[0], strs[1])
        mention2ID[men.get_id()] = men
        Amentions.append(men.get_id())

        if strs[2] == 'NIL':
            result[men] = 'NIL'
        else:
            can = []
            for i in range(2, len(strs)):
                canE = canEntity.canEntity(strs[i].split('*')[0], float(strs[i].split('*')[1]), float(strs[i].split('*')[2]), len(mentions))
                can.append(canE)
            canEntities[men.get_id()] = can
            mentions.append(men.get_id())
    state = inference(mentions, canEntities, theta)
    final_mapping = state[-1][0]

    # record the answer
    reout = open('./data_new/test_ans/'+ str(it) + '.txt', 'w')
    counter = 0
    for m in Amentions:
        if m not in final_mapping:
            reout.write(mention2ID[m].get_name() + '\t' + 'NIL')
        else:
            men = mention2ID[m]
            true = men.get_trueEn()
            re = final_mapping[m].get_name()
            reout.write(men.get_name() + '\t' + true + '\t' + re)
            if true == re:
                counter += 1
        reout.write('\n')
    #############
    true_counter += counter
    p_counter += len(final_mapping)
    r_counter += len(Amentions)
    #############
    print final_mapping
    print Amentions
    if float(len(final_mapping))>0:
        d_precision = float(counter) / float(len(final_mapping))
    else:
        d_precision = 0
    if float(len(Amentions))>0:
        d_recall = float(counter) / float(len(Amentions))
    else:
        d_recall = 0
    if float(len(final_mapping)) + float(len(Amentions))>0:
        d_f1 = 2*float(counter)/ (float(len(final_mapping)) + float(len(Amentions)))
    else:
        d_f1 = 0
    print str(it) + '\t' + str(d_precision) + '\t' + str(d_recall) + '\t' + str(d_f1)

    reout.write('\n')
    reout.flush()

allout = open('./test_answer.txt', 'w')

all_precision = float(true_counter) / float(p_counter)
all_recall = float(true_counter) / float(r_counter)
all_f1 = 2*float(true_counter)/ (float(p_counter) + float(r_counter))

allout.write(str(true_counter) + '\t' + str(p_counter) + '\t' + str(r_counter) + '\t' + str(all_precision) + '\t' + str(all_recall) + '\t' + str(all_f1))