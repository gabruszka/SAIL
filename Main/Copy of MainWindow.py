'''
Created on 03-11-2013

@author: Gabco
'''
from PyQt4 import QtCore, QtGui, uic


class MyTableWidgetItem(QtGui.QTableWidgetItem):
    def __lt__(self, other):
        if ( isinstance(other, QtGui.QTableWidgetItem) ):
            my_value, my_ok = self.data(QtCore.Qt.EditRole).toInt()
            other_value, other_ok = other.data(QtCore.Qt.EditRole).toInt()

            if ( my_ok and other_ok ):
                return my_value < other_value

        return super(MyTableWidgetItem, self).__lt__(other)




class MainWindow(QtGui.QMainWindow):
    
    def __init__(self, engine):
        self.engine = engine
        super(MainWindow, self).__init__()
        self.initUI()
        self.connectSlots()
        #self.dialogsList = []
        
    def initUI(self):
        self.ui = uic.loadUi("form.ui")
        self.ui.show()
        self.ui.tabWidget.setEnabled(False)
        self.ui.load.setEnabled(False)
        
    def connectSlots(self):
        self.connect(self.ui.browse, QtCore.SIGNAL("clicked()"), self.onSelectFile)
        self.connect(self.ui.load, QtCore.SIGNAL("clicked()"), self.onLoadCorpus)
        self.connect(self.ui.findMostCommon, QtCore.SIGNAL("clicked()"), self.onFindMostCommon)
         
    def onLoadCorpus(self):
        self.engine.setPath(self.ui.corpusPath.text())
        self.engine.loadCorpus()
        self.ui.wordCount.setText(str(self.engine.getWordCount()))
        self.ui.tabWidget.setEnabled(True)
        self.ui.load.setEnabled(False)
        #self.ui.listWidget.addItems(self.engine.getTokens())
        
    def onSelectFile(self):
        self.ui.corpusPath.setText(QtGui.QFileDialog.getOpenFileName())
        self.ui.load.setEnabled(True)
        
    def onFindMostCommon(self):
        title = str(self.ui.mostCommonCount.value()) +' Most Common Words'
        
        
        dialog= QtGui.QDialog(self)
        dialog.setMinimumHeight(300)
        dialog.setFixedWidth(250)
        dialog.setWindowTitle(title)
        
        #=======================================================================
        # table = QtGui.QTableView(dialog)
        # table.setSelectionMode(3)
        # table.setFixedWidth(250)
        # table.setMinimumHeight(400)
        # table.setSortingEnabled(True)
        #=======================================================================
        mostCommon = self.engine.getMostCommon(self.ui.mostCommonCount.value())
        
        
        table = QtGui.QTableWidget(len(mostCommon), 2, dialog)
        table.setSelectionMode(3)
        table.setFixedWidth(250)
        table.setMinimumHeight(400)
        table.setSortingEnabled(True)
        
        #model = QtGui.QStandardItemModel(table)
        
        for i in range(len(mostCommon)):

            table.setItem(i, 0, MyTableWidgetItem(mostCommon[i][0]))
            table.setItem(i, 1, MyTableWidgetItem(str(mostCommon[i][1])))
            print mostCommon[i]
            #===================================================================
            # 
            # item =  MyTableWidgetItem()
            # item.setData(QtCore.Qt.DisplayRole, QtCore.QVariant(str(mostCommon[i][1])))
            # table.setItem(i, 1,item)
            #===================================================================
        
        #table.setModel(model)
        #table.setColumnWidth(1, 40)
        #table.setHorizontalHeaderLabels(['Word', 'Occurence'])
        dialog.show()        
        
        
        
        
        