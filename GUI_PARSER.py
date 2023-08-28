import sys
from PyQt5.QtWidgets import QFileDialog
from PyQt5 import QtCore,QtWidgets
from PyQt5.QtCore import QDir
from PyQt5.QtGui import QIcon,QFont
from PARSER import Parser,Point,Triangle,Rectangle
import re


class Ui(QtWidgets.QMainWindow):
    def __init__(self, *args, **kwargs):
        super(Ui,self).__init__(*args,**kwargs)
        self.two_files_selected = False
        self.BDF_filename = None
        self.excel_filename = None

        button_size = 150
        self.setWindowTitle('PARSER')
        self.setFixedSize(900, 600)
        gridLayout = QtWidgets.QGridLayout()
        widget = QtWidgets.QWidget()
        widget.setLayout(gridLayout)         
        self.setCentralWidget(widget)    
        ###TWORZYMY WIDGETY I USTAWIAMY JE###
        self.label = QtWidgets.QLabel(widget)
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setText("Wybierz pliki")
        #self.label.setFixedSize(button_size, button_size)
        gridLayout.addWidget(self.label, 0, 2) 
        
        self.pushButton1 = QtWidgets.QPushButton(widget)
        self.pushButton1.setText("Plik BDF")
        self.pushButton1.setFixedSize(button_size, button_size)
        self.pushButton1.clicked.connect(self.get_BDFfile)
        gridLayout.addWidget(self.pushButton1, 0, 0)

        self.pushButton2 = QtWidgets.QPushButton(widget)
        self.pushButton2.setText("Plik Excel")
        self.pushButton2.setFixedSize(button_size, button_size)
        self.pushButton2.clicked.connect(self.get_XLSXfile)
        gridLayout.addWidget(self.pushButton2, 0, 1)

        self.copyButton = QtWidgets.QPushButton(widget)
        self.copyButton.setText("Skopiuj pliki")
        self.copyButton.clicked.connect(self.copy_files)
        self.copyButton.setFixedSize(button_size, button_size)
        gridLayout.addWidget(self.copyButton, 1, 0)

        self.deleteButton = QtWidgets.QPushButton(widget)
        self.deleteButton.setText("Usuń stare pliki")
        self.deleteButton.clicked.connect(self.copy_files)
        self.deleteButton.setFixedSize(button_size, button_size)
        gridLayout.addWidget(self.deleteButton, 1, 1)

        self.testButton = QtWidgets.QPushButton(widget)
        self.testButton.setText("Test BAT")
        self.testButton.clicked.connect(self.copy_files)
        self.testButton.setFixedSize(button_size, button_size)
        gridLayout.addWidget(self.testButton, 1, 2)


    def get_BDFfile(self):   
        try:       
            self.BDF_filename, _ = QFileDialog.getOpenFileName(self, 'Choose BDF file', r"C:\Users\koste\OneDrive\Pulpit\ESATAN_PARSER", "BDF files (*.bdf)")
        except:
            pass
        # result = re.findall(r'[^\\]+',self.BDF_filename)
        # self.label.setText(f"Wybrano \n {result[-1]}")

        if self.are_files_selected():
            self.create_parser()

    def get_XLSXfile(self):   
        try:       
            self.excel_filename, _ = QFileDialog.getOpenFileName(self, 'Choose Excel file', r"C:\Users\koste\OneDrive\Pulpit\ESATAN_PARSER", "Excel files (*.xlsx)")
        except:
            pass
        # result = re.findall(r'[^\\]+',self.excel_filename)
        # self.label.setText(f"Wybrano \n {result[-1]}")

        if self.are_files_selected():
            self.create_parser()

    def create_parser(self):
        self.EsatanParser = Parser(self.BDF_filename, self.excel_filename)
        self.BDF_filename = None
        self.excel_filename = None

    def are_files_selected(self):
        return self.BDF_filename is not None and self.excel_filename is not None
    
    def copy_files(self):
            # Tutaj umieść kod do kopiowania plików
            # Możesz użyć funkcji shutil.copy() lub podobnych
        pass

    def delete_files(self):
        
            # Tutaj umieść kod do usuwania plików
            # Możesz użyć funkcji os.remove() lub podobnych
        pass

    def test_ERG(self):
        pass
    

if __name__ == '__main__':
    import sys
    app = QtWidgets.QApplication(sys.argv)
    ui = Ui()
    ui.show()
    sys.exit(app.exec_())