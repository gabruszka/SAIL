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

class MainWindow(QtGui.QMainWindow):
    
    def __init__(self, engine):
        self.engine = engine
        super(MainWindow, self).__init__()
        self.initUI()
        self.connectSlots()

    def initUI(self):
        self.ui = uic.loadUi("form.ui")
        self.ui.show()
        self.ui.tabWidget.setEnabled(False)
        self.ui.loadBtn.setEnabled(False)
        self.ui.POSloadBtn.setEnabled(False)
        self.ui.zipfFrame.setEnabled(False)
        self.ui.tagPOSCorpusRadio.setEnabled(False)
        
    def connectSlots(self):
        self.connect(self.ui.browseBtn, QtCore.SIGNAL("clicked()"), self.onSelectFile)
        self.connect(self.ui.loadBtn, QtCore.SIGNAL("clicked()"), self.onLoadCorpus)
        
        
        #Basic Data
        self.connect(self.ui.findMostCommonBtn, QtCore.SIGNAL("clicked()"), self.onFindMostCommon)
        self.connect(self.ui.ignoreListCommonBtn, 
                     QtCore.SIGNAL("clicked()"),
                     lambda: self.onIgnoreList('foreign', self.engine.get_ignored_common, self.engine.set_ignored_common))
        self.connect(self.ui.computeZipfBtn, QtCore.SIGNAL("clicked()"), self.onComputeZipf)
        self.connect(self.ui.ZipfPlotBtn, QtCore.SIGNAL("clicked()"), self.onZipfPlot)
        
        self.connect(self.ui.previewForeignBtn, QtCore.SIGNAL("clicked()"), self.onPreviewForeignWords)
        self.connect(self.ui.ignoreListForeignBtn, 
                     QtCore.SIGNAL("clicked()"),
                     lambda: self.onIgnoreList('foreign', self.engine.getAllowedForeignWordSet, self.engine.setAllowedForeignWordSet, self.onRefreshForeignWords))
        self.connect(self.ui.hapaxesBtn, QtCore.SIGNAL("clicked()"), self.onFindHapaxes)
        
        
        #POS tagging
        self.connect(self.ui.POSbrowseBtn, QtCore.SIGNAL("clicked()"), self.onPOSbrowse)
        self.connect(self.ui.POSloadBtn, QtCore.SIGNAL("clicked()"), self.onPOSload)
        self.connect(self.ui.applyTaggerBtn, QtCore.SIGNAL("clicked()"), self.onApplyTagger)
        #self.connect(self.ui.definePatternsBtn, QtCore.SIGNAL("clicked()"), self.onDefinePatterns)
        self.connect(self.ui.previewTaggingBtn, QtCore.SIGNAL("clicked()"), self.onPreviewTagging)
        
        #Custom Search
        self.connect(self.ui.findContextBtn, QtCore.SIGNAL("clicked()"), self.onFindContext)
        self.connect(self.ui.findPatternBtn, QtCore.SIGNAL("clicked()"), self.onFindPattern)
        
    def onLoadCorpus(self):
        
        self.ui.wordCount.setText("")
        self.ui.tabWidget.setEnabled(False)
        self.ui.loadBtn.setEnabled(False)
        self.ui.corpusText.setPlainText("")
        self.ui.taggedWordCount.setText("")
        self.ui.taggedPercentage.setText("")
        
        encoding = self.engine.loadCorpus(self.ui.corpusPath.text())
        
        if encoding != "":
            self.ui.tabWidget.setEnabled(True)
            self.ui.loadBtn.setEnabled(False)
            
            self.ui.encoding.setText(encoding)
            self.ui.wordCount.setText(str(self.engine.getWordCount()))
            self.ui.corpusText.setPlainText(self.engine.getRawText())
            #self.ui.rawText.setPlainText('\n'.join([token[0]+ '\t\t' + token[1] for token in self.engine.getTaggedTokens()]))
            self.ui.avgWordLength.setText(str(self.engine.getAvgWordLength()))
            self.ui.avgSentLength.setText(str(self.engine.getAvgSentLength()))
            self.ui.lexicalDiversity.setText(str(self.engine.getLexicalDiversity()))
            
            self.ui.wordTypesCount.setText(str(self.engine.getWordTypesCount()))
            self.ui.hapaxCount.setText(str(self.engine.getHapaxCount()))
            self.ui.hapaxPercentage.setText(str(self.engine.getHapaxPercentage()))
            
            self.onRefreshForeignWords()
        else:
            self.ui.encoding.setText("not recognized!")
        
    def onSelectFile(self):
        self.ui.corpusPath.setText(QtGui.QFileDialog.getOpenFileName())
        self.ui.loadBtn.setEnabled(True)
        
    def onRefreshForeignWords(self):
        self.engine.findForeignWords()
        self.ui.foreignWordsCount.setText(str(self.engine.getForeignWordsCount()))
        self.ui.foreignPercentage.setText(str(self.engine.getForeignPercentage()))
        
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
        layout = QtGui.QHBoxLayout(dialog)
        layout.addWidget(tableView)
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
        
        layout = QtGui.QHBoxLayout(dialog)
        layout.addWidget(tableView)
        
        dialog.setLayout(layout)
        dialog.show()
        
    def onDeleteFromCommonSet(self, words):
        self.engine.set_ignored_common(self.engine.get_ignored_common().union(set(words)))
        
    def onDeleteFromForeignSet(self, words):
        self.engine.setAllowedForeignWordSet(self.engine.getAllowedForeignWordSet().union(set(words)))
        self.onRefreshForeignWords()
        
    def onPreviewForeignWords(self):
    
        foreignWords = self.engine.getForeignWords()
        title = str(self.engine.getForeignWordsCount()) +' foreign words found'
        self.showTableDialog(foreignWords, title, ["Word", "Count"], self.onDeleteFromForeignSet)
        
    def onFindMostCommon(self):
        
        title = str(self.ui.mostCommonCount.value()) +' Most Common Words'
        mostCommon = self.engine.getMostCommon(self.ui.mostCommonCount.value())
        self.showTableDialog(mostCommon, title, ["Word", "Count"], self.onDeleteFromCommonSet)

    def onFindHapaxes(self):
        
        hapaxes = self.engine.getHapaxes()
        title = str(len(hapaxes)) +' Hapaxes'
        self.showListDialog(hapaxes, title, "Word")
        
    def onFindContext(self):
        if self.ui.contextWord.text() != "":
            contexts = self.engine.findWordContext(self.ui.contextWord.text(), self.ui.contextCount.value(), self.ui.contextLength.value())
            if contexts != []:
                title = str(len(contexts)) + ' contexts of \'' + self.ui.contextWord.text() + '\''
                self.showListDialog(contexts, title, "Context")
            else:
                self.noMatchesWindow()
           
    def onFindPattern(self):
        if self.ui.patternTxt.text() != "":
            words = self.engine.findPattern(self.ui.patternTxt.text())
            wordCount = sum([word[1] for word in words])
            percentage = round(wordCount*100/float(self.engine.getWordCount()), 2)
            self.ui.patternPercentage.setText(str(percentage))

            if words != []:
                title = str(wordCount) + ' words matching pattern \'' + self.ui.patternTxt.text() + '\''
                self.showTableDialog(words, title, ["Word", "Count"])
            else:
                self.noMatchesWindow()
            
    def onComputeZipf(self):
        self.ui.zipfFrame.setEnabled(True)
        input = ''
        if self.ui.wordZipfRadio.isChecked():
            input='word'
        if self.ui.bigramZipfRadio.isChecked():
            input='bigram'
        if self.ui.letterZipfRadio.isChecked():
            input='letter'
        
        self.engine.computeZipf(input)
        self.ui.ZipfTrend.setText( str( round(self.engine.getPolyFit()[0], 3) ) + 'x + ' + str( round( self.engine.getPolyFit()[1], 3) ) )
        self.ui.ZipfError.setText( str( round( self.engine.get_relZipfError(), 3 ) ) )
        
    def onZipfPlot(self):
        
        pg.setConfigOptions(antialias=True)
        dialog= QtGui.QDialog(self)
        plotWidget = pg.PlotWidget(name='Zipf\'s Law Plot')
        
        logx = self.engine.get_logx()
        ab = self.engine.getPolyFit()
        s = ScatterPlotItem(logx, self.engine.get_logfreqDist(), size=4, pen=None, brush=pg.mkBrush(255, 255, 255))
        s.addPoints(logx, self.engine.get_logfreqDist())
        plot = plotWidget.plot(logx, [self.engine.getPoly(x) for x in logx],  pen=(255,0,0), size=3)
        
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
        self.ui.POScorpusPath.setText(QtGui.QFileDialog.getOpenFileName())
        self.ui.POSloadBtn.setEnabled(True)
        
    def onPOSload(self):
        self.engine.loadPOSCorpus(self.ui.POScorpusPath.text())
        self.ui.corpusText.setPlainText('\n'.join([token[0]+ '\t\t' + token[1] for token in self.engine.getTaggedCorpus()]))
        self.ui.tagPOSCorpusRadio.setEnabled(True)
        
    def onApplyTagger(self):
        taggers = []
        if self.ui.manualTaggerChk.checkState():
            taggers.append('manual')
        if self.ui.regExTaggerChk.checkState():
            taggers.append('regex')
        if self.ui.syntaxTaggerChk.checkState():
            taggers.append('syntax')
        if self.ui.probabilityTaggerChk.checkState():
            taggers.append('probability')
            
        if taggers != []:
            self.engine.applyTaggers(taggers, self.ui.tagPOSCorpusRadio.isChecked())
            
            self.ui.taggedWordCount.setText(str(self.engine.getTagCount()))
            percentage = round(self.engine.getTagCount()*100/float(self.engine.getTaggedTokensCount()), 2)
            self.ui.taggedPercentage.setText(str(percentage))
            
            if self.ui.tagPOSCorpusRadio.isChecked():
                self.ui.wrongTagsCount.setText(str(self.engine.getTagErrorCount()))
                percentage = 0 if self.engine.getTagCount() == 0 else round(self.engine.getTagErrorCount()*100/float(self.engine.getTagCount()), 2)
                self.ui.wrongTagsPercentage.setText(str(percentage))
            else:
                self.ui.wrongTagsCount.setText("")
                self.ui.wrongTagsPercentage.setText("")
                
    def onPreviewTagging(self):
        self.ui.tokenizedText.setPlainText('\n'.join([token[0]+ '\t\t' + token[1] for token in self.engine.getTaggedTokens()]))
        
        
        
        
        
        
        
        