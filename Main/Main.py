import sys

from PyQt4 import QtGui
from Presenter import Presenter
from Model import Model

def main():
     
    app = QtGui.QApplication(sys.argv)
    model = Model()
 
    win = Presenter(model)
    app.exec_()
 
if __name__ == '__main__':
    sys.exit(main())
