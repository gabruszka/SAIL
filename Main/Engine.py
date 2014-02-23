'''
Created on 03-11-2013

@author: Gabco
'''
import re
import numpy as np
import math
from nltk import FreqDist
from nltk import punkt
import nltk
import codecs
from operator import itemgetter

class Engine():
    
    def __init__(self ):
        self.__path = ""
        self.__rawTokenized = False
        self.__allowed = set(open('D:\\Studia\\MGR\workspace\\SAIL\\Main\\allowed.txt').read().split())
        self.__ignoredCommon = set([])
        self.__freqDist = None
        self.__logx = []
        self.__logfreqDist = []
        self.__polyFit = None
        self.__foreignWords = None
        self.__absZipfError = None
        self.__sentences = None
        
    def get_freq_dist(self):
        return self.__freqDist

    def get_absZipfError(self):
        return self.__absZipfError

    def get_logfreqDist(self):
        return self.__logfreqDist

    def get_logx(self):
        return self.__logx

    def getPoly(self, x):
        return np.poly1d(self.__polyFit)(x)

    def getPolyFit(self):
        return self.__polyFit
    
    def get_ignored_common(self):
        return self.__ignoredCommon

    def set_ignored_common(self, value):
        self.__ignoredCommon = value

    def setPath(self,path):
        self.__path = path
        
    def setAllowedForeignWordSet(self, newSet):
        self.__allowed = newSet
            
    def getAllowedForeignWordSet(self):
        return self.__allowed
        
    def getForeignWords(self):
        return self.__foreignWords
    
    def getForeignPercentage(self):
        return round(self.__foreignWords.N()*100/float(self.__tokens.__len__()), 2)
    
    def getRawText(self):
        return self.__rawText
        
    def getWordCount(self):
        return self.__tokens.__len__()
        
    def getTokens(self):
        return self.__tokens
        
    def getSentences(self):
        return self.__sentences
        
    def getMostCommon(self, count):
        out = []
        i=0
        while len(out)<count:
            if self.__freqDist.items()[i][0] not in self.__ignoredCommon:
                out.append(self.__freqDist.items()[i])
            i+=1
        return out
        #return self.freqDist.items()[:count]
    
    def getHapaxes(self):
        return self.__freqDist.hapaxes()
    
    def getAvgWordLength(self):
        return round(sum([len(token) for token in self.__tokens])/float(self.__tokens.__len__()), 3)
    
    def getLexicalDiversity(self):
        return round(self.__tokens.__len__()/float(len(set([token for token in self.__tokens]))), 3)
        
    def loadCorpus(self):
        
        self.rawTokenized = False
        #badChars = '[\\\*\-\"\`\%\&()\[\]\'\.\,\{\}\d_@:;<>\?\!]'
        
        encodingList = ['utf8', 'iso-8859-1']
        
        for encoding in encodingList:
            
            try:
                fileName = codecs.open(self.__path,'r',encoding=encoding)
                
                self.__rawText = fileName.read()
                purified = re.sub('[^a-zA-Z0-9\xE0\xE8\xEC\xF2\xF9\xE1\xE9\xED\xF3\xFA\,\.\?\!\(\)]', ' ', self.__rawText)
                
                sent_tokenizer=nltk.data.load('tokenizers/punkt/italian.pickle')
                self.__sentences = sent_tokenizer.tokenize(purified.strip())
                print self.__sentences[:2]
                self.__tokens = nltk.word_tokenize(purified.lower())
                
                self.__freqDist = FreqDist(self.__tokens)

                return encoding
            
            except UnicodeDecodeError:
                print 'UnicodeDecodeError'
                 
            except UnicodeEncodeError:
                print 'UnicodeEncodeError'
                
        return ""
    
    #tokeny
    def computeZipf(self):
        self.__logx = np.array([math.log(i, 10) for i in  range(1, len(self.__freqDist.values())+1) ] )
        self.__logfreqDist = np. array([math.log(i, 10) for i in self.__freqDist.values() ])
        self.__polyFit = np.polyfit(self.__logx, self.__logfreqDist, 1)
        rel_error = sum([abs(self.__logfreqDist[i] - self.getPoly(self.__logx[i])) for i in self.__logx ])
        self.__absZipfError = rel_error/float(sum([self.__logfreqDist[i] for i in self.__logx]))
    
    
    #tokeny
    def findBigrams(self):
        
        bigrams = dict()
        allowed = {'q', 'w', 'e', 'r', 't', 'y', 'u', 'i', 'o', 'p', 'a', 's', 'd', 'f', 'g', 'h', 'j', 'k', 'l', 'z', 'x', 'c', 'v', 'b', 'n', 'm', u'\xe0', u'\xe8', u'\xec', u'\xe9', u'\xf9', u'\xf2'}
        for first in allowed:
            for second in allowed:
                bigrams[first+second] = 0
                
        for token in self.__tokens:
            for i in range(len(token)-1):
                bigram = token[i]+token[i+1]
                bigrams[bigram] = bigrams[bigram] + 1;
                    
        self.__sortedBigrams = sorted(bigrams.items(), key=itemgetter(1))
        
        for i in range(len(self.__sortedBigrams)):
            print str(i) + ' ' + self.__sortedBigrams[i][0].encode('iso-8859-1') + ' ' + str(self.__sortedBigrams[i][1])
    
    #tokeny
    def findForeignWords(self):
        cond1 = re.compile('.*[xkwjy].*')
        cond2 = re.compile('.*[qrtpsdfghlzcvbnm]$')
        self.__foreignWords = FreqDist([token  for token in self.__tokens if cond1.match(token) or (cond2.match(token) and token not in self.__allowed)])
       # self.findBigrams()
        
        
    # tokeny
    def findPattern(self, pattern):
        cond = re.compile(unicode(pattern))
        return FreqDist([token  for token in self.__tokens if cond.match(token)])
        
        
        
    # zdania
    def findWordContext(self, word, lines=25, wordCount=2):
        
#         if (not self.rawTokenized):
#             self.rawTokenized = True
#             self.rawTokens = nltk.word_tokenize(self.rawText)
        
        c = nltk.ConcordanceIndex(self.__tokens, key = lambda s: s.lower())
        contexts = []
        offsets = c.offsets(unicode(word))
  
        if offsets:
            lines = min(lines, len(offsets))
            for i in offsets:
                if lines <= 0:
                    break
                left = (' '.join(self.__tokens[i-wordCount:i]))
                right = ' '.join(self.__tokens[i+1:i+wordCount+1])
                contexts.append( left + ' ' + self.__tokens[i].upper() + ' ' + right)
                lines -= 1
        return contexts

