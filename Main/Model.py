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


class Model():
    
    def __init__(self ):
        self.__letters = {'q', 'w', 'e', 'r', 't', 'y', 
                          'u', 'i', 'o', 'p', 'a', 's', 
                          'd', 'f', 'g', 'h', 'j', 'k', 
                          'l', 'z', 'x', 'c', 'v', 'b', 
                          'n', 'm', 
                          u'\xe0', u'\xe1', u'\xe8', u'\xe9', u'\xec', u'\xed', 
                          u'\xf2', u'\xf3', u'\xf9', u'\xfa'
                          }
            
        self.__encodings = ['utf8', 'iso-8859-1']
        print len(self.__letters)
        print self.__letters
        self.__defaultTag = ''
        self.__defTagger = nltk.DefaultTagger(self.__defaultTag)
        
    def initFields(self):
        
#         self.__tokens = []
#         self.__freqDist = None
        
        #Zipf
#         self.__logx = []
#         self.__logfreqDist = []
#         self.__polyFit = None
#         self.__relZipfError = None
        
        #foreign
#         self.__foreignWords = None
#         self.__foreignWordsCount = 0
        
        #POS tagging
#         self.__taggedCorpus = []
#         self.__taggedTokens = []
#         self.__tagCount = 0
#         self.__tagErrorCount = 0
#         self.__wrongTags = []

        path = 'D:\\Studia\\MGR\workspace\\SAIL\\Main\\'
        self.__allowedForeign = set(open(path + 'allowedForeign.txt').read().split())
        self.__ignoredCommon = set([])
        self.__ignoredColl = set(open(path + 'ignoredColl.txt').read().split())
        self.__concordanceIndex = None
        #self.__syntaxRules = []
        
    def getWords(self):
        return self.__words
        
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
        self.__allowedForeign = newSet
            
    def getAllowedForeignWordSet(self):
        return self.__allowedForeign
        
    def getForeignWords(self):
        return self.__foreignWords
    
    def getForeignWordsCount(self):
        return self.__foreignWordsCount
        
    def getForeignPercentage(self):
        return round(self.__foreignWordsCount*100/float(self.__wordCount), 2)
    
    def getPatternWords(self):
        return self.__patternWords
    
    def getPatternWordsCount(self):
        return self.__patternWordsCount
        
    def getPatternPercentage(self):
        return round(self.__patternWordsCount*100/float(self.__wordCount), 2)
    
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
        
        #badChars = '[\\\*\-\"\`\%\&()\[\]\'\.\,\{\}\d_@:;<>\?\!]'

        for encoding in self.__encodings:

            try:
                self.__path = path
                fileName = codecs.open( self.__path,'r', encoding=encoding )
                self.__rawText = fileName.read()
                break
            
            except UnicodeDecodeError:
                encoding = ''
                continue
                 
        if encoding!='':
            self.initFields()
            
            #SENTENCES
            punkt_param = PunktParameters()
            punkt_param.abbrev_types = set(['dr', 'vs', 'n', 'v', 'etc', 'art', 'p', 'Cost', 'ss', 'pag'])
            sentence_splitter = PunktSentenceTokenizer(punkt_param)
            text = re.sub('[\'\<\>`]', ' ', self.__rawText)
            #text = re.sub('(\d+)', r' \1 ', text)
            sentences = sentence_splitter.tokenize(text)
            
            #TOKENS
            self.__tokens = list(itertools.chain(*[ customWordtokenize(sent) for sent in sentences]))
            
            wordTokenizer = RegexpTokenizer('[a-zA-Z0-9\xe0\xe1\xe8\xe9\xec\xed\xf2\xf3\xf9\xfa]+')
            #wordTokenizer = RegexpTokenizer('\W+', re.UNICODE)
            sentences = [wordTokenizer.tokenize(sent.lower()) for sent in sentences if len(wordTokenizer.tokenize(sent)) > 0]
            words =  list(itertools.chain(*sentences))
            #self.__words = words
            
            self.__avgSentLength = round(np.mean( [len(sent) for sent in sentences]), 3)
            self.__avgWordLength = round(np.mean( [len(word) for word in words]), 3)
            self.__freqDist = FreqDist(words)
            self.__wordCount = len(words)
            self.__lexicalDiversity = round(len(self.__freqDist.items())/float(len(words)), 3)
                 
        return encoding
    
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
        
    def computeZipf(self, unit):
        
        if unit == 'word':
            self.__logx = np.array([math.log(i, 10) for i in  range(1, len(self.__freqDist.values())+1) ] )
            self.__logfreqDist = np. array([math.log(i, 10) for i in self.__freqDist.values() ])
        
        if unit == 'bigram':
            
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
            
        if unit == 'letter':

            letterFreqDist = dict()
            for letter in self.__letters:
                    letterFreqDist[letter] = 0
                
            for token in self.__freqDist.items():
                for ii in range(len(token[0])):
                    try:
                        letter = token[0][ii]
                        letterFreqDist[letter] += token[1]
                    except KeyError:
                        print token
                        
            self.__sortedLetters = sorted([x for x in letterFreqDist.items() if x[1]>0], key=itemgetter(1))
            self.__sortedLetters.reverse()
            self.__logx = np.array([math.log(i, 10) for i in  range(1, len(self.__sortedLetters)+1) ] )
            self.__logfreqDist = np. array([math.log(i[1], 10) for i in self.__sortedLetters])
        
        self.__polyFit = np.polyfit(self.__logx, self.__logfreqDist, 1)
        
        poweredPoly = [np.power(10, self.getPoly( self.__logx[i] ) ) for i in  range(len(self.__logx))]
        relativeErrors = [ abs( self.__freqDist.values()[i] - poweredPoly[i] )
                                        / float( self.__freqDist.values()[i] ) for i in  range(len(self.__logx)) ]
        
        self.__relZipfError = np.mean( relativeErrors ) * 100
        
    def prepareFreqDist(self, areBigramsChecked):
        
        if areBigramsChecked:
            return self.__sortedBigrams
        else:
            return self.__sortedLetters            
            
        
    def findForeignWords(self, rules):
        foreignWords = []
        if 'consonant' in rules:
            cond = re.compile('.*[qrtpsdfghlzcvbnm]$')
            foreignWords += [item for item in self.__freqDist.items() if cond.match(item[0])]
            
        if 'wyjkx' in rules:
            cond = re.compile('.*[wyjkx].*')
            foreignWords += [item for item in self.__freqDist.items() if cond.match(item[0])]
            
        self.__foreignWords = [item for item in foreignWords
                               if item[0] not in self.__allowedForeign]
        self.__foreignWordsCount = sum([word[1] for word in self.__foreignWords])

    def findPatternWords(self, pattern):
        
        try:
            cond = re.compile(unicode(pattern))
            self.__patternWords = [item for item in self.__freqDist.items() if cond.match(item[0])]
            self.__patternWordsCount = sum([word[1] for word in self.__patternWords])
            return 0
        except re.error:
            return -1
        
        
    def findWordContext(self, word, lines=25, wordCount=2):
        
        if not self.__concordanceIndex:
            self.__concordanceIndex = nltk.ConcordanceIndex([token for token in self.__tokens])
            
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
                
        path = 'D:\\Studia\\MGR\workspace\\SAIL\\Main\\'
        self.__customTags = dict()
        for line in codecs.open(path + 'manualTaggingRules.txt', encoding='utf-8').readlines():
            words = line.split()
            self.__customTags[words[0]] = set(words[1:])
            
        for i in range(len(self.__taggedTokens)):
            if self.__taggedTokens[i][1] == self.__defaultTag:
                for tag in self.__customTags:
                    if self.__taggedTokens[i][0].lower() in self.__customTags[tag]:
                        self.__taggedTokens[i] = (self.__taggedTokens[i][0], tag)

    def applyRegexTagger(self):
        
        path = 'D:\\Studia\\MGR\workspace\\SAIL\\Main\\'
        self.__regexTagRules = dict()
        for line in set(codecs.open(path + 'regexpTaggingRules.txt', encoding='utf-8').readlines()):
            if len(line)>4 and  line[0]!= '#':
                words = line.split()
                self.__regexTagRules[re.compile(unicode(words[1]))] = (words[0], words[2:])
        
        
        for i in range(len(self.__taggedTokens)):
            if self.__taggedTokens[i][1] == self.__defaultTag:
                for rule in self.__regexTagRules:
                    if self.__taggedTokens[i][1] == self.__defaultTag:
                        word = self.__taggedTokens[i][0].lower()
                        if word not in self.__regexTagRules[rule][1] and rule.match(word):
                            self.__taggedTokens[i] = (self.__taggedTokens[i][0], self.__regexTagRules[rule][0])
                        #if self.__taggedTokens[i][0].lower() in self.__customTags[tag]:
                        #    self.__taggedTokens[i] = (self.__taggedTokens[i][0], tag)
        
    def getTaggingRules(self, tagger):
        path = 'D:\\Studia\\MGR\workspace\\SAIL\\Main\\'
        #if tagger == "manual":
        f = codecs.open(path + tagger + 'TaggingRules.txt', encoding='utf-8')
        rules = f.read()
        f.close()
        return rules

    def setTaggingRules(self, tagger, rules):
        path = 'D:\\Studia\\MGR\workspace\\SAIL\\Main\\'
        f = codecs.open(path + tagger + 'TaggingRules.txt', 'w', encoding='utf-8' )
        f.seek(0)
        f.write(rules)
        f.truncate()
        f.close()
        
        
    def findCollocations(self):
        self.__collWords = []
        allowed = re.compile('[a-zA-Z0-9\xe0\xe1\xe8\xe9\xec\xed\xf2\xf3\xf9\xfa]+')
        special = re.compile('[&\"\*\+%\-/\.\,\?\:;\(\)!]+')
        
        for token in self.__tokens:
            #if token.lower() not in self.__ignoredColl and allowed.match(token):
            token = token.lower()
            if not special.match(token):
                self.__collWords.append(token)
        
        collocations = []
        for i in range(len(self.__collWords)-1):
            collocations.append((self.__collWords[i], self.__collWords[i+1]))
        
        
        
        path = 'D:\\Studia\\MGR\workspace\\SAIL\\Main\\'   
        output = codecs.open(path+'collocations.txt', 'w', encoding='utf-8') 
        self.__collFreqDist = FreqDist(collocations)
        for item in self.__collFreqDist.items():
            if item[1]>2:
                output.write(unicode(item[0][0]) + ' ' + unicode(item[0][1]) + ' ' + unicode(item[1]) + '\n')
            
        output.close()
            
        
            
