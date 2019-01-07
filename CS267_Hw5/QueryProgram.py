import sys
import math
import re

N = 0
lenD = {}
d = {}
queryDict = {}
Result = {}

def computelAvg():
    avg = 0.0
    if N==0:
        return 0
    for doc in lenD:
        avg = avg + float(lenD[doc])
    return avg/float(N)

def computeLc():
    res = 0
    for doc in lenD:
        res = res + int(lenD[doc])
    return res

def computeLt(term):
    res = 0
    for doc in lenD:
        if term not in d or str(doc) not in d[term]:
            res = res + 0
        else:
            res = res + len(d[term][str(doc)])
    return res

def TFBM25(term, docNo):
    tfbm25 = 0
    k1 = 1.2
    b = 0.75
    if term not in d or str(docNo) not in d[term]:
        return 0
    ftd = len(d[term][str(docNo)])
    Nr = ftd * (k1+1)
    lavg = computelAvg()
    if lavg == 0:
        return 0
    ldDivlavg = float(lenD[str(docNo)])/lavg
    Dr = ftd+(k1*((1-b)+b*(ldDivlavg)))
    if Dr != 0:
        tfbm25 = Nr/Dr
    return tfbm25

def IDF(term):
    if term not in d:
        return 0
    if len(d[term]) == 0:
        return 0
    return math.log(float(N)/float(len(d[term])),2)

def checkAllTermsPresent(doc):
    for term in queryDict:
        if term not in d:
            return False
        if str(doc) not in d[term]:
            return False
    return True
 
def rankBM25():
    for doc in range(1,int(N)+1):
        score = 0
        allTermsPresent = checkAllTermsPresent(doc)
        if allTermsPresent == True:
            for term in queryDict:
                val = TFBM25(term, doc)*IDF(term)
                score = score + val
        if score != 0:
            Result[doc] = score

def rankLMJM():
    lc = computeLc()
    lamda = 0.5
    for doc in range(1,int(N)+1):
        score = 0
        allTermsPresent = checkAllTermsPresent(doc)
        if allTermsPresent:
            for term in queryDict:
                lt = computeLt(term)
                ld = lenD[str(doc)]
                ftd = len(d[term][str(doc)])
                qt = queryDict[term]
                if ld!=0 and lt!=0:
                    val = qt*(math.log(1+(((1-lamda)/lamda)*(float(ftd)/int(ld))*(float(lc)/lt)),2))
                    score = score + val
        if score != 0:   
            Result[doc] = score

def computeQId():
    for term in queryDict:
        return ord(term[0])

#prints result in trec_top_file format
def printResultTrecTopFile():
    listOfTuples = sorted(Result.items(), reverse=True, key=lambda x:x[1])
    numofResults = len(listOfTuples)
    qid = computeQId()
    for i in range(0,numofResults):
        print str(qid) + " 0 " + str(listOfTuples[i][0]) + " " + str(i+1) + " " + str(listOfTuples[i][1]) + " "+ "run1"    

def binaryToDecimal(num):
    if num == 0:
        return 0
    if num == 1:
        return 1
    res = 0
    i = 0
    while num != 0:
        x = int(num) % 10
        res = pow(2,i)*x + res
        i = i + 1
        num = int(num)/10
    return res
        
def computeM(nt,n):
    if n == 0:
        return 0
    nr = -float(math.log(2.0,2))
    inputlog = 1.0 - (float(nt)/float(n))
    dr = float(math.log(inputlog,2))
    if dr == 0:
        return 0
    mstar = float(nr)/float(dr)
    logmstar = float(math.log(float(mstar),2))
    max = pow(2,float(math.ceil(float(logmstar))))
    return max

def decodeRice(q_k,r_k,lamda):
    return (q_k *pow(2,lamda)) + (r_k) + 1
    
def encodeCode(code, term):
    i = 1
    while(i < len(code)):
        doc = ""
        if i != 1:
            i = i + 1
        while(code[int(i)] != "#"):
            doc = doc + code[int(i)]
            i = i + 1
        d[term][doc] = []
        cnt = 1
        i = i + 1
        while(code[int(i)] != '1'):
            cnt = cnt+1
            i = i+1
        ftd = binaryToDecimal(code[int(i):int(i+cnt)])
        i = i + cnt
        noOfTermsInDoc = 0
        currOffset = 0
        M = computeM(ftd,lenD[doc])
        lamda = math.ceil(math.log(float(M),2))
        while(noOfTermsInDoc < ftd):
            noOfTermsInDoc = noOfTermsInDoc + 1
            q_k = 0
            while(code[int(i)] != '1'):
                q_k = q_k+1
                i = i + 1
            r_k = binaryToDecimal(code[int(i+1):int(i+1+lamda)])
            offset = decodeRice(q_k,r_k,lamda)
            currOffset = currOffset + offset
            d[term][doc].append(int(currOffset))
            i = i+1+lamda 

file = open(sys.argv[1], "r")
lineNumber = 1
for line in file:
    if lineNumber == 1:
        N = line[0:len(line)-1]
    elif line.count(':') == 2:
        locFirstSeperator = line.find(":")
        locSecondSeperator = line.find(":",locFirstSeperator+1)
        docNum = line[0:locFirstSeperator]
        fileName = line[locFirstSeperator+1:locSecondSeperator]
        lenFile = line[locSecondSeperator+1:len(line)-1]
        lenD[docNum] = lenFile
    else:
        locFirstSeperator = line.find(":")
        term = line[0:locFirstSeperator]
        d[term] = {}
        encodeCode(line[locFirstSeperator+1:len(line)-1],term)

    lineNumber = lineNumber + 1

termsinQuery = re.findall(r"[\w']+", sys.argv[2])
for term in termsinQuery:
    lTerm = term.lower()
    if lTerm not in queryDict:
        queryDict[lTerm] = 0
    queryDict[lTerm] = queryDict[lTerm] + 1

if sys.argv[3] == "bm25":
    rankBM25()
if sys.argv[3] == "lmjm":
    rankLMJM()

printResultTrecTopFile()
