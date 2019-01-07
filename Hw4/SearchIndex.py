import math
import sys
import os
import re


########################## VARIABLES ######################
d = {} 			#dictionary of term vs {dictionary of doc vs term offsets}
docCnt = 0 		#Total number of documents
queryDict = {} 	#stores unique terms of query after lowering and removing punctuation
DocNoVsTermOffsetDict = {}
ld = {}         #lengths of all documents
##########################################################

#compute TFbm25 for a term in document
def TFBM25(term, docNo):
    tfbm25 = 0
    k1 = 1.2
    b = 0.75
    if term not in d or docNo not in d[term]:
        #print "1"
        return 0
    ftd = len(d[term][docNo])
    Nr = ftd * (k1+1)
    lavg = computelAvg()
    if lavg == 0:
        #print "2"
        return 0
    ldDivlavg = ld[docNo]/lavg
    Dr = ftd+(k1*((1-b)+b*(ldDivlavg)))
    if Dr != 0:
        tfbm25 = Nr/Dr
    return tfbm25

#compute IDF for a term
def IDF(term):
    if term not in d:
        return 0
    if len(d[term]) == 0:
        return 0
    return math.log(float(docCnt)/float(len(d[term])),2) 

#class of docno and corresponding offset
class termPosAndDocNoC:
    def __init__(self, DocNo, termOffset):
        self.termOffset = termOffset
        self.DocNo = DocNo

    def docId(self):
        return self.DocNo

    def termPosInDoc(self):
        return self.termOffset

    def IsEmpty(self):
        return self.DocNo == -1

    #operator overloading
    def __eq__(self,other):
        return self.DocNo == other.DocNo and self.termOffset == other.termOffset

    def __gt__(self,other):
        if self.DocNo > other.DocNo:
            return self.DocNo > other.DocNo
        if self.DocNo < other.DocNo:
            return self.DocNo > other.DocNo
        if self.termOffset > other.termOffset:
            return self.termOffset > other.termOffset
        else:
            return self.termOffset > other.termOffset

    def __lt__(self,other):
        if self.DocNo < other.DocNo:
            return self.DocNo < other.DocNo
        if self.DocNo > other.DocNo:
            return self.DocNo < other.DocNo
        if self.termOffset < other.termOffset:
            return self.termOffset < other.termOffset
        else:
            return self.termOffset < other.termOffset

    def __le__(self,other):
        if self < other:
            return self < other
        elif self == other:
            return self == other
        else:
            return self == other

    def __ge__(self,other):
        if self > other:
            return self > other
        elif self == other:
            return self == other
        else:
            return self == other

    def __add__(self, number):
        return termPosAndDocNoC(self.DocNo, self.termOffset+number)

    def __sub__(self, other):
        res = 0
        if self.DocNo == other.DocNo and self.termOffset == other.termOffset:
            return res
        for doc in DocNoVsTermOffsetDict:
            if doc > other.DocNo:
                if doc < self.DocNo :
                    res = res + len(DocNoVsTermOffsetDict[doc])
                elif doc == self.DocNo:
                    for offset in DocNoVsTermOffsetDict[doc]:
                        if offset < self.termOffset:
                            res = res + 1
            if doc == other.DocNo:
                if doc == self.DocNo:
                    for offset in DocNoVsTermOffsetDict[doc]:
                        if offset > other.termOffset and offset < self.termOffset:
                            res = res + 1
                else :
                    for offset in DocNoVsTermOffsetDict[doc]:
                        if offset > other.termOffset:
                            res = res + 1
             
        return res+1

#utility function for galloping search
P = {}
def populatePostingListGallopingSearch():
    for term in d:
        for doc in sorted(d[term].iterkeys()):
            if term not in P:
                P[term] = []
            for offset in sorted(d[term][doc]):
                P[term].append(termPosAndDocNoC(doc,offset))

#utility function for galloping search
l = {}
def populateLengthPostingList():
    for term in P:
        l[term] = len(P[term])

# ADT : first 
def first(term):
    if term in d:
        for docNo in sorted(d[term].iterkeys()):
            for offset in sorted(d[term][docNo]):
                return termPosAndDocNoC(docNo,offset)
    return ""

# ADT : last
def last(term):
    if term in d:
        for docNo in sorted(d[term].keys(), reverse=True):
            for offset in sorted(d[term][docNo],reverse=True):
                return termPosAndDocNoC(docNo,offset)
    return ""

#binary search for galloping search for next
def binarySearchNext(term, low, high, current):
    while high - low > 1:
        mid = (low+high)/2
        if P[term][mid] <= current:
            low = mid
        else:
            high = mid
    return high

#binary search for galloping search for prev
def binarySearchPrev(term, low, high, current):
    while high - low > 1:
        mid = (low+high)/2
        if P[term][mid] >= current:
            high = mid
        else:
            low = mid
    return low

# ADT galloping search for next term
c = {}
def next(term, current):
    if term not in l:
        return termPosAndDocNoC(-1,-1)
    if l[term] == 0 or P[term][l[term]-1] <= current:
        return termPosAndDocNoC(-1,-1)
    if P[term][0] > current:
        c[term] = 0
        return P[term][c[term]]
    
    if c[term] > 0 and P[term][c[term]-1] <= current:
        low = c[term] - 1
    else:
        low = 0
   
    jump = 1
    high = low + jump
  
    while (high < l[term] and P[term][high] <= current):
        low = high
        jump = jump*2
        high = low + jump
   
    if high > l[term]:
        high = l[term]
   
    c[term] = binarySearchNext(term, low, high, current)
    return P[term][c[term]]

#ADT galloping search for prev term
b = {}
def prev(term, current):
    if l[term] == 0 or P[term][0] >= current:
        return termPosAndDocNoC(-1,-1)
    
    if P[term][l[term]-1] < current:
        c[term] = l[term] - 1
        return P[term][c[term]]

    if b[term] < l[term] and P[term][b[term]+1] >= current:
        high = b[term] + 1
    else:
        high = len(P[term]) - 1
    
    jump = 1
    low = high - jump

    while low >= 0 and P[term][low] >= current:
        high = low
        jump = jump*2
        low = high - jump

    if low < 0:
        low = 0

    b[term] = binarySearchPrev(term, low, high, current)
    return P[term][b[term]]

def farthestNextTermUtil(term,position):
    res = position
    for i in range(0,queryDict[term]):
        res = next(term, res)
    return res

#utility functions for nextCover
def farthestNextTermLocFromCurr(position):
    res = termPosAndDocNoC(-1,-1)
    for term in queryDict:
        nextLoc = farthestNextTermUtil(term, position)
        if nextLoc.IsEmpty():
            return nextLoc
        if (res.IsEmpty()):
            res = nextLoc
        elif nextLoc > res :
            res = nextLoc
    return res

def farthestPrevTermUtil(term,position):
    res = position
    for i in range(0,queryDict[term]):
        res = prev(term, res)
    return res

#utility functions for nextCover
def farthestPrevTermLocFromCurr(position):
    res = termPosAndDocNoC(-1,-1)
    for term in queryDict:
        prevLoc = farthestPrevTermUtil(term,position)
        if prevLoc.IsEmpty():
            return prevLoc
        if (res.IsEmpty()):
            res = prevLoc
        elif prevLoc < res:
            res = prevLoc
    return res

#finds cover having start and end in same document
def nextCover(position):
    v = farthestNextTermLocFromCurr(position)
    if v.IsEmpty():
        return [(v,v)]
    u = farthestPrevTermLocFromCurr(v + 1)
    if u.docId() == v.docId():
        return [(u,v)]
    else:
        return nextCover(u)

# computes rank proximity scores for required documents
Result = {}
def rankProximity():
    pos = termPosAndDocNoC(-1,-1)
    nCover = nextCover(pos)
    for s,e in nCover:
        u = s
        v = e
    d = u.docId()
    score = 0.0
    j = 0
    while(not u.IsEmpty()) :
        if d < u.docId():
            j = j + 1
            Result[d] = score
            d = u.docId()
            score = 0.0
        if v-u != -1:
            score = score + 1.0/float((v-u+1))
        nCover = nextCover(u)
        for s,e in nCover:
            u = s
            v = e
    if(d <= docCnt):
        j = j + 1
        if d != -1:
            Result[d] = score

# doc at a time, for debugging purposes
def rankBM25():
    for doc in range(1,docCnt+1):
        score = 0
        for term in queryDict:
            #print term + " " + str(doc) + " " + str(TFBM25(term, doc)) + " " + str(IDF(term))
            val = TFBM25(term, doc)*IDF(term)
            score = score + val
        if score != 0:
            Result[doc] = score

def computevTF(tfStats, q, quotaLeft):
    sum = 0
    index = 0
    while sum < quotaLeft and index < len(tfStats):
        sum = sum + tfStats[index]*q
        index = index + 1
    if index >= len(tfStats):
        return 0
    return index

#term at a time with pruning
def rankBM25TermAtATimePruning(amax,u):
    sortedT = sorted(queryDict.items(), reverse=False, key=lambda x:x[1])
    acc = []
    acc_dash = []
    acc.append([float('inf'),0])

    for item in sortedT:
        quotaLeft = amax - len(acc) + 1 # Added 1 as end of list should not be considered
        term = item[0]
        if term not in d:
            continue
        if len(d[term]) <= quotaLeft:
            #do same as rankBM25TermAtATime
            inPos = 0
            outPos = 0
            for doc in sorted(d[term]):
                while acc[inPos][0] < doc:
                    acc_dash.insert(outPos,acc[inPos])
                    outPos = outPos + 1
                    inPos = inPos + 1
                score = IDF(term) * TFBM25(term,doc)
                acc_dash.insert(outPos, [doc, score])
                if acc[inPos][0] == doc:
                    acc_dash[outPos][1] = acc_dash[outPos][1] + acc[inPos][1]
                    inPos = inPos + 1
                outPos = outPos + 1

            while acc[inPos][0] < float('inf'):
                 acc_dash.insert(outPos,acc[inPos])
                 outPos = outPos + 1
                 inPos = inPos + 1
            acc_dash.insert(outPos,[float('inf'),0])
            temp = {}
            temp = acc
            acc = acc_dash
            acc_dash = temp

        elif quotaLeft == 0:
            for j in range(0,len(acc)-1):
                acc[j][1] = acc[j][1] + IDF(term) * TFBM25(term,acc[j][0])

        else:
            tfStats = []
            for i in range(0,2000):
                tfStats.insert(i,0)
            Vtf = 0
            postingsSeen = 0
            inPos = 0
            outPos = 0
            for doc in sorted(d[term]):
                while acc[inPos][0] < doc:
                    acc_dash.insert(outPos,acc[inPos])
                    outPos = outPos + 1
                    inPos = inPos + 1
                if acc[inPos][0] == doc:
                    score = acc[inPos][1] + IDF(term) * TFBM25(term, doc)
                    acc_dash.insert(outPos,[doc,score])
                    inPos = inPos + 1
                    outPos = outPos + 1
                elif quotaLeft > 0:
                    if len(d[term][doc]) >= Vtf:
                        score = IDF(term) * TFBM25(term,doc)
                        acc_dash.insert(outPos,[doc,score])
                        outPos = outPos + 1
                        quotaLeft = quotaLeft - 1
                    ftd = len(d[term][doc])
                    tfStats[ftd] = tfStats[ftd] + 1
                
                postingsSeen = postingsSeen + 1
                if postingsSeen % u == 0:
                    q = (len(d[term]) - postingsSeen)/postingsSeen
                    Vtf = computevTF(tfStats, q, quotaLeft)
            while acc[inPos][0] < float('inf'):
                acc_dash.insert(outPos,acc[inPos])
                outPos = outPos + 1
                inPos = inPos + 1
            acc_dash.insert(outPos,[float('inf'),0])
            temp = {}
            temp = acc
            acc = acc_dash
            acc_dash = temp

    for item in acc:
        if item[0] != float('inf') and item[1] != 0:
            Result[item[0]] = item[1]

def computeQId():
    for term in queryDict:
        return ord(term[0])

#prints result in trec_top_file format
def printResultTrecTopFile(numOfRes):
    listOfTuples = sorted(Result.items(), reverse=True, key=lambda x:x[1])
    numofResults = min(len(listOfTuples),int(numOfRes))
    qid = computeQId()
    for i in range(0,numofResults):
        print str(qid) + " 0 " + str(listOfTuples[i][0]) + " " + str(i+1) + " " + str(listOfTuples[i][1]) + " " + "run1"  
    

def computelAvg():
    sum = 0
    if len(ld) == 0:
        laverage = 0
    else:
        for l in ld:
            sum = sum + ld[l]
        laverage = sum / len(ld)
    return laverage

#utility function to store doc vs corresponding offsets
def computeDocNoVsTermOffsets():
    for term in d:
        for doc in d[term]:
            if doc not in DocNoVsTermOffsetDict:
                DocNoVsTermOffsetDict[doc] = []
            for offset in sorted(d[term][doc]):
                DocNoVsTermOffsetDict[doc].append(offset)
        
file = open(sys.argv[1], "r+")

offset = 0
if(os.stat(sys.argv[1]).st_size != 0):
    docCnt = 1

#stores the corpus in dictionary, term vs (doc vs offset)
#removes punctuation, lowers the term 
for line in file:
    if len(line) == 1:
        ld[docCnt] = offset
        docCnt = docCnt + 1
        offset = 0
    termsInLine = re.findall(r"[\w']+", line)
    for term in termsInLine:
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
            else :
                d[lTerm][docCnt].append(offset)

ld[docCnt] = offset


#utility functions for computing scores
computeDocNoVsTermOffsets()

#find unique terms in query
termsinQuery = re.findall(r"[\w']+", sys.argv[4])
for term in termsinQuery:
    lTerm = term.lower()
    if lTerm not in queryDict:
        queryDict[lTerm] = 0
    queryDict[lTerm] = queryDict[lTerm] + 1

#temporary variables used in galloping search
for term in queryDict:
    c[term] = 0
    b[term] = 0

# Utility Functions
populatePostingListGallopingSearch()
populateLengthPostingList()

if sys.argv[2] == "proximity":
    rankProximity() 
if sys.argv[2] == "bm25":
    rankBM25TermAtATimePruning(5,1)
if sys.argv[2] == "bm25_doc":
    rankBM25()

printResultTrecTopFile(sys.argv[3])

file.close()
