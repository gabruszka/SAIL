'''
Created on 03-11-2013

@author: Gabco
'''
import pyqtgraph as pg
from pyqtgraph.graphicsItems.ScatterPlotItem import ScatterPlotItem
from pyqtgraph.graphicsItems.LegendItem import LegendItem

from PyQt4 import QtCore, QtGui, uic
from CustomWidgets import MyTableItem
from CustomWidgets import MyPlainTextEdit
from CustomWidgets import MyTableView
from CustomWidgets import MyDeletableTableView
import codecs

class Presenter(QtGui.QMainWindow):
    
    def __init__(self, model):
        self.model = model
        super(Presenter, self).__init__()
        self.initUI()
        self.connectSlots()

    def initUI(self):
        self.view = uic.loadUi("form.ui")
        self.view.show()
        self.view.tabWidget.setEnabled(False)
        self.view.loadBtn.setEnabled(False)
        self.view.POSloadBtn.setEnabled(False)
        self.view.zipfFrame.setEnabled(False)
        self.view.tagPOSCorpusRadio.setEnabled(False)
        
    def connectSlots(self):
        self.connect(self.view.browseBtn, QtCore.SIGNAL("clicked()"), self.onSelectFile)
        self.connect(self.view.loadBtn, QtCore.SIGNAL("clicked()"), self.onLoadCorpus)
        
        
        #Basic Data
        self.connect(self.view.findMostCommonBtn, QtCore.SIGNAL("clicked()"), self.onFindMostCommon)
        self.connect(self.view.ignoreListCommonBtn, 
                     QtCore.SIGNAL("clicked()"),
                     lambda: self.onIgnoreList('foreign', self.model.get_ignored_common, self.model.set_ignored_common))
        self.connect(self.view.computeZipfBtn, QtCore.SIGNAL("clicked()"), self.onComputeZipf)
        self.connect(self.view.ZipfPlotBtn, QtCore.SIGNAL("clicked()"), self.onZipfPlot)
        
        self.connect(self.view.previewForeignBtn, QtCore.SIGNAL("clicked()"), self.onPreviewForeignWords)
        self.connect(self.view.ignoreListForeignBtn, 
                     QtCore.SIGNAL("clicked()"),
                     lambda: self.onIgnoreList('foreign', self.model.getAllowedForeignWordSet, self.model.setAllowedForeignWordSet, self.onRefreshForeignWords))
        self.connect(self.view.hapaxesBtn, QtCore.SIGNAL("clicked()"), self.onFindHapaxes)
        
        
        #POS tagging
        self.connect(self.view.POSbrowseBtn, QtCore.SIGNAL("clicked()"), self.onPOSbrowse)
        self.connect(self.view.POSloadBtn, QtCore.SIGNAL("clicked()"), self.onPOSload)
        self.connect(self.view.applyTaggerBtn, QtCore.SIGNAL("clicked()"), self.onApplyTagger)
        #self.connect(self.view.definePatternsBtn, QtCore.SIGNAL("clicked()"), self.onDefinePatterns)
        self.connect(self.view.previewTaggingBtn, QtCore.SIGNAL("clicked()"), self.onPreviewTagging)
        
        #Custom Search
        self.connect(self.view.findContextBtn, QtCore.SIGNAL("clicked()"), self.onFindContext)
        self.connect(self.view.findPatternBtn, QtCore.SIGNAL("clicked()"), self.onFindPattern)
        
        #Collocations
        self.connect(self.view.findCollBtn, QtCore.SIGNAL("clicked()"), self.onFindColl)
        #self.connect(self.view.showCollBtn, QtCore.SIGNAL("clicked()"), self.onShowColl)
        
    def onLoadCorpus(self):
        
        self.view.wordCount.setText("")
        self.view.tabWidget.setEnabled(False)
        self.view.loadBtn.setEnabled(False)
        self.view.corpusText.setPlainText("")
        self.view.taggedWordCount.setText("")
        self.view.taggedPercentage.setText("")
        
        encoding = self.model.loadCorpus(self.view.corpusPath.text())
        
        if encoding != "":
            self.view.tabWidget.setEnabled(True)
            self.view.loadBtn.setEnabled(False)
            
            self.view.encoding.setText(encoding)
            self.view.wordCount.setText(str(self.model.getWordCount()))
            self.view.corpusText.setPlainText(self.model.getRawText())
            #self.view.rawText.setPlainText('\n'.join([token[0]+ '\t\t' + token[1] for token in self.model.getTaggedTokens()]))
            self.view.avgWordLength.setText(str(self.model.getAvgWordLength()))
            self.view.avgSentLength.setText(str(self.model.getAvgSentLength()))
            self.view.lexicalDiversity.setText(str(self.model.getLexicalDiversity()))
            
            self.view.wordTypesCount.setText(str(self.model.getWordTypesCount()))
            self.view.hapaxCount.setText(str(self.model.getHapaxCount()))
            self.view.hapaxPercentage.setText(str(self.model.getHapaxPercentage()))
            
            self.view.tokenizedText.setPlainText('\n'.join(self.model.getTokens()))
            
            self.onRefreshForeignWords()
        else:
            self.view.encoding.setText("not recognized!")
        
    def onSelectFile(self):
        self.view.corpusPath.setText(QtGui.QFileDialog.getOpenFileName())
        self.view.loadBtn.setEnabled(True)
        
    def onRefreshForeignWords(self):
        self.model.findForeignWords()
        self.view.foreignWordsCount.setText(str(self.model.getForeignWordsCount()))
        self.view.foreignPercentage.setText(str(self.model.getForeignPercentage()))
        
    def showTableDialog(self, data, windowTitle, headerList, onDeleteFromSet=None):
        
        dialog= QtGui.QDialog(self)
        dialog.setMinimumHeight(300)
        dialog.setWindowTitle(windowTitle)
        
        tableView = MyTableView(dialog)
        if onDeleteFromSet:
            tableView = MyDeletableTableView(dialog)
            tableView.registerDeleteHandler(onDeleteFromSet)
        else:
            tableView = MyTableView(dialog)
            
        model = QtGui.QStandardItemModel(tableView)
        
        for row in range(len(data)):
            itemList = []
            itemList.append(MyTableItem(data[row][0])) 
            for j in range(1, len(data[row])):
                itemList.append(MyTableItem(str(data[row][j])))
            model.appendRow(itemList)
                
        for column in range(len(headerList)):
            model.setHeaderData(column, QtCore.Qt.Horizontal, QtCore.QVariant(headerList[column]))
                        
        tableView.setModel(model)
        tableView.resizeColumnsToContents()
        
        saveToFile = QtGui.QPushButton("Save to File")
        
        self.connect(saveToFile, 
                     QtCore.SIGNAL("clicked()"),
                     lambda: self.onSaveToFile([line[0]+' ' + unicode(line[1]) + '\n' for line in data  ] ))
        
        
        layout = QtGui.QVBoxLayout(dialog)
        layout.addWidget(tableView)
        layout.addWidget(saveToFile)
        
        dialog.setLayout(layout)
        dialog.show()

    def showListDialog(self, data, windowTitle, headerTitle):
        
        dialog= QtGui.QDialog(self)
        dialog.setMinimumHeight(300)
        dialog.setWindowTitle(windowTitle)
        
        tableView = MyTableView(dialog)
         
        model = QtGui.QStandardItemModel(tableView)
        for row in range(len(data)):
            model.appendRow([MyTableItem(data[row])])
        model.setHeaderData(0, QtCore.Qt.Horizontal, QtCore.QVariant(headerTitle))
             
        tableView.setModel(model)
        tableView.resizeColumnsToContents()
        
        saveToFile = QtGui.QPushButton("Save to File")
        
        self.connect(saveToFile, 
                     QtCore.SIGNAL("clicked()"),
                     lambda: self.onSaveToFile(data))
        
        layout = QtGui.QVBoxLayout(dialog)
        layout.addWidget(tableView)
        layout.addWidget(saveToFile)
        
        dialog.setLayout(layout)
        dialog.show()
        
    def onSaveToFile(self, data):
        
        filename = QtGui.QFileDialog.getSaveFileName(self, 'Save to File', '.')
        fname = codecs.open(filename, 'w', encoding='utf-8')
        fname.writelines(data)
        fname.close() 
        
    def onDeleteFromCommonSet(self, words):
        self.model.set_ignored_common(self.model.get_ignored_common().union(set(words)))
        
    def onDeleteFromForeignSet(self, words):
        self.model.setAllowedForeignWordSet(self.model.getAllowedForeignWordSet().union(set(words)))
        self.onRefreshForeignWords()
        
    def onPreviewForeignWords(self):
    
        foreignWords = self.model.getForeignWords()
        title = str(self.model.getForeignWordsCount()) +' foreign words found'
        self.showTableDialog(foreignWords, title, ["Word", "Count"], self.onDeleteFromForeignSet)
        
    def onFindMostCommon(self):
        
        title = str(self.view.mostCommonCount.value()) +' Most Common Words'
        mostCommon = self.model.getMostCommon(self.view.mostCommonCount.value())
        self.showTableDialog(mostCommon, title, ["Word", "Count"], self.onDeleteFromCommonSet)

    def onFindHapaxes(self):
        
        hapaxes = self.model.getHapaxes()
        title = str(len(hapaxes)) +' Hapaxes'
        self.showListDialog(hapaxes, title, "Word")
        
    def onFindContext(self):
        if self.view.contextWord.text() != "":
            contexts = self.model.findWordContext(self.view.contextWord.text(), self.view.contextCount.value(), self.view.contextLength.value())
            if contexts != []:
                title = str(len(contexts)) + ' contexts of \'' + self.view.contextWord.text() + '\''
                self.showListDialog(contexts, title, "Context")
            else:
                self.noMatchesWindow()
           
    def onFindPattern(self):
        if self.view.patternTxt.text() != "":
            words = self.model.findPattern(self.view.patternTxt.text())
            wordCount = sum([word[1] for word in words])
            percentage = round(wordCount*100/float(self.model.getWordCount()), 2)
            self.view.patternPercentage.setText(str(percentage))

            if words != []:
                title = str(wordCount) + ' words matching pattern \'' + self.view.patternTxt.text() + '\''
                self.showTableDialog(words, title, ["Word", "Count"])
            else:
                self.noMatchesWindow()
            
    def onComputeZipf(self):
        self.view.zipfFrame.setEnabled(True)
        input = ''
        if self.view.wordZipfRadio.isChecked():
            input='word'
        if self.view.bigramZipfRadio.isChecked():
            input='bigram'
        if self.view.letterZipfRadio.isChecked():
            input='letter'
        
        self.model.computeZipf(input)
        self.view.ZipfTrend.setText( str( round(self.model.getPolyFit()[0], 3) ) + 'x + ' + str( round( self.model.getPolyFit()[1], 3) ) )
        self.view.ZipfError.setText( str( round( self.model.get_relZipfError(), 3 ) ) )
        
    def onZipfPlot(self):
        
        pg.setConfigOptions(antialias=True)
        dialog= QtGui.QDialog(self)
        plotWidget = pg.PlotWidget(name='Zipf\'s Law Plot')
        
        logx = self.model.get_logx()
        ab = self.model.getPolyFit()
        s = ScatterPlotItem(logx, self.model.get_logfreqDist(), size=4, pen=None, brush=pg.mkBrush(255, 255, 255))
        s.addPoints(logx, self.model.get_logfreqDist())
        plot = plotWidget.plot(logx, [self.model.getPoly(x) for x in logx],  pen=(255,0,0), size=3)
        
        legend = LegendItem((130,60), offset=(500,30))
        legend.setParentItem(plotWidget.getPlotItem())
        legend.addItem(s, 'Corpus data')
        legend.addItem(plot, str(round(ab[0], 3)) + 'x + ' +str(round(ab[1], 3)))
        
        plotWidget.addItem(s)
        lay = QtGui.QVBoxLayout()
        lay.addWidget(plotWidget)
        
        dialog.setLayout(lay)
        dialog.show()
                
    def onIgnoreList(self, title, getter, setter, func=None):
        
        dialog= QtGui.QDialog(self)
        dialog.setWindowTitle('List of ' + title + ' ignored words')
        
        plainText = MyPlainTextEdit(dialog)
        plainText.setPlainText(QtCore.QString('\n'.join(getter())))
        plainText.textChanged.connect(plainText.listChanged)
        
        okBtn = QtGui.QPushButton(dialog)
        okBtn.setText('Apply')
        okBtn.clicked.connect(dialog.close)
        okBtn.clicked.connect(lambda: self.onIgnoredWordSetClose(plainText.hasChanged, 
                                                                 set(str(plainText.toPlainText()).split()),
                                                                 getter,
                                                                 setter,
                                                                 func))
        
        layout = QtGui.QVBoxLayout()
        layout.addWidget(plainText)
        layout.addWidget(okBtn)
        
        dialog.setLayout(layout)
        dialog.show()
        
    def onIgnoredWordSetClose(self, hasChanged, newSet, getter, setter, func):
        if hasChanged:
            if getter() != newSet:
                setter(newSet)
                if func:
                    func()
        
    def noMatchesWindow(self):
        box= QtGui.QMessageBox(self)
        box.setText("No matches")
        box.setMinimumHeight(300)
        box.setWindowTitle("No matches")
        box.exec_()
        
    def onPOSbrowse(self):
        self.view.POScorpusPath.setText(QtGui.QFileDialog.getOpenFileName())
        self.view.POSloadBtn.setEnabled(True)
        
    def onPOSload(self):
        self.model.loadPOSCorpus(self.view.POScorpusPath.text())
        self.view.corpusText.setPlainText('\n'.join([token[0]+ '\t\t' + token[1] for token in self.model.getTaggedCorpus()]))
        self.view.tagPOSCorpusRadio.setEnabled(True)
        
    def onApplyTagger(self):
        taggers = []
        if self.view.manualTaggerChk.checkState():
            taggers.append('manual')
        if self.view.regExTaggerChk.checkState():
            taggers.append('regex')
        if self.view.syntaxTaggerChk.checkState():
            taggers.append('syntax')
        if self.view.probabilityTaggerChk.checkState():
            taggers.append('probability')
            
        if taggers != []:
            self.model.applyTaggers(taggers, self.view.tagPOSCorpusRadio.isChecked())
            
            self.view.taggedWordCount.setText(str(self.model.getTagCount()))
            percentage = round(self.model.getTagCount()*100/float(self.model.getTaggedTokensCount()), 2)
            self.view.taggedPercentage.setText(str(percentage))
            
            if self.view.tagPOSCorpusRadio.isChecked():
                self.view.wrongTagsCount.setText(str(self.model.getTagErrorCount()))
                percentage = 0 if self.model.getTagCount() == 0 else round(self.model.getTagErrorCount()*100/float(self.model.getTagCount()), 2)
                self.view.wrongTagsPercentage.setText(str(percentage))
            else:
                self.view.wrongTagsCount.setText("")
                self.view.wrongTagsPercentage.setText("")
                
    def onPreviewTagging(self):
        self.view.tokenizedText.setPlainText('\n'.join([token[0]+ '\t\t' + token[1] for token in self.model.getTaggedTokens()]))
        
        
        
    def onFindColl(self):

        self.model.findCollocations()
        
        
        
        
        
        
        