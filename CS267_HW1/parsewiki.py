#reads the file token.txt which has tokens of wikipedia page and computes rank and frquency

#!/usr/bin/python
file=open("tokens.txt","r+")
wordcount={}
for word in file.read().split():
    if word not in wordcount:
        wordcount[word] = 1
    else:
        wordcount[word] += 1

from collections import Counter
x = Counter(wordcount)

rank = 1
s = ' '
print("---------------------------------------------")
print("Rank  Frequency  Token")
print("---------------------------------------------")
for k,v in x.most_common():
    print   rank,s*5,v,s*5,k
    rank = rank + 1

file.close();
