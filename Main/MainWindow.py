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
        
    def connectSlots(self):
        self.connect(self.ui.browseBtn, QtCore.SIGNAL("clicked()"), self.onSelectFile)
        self.connect(self.ui.loadBtn, QtCore.SIGNAL("clicked()"), self.onLoadCorpus)
        self.connect(self.ui.findMostCommonBtn, QtCore.SIGNAL("clicked()"), self.onFindMostCommon)
        self.connect(self.ui.hapaxesBtn, QtCore.SIGNAL("clicked()"), self.onFindHapaxes)
        self.connect(self.ui.findContextBtn, QtCore.SIGNAL("clicked()"), self.onFindContext)
        self.connect(self.ui.previewBtn, QtCore.SIGNAL("clicked()"), self.onPreviewForeignWords)
        self.connect(self.ui.ZipfPlotBtn, QtCore.SIGNAL("clicked()"), self.onZipfPlot)
        self.connect(self.ui.ignoreListForeignBtn, 
                     QtCore.SIGNAL("clicked()"),
                     lambda: self.onIgnoreList('foreign', self.engine.getAllowedForeignWordSet, self.engine.setAllowedForeignWordSet, self.onRefreshForeignWords))
        
        self.connect(self.ui.ignoreListCommonBtn, 
                     QtCore.SIGNAL("clicked()"),
                     lambda: self.onIgnoreList('foreign', self.engine.get_ignored_common, self.engine.set_ignored_common))
         
    def onLoadCorpus(self):
        
        self.ui.wordCount.setText("")
        self.ui.tabWidget.setEnabled(False)
        self.ui.loadBtn.setEnabled(False)
        self.ui.rawText.setPlainText("")
        
        self.engine.setPath(self.ui.corpusPath.text())
        encoding = self.engine.loadCorpus()
        
        if encoding != "":
            self.ui.tabWidget.setEnabled(True)
            self.ui.loadBtn.setEnabled(False)
            
            self.ui.encoding.setText(encoding)
            self.ui.wordCount.setText(str(self.engine.getWordCount()))
            self.ui.rawText.setPlainText(self.engine.getRawText())
            self.ui.avgLength.setText(str(self.engine.getAvgWordLength()))
            self.ui.lexicalDiversity.setText(str(self.engine.getLexicalDiversity()))
            self.ui.ZipfTrend.setText( str( round(self.engine.getPolyFit()[0], 3) ) + 'x + ' + str( round( self.engine.getPolyFit()[1], 3) ) )
            self.ui.ZipfError.setText( str( round( self.engine.get_absZipfError(), 3 ) ) + '%')
            self.onRefreshForeignWords()
        else:
            self.ui.encoding.setText("not recognized!")
        
    def onRefreshForeignWords(self):
        self.engine.findForeignWords()
        self.ui.foreignWordsCount.setText(str(self.engine.getForeignWords().N()))
        self.ui.foreignPercentage.setText(str(self.engine.getForeignPercentage()))
        
    def onSelectFile(self):
        self.ui.corpusPath.setText(QtGui.QFileDialog.getOpenFileName())
        self.ui.loadBtn.setEnabled(True)
        
    def onShow(self):
        dialog= QtGui.QDialog(self)
        dialog.setMinimumHeight(300)
        dialog.setWindowTitle("Corpus Text")
        
        plainText = QtGui.QPlainTextEdit()
        plainText.setPlainText(self.engine.getFullText())
        
        layout = QtGui.QHBoxLayout(dialog)
        layout.addWidget(plainText)
        dialog.setLayout(layout)
        dialog.show()
        
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
        title = str(foreignWords.N()) +' foreign words found'
        self.showTableDialog(foreignWords.items(), title, ["Word", "Count"], self.onDeleteFromForeignSet)
        
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
           
    def onZipfPlot(self):
        
        pg.setConfigOptions(antialias=True)
        dialog= QtGui.QDialog(self)
        plotWidget = pg.PlotWidget(name='Zipf\'s Law Plot')
        
        logx = self.engine.get_logx()
        ab = self.engine.getPolyFit()
        s4 = ScatterPlotItem(logx, self.engine.get_logfreqDist(), size=4, pen=None, brush=pg.mkBrush(255, 255, 255))
        s4.addPoints(logx, self.engine.get_logfreqDist())
        p1 = plotWidget.plot(logx, [self.engine.getPoly(x) for x in logx],  pen=(255,0,0), size=3)
        
        l = LegendItem((130,60), offset=(500,30))
        l.setParentItem(plotWidget.getPlotItem())
        l.addItem(s4, 'Corpus data')
        l.addItem(p1, str(round(ab[0], 3)) + 'x + ' +str(round(ab[1], 3)))
        
        plotWidget.addItem(s4)
        l = QtGui.QVBoxLayout()
        l.addWidget(plotWidget)
        
        dialog.setLayout(l)
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
        