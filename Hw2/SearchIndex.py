import math
import sys
import os
import re


########################## VARIABLES ######################
d = {} 			#dictionary of term vs {dictionary of doc vs term offsets}
docCnt = 0 		#Total number of documents
queryDict = {} 	#stores unique terms of query after lowering and removing punctuation
DocNoVsTermOffsetDict = {} 
##########################################################

#compute TF for a term in document
def TF(term,docNo):
    ftd = len(d[term][docNo])
    if ftd > 0:
        return math.log(ftd,2) + 1
    return 0

#compute IDF for a term
def IDF(term):
    if term not in d:
        return -1
    if len(d[term]) == 0:
        return 0
    return math.log(float(docCnt)/float(len(d[term])),2) 

#product of TF and IDF
def TFIDF(term,docNo):
    tfVal = TF(term, docNo)
    idfVal = IDF(term)
    return tfVal * idfVal

#store product of TF and IDF for a document
TfIdfRes = {}
def computeDocTfIdf(dictTfIdf):
    for term in sorted(dictTfIdf.iterkeys()):
        for docNo in dictTfIdf[term]:
            if docNo not in TfIdfRes:
                TfIdfRes[docNo] = []
            TfIdfRes[docNo].append(dictTfIdf[term][docNo])
 
#store normalized TF*IDF for a document
TfIdfNormalized = {}
def normalizeTfIdf():
    for docNo in TfIdfRes:
        normalizedVal = 0
        for val in TfIdfRes[docNo]:
            normalizedVal = normalizedVal + val*val
        res = math.sqrt(normalizedVal)
        for val in TfIdfRes[docNo]:
            if docNo not in TfIdfNormalized:
                TfIdfNormalized[docNo] = []
            if res == 0:
                TfIdfNormalized[docNo].append(0)
            else:
                TfIdfNormalized[docNo].append(val/res)

#computes TF.IDF, stores in doc vector, then computes normalized values
dictTfIdf = {}
def computeTFIDF():
    for term in sorted(d.iterkeys()):
        for docNo in range(1,docCnt+1):
            TfIdfRes = 0
            if docNo in d[term]:
                TfIdfRes = TFIDF(term,docNo)
            if term not in dictTfIdf:
                dictTfIdf[term] = {}
            
            dictTfIdf[term][docNo] = TfIdfRes

    computeDocTfIdf(dictTfIdf)
    normalizeTfIdf()

#computes TF for a query vector
def TFQuery(term):
    if queryDict[term] > 0 :
        return math.log(queryDict[term],2) + 1
    return 0

#computes product of TF and IDF
def computeTfIdfQuery(term):
    tfVal = TFQuery(term)
    idfVal = IDF(term)
    return tfVal * idfVal    
 
#computes product of TF and IDF and stores in query vector
TfIdfQueryVec = []
def computeTfIdfQueryVec():
    for term in sorted(d.iterkeys()):
        if term in queryDict:
            TfIdfQueryVec.append(computeTfIdfQuery(term))
        else:
            TfIdfQueryVec.append(0)

#computes normalized query vector 
TfIdfNormalizedQuery = []
def computeNormalizedQueryVec():
    computeTfIdfQueryVec()
    res = 0
    for val in TfIdfQueryVec:
        res = res + val*val
    res = math.sqrt(res)  
    for val in TfIdfQueryVec:
        if res == 0:
            TfIdfNormalizedQuery.append(0)
        else:
            TfIdfNormalizedQuery.append(val/res)

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

#debugging utilities
def debugPoint(pos):
    print pos.docId(),
    print pos.termPosInDoc()

def debugNCover(nCover):
    for s,e in nCover:
        print "START ",
        debugPoint(s)
        print "END ",
        debugPoint(e)

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

#utility functions for nextCover
def farthestNextTermLocFromCurr(position):
    res = termPosAndDocNoC(-1,-1)
    for term in queryDict:
        nextLoc = next(term, position)
        if nextLoc.IsEmpty():
            return nextLoc
        if (res.IsEmpty()):
            res = nextLoc
        elif nextLoc > res :
            res = nextLoc
    return res

#utility functions for nextCover
def farthestPrevTermLocFromCurr(position):
    res = termPosAndDocNoC(-1,-1)
    for term in queryDict:
        prevLoc = prev(term,position)
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
        Result[d] = score

    for x in range(1,docCnt+1):
        if x not in Result:
            Result[x] = 0

#finds next document containing all terms
def nextDoc(start):
    for docNo in range(start+1,docCnt+1):
        allTerms = True
        for term in queryDict:
            if(term not in d):
                allTerms = False
                break
            else:
                if docNo not in d[term]:
                    allTerms = False
                    break
        if allTerms == True:
            return docNo
    return 0

#computes dot product of query and document
def computeScore(docNo):
    score = 0
    for i in range(0,len(TfIdfNormalizedQuery)):
        score = score + TfIdfNormalizedQuery[i]*TfIdfNormalized[docNo][i]
    return score

# computes cos values for required documents
def rankCosine():
    d = nextDoc(0)
    while d != 0:
        Result[d] = computeScore(d)
        d = nextDoc(d)
    
    for x in range(1,docCnt+1):
        if x not in Result:
            Result[x] = 0

#prints result in required format
def printResult(numOfRes):
    print "DocId  Score "
    listOfTuples = sorted(Result.items(), reverse=True, key=lambda x:x[1])
    for i in range(0,int(numOfRes)):
        print listOfTuples[i][0],
        print "    ",
        print listOfTuples[i][1]

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
    if line == "\n":
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

#utility functions for computing scores
computeDocNoVsTermOffsets()
computeTFIDF()

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
computeNormalizedQueryVec()
populatePostingListGallopingSearch()
populateLengthPostingList()


if sys.argv[2] == "proximity":
    rankProximity() 
if sys.argv[2] == "cos":
    rankCosine()

printResult(sys.argv[3])

file.close()
