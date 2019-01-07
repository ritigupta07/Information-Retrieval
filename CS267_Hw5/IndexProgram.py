import sys
import glob 
import os
import math
import re

############################################################################
d = {}          #dictionary of term vs {dictionary of doc vs term offsets}
ld = {}
############################################################################

def findUnary(num):
    if num == 1:
        return 1
    if num == 0:
        return 0
    res = "1"
    for i in range(0,num-1):
        res = "0" + res
    return res

def findBinary(num):
    num = int(num)
    if num == 0:
        return "0"
    res = ""
    while num != 0:
        rem = num % 2
        res = str(rem) + res
        num = num/2
    return res

def findMforRice(nt,n):
    if n == 0:
        return 0
    nr = -float(math.log(2.0,2))
    dr = float(math.log(1.0 - (float(nt)/float(n)),2))
    if dr == 0:
        return 0
    mstar = float(nr)/float(dr)
    logmstar = float(math.log(float(mstar),2))
    max = pow(2,float(math.ceil(float(logmstar))))
    return max

def findRiceCode(k, M):
    if M == 0:
        return 0
    q_k = math.floor((float(k-1)/float(M)))
    r_k = (k-1) % M
    res = findUnary(int(q_k)+1)
    binary_r_k = findBinary(r_k)
    numofbits_r_k = math.ceil(float(math.log(float(M),2)))
    if(numofbits_r_k > len(binary_r_k)) :
        diff = numofbits_r_k - len(binary_r_k)
        for i in range(0,int(diff)):
            binary_r_k = "0" + binary_r_k
    res = str(res) + binary_r_k
    return res
    
def findGammaCode(freq):
    if freq == 1:
        return 1
    res = ""
    while freq != 0:
        rem = freq % 2
        res = str(rem) + res
        freq = freq/2

    for i in range(0,len(res)-1):
        res = "0" + res
    return res

def parseCountAndStoreInDict(f, docCnt):
    terms = re.findall(r"[\w']+", f.read())
    offset = 0
    for term in terms:
        offset = offset + 1
        lTerm = term.lower()
        if lTerm not in d:
            d[lTerm] = {}
            d[lTerm][docCnt] = []
            d[lTerm][docCnt].append(offset)
        else:
            if docCnt not in d[lTerm]:
                d[lTerm][docCnt] = []
                d[lTerm][docCnt].append(offset)
            else:
                d[lTerm][docCnt].append(offset)
    return len(terms)

outputFile = open(sys.argv[2], "w")
def convertDictToDeltaList(N):
    for term in sorted(d):
        outputFile.write(term + ":")
        for doc in sorted(d[term].iterkeys()):
            outputFile.write("#" + str(doc) + "#" + str(findGammaCode(len(d[term][doc]))))
            startOffset=0
            M = findMforRice(len(d[term][doc]),ld[doc])
            for offset in sorted(d[term][doc]):
                diffOffset = offset-startOffset
                startOffset = offset
                outputFile.write(findRiceCode(diffOffset,M))
        outputFile.write("\n")

path = sys.argv[1]
files = os.listdir(path)
N = len(files)
outputFile.write(str(N)+"\n")
docNo = 0
for file in sorted(files):
    if file[len(file)-4:len(file)] == ".txt":
        docNo = docNo + 1
        f=open(path+"/"+file, 'r')
        c = parseCountAndStoreInDict(f, docNo)
        outputFile.write(str(docNo) + ":" + file+ ":" + str(c) + "\n")
        ld[docNo] = c
        sys.stdout.write(f.read())
        f.close()

convertDictToDeltaList(N)
outputFile.close()
