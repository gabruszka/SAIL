'''
Created on 03-11-2013

@author: Gabco
'''
import re
import numpy as np
import math
from nltk import FreqDist
from nltk.tokenize.punkt import PunktSentenceTokenizer, PunktParameters
from nltk.tokenize import RegexpTokenizer
import nltk
import codecs
import itertools
from operator import itemgetter

def customWordtokenize(text):
        #starting quotes
        text = re.sub(r'([ (\[{<])"', r'\1 " ', text)

        #punctuation
        text = re.sub(r'([:,])([^\d])', r' \1 \2', text)
        text = re.sub(r'\.\.\.', r' ... ', text)
        text = re.sub(r'[;@#$%&]', r' \g<0> ', text)
        text = re.sub(r'([^\.])(\.)([\]\)}>"\']*)\s*$', r'\1 \2\3 ', text)
        text = re.sub(r'[?!]', r' \g<0> ', text)

        text = re.sub(r"([^'])' ", r"\1 ' ", text)

        #parens, brackets, etc.
        #text = re.sub(r'\<.*\>', r' ', text)
        text = re.sub(r'[\]\[\(\)\{\}]', r' \g<0> ', text)
        text = re.sub(r'--', r' -- ', text)

        #add extra space to make things easier
        text = " " + text + " "

        #ending quotes
        text = re.sub(r'"', " \" ", text)
        text = re.sub(r'(\S)(\'\')', r'\1 \2 ', text)

        text = re.sub(r"([^' ])('[sS]|'[mM]|'[dD]|') ", r"\1 \2 ", text)
        text = re.sub(r"([^' ])('ll|'re|'ve|n't|) ", r"\1 \2 ", text)
        text = re.sub(r"([^' ])('LL|'RE|'VE|N'T|) ", r"\1 \2 ", text)

        text = re.sub(" +", " ", text)
        text = text.strip()

        #add space at end to match up with MacIntyre's output (for debugging)
        if text != "":
            text += " "

        return text.split()


class Engine():
    
    def __init__(self ):
        path = 'D:\\Studia\\MGR\workspace\\SAIL\\Main\\'
        
        self.__encodings = ['utf8', 'iso-8859-1']
        self.__tokens = []
        self.__ignoredCommon = set([])
        self.__freqDist = None
        
        #Zipf
        self.__logx = []
        self.__logfreqDist = []
        self.__polyFit = None
        self.__absZipfError = None
        
        #foreign
        self.__allowed = set(open(path + 'allowed.txt').read().split())
        self.__foreignWords = None
        self.__foreignWordsCount = 0
        
        #POS tagging
        self.__taggedCorpus = []
        self.__taggedTokens = []
        self.__tagCount = 0

        self.__regexRules = set(open(path + 'regexTagsRules.txt').readlines())
        self.__customTags = dict()
        for line in codecs.open(path + 'customTags.txt', encoding='utf-8').readlines():
            words = line.split()
            self.__customTags[words[0]] = set(words[1:])
        self.__syntaxRules = []
        
        self.__defaultTag = ''
        self.__defTagger = nltk.DefaultTagger(self.__defaultTag)
        
        
    def getTokens(self):
        return self.__tokens
        
    def getTaggedTokens(self):
        return self.__taggedTokens
        
    def getTaggedTokensCount(self):
        return len(self.__taggedTokens)
        
    def getTagCount(self):
        return self.__tagCount
    
    def getTaggedCorpus(self):
        return self.__taggedCorpus
        
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

    def setAllowedForeignWordSet(self, newSet):
        self.__allowed = newSet
            
    def getAllowedForeignWordSet(self):
        return self.__allowed
        
    def getForeignWords(self):
        return self.__foreignWords
    
    def getForeignWordsCount(self):
        return self.__foreignWordsCount
        
    def getForeignPercentage(self):
        return round(self.__foreignWordsCount*100/float(self.__wordCount), 2)
    
    def getRawText(self):
        return self.__rawText
        
    def getWordCount(self):
        return self.__wordCount
        
    def getMostCommon(self, count):
        out = []
        i=0
        while len(out)<count:
            if self.__freqDist.items()[i][0] not in self.__ignoredCommon:
                out.append(self.__freqDist.items()[i])
            i+=1
        return out
    
    def getHapaxes(self):
        return self.__freqDist.hapaxes()
    
    def getAvgWordLength(self):
        return self.__avgWordLength
    
    def getAvgSentLength(self):
        return self.__avgSentLength
    
    def getLexicalDiversity(self):
        return self.__lexicalDiversity
        
    def loadCorpus(self, path):
        
        self.rawTokenized = False
        #badChars = '[\\\*\-\"\`\%\&()\[\]\'\.\,\{\}\d_@:;<>\?\!]'
        
        for encoding in self.__encodings:
            
            try:
                fileName = codecs.open(path,'r',encoding=encoding)
                self.__rawText = fileName.read()
                
                punkt_param = PunktParameters()
                punkt_param.abbrev_types = set(['dr', 'vs', 'n', 'v', 'etc', 'art', 'p', 'Cost', 'ss', 'pag'])
                sentence_splitter = PunktSentenceTokenizer(punkt_param)
                text = re.sub('[\'\<\>]', ' ', self.__rawText)
                sentences = sentence_splitter.tokenize(text)
                
                tokenizer = RegexpTokenizer('[a-zA-Z0-9\xE0\xE8\xEC\xF2\xF9\xE1\xE9\xED\xF3\xFA]+')
                self.__avgSentLength = round(sum([len(tokenizer.tokenize(sent)) for sent in sentences if len(tokenizer.tokenize(sent)) > 0])/float(len(sentences)), 3)
                self.__tokens = list(itertools.chain(*[ customWordtokenize(sent) for sent in sentences]))
                self.__concordanceIndex = nltk.ConcordanceIndex([token for token in self.__tokens])
                
                #TOKENS
                purified = re.sub('[^a-zA-Z\xE0\xE8\xEC\xF2\xF9\xE1\xE9\xED\xF3\xFA]', ' ', self.__rawText)
                tokens = nltk.word_tokenize(purified.lower())
                self.__freqDist = FreqDist(tokens)

                self.__wordCount = len(tokens)
                self.__lexicalDiversity = round(len(tokens)/float(len(self.__freqDist.items())), 3)
                self.__avgWordLength = round(sum([len(token) for token in tokens])/float(len(tokens)), 3)
                
                self.resetTags()
                
                return encoding
            
            except UnicodeDecodeError:
                print 'UnicodeDecodeError'
                 
            except UnicodeEncodeError:
                print 'UnicodeEncodeError'
                
        return ""
    
    def loadPOSCorpus(self, path):
        
        for encoding in self.__encodings:
            
            try:
                file = codecs.open(path,'r',encoding=encoding)
                POScorpus = []
                for line in file.readlines():
                    words = line.split()
                    if words[1] in {'NOUN', 'ADV', 'ADJ', 'PRON', 'DPREP', 'VERB', 'NUM', 'PREP', 'ART', 'CONJ', 'PRONVERB', 'PUNCT'}:
                        POScorpus.append((words[0], words[1]))
                    else:
                        print 'Unknown tag!: ' + words[1]
                break
            except UnicodeDecodeError:
                print 'UnicodeDecodeError'
                 
            except UnicodeEncodeError:
                print 'UnicodeEncodeError'
                
        self.__taggedCorpus = POScorpus
        
    def computeZipf(self):
        self.__logx = np.array([math.log(i, 10) for i in  range(1, len(self.__freqDist.values())+1) ] )
        self.__logfreqDist = np. array([math.log(i, 10) for i in self.__freqDist.values() ])
        self.__polyFit = np.polyfit(self.__logx, self.__logfreqDist, 1)
        rel_error = sum([abs(self.__logfreqDist[i] - self.getPoly(self.__logx[i])) for i in self.__logx ])
        self.__absZipfError = rel_error/float(sum([self.__logfreqDist[i] for i in self.__logx]))
        
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
    
    def findForeignWords(self):
        
        cond1 = re.compile('.*[xkwjy].*')
        cond2 = re.compile('.*[qrtpsdfghlzcvbnm]$')
        self.__foreignWords = [item for item in self.__freqDist.items() if cond1.match(item[0]) or (cond2.match(item[0]) and item[0] not in self.__allowed)]
        self.__foreignWordsCount = sum([word[1] for word in self.__foreignWords])

    def findPattern(self, pattern):
        
        cond = re.compile(unicode(pattern))
        return [item for item in self.__freqDist.items() if cond.match(item[0])]        
        
    # zdania
    def findWordContext(self, word, lines=25, wordCount=2):
        
        contexts = []
        offsets = self.__concordanceIndex.offsets(unicode(word))
  
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

    def applyTaggers(self, taggers, fromPOSCorpus = False):
        
        if len(self.__taggedTokens) == 0:
            self.resetTags(fromPOSCorpus)
            
        for tagger in taggers:
            if tagger == 'manual':
                self.applyManualTagger()
                
        tagCount = 0
        notTagged=[]
        for token in self.__taggedTokens:
            if token[1]!=self.__defaultTag:
                tagCount+=1
            else:
                notTagged.append(token[0])
                
        for token in FreqDist(notTagged).items():
            print token[0].encode('utf-8') + ' '+ str(token[1])
            
        self.__tagCount = tagCount
        
    def resetTags(self, fromPOSCorpus=False):
        if fromPOSCorpus:
            self.__taggedTokens = self.__defTagger([token[0] for token in self.__taggedCorpus])
        else:
            self.__taggedTokens = self.__defTagger.tag(self.__tokens)

    def applyManualTagger(self):
                
        for i in range(len(self.__taggedTokens)):
            for tag in self.__customTags:
                if self.__taggedTokens[i][0].lower() in self.__customTags[tag]:
                    self.__taggedTokens[i] = (self.__taggedTokens[i][0], tag)





