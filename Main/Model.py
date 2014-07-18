#!/usr/bin/env python
# -*- coding: UTF-8 -*-
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
from nltk.collocations import BigramCollocationFinder
from nltk.util import ingrams
import nltk
import codecs
import itertools
from operator import itemgetter

class MyBigramCollFinder(BigramCollocationFinder):
    def getBigramFd(self):
        return self.ngram_fd

class SyntaxTaggingRule():
    def __init__(self, before, word, after):
        self.before = before
        self.tag = word
        self.after = after

def customWordtokenize(text):
    
        text = re.sub(ur'[\'\<\>`’“”«»]', ' ', text)
        
        #starting quotes
        text = re.sub(r'([ (\[{<])"', r'\1 " ', text)

        #punctuation
        text = re.sub(r'([:,])([^\d])', r' \1 \2', text)
        text = re.sub(r'\.\.\.', r' ... ', text)
        text = re.sub(r'[;@#$%&]', r' \g<0> ', text)
        text = re.sub(r'([^\.])(\.)([\]\)}>"\']*)\s*$', r'\1 \2\3 ', text)
        text = re.sub(r'[?!]', r' \g<0> ', text)
        

        #text = re.sub(r"([^'])' ", r"\1 ' ", text)

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
        self.__defaultTag = ''
        self.__defTagger = nltk.DefaultTagger(self.__defaultTag)
        self.__tags = {'NOUN', 'ADV', 'ADJ', 'PRON', 'DPREP', 'VERB', 'NUM', 'PREP', 'ART', 'CONJ', 'PRONVERB', 'PUNCT', 'SPECIAL'}
        self.__manualTags = {tag: set() for tag in self.__tags}
#                              'ADJ': set(),
#                              'ADV': set(),
#                              'ART': set(),
#                              'CONJ': set(),
#                              'DPREP': set(),
#                              'NOUN': set(),
#                              'NUM': set(),
#                              'PREP': set(),
#                              'PUNCT': set(),
#                              'PRON': set(),
#                              'PRONVERB': set(),
#                              'SPECIAL': set(),
#                              'VERB': set()                             
#                             }
        self.__tmpPath = 'D:\\Studia\\MGR\workspace\\SAIL\\Main\\'
        self.parseSyntaxRules()
        
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

        self.__allowedForeign = set(codecs.open(self.__tmpPath + 'allowedForeign.txt', encoding='utf-8').read().split())
        self.__ignoredCommon = set([])
        self.__ignoredColl = set(codecs.open(self.__tmpPath + 'ignoredColl.txt', encoding='utf-8').read().split())
        self.__concordanceIndex = None
        #self.__syntaxRules = []
        
        
    ################################
    #                              #
    #           GETTERS            #
    #                              #
    ################################
        
    ######### GENERAL DATA #########
    def getSentences(self):
        return self.__sentences
        
    def getTokens(self):
        return self.__tokens
        
    def getRawText(self):
        return self.__rawText
        
    def getWordCount(self):
        return self.__wordCount
        
    def getWordTypesCount(self):
        return len(self.__freqDist.items())
        
    def getAvgWordLength(self):
        return self.__avgWordLength
    
    def getAvgSentLength(self):
        return self.__avgSentLength
    
    def getLexicalDiversity(self):
        return self.__lexicalDiversity
        
    ######### FREQUENCY TAB #########
    def getIgnoredCommon(self):
        return self.__ignoredCommon

    def setIgnoredCommon(self, value):
        self.__ignoredCommon = value

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
    
    def getHapaxPercentage(self):
        return round(len(self.__freqDist.hapaxes())*100/float(len(self.__freqDist.items())), 2)
    
        ### ZIPF'S PLOT
    def getRelZipfError(self):
        return self.__relZipfError

    def getLogfreqDist(self):
        return self.__logfreqDist

    def getLogX(self):
        return self.__logx

    def getPoly(self, x):
        return np.poly1d(self.__polyFit)(x)

    def getPolyFit(self):
        return self.__polyFit
    
    
    ########## PATTERNS TAB #########
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
    
    
    
    ### PARTS OF SPEECH TAGGING TAB
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
        
    def getWrongTags(self):
        return self.__wrongTags
        
    ####### COLLOCATIONS TAB ######
    
    def getIgnoredColl(self):
        return self.__ignoredColl

    def setIgnoredColl(self, value):
        self.__ignoredColl = value

    def getCollocations(self):
        #return [(unicode(x[0]+' '+x[1]),y) for x,y in self.__collocations]
        return self.__collocations
        
    ################################
    #                              #
    #           METHODS            #
    #                              #
    ################################
        
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
            # more abbreviations with dots
            punkt_param = PunktParameters()
            punkt_param.abbrev_types = set(['dr', 'vs', 'n', 'v', 'etc', 'art', 'p', 'Cost', 'ss', 'pag'])
            
            punkt_param = PunktParameters()
            sentence_splitter = PunktSentenceTokenizer(punkt_param)
            text = re.sub(ur'[\'\<\>`’]', ' ', self.__rawText)
            #text = re.sub('(\d+)', r' \1 ', text)
            sentences = sentence_splitter.tokenize(text)
            
            #TOKENS
            self.__tokens = list(itertools.chain(*[ customWordtokenize(sent) for sent in sentences]))
            #wordTokenizer = RegexpTokenizer('[a-zA-Z0-9\xe0\xe1\xe8\xe9\xec\xed\xf2\xf3\xf9\xfa]+')
            
            
            wordTokenizer = RegexpTokenizer('[\w]+')
            
            
            sentences = [wordTokenizer.tokenize(sent.lower()) for sent in sentences if len(wordTokenizer.tokenize(sent)) > 0]
            words =  list(itertools.chain(*sentences))
            self.__words = words
            self.__sentences = sentences
            
            self.__avgSentLength = round(np.mean( [len(sent) for sent in sentences]), 3)
            self.__avgWordLength = round(np.mean( [len(word) for word in words]), 3)
            self.__freqDist = FreqDist(words)
            self.__wordCount = len(words)
            self.__lexicalDiversity = round(len(self.__freqDist.items())/float(len(words)), 3)
        
            ### resetting members
            self.__concordanceIndex = None
            self.__bigrams = None
                 
        return encoding
    
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
                        print "Key error on token: ", token

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
                        print "Key Error on token: ", token
                        
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
          
          
    ######### PATTERNS TAB ###########
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


    ######## PARTS OF SPEECH TAGGING TAB ##########
    
    def loadPOSCorpus(self, path):
        
        for encoding in self.__encodings:
            try:
                POSfile = codecs.open(path,'r',encoding=encoding)
                POScorpus = []
                for line in POSfile.readlines():
                    words = line.split()
                    if len(words) > 1:
                        if words[1] in {'NOUN', 'ADV', 'ADJ', 'PRON', 'DPREP', 'VERB', 'NUM', 'PREP', 'ART', 'CONJ', 'PRONVERB', 'PUNCT', 'SPECIAL'}:
                            POScorpus.append((words[0], words[1]))
                        else:
                            print 'Unknown tag!: ' + words[1]
                POSfile.close()
                break
            except UnicodeDecodeError:
                print 'UnicodeDecodeError'
                 
            except UnicodeEncodeError:
                print 'UnicodeEncodeError'
                
        self.__taggedCorpus = POScorpus
        
    def applyTaggers(self, taggers, fromPOSCorpus = False):
        
        self.resetTags(fromPOSCorpus)
            
        for tagger in taggers:
            if tagger == 'manual':
                self.applyManualTagger()
            if tagger == 'regex':
                self.applyRegexTagger()
            if tagger == 'syntax':
                self.applySyntaxTagger()
            if tagger == 'probability':
                self.applyProbabilityTagger()
                
        tagCount = 0
        notTagged = []
        self.__wrongTags = []
        if fromPOSCorpus:
            errorCount = 0
            #wrongTags = []
            for i  in range(len(self.__taggedTokens)):
                if self.__taggedTokens[i][1]!=self.__defaultTag:
                    tagCount+=1
                    if self.__taggedTokens[i][1] != self.__taggedCorpus[i][1]:
                        errorCount+=1
                        #wrongTags.append((i, self.__taggedTokens[i][0], self.__taggedTokens[i][1], self.__taggedCorpus[i][1]))
                        self.__wrongTags.append([self.__taggedTokens[i][0], self.__taggedTokens[i][1], self.__taggedCorpus[i][1]])
                else:
                    notTagged.append(self.__taggedTokens[i][0])
                    
            self.__tagErrorCount = errorCount
                   
        else:
            for token in self.__taggedTokens:
                if token[1]!=self.__defaultTag:
                    tagCount+=1
                else:
                    notTagged.append(token[0])
        self.__tagCount = tagCount
            
    def resetTags(self, fromPOSCorpus):
        if fromPOSCorpus:
            self.__taggedTokens = self.__defTagger.tag([token[0] for token in self.__taggedCorpus])
        else:
            self.__taggedTokens = self.__defTagger.tag(self.__tokens)

    def applyManualTagger(self):

        for line in codecs.open(self.__tmpPath + 'manualTaggingRules.txt', encoding='utf-8').readlines():
            if len(line)>4 and  line[0]!= '#':
                words = line.split()
                self.__manualTags[words[0]] = self.__manualTags[words[0]].union(set(words[1:]))
            
        for i in range(len(self.__taggedTokens)):
            if self.__taggedTokens[i][1] == self.__defaultTag:
                for tag in self.__manualTags:
                    if self.__taggedTokens[i][0].lower() in self.__manualTags[tag]:
                        self.__taggedTokens[i] = (self.__taggedTokens[i][0], tag)

    def applyRegexTagger(self):
        
        self.__regexTagRules = dict()
        for line in set(codecs.open(self.__tmpPath + 'regexpTaggingRules.txt', encoding='utf-8').readlines()):
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

    def parseSyntaxRules(self):
        self.__syntaxTagRules = []
        for line in set(codecs.open(self.__tmpPath + 'syntaxTaggingRules.txt', encoding='utf-8').readlines()):
            if line[0]!= '#':
                words = line.split()
                before = []
                after = []
                insertedTag = ""
                i = 0
                for i in range(0, len(words)):
                    if words[i][0] == '$':
                        insertedTag = words[i][1:]
                        break
                    before.append(words[i])
                for j in range(i+1, len(words)):
                    after.append(words[j])
                if (insertedTag!="" and (before!=[] or after!=[])):
                    self.__syntaxTagRules.append(SyntaxTaggingRule(before, insertedTag, after))

    def applySyntaxTagger(self):
        self.parseSyntaxRules()
        for i in range(len(self.__taggedTokens)):
            if self.__taggedTokens[i][1] == self.__defaultTag:
                
                for rule in self.__syntaxTagRules:
                    #rule lenghts check
                    if i >= len(rule.before) and len(self.__taggedTokens) - i >= len(rule.after):
                        poniechaj = False
                        tagsCount = len(rule.before)

                        for before_it in range(tagsCount):
                            if rule.before[before_it] in self.__tags:
                                if self.__taggedTokens[i - tagsCount + before_it][1] != rule.before[before_it]:
                                    poniechaj = True
                            else:
                                if self.__taggedTokens[i - tagsCount + before_it][0] != rule.before[before_it]:
                                    poniechaj = True
                                    
                        if (poniechaj):
                            continue
                        
                        for after_it in range(len(rule.after)):
                            if rule.after[after_it] in self.__tags:
                                if rule.after[after_it] != self.__taggedTokens[i + 1 + after_it][1]:
                                    poniechaj = True
                            else:
                                if rule.after[after_it] != self.__taggedTokens[i + 1 + after_it][0]:
                                    poniechaj = True
                                
                        if (poniechaj):
                            continue
                                
                        self.__taggedTokens[i] = (self.__taggedTokens[i][0], rule.tag)
                        break
        
    def findMostCommonTag(self):
        tagsFreqDistMap = dict()
        for word in self.__taggedCorpus:
            if word[0] not in tagsFreqDistMap.keys():
                tagsFreqDistMap[word[0]] = FreqDist([word[1]])
            else:
                tagsFreqDistMap[word[0]].inc(word[1])
        
        self.__mostCommonTagMap = dict()
        for word in tagsFreqDistMap.keys():
            self.__mostCommonTagMap[word] = tagsFreqDistMap[word].keys()[0]
        
    def applyProbabilityTagger(self):
        self.findMostCommonTag()
        
        for i in range(len(self.__taggedTokens)):
            if self.__taggedTokens[i][1] == self.__defaultTag:
                if self.__taggedTokens[i][0] in self.__mostCommonTagMap.keys():
                    self.__taggedTokens[i] = (self.__taggedTokens[i][0], self.__mostCommonTagMap[self.__taggedTokens[i][0]])
        
    def getTaggingRules(self, tagger):
        f = codecs.open(self.__tmpPath + tagger + 'TaggingRules.txt', encoding='utf-8')
        rules = f.read()
        f.close()
        return rules

    def setTaggingRules(self, tagger, rules):
        f = codecs.open(self.__tmpPath + tagger + 'TaggingRules.txt', 'w', encoding='utf-8' )
        f.seek(0)
        f.write(rules)
        f.truncate()
        f.close()
        
    ########## COLLOCATIONS TAB ############
    
    def findCollocations(self, test, window, min_freq, count, searchedWord):
        print searchedWord
        if self.__bigrams == None or self.__currentWindow != window or self.__currentSearchedWord != searchedWord:
            self.prepareBigrams(window, searchedWord)
            #self.__bigrams = BigramCollocationFinder.from_words(self.__words, window)
            
        self.__bigrams.apply_freq_filter(min_freq)
        self.__currentWindow = window
        self.__currentSearchedWord = searchedWord
        
        bfd = self.__bigrams.getBigramFd()
        scored_bigrams = []
        bigram_measures = nltk.collocations.BigramAssocMeasures()
        print bfd
        if test == 'Raw Frequency':
            scored_bigrams = self.__bigrams.score_ngrams(bigram_measures.raw_freq)[:count]
            
        if test == 'T Student Test':
            scored_bigrams = self.__bigrams.score_ngrams(bigram_measures.student_t)[:count]
            
        if test == 'Pearson Test':
            scored_bigrams = self.__bigrams.score_ngrams(bigram_measures.chi_sq)[:count]
            
        if test == 'Pointwise Mutual Information':
            scored_bigrams = self.__bigrams.score_ngrams(bigram_measures.pmi)[:count]
            
        if test == 'Dice':
            scored_bigrams = self.__bigrams.score_ngrams(bigram_measures.dice)[:count]
            
        if test == 'Jaccard':
            scored_bigrams = self.__bigrams.score_ngrams(bigram_measures.jaccard)[:count]

        if test == 'Likelihood Ratio':
            scored_bigrams = self.__bigrams.score_ngrams(bigram_measures.likelihood_ratio)[:count]
            
        if test == 'Variant of Mutual Information':
            scored_bigrams = self.__bigrams.score_ngrams(bigram_measures.mi_like)[:count]
            
        if test == 'Poisson Stirling':
            scored_bigrams = self.__bigrams.score_ngrams(bigram_measures.poisson_stirling)[:count]
            
        if test == 'Phi square':
            scored_bigrams = self.__bigrams.score_ngrams(bigram_measures.phi_sq)[:count]
            
        self.__collocations = [[unicode(x[0]+' '+x[1]), y, bfd[x]] for x,y in scored_bigrams]

    def prepareBigrams(self, window_size, word):
        wfd = FreqDist()
        bfd = FreqDist()
        
        if word == '':
            for sentence in self.__sentences:
                if len(sentence) > 1:
                    for window in ingrams(sentence, window_size, pad_right=True):
                        if window[0] not in self.__ignoredColl:
                            w1 = window[0]
                            try:
                                window = window[:list(window).index(w1, 1)]
                            except ValueError:
                                pass
                            wfd.inc(w1)
                            for w2 in set(window[1:]):
                                if w2 is not None and w2 not in self.__ignoredColl:
                                    bfd.inc((w1, w2))
        else:
            for sentence in self.__sentences:
                if len(sentence) > 1:
                    for window in ingrams(sentence, window_size, pad_right=True):
                        if window[0] not in self.__ignoredColl:
                            w1 = window[0]
                            try:
                                window = window[:list(window).index(w1, 1)]
                            except ValueError:
                                pass
                            bigramOK = False
                            for w2 in set(window[1:]):
                                if w2 is not None and w2 not in self.__ignoredColl and (w1 == word or w2==word):
                                    bfd.inc((w1, w2))
                                    bigramOK = True
                            if bigramOK:
                                wfd.inc(w1)
                                
        self.__bigrams = MyBigramCollFinder(wfd, bfd)

    ######### CONTEXT TAB ###########
    def findWordContext(self, word, lines=25, wordCount=2):
        
        if not self.__concordanceIndex:
            self.__concordanceIndex = nltk.ConcordanceIndex([token for token in self.__tokens],
                                                            key=lambda s:s.lower())
            
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
