import sys
#from nltk.corpus import PlaintextCorpusReader
from PyQt4 import QtGui
from MainWindow import MainWindow
from Engine import Engine

def main():
    
    app = QtGui.QApplication(sys.argv)
    engine = Engine()

    win = MainWindow(engine)
    app.exec_()



if __name__ == '__main__':
    sys.exit(main())
