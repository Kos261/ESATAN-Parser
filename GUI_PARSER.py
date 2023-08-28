import sys
from PyQt5.QtWidgets import QFileDialog
from PyQt5 import QtCore,QtWidgets
from PyQt5.QtCore import QDir
from PyQt5.QtGui import QIcon,QFont
from PARSER import Parser,Point,Triangle,Rectangle


class Ui(QtWidgets.QMainWindow):
    def __init__(self, *args, **kwargs):
        super(Ui,self).__init__(*args,**kwargs)
        self.setWindowTitle('PARSER')
        self.setFixedSize(400, 300)
        self.BDF_filename = None
        self.excel_filename = None
        HLayout =  QtWidgets.QHBoxLayout()
        widget = QtWidgets.QWidget()
        widget.setLayout(HLayout)         
        self.setCentralWidget(widget)    
        ###TWORZYMY WIDGETY I USTAWIAMY JE###

        self.pushButton1 = QtWidgets.QPushButton(widget)
        self.pushButton1.setText("Plik BDF")
        self.pushButton1.clicked.connect(self.get_BDFfile)
        HLayout.addWidget(self.pushButton1)

        self.pushButton2 = QtWidgets.QPushButton(widget)
        self.pushButton2.setText("Plik Excel")
        self.pushButton2.clicked.connect(self.get_XLSXfile)
        HLayout.addWidget(self.pushButton2)

    def get_BDFfile(self):   
        try:       
            self.BDF_filename, _ = QFileDialog.getOpenFileName(self,'Choose BDF file',r"C:\Users\koste\OneDrive\Pulpit\ESATAN_PARSER","BDF files (*.bdf)")
        except:
            pass
        if self.are_files_selected():
            self.EsatanParser = Parser(self.BDF_filename,self.excel_filename)
        return self.BDF_filename
    
    def get_XLSXfile(self):   
        try:       
            self.excel_filename, _ = QFileDialog.getOpenFileName(self,'Choose Excel file',r"C:\Users\koste\OneDrive\Pulpit\ESATAN_PARSER","Excel files (*.xlsx)")
        except:
            pass
        if self.are_files_selected():
            self.EsatanParser = Parser(self.BDF_filename,self.excel_filename)
        return self.excel_filename
    
    def are_files_selected(self):
        return self.BDF_filename is not None and self.excel_filename is not None
    
if __name__ == '__main__':
    import sys
    app = QtWidgets.QApplication(sys.argv)
    ui = Ui()
    ui.show()
    sys.exit(app.exec_())