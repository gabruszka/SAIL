'''
Created on 07-02-2014

@author: Gabco
'''

from PyQt4 import QtCore, QtGui

class MyTableItem(QtGui.QStandardItem):
    
    def __init__(self, parent):
        super(MyTableItem, self).__init__(parent)
    
    def __lt__(self, other):
        if ( isinstance(other, QtGui.QStandardItem) ):
            my_value, my_ok = self.data(QtCore.Qt.EditRole).toInt()
            other_value, other_ok = other.data(QtCore.Qt.EditRole).toInt()

            if ( my_ok and other_ok ):
                return my_value < other_value

        return super(MyTableItem, self).__lt__(other)

class MyPlainTextEdit(QtGui.QPlainTextEdit):
    def __init__(self, parent):
        super(MyPlainTextEdit, self).__init__(parent)
        self.changed = False
        
    def listChanged(self):
        self.changed = True
    
    def hasChanged(self):
        return self.changed
    
    
class MyTableView(QtGui.QTableView):
    def __init__(self, parent):
        super(MyTableView, self).__init__(parent)
        self.setMinimumHeight(400)
        self.setSortingEnabled(True)
        self.verticalHeader().setDefaultSectionSize(20)
        self.horizontalHeader().setResizeMode(QtGui.QHeaderView.Stretch)
            
    
class MyDeletableTableView(MyTableView):
    def __init__(self, parent):
        super(MyDeletableTableView, self).__init__(parent)
        self.deleteHandler = None
    
    def registerDeleteHandler(self, func):
        self.deleteHandler = func

    def keyPressEvent(self, e):
        if e.key() == QtCore.Qt.Key_Delete and self.deleteHandler and self.selectionModel().selectedIndexes() :
            deletedWords = []
            for index in self.selectionModel().selectedIndexes():
                deletedWords.append(unicode(self.model().data(index).toString())) 
            self.model().removeRows(self.selectionModel().selectedIndexes()[0].row(), len(self.selectionModel().selectedIndexes()))
            
            self.deleteHandler(deletedWords)
    