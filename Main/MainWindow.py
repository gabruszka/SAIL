'''
Created on 03-11-2013

@author: Gabco
'''
from PyQt4 import QtCore, QtGui, uic

class MyTableItem(QtGui.QStandardItem):
    def __lt__(self, other):
        if ( isinstance(other, QtGui.QStandardItem) ):
            my_value, my_ok = self.data(QtCore.Qt.EditRole).toInt()
            other_value, other_ok = other.data(QtCore.Qt.EditRole).toInt()

            if ( my_ok and other_ok ):
                return my_value < other_value

        return super(MyTableItem, self).__lt__(other)


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
        self.connect(self.ui.showBtn, QtCore.SIGNAL("clicked()"), self.onShow)
         
    def onLoadCorpus(self):
        self.engine.setPath(self.ui.corpusPath.text())
        self.engine.loadCorpus()
        self.ui.wordCount.setText(str(self.engine.getWordCount()))
        self.ui.tabWidget.setEnabled(True)
        self.ui.loadBtn.setEnabled(False)
        
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
        
        # wyswietlanie danych - jesli tabelka to stringi w pierwszej kolumnie parametru data, reszta liczbowo //do przemyslenia
        # jesli nie tabelka to lista danych (stringi)
    def showDataDialog(self, isTable, data, windowTitle, headerList, rowWidth=50):
        
        dialog= QtGui.QDialog(self)
        
        dialog.setMinimumHeight(300)
        dialog.setWindowTitle(windowTitle)
        
        tableView = QtGui.QTableView(dialog)
        tableView.setSelectionMode(3)
        tableView.setMinimumHeight(400)
        tableView.setSortingEnabled(True)

        model = QtGui.QStandardItemModel(tableView)
        
        if isTable:
            dialog.setFixedWidth(250)
            tableView.setFixedWidth(150 + rowWidth*(len(data)-1))
            for column in range(len(data)):
                
                tableView.setColumnWidth(column, 40)
                itemList = []
                itemList.append(MyTableItem(data[column][0]))
                for j in range(1, len(data[column])):
                    itemList.append(MyTableItem(str(data[column][j])))
                model.appendRow(itemList)
                
        else:
            tableView.setColumnWidth(1, rowWidth)
            dialog.setFixedWidth(200+rowWidth)
            tableView.setFixedWidth(150+rowWidth)
            for i in range(len(data)):
    
                itemList = []
                itemList.append(MyTableItem(data[i]))
                model.appendRow(itemList)
                
        for i in range(len(headerList)):
            model.setHeaderData(i, QtCore.Qt.Horizontal, QtCore.QVariant(headerList[i]))
            
        tableView.setModel(model)
        tableView.setColumnWidth(1, rowWidth)
        tableView.horizontalHeader().setResizeMode(QtGui.QHeaderView.Stretch)
        layout = QtGui.QHBoxLayout(dialog)
        layout.addWidget(tableView)
        dialog.setLayout(layout)
        dialog.show()
        
    def noMatchesWindow(self):
        box= QtGui.QMessageBox(self)
        box.setText("No matches")
        box.setMinimumHeight(300)
        box.setWindowTitle("No matches")
        
        box.exec_()
        
        
    def onFindMostCommon(self):
        
        title = str(self.ui.mostCommonCount.value()) +' Most Common Words'
        mostCommon = self.engine.getMostCommon(self.ui.mostCommonCount.value())
        self.showDataDialog(True, mostCommon, title, ["Word", "Count"])

    def onFindHapaxes(self):
        
        hapaxes = self.engine.getHapaxes()
        title = str(len(hapaxes)) +' Hapaxes'
        self.showDataDialog(False, hapaxes, title, ["Word"])
        
    def onFindContext(self):
        if self.ui.contextWord.text() != "":
            contexts = self.engine.findWordContext(self.ui.contextWord.text(), self.ui.wordsOnLeft.value(), self.ui.wordsOnRight.value(), self.ui.contextCount.value())
            if contexts != []:
                title = str(self.ui.contextCount.value()) + ' contexts of \'' + self.ui.contextWord.text() + '\''
                self.showDataDialog(False, contexts, title, ["Context"], 300)
            else:
                self.noMatchesWindow()