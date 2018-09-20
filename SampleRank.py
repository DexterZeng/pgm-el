# implementation of SampleRank with MCMC
def SampleRank(mapping1, mapping2, mention2ID):
    # Input : performance metric # trasition approach # training set
    # Output : 1/t (sum (theta_t))
    y_max, y_min, gap = w(mapping1, mapping2, mention2ID)

def w(mapping1, mapping2, mention2ID):
    # self-defined assessment function
    counter1 = 0
    for item in mapping1:
        men = mention2ID[item]
        true = men.get_trueEn()
        re = mapping1[item].get_name()
        if true == re:
            counter1 += 1
    score1 = float(counter1) / float(len(mapping1))
    counter2 = 0
    for item in mapping2:
        men = mention2ID[item]
        true = men.get_trueEn()
        re = mapping2[item].get_name()
        if true == re:
            counter2 += 1
    score2 = float(counter2) / float(len(mapping2))
    if score1 >= score2:
        y_max = mapping1
        y_min = mapping2
        gap = score1 - score2
    else:
        y_min = mapping1
        y_max = mapping2
        gap = score2 - score1
    return y_max, y_min, gap

