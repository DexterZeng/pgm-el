import Mention
import itertools
## genrate candidate entities
## genrate two feature scores... co-occurence... and relative pagerank score~

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
                    # now we can record the mentions and true entities
                    men = Mention.Mention(len(mens), strs[2], strs[4].split('/')[-1])
                    mens.append(men)

    return mens, words

NIL_counter = []
for it in range(600,602):
    path = './data/split/' + str(it) + '.tsv'
    mens, words = read(path)
    print words
    print mens

    ## it is hard to load and store mention-entity dictionary... calls it when needs it
    ## generate the candidate entites and the first feature!!!
    meinput = open('./data/MentionEntity.ttl', 'r')
    menName = []
    for men in mens:
        if men.get_name() not in menName:
            menName.append(men.get_name().lower())
    menCan = {}
    for line in meinput:
        strs = line.strip().split('\t')
        if len(strs) >=3: ############################################### newly added
            if strs[0] in menName:
                if strs[0] not in menCan:
                    canEn = {}
                else:
                    canEn = menCan[strs[0]]
                canEn[strs[1]] = int(strs[2])
                menCan[strs[0]] = canEn

    finalcan = [] # enitties
    for men in menCan:
        canEnts = menCan[men]
        sort = sorted(canEnts.items(), lambda x, y: cmp(x[1], y[1]), reverse=True)
        if len(sort)>10:
            sort = sort[:10]
        #print sort
        for item in sort:
            if item[0] not in finalcan:
                finalcan.append(item[0])
    #print finalcan

    ### generate the second feature priority
    popolarity = {}
    input = open('./data/pagerank.csv','r')
    for line in input:
        if line.strip().split('\t')[1] in finalcan:
            popolarity[line.strip().split('\t')[1]] = line.strip().split('\t')[2]


    # record the candidate entitites
    finalcanscore = {}
    for fc in finalcan:
        if fc in popolarity:
            finalcanscore[fc] = float(popolarity[fc])
        else:
            finalcanscore[fc] = 0

    if it>=1 and it<= 946:
        output = open('./data/train/canEnt_' + str(it) + '.txt', 'w')
    elif it>946 and it<= 1162:
        output = open('./data/dev/canEnt_' + str(it) + '.txt', 'w')
    else:
        output = open('./data/test/canEnt_' + str(it) + '.txt', 'w')

    top10 = {}
    for ment in mens:
        men = ment.get_name()
        output.write(men + '\t' + ment.get_trueEn() + '\t')
        if men.lower() not in menCan:
            output.write('NIL')
            NIL_counter.append([it, men])
        else:
            canEnts = menCan[men.lower()]
            top10ents = []
            sort = sorted(canEnts.items(), lambda x, y: cmp(x[1], y[1]), reverse=True)
            if len(sort)>10:
                sort = sort[:10]
            #print sort
            s = 0
            sp = 0
            for item in sort:
                top10ents.append(item[0])
                s += item[1]
                sp += finalcanscore[item[0]]
            top10[men.lower()] = top10ents
            for item in sort:
                if float(s) != 0:
                    output.write(item[0] + '*' + str(round(float(item[1])/float(s),3)))
                else:
                    output.write(item[0] + '*' + str(0))
                if float(sp) != 0:
                    output.write('*' + str(round(finalcanscore[item[0]]/float(sp),3))+ '\t')
                else:
                    output.write('*' + str(0)+ '\t')
        output.write('\n')

    Can2ID = {}

    idinput = open('./data/tsprPageIDs.keys', 'r')
    for line in idinput:
        line = line.strip()
        strs = line.split('\t')
        if len(strs) == 2:
            if strs[1] in finalcan:
                Can2ID[strs[1]] = strs[0]

    idinput = open('./data/tspr.all', 'r')
    record = {}

    for line in idinput:
        line = line.strip()
        strs = line.split('\t')
        if strs[0] in Can2ID.values():
            insidedic = {}
            for i in range(1,len(strs)):
                insidedic[strs[i].split(':')[0]] = strs[i].split(':')[1]
            record[strs[0]] = insidedic

    if it>=1 and it<= 946:
        output1 = open('./data/train/record_' + str(it) + '.txt', 'w')
    elif it>946 and it<= 1162:
        output1 = open('./data/dev/record_' + str(it) + '.txt', 'w')
    else:
        output1 = open('./data/test/record_' + str(it) + '.txt', 'w')

    for com in itertools.combinations(top10.keys(), 2):
        canen0 = top10[com[0]]
        canen1 = top10[com[1]]
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
    if (it%10 == 0):
        print NIL_counter
