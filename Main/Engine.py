'''
Created on 03-11-2013

@author: Gabco
'''
import nltk
import re
from nltk import FreqDist
import codecs

class Engine():
    
    def __init__(self ):
        self.path = ""
        #raw=open('lowerBlogs.txt','r').read()
        
    def setPath(self,path):
        self.path = path
        
    def loadCorpus(self):

        badChars = '[\\\*\-\"\`\%\&()\[\]\'\.\,{}_@:;<>\?\!]'
        file = codecs.open(self.path,'r',encoding='iso-8859-1')

        fullText = file.read().lower()
        fullText = re.sub(badChars, ' ', fullText)

        self.tokens=nltk.word_tokenize(fullText)
        self.freqDist = FreqDist(nltk.Text(self.tokens))
        
    def getWordCount(self):
        return self.tokens.__len__()
        
    def getTokens(self):
        return self.tokens
        
    def getMostCommon(self, count):
        return self.freqDist.items()[:count]
    
    def getHapaxes(self):
        hapaxes = []
        for word in self.freqDist.items():
            if word[1]==1:
                hapaxes.append(word[0])
        return hapaxes
    
    def findWordContext(self, word, wordsOnLeft=7, wordsOnRight=7, lines=25):
        c = nltk.ConcordanceIndex(self.tokens, key = lambda s: s.lower())
        contexts = []
        offsets = c.offsets(str(word))
        
        for line in range(0, lines):
            left = ' '.join([self.tokens[offsets[line]-j] for j in reversed(range(1, wordsOnLeft+1))])
            right = ' '.join([self.tokens[offsets[line]+j] for j in range(1, wordsOnRight+1)])
            contexts.append(left + ' ' + self.tokens[offsets[line]] + ' ' + right)
        return contexts
        #c.offsets("non")
        #print([self.tokens[offset+1] for offset in c.offsets('non')])
        #contexts =  text.concordance("non")
        #return text.concordance(word)
        
        
        