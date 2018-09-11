# question 3
# counts number of docs in which term appears
def countTermDocs(docList):
    # converting to list to find unique docs
    docSet = set([])
    for a,b in docList:
        docSet.add(a)
    return len(docSet)

# prints document number and character offset
def printDocNumAndCharOffset(docNumAndCharOffsetList):
    i = 1
    for docNo,charOffset in docNumAndCharOffsetList:
        x = (docNo, charOffset)
        print x,
        # print ',' between all entries except for the last one
        if i != len(docNumAndCharOffsetList):
            sys.stdout.write(',')
        i = i + 1
    
    print ''

# checks if term at index is valid. valid term would be between two non-alphanumeric characters
def checkIsValidIndex(line,term,index):
    lastChar = line[index + len(term)]
    if index == 0:
        if not(lastChar.isalnum()):
            return 1
    if not(line[index-1].isalnum()):
        if not(lastChar.isalnum()):
            return 1        
    return 0

import sys
import re
import os

# dictionary would store "term" ==> list of "docNo, CharOffset"
d = {}
file = open(sys.argv[1],"r+")

docCnt = 0
offset = 0

if(os.stat(sys.argv[1]).st_size != 0):
    docCnt = 1

for line in file:
    # increase document counts if '\n' encountered
    # reset offset to 0 within each doc
    if line == "\n":
        docCnt = docCnt+1
        offset = 0

    # find terms using regular expression separators
    termsInLine = re.findall(r"[\w']+", line)

    # find unique terms
    termsSet = set([])
    for term in termsInLine:
        termsSet.add(term)

    # computes characterOffset within document
    for term in termsSet:
        index = 0
        while index < len(line):
            index = line.find(term, index)
            if index == -1:
                break
            if (checkIsValidIndex(line,term,index)):
                y = (docCnt,offset+index)

                # convert to lower case. "Mike" and "mike" treated similar.
                lowerCaseTerm = term.lower()
                if lowerCaseTerm not in d:
                    d[lowerCaseTerm] = []
                d[lowerCaseTerm].append(y)
            index += len(term)

    if line != "\n":
        offset = offset+len(line)


file.close();

for term in sorted(d.iterkeys()):
    print term

    # prints number of docs in which term appears
    sys.stdout.write(str(countTermDocs(d[term])))

    sys.stdout.write(',')

    # prints number of times terms appears across all docs
    sys.stdout.write(str(len(d[term])))

    sys.stdout.write(',')

    # prints document number and character offset
    printDocNumAndCharOffset(d[term])
