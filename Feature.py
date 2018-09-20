import Levenshtein
# Relative Term Frequency
# all canEN for the mention, add up the frequencies, devide by this one
# also need preprocessing  # ready to read
def rtf(men, en):

    return 0

# edit distance
# input: two name string // output: similarity
def es(string1, string2):
    return 1-float(Levenshtein.distance(string1, string2))/float(max(len(string1), len(string2)))

# document similarity (does not prove to be great!!!)
def ds(men, en):
    return 0

# Relative Page Rank, popularity
# input: name of an entity, candidates, dictionary {entity, unnormalized score,} // output: probability over all candidates
# key issue: need to calculate before hand
def rpm(en, candidates, dic):
    total = 0
    for can in candidates:
        total += dic[can]
    return dic[en]/total

# Topic-Specific PageRank
# two entities per factor
# need to calculate before hand
def tspr(en1, en2, eeDic):
    value = 0.0
    if en1 == en2:
        value += 0.1
    else:
        if en1 in eeDic:
            if en2 in eeDic[en1]:
                value += eeDic[en1][en2]
        if en2 in eeDic:
            if en1 in eeDic[en2]:
                value += eeDic[en2][en1]
    return value
