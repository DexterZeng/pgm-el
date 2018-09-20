
input = open('./recordTheta.txt', 'r')
theta = [0,0,0,0]
counter = 0
for line in input:
    strs = line.strip().split('\t')
    if len(strs) == 5:
        counter += 1
        for i in range(0,4):
            if float(strs[i+1])>0 and float(strs[i+1])<5:
                theta[i] += float(strs[i+1])
finatheta = [0,0,0,0]
for i in range(0,4):
    finatheta[i] = theta[i]/float(counter)

print finatheta

