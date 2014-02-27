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
        self.__letters = {'q', 'w', 'e', 'r', 't', 'y', 
                          'u', 'i', 'o', 'p', 'a', 's', 
                          'd', 'f', 'g', 'h', 'j', 'k', 
                          'l', 'z', 'x', 'c', 'v', 'b', 
                          'n', 'm', 
                          u'\xe0', u'\xe1', u'\xe8', u'\xe9', u'\xec', u'\xed', 
                          u'\xf2', u'\xf3', u'\xf9', u'\xfa'
                          }
            
        self.__encodings = ['utf8', 'iso-8859-1']
        self.__tokens = []
        self.__ignoredCommon = set([])
        self.__freqDist = None
        
        #Zipf
        self.__logx = []
        self.__logfreqDist = []
        self.__polyFit = None
        self.__relZipfError = None
        
        #foreign
        self.__allowed = set(open(path + 'allowed.txt').read().split())
        self.__foreignWords = None
        self.__foreignWordsCount = 0
        
        #POS tagging
        self.__taggedCorpus = []
        self.__taggedTokens = []
        self.__tagCount = 0
        self.__tagErrorCount = 0
        self.__wrongTags = []

        self.__regexTagRules = dict()
        for line in set(codecs.open(path + 'regexTagsRules.txt', encoding='utf-8').readlines()):
            if len(line)>4 and  line[0]!= '#':
                words = line.split()
                self.__regexTagRules[re.compile(unicode(words[0]))] = (words[1], words[2:])
        
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
    
    def getTagErrorCount(self):
        return self.__tagErrorCount
    
    def getTaggedCorpus(self):
        return self.__taggedCorpus
        
    def get_relZipfError(self):
        return self.__relZipfError

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
        
    def getWordTypesCount(self):
        return len(self.__freqDist.items())
        
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
    
    def getHapaxCount(self):
        return len(self.__freqDist.hapaxes())
    
    def getHapaxPercentage(self):
        return round(len(self.__freqDist.hapaxes())*100/float(len(self.__freqDist.items())), 2)
    
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
                text = re.sub('[\'\<\>`]', ' ', self.__rawText)
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
                    if len(words) > 1:
                        if words[1] in {'NOUN', 'ADV', 'ADJ', 'PRON', 'DPREP', 'VERB', 'NUM', 'PREP', 'ART', 'CONJ', 'PRONVERB', 'PUNCT', 'SPECIAL'}:
                            POScorpus.append((words[0], words[1]))
                        else:
                            print 'Unknown tag!: ' + words[1]
                    else:
                        print line
                break
            except UnicodeDecodeError:
                print 'UnicodeDecodeError'
                 
            except UnicodeEncodeError:
                print 'UnicodeEncodeError'
                
                
                
        self.__taggedCorpus = POScorpus
        
    def computeZipf(self, input):
        
        if input == 'word':
            self.__logx = np.array([math.log(i, 10) for i in  range(1, len(self.__freqDist.values())+1) ] )
            self.__logfreqDist = np. array([math.log(i, 10) for i in self.__freqDist.values() ])
        
        if input == 'bigram':
            
            bigramFreqDist = dict()
            for first in self.__letters:
                for second in self.__letters:
                    bigramFreqDist[first+second] = 0
            
            for token in self.__freqDist.items():
                for ii in range(len(token[0])-1):
                    try:
                        bigram = token[0][ii]+token[0][ii+1]
                        bigramFreqDist[bigram] += token[1]
                    except KeyError:
                        print token
                        
            
            self.__sortedBigrams = sorted([x for x in bigramFreqDist.items() if x[1]>0], key=itemgetter(1))
            self.__sortedBigrams.reverse()
            self.__logx = np.array([math.log(i, 10) for i in  range(1, len(self.__sortedBigrams)+1) ] )
            self.__logfreqDist = np. array([math.log(i[1], 10) for i in self.__sortedBigrams])
            
        if input == 'letter':

            letterFreqDist = dict()
            for letter in self.__letters:
                    letterFreqDist[letter] = 0
                
            for token in self.__freqDist.items():
                for ii in range(len(token[0])):
                    letter = token[0][ii]
                    letterFreqDist[letter] += token[1]
            
            self.__sortedLetters = sorted([x for x in letterFreqDist.items() if x[1]>0], key=itemgetter(1))
            self.__sortedLetters.reverse()
            self.__logx = np.array([math.log(i, 10) for i in  range(1, len(self.__sortedLetters)+1) ] )
            self.__logfreqDist = np. array([math.log(i[1], 10) for i in self.__sortedLetters])
        
        self.__polyFit = np.polyfit(self.__logx, self.__logfreqDist, 1)
        
        poweredPoly = [np.power(10, self.getPoly( self.__logx[i] ) ) for i in  range(len(self.__logx))]
        
        relativeErrors = [ abs( self.__freqDist.values()[i] - poweredPoly[i] )
                                        / float( self.__freqDist.values()[i] ) for i in  range(len(self.__logx)) ]
        
        self.__relZipfError = np.mean( relativeErrors ) * 100
        
    def findForeignWords(self):
        
        cond1 = re.compile('.*[xkwjy].*')
        cond2 = re.compile('.*[qrtpsdfghlzcvbnm]$')
        self.__foreignWords = [item for item in self.__freqDist.items() if cond1.match(item[0]) or (cond2.match(item[0]) and item[0] not in self.__allowed)]
        self.__foreignWordsCount = sum([word[1] for word in self.__foreignWords])

    def findPattern(self, pattern):
        
        cond = re.compile(unicode(pattern))
        return [item for item in self.__freqDist.items() if cond.match(item[0])]        
        
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
        
        self.resetTags(fromPOSCorpus)
            
        for tagger in taggers:
            if tagger == 'manual':
                self.applyManualTagger()
            if tagger == 'regex':
                self.applyRegexTagger()
                
        tagCount = 0
        notTagged = []
        self.__wrongTags = []
        if fromPOSCorpus:
            errorCount = 0
            wrongTags = []
            for i  in range(len(self.__taggedTokens)):
                if self.__taggedTokens[i][1]!=self.__defaultTag:
                    tagCount+=1
                    if self.__taggedTokens[i][1] != self.__taggedCorpus[i][1]:
                        errorCount+=1
                        wrongTags.append((i, self.__taggedTokens[i][0], self.__taggedTokens[i][1], self.__taggedCorpus[i][1]))
                        self.__wrongTags.append(self.__taggedTokens[i][0])
                else:
                    notTagged.append(self.__taggedTokens[i][0])
                    
            for token in wrongTags:
                print token
            
            self.__tagErrorCount = errorCount
                   
        else:
            for token in self.__taggedTokens:
                if token[1]!=self.__defaultTag:
                    tagCount+=1
                else:
                    notTagged.append(token[0])
        #for token in FreqDist(notTagged).items():
        #    print token
        
        self.__tagCount = tagCount
            
    def resetTags(self, fromPOSCorpus):
        if fromPOSCorpus:
            self.__taggedTokens = self.__defTagger.tag([token[0] for token in self.__taggedCorpus])
        else:
            self.__taggedTokens = self.__defTagger.tag(self.__tokens)

    def applyManualTagger(self):
                
        for i in range(len(self.__taggedTokens)):
            if self.__taggedTokens[i][1] == self.__defaultTag:
                for tag in self.__customTags:
                    if self.__taggedTokens[i][0].lower() in self.__customTags[tag]:
                        self.__taggedTokens[i] = (self.__taggedTokens[i][0], tag)

    def applyRegexTagger(self):
        
        path = 'D:\\Studia\\MGR\workspace\\SAIL\\Main\\'
        self.__regexTagRules = dict()
        for line in set(codecs.open(path + 'regexTagsRules.txt', encoding='utf-8').readlines()):
            if len(line)>4 and  line[0]!= '#':
                words = line.split()
                self.__regexTagRules[re.compile(unicode(words[0]))] = (words[1], words[2:])
                print words[0].encode('utf-8')
                print words[1], words[2:]
        
        
        
        
        
        for i in range(len(self.__taggedTokens)):
            if self.__taggedTokens[i][1] == self.__defaultTag:
                for rule in self.__regexTagRules:
                    if self.__taggedTokens[i][1] == self.__defaultTag:
                        word = self.__taggedTokens[i][0].lower()
                        if word not in self.__regexTagRules[rule][1] and rule.match(word):
                            self.__taggedTokens[i] = (self.__taggedTokens[i][0], self.__regexTagRules[rule][0])
                        #if self.__taggedTokens[i][0].lower() in self.__customTags[tag]:
                        #    self.__taggedTokens[i] = (self.__taggedTokens[i][0], tag)
        



