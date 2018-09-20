import Mention
import itertools

def read(path):
    words = []
    mens = []
    input = open(path, 'r')
    for line in input:
        if line.startswith('-DOCSTART-') is not True:
            strs = line.strip().split('\t')
            words.append(strs[0])
            if len(strs) == 7:
                if strs[1] == 'B':
                    men = Mention.Mention(len(mens)+1, strs[2], strs[4].split('/')[-1])
                    mens.append(men)
    return mens, words

recall_counter = 0
all_counter = 0
count_men = 0

#######################read freebasepop
Ent2F1 = {}
input_f1 = open('./data/PPRforNED-master/Freebase_popularity_CONLL', 'r')
for line in input_f1:
    strs = line.strip().split('\t')
    Ent2F1[strs[0]] = strs[1]
print 'F1 loaded ...'

Ent2F2 = {}
input_f2 = open('./data/pagerank_CONLL', 'r')
for line in input_f2:
    strs = line.strip().split('\t')
    Ent2F2[strs[0]] = strs[1]
print 'F2 loaded ...'

Can2ID = {}
idinput = open('./data/tsprPageIDs.keys_CONLL', 'r')
for line in idinput:
    line = line.strip()
    strs = line.split('\t')
    Can2ID[strs[1]] = strs[0]
print 'tsprPageIDs loaded ...'

idinput = open('./data/tspr.CONLL', 'r')
record = {}
for line in idinput:
    line = line.strip()
    strs = line.split('\t')
    if strs[0] in Can2ID.values():
        insidedic = {}
        for i in range(1,len(strs)):
            insidedic[strs[i].split(':')[0]] = strs[i].split(':')[1]
        record[strs[0]] = insidedic
print 'tspr_all loaded ...'

for it in range(1,1394):
    ####### read the mentions and possibly entities
    path = './data/split/' + str(it) + '.tsv'
    mens, words = read(path)
    count_men += len(mens)
    ####### read the entities
    path = './data/PPRforNED-master/AIDA_candidates/' + str(it)
    input1 = open(path, 'r')
    ID2Cans = {}
    ID2Men = {}
    flag = 0
    for line in input1:
        if line.startswith('ENTITY') is True:
            flag += 1
            s = line.strip().split('\t')
            men = Mention.Mention(flag, s[1].split(':')[-1], s[8].split('/')[-1])
            ID2Men[flag] = men
        else:
            if flag not in ID2Cans:
                words = []
            else:
                words = ID2Cans[flag]
            strs = line.strip().split('\t')
            word = strs[5].split('/')[-1]
            words.append(word)
            ID2Cans[flag] = words
    print it

    ID2Men_linkable = {}

    for id in ID2Men:
        if ID2Men[id].get_trueEn() != 'url:NIL':
            ID2Men_linkable[id] = ID2Men[id]


    refinedmens = [] ##### remove the inconsistency all mentions left
    ref_ID2Cans = {} ##### left mentions
    ref_ID2Mention = {}
    for men in mens:
        for t_men in ID2Men_linkable.values():
            if men.get_name() == t_men.get_name():
                men.set_trueEn(t_men.get_trueEn())
                ref_ID2Cans[men.get_id()] = ID2Cans[t_men.get_id()]
                ref_ID2Mention[men.get_id()] = men
                refinedmens.append(men)
                break
    ### read the two features and write
    if it>=1 and it<= 946:
        output = open('./data/train/canEnt_' + str(it) + '.txt', 'w')
    elif it>946 and it<= 1162:
        output = open('./data/dev/canEnt_' + str(it) + '.txt', 'w')
    else:
        output = open('./data/test/canEnt_' + str(it) + '.txt', 'w')

    for ment in refinedmens:
        men = ment.get_name()
        output.write(men + '\t' + ment.get_trueEn() + '\t')
        if ment.get_id() not in ref_ID2Cans:
            output.write('NIL')
        else:
            canEnts = ref_ID2Cans[ment.get_id()]
            sf1 = 0
            sf2 = 0
            for item in canEnts:
                if item in Ent2F1:
                    sf1 += float(Ent2F1[item])
                else:
                    sf1 += 0
                    Ent2F1[item] = 0
                if item in Ent2F2:
                    sf2 += float(Ent2F2[item])
                else:
                    sf2 += 0
                    Ent2F2[item] = 0
            for item in canEnts:
                if float(sf1) != 0:
                    output.write(item + '*' + str(round(float(Ent2F1[item])/float(sf1),3)))
                else:
                    output.write(item + '*' + str(0))
                if float(sf2) != 0:
                    output.write('*' + str(round(float(Ent2F2[item])/float(sf2),3))+ '\t')
                else:
                    output.write('*' + str(0)+ '\t')
        output.write('\n')

    # generate TSPR
    # id 2 entity
    if it>=1 and it<= 946:
        output1 = open('./data/train/record_' + str(it) + '.txt', 'w')
    elif it>946 and it<= 1162:
        output1 = open('./data/dev/record_' + str(it) + '.txt', 'w')
    else:
        output1 = open('./data/test/record_' + str(it) + '.txt', 'w')

    for com in itertools.combinations(ref_ID2Cans.keys(), 2):
        canen0 = ref_ID2Cans[com[0]]
        canen1 = ref_ID2Cans[com[1]]
        for e0 in canen0:
            for e1 in canen1:
                if e0 in Can2ID and Can2ID[e0] in record and e1 in Can2ID:
                    insidedic = record[Can2ID[e0]]
                    if Can2ID[e1] in insidedic:
                        output1.write(e0 + '\t' + e1 + '\t' + insidedic[Can2ID[e1]] + '\n')
        for e1 in canen1:
            for e0 in canen0:
                if e1 in Can2ID and Can2ID[e1] in record and e0 in Can2ID:
                    insidedic = record[Can2ID[e1]]
                    if Can2ID[e0] in insidedic:
                        output1.write(e1 + '\t' + e0 + '\t' + insidedic[Can2ID[e0]] + '\n')




