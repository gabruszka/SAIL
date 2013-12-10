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

        badChars = '[\\\*\-\"\`\%\&()\[\]\'\.\,\{\}\d_@:;<>\?\!]'
        file = codecs.open(self.path,'r',encoding='iso-8859-1')

        self.fullText = file.read()
        fullText = re.sub(badChars, ' ', self.fullText.lower())

        self.tokens=nltk.word_tokenize(fullText)
        self.freqDist = FreqDist(nltk.Text(self.tokens))
        
    def getFullText(self):
        return self.fullText
        
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
    
    def findWordContext(self, word, lines=25, width=75):
        c = nltk.ConcordanceIndex(self.tokens, key = lambda s: s.lower())
        contexts = []
        offsets = c.offsets(str(word))
        #textLen = len(self.tokens)
        #if offsets != []:
           # for line in range(0, min(lines,len(offsets)) ):
               # left = ' '.join([self.tokens[offsets[line]-j] for j in reversed(range(1, wordsOnLeft+1)) if offsets[line]-j > 0])
               # right = ' '.join([self.tokens[offsets[line]+j] for j in range(1, wordsOnRight+1) if offsets[line]+j < textLen])
                #contexts.append(left + ' ' + self.tokens[offsets[line]] + ' ' + right)
        #return contexts
    
        half_width = (width - len(word) - 2) / 2
        context = width/5 # approx number of words of context

        #offsets = self.offsets(word)
        if offsets:
            lines = min(lines, len(offsets))
            #print "Displaying %s of %s matches:" % (lines, len(offsets))
            for i in offsets:
                if lines <= 0:
                    break
                left = (' ' * half_width +
                        ' '.join(self.tokens[i-context:i]))
                right = ' '.join(self.tokens[i+1:i+context])
                left = left[-half_width:]
                right = right[:half_width]
                contexts.append( left + ' ' + self.tokens[i].upper() + ' ' + right)
                lines -= 1
        return contexts
    
    
    
    
        #c.offsets("non")
        #print([self.tokens[offset+1] for offset in c.offsets('non')])
        #contexts =  text.concordance("non")
        #return text.concordance(word)
        
        
        